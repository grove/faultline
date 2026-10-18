"""One separately authorized, pinned setup-v2 recovery. Never starts a service."""

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location('setup_identity', HERE / 'apple_container_service_setup.py')
identity = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(identity)
PLAN = HERE / '2026-10-18-apple-container-recovery-plan.json'
PLAN_SHA256 = 'f727a96cbea4ac6751aa00894049c35b5c1b0d5a8206e36757f96734f643f9a9'
ENV = {'PATH': '/usr/bin:/bin', 'LC_ALL': 'C'}
DOMAINS = ('system', 'user/501', 'gui/501')
JOURNAL = Path('/private/tmp/faultline-apple-positive-v2/evidence/recovery-setup-v2-01.jsonl')


def command(argv):
    # shortcut: capture trusts finite CLI metadata; stream before adding untrusted output.
    result = subprocess.run(argv, cwd='/', env=ENV, stdin=subprocess.DEVNULL,
                            capture_output=True, timeout=5)
    empty = argv[0] == '/usr/sbin/lsof' and result.returncode == 1 and not result.stdout
    if (result.returncode != 0 and not empty) or result.stderr or len(result.stdout) > 4194304:
        raise ValueError('Recovery command failed or observation incomplete: ' + str(argv))
    return result.stdout.decode('utf-8', 'strict')


def inspect_service(entry, run=command):
    target = entry['target']
    text = run(['/bin/launchctl', 'print', target])
    owned = identity.owned_plist(text, target)
    pid = re.findall(r'^\tpid = (\d+)$', text, re.M)
    state = re.findall(r'^\tstate = (.+)$', text, re.M)
    roots = {}
    for name in ('CONTAINER_APP_ROOT', 'CONTAINER_INSTALL_ROOT'):
        values = re.findall(r'^\t\t' + name + r' => (.+)$', text, re.M)
        if len(values) != 1:
            raise ValueError('Missing/ambiguous effective service root')
        roots[name] = values[0]
    if (owned != entry['identity'] or pid != [str(entry['pid'])] or state != ['running'] or
            not identity.same_path(roots['CONTAINER_APP_ROOT'], identity.ENV['CONTAINER_APP_ROOT']) or
            not identity.same_path(roots['CONTAINER_INSTALL_ROOT'], '/usr/local')):
        raise ValueError('Live service identity changed; no removal')
    executable = Path(owned['executable'])
    with executable.open('rb') as source:
        digest = hashlib.file_digest(source, 'sha256').hexdigest()
    if digest != entry['executable_sha256']:
        raise ValueError('Executable bytes changed; no removal')
    return {'target': target, 'pid': int(pid[0]), 'identity': owned, 'effective_roots': roots}


def registrations(run=command):
    return {domain: identity.domain_names(run(['/bin/launchctl', 'print', domain]), domain)
            for domain in DOMAINS}


def processes(entries, run=command):
    text = run(['/bin/ps', '-ww', '-axo', 'pid=,uid=,lstart=,comm='])
    pids = {entry['pid'] for entry in entries}
    executables = {entry['identity']['executable'] for entry in entries}
    names = {Path(path).name for path in executables}
    found = []
    for row in text.splitlines():
        fields = row.split(maxsplit=7)
        if len(fields) != 8 or not fields[0].isdigit() or not fields[1].isdigit():
            raise ValueError('Unrecognized process observation')
        pid, uid = int(fields[0]), int(fields[1])
        program = fields[7]
        if pid in pids or (uid == 501 and Path(program).name in names):
            found.append({'pid': pid, 'uid': uid, 'started': ' '.join(fields[2:7]), 'executable': program})
    return found


def listeners(run=command):
    text = run(['/usr/sbin/lsof', '-nP', '-i:1053,2053', '-F', 'pPn'])
    found = []
    pid = protocol = None
    for line in text.splitlines():
        if line.startswith('p'):
            pid = int(line[1:])
        elif line.startswith('f'):
            protocol = None
        elif line.startswith('P'):
            protocol = line[1:]
        elif line.startswith('n'):
            if pid is None or protocol is None:
                raise ValueError('Incomplete network observation')
            found.append({'pid': pid, 'protocol': protocol, 'address': line[1:]})
        elif line:
            raise ValueError('Unrecognized network observation')
    return sorted(found, key=lambda item: (item['pid'], item['protocol'], item['address']))


def verify_registrations(observed, entries):
    if (set(observed['user/501']['services']) != {e['target'].split('/')[-1] for e in entries} or
            set(observed['user/501']['endpoints']) != {name for e in entries for name in e['mach_services']} or
            any(observed[d]['services'] or observed[d]['endpoints'] for d in ('system', 'gui/501'))):
        raise ValueError('Unexpected registrations; no cross-domain or unknown-service removal')


def recover(run=command, pause=time.sleep):
    raw = PLAN.read_bytes()
    if hashlib.sha256(raw).hexdigest() != PLAN_SHA256:
        raise ValueError('Reviewed recovery plan changed')
    plan = json.loads(raw)
    if hashlib.sha256((JOURNAL.parent / 'setup-v2.json').read_bytes()).hexdigest() != plan['setup_receipt_sha256']:
        raise ValueError('Original setup-v2 receipt identity changed')
    if os.getuid() != 501 or hashlib.sha256((HERE / 'apple_container_service_setup.py').read_bytes()).hexdigest() != plan['identity_helper_sha256']:
        raise ValueError('Recovery user/source identity differs')
    entries = plan['services']
    if {e['target'] for e in entries} != {'user/501/' + name for name in identity.SERVICE_PROGRAMS}:
        raise ValueError('Recovery target allowlist differs')
    with JOURNAL.open('x', encoding='utf-8') as journal:
        def emit(value):
            journal.write(json.dumps(value, sort_keys=True) + '\n')
            journal.flush()
            os.fsync(journal.fileno())
        emit({'phase': 'BEGIN', 'plan_sha256': PLAN_SHA256,
              'recovery_source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'cwd': '/', 'environment': ENV, 'qualification_granted': False})
        removed = []
        attempted = []
        try:
            verify_registrations(registrations(run), entries)
            before = [inspect_service(entry, run) for entry in entries]
            emit({'phase': 'IDENTITIES', 'services': before})
            current_processes = processes(entries, run)
            if {p['pid'] for p in current_processes} != {e['pid'] for e in entries}:
                raise ValueError('Unexpected/missing setup processes; no removal')
            for entry in entries:
                process = next(p for p in current_processes if p['pid'] == entry['pid'])
                if process['uid'] != 501 or not identity.same_path(process['executable'], entry['identity']['executable']):
                    raise ValueError('Process executable/owner differs; no removal')
            ports = listeners(run)
            foreign = [item for item in ports if item['pid'] not in {e['pid'] for e in entries}]
            emit({'phase': 'PREFLIGHT', 'services': before, 'processes': current_processes, 'listeners': ports})
            for entry in entries:
                verify_registrations(registrations(run), [e for e in entries if e['target'] not in removed])
                current = inspect_service(entry, run)
                process = [p for p in processes(entries, run) if p['pid'] == entry['pid']]
                if process != [p for p in current_processes if p['pid'] == entry['pid']]:
                    raise ValueError('Process identity changed; no removal')
                emit({'phase': 'BEFORE_BOOTOUT', 'service': current, 'process': process})
                attempted.append(entry['target'])
                run(['/bin/launchctl', 'bootout', entry['target']])
                removed.append(entry['target'])
                emit({'phase': 'BOOTOUT_RETURNED_ZERO', 'target': entry['target']})
            for attempt in range(5):
                observed = registrations(run)
                remaining_processes = processes(entries, run)
                remaining_ports = listeners(run)
                emit({'phase': 'POSTCHECK', 'registrations': observed, 'processes': remaining_processes,
                      'listeners': remaining_ports})
                if (not any(names for rows in observed.values() for names in rows.values()) and
                        not remaining_processes and remaining_ports == foreign):
                    emit({'phase': 'COMPLETE', 'result': 'SCOPED_RECOVERY_OBSERVED', 'removed': removed})
                    return 0
                if attempt < 4:
                    pause(1)
            raise ValueError('Registrations/processes/network bindings remain or observations changed')
        except (Exception, KeyboardInterrupt) as error:
            emit({'phase': 'INCOMPLETE_STOP_AND_REVIEW', 'removed': removed, 'attempted': attempted,
                  'error': type(error).__name__ + ': ' + str(error)})
            if attempted:
                try:
                    emit({'phase': 'PARTIAL_POSTCHECK', 'registrations': registrations(run),
                          'processes': processes(entries, run), 'listeners': listeners(run)})
                except Exception as observation_error:
                    emit({'phase': 'PARTIAL_OBSERVATION_UNAVAILABLE', 'error': str(observation_error)})
            return 1


if __name__ == '__main__':
    if sys.argv[1:] != ['recover-setup-v2-01']:
        raise SystemExit('Separate approval required: recover-setup-v2-01')
    raise SystemExit(recover())
