"""One separately authorized, pinned setup-v2 recovery. Never starts a service."""

from datetime import datetime
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
PLAN = HERE / '2026-10-19-apple-container-recovery-02-plan.json'
PLAN_SHA256 = '26b72f4f05406f714c2f6ac92fdaba9d5fe39b6b387bb4f4568c43274146e679'
ENV = {'PATH': '/usr/bin:/bin', 'LC_ALL': 'C', 'TZ': 'Europe/Oslo'}
DISCOVERY = ['/usr/bin/pgrep', '-u', '501', '^(container-|machine-api)']
DOMAINS = ('system', 'user/501', 'gui/501')
JOURNAL = Path('/private/tmp/faultline-apple-positive-v2/evidence/recovery-setup-v2-02.jsonl')


def command(argv):
    # shortcut: capture trusts finite CLI metadata; stream before adding untrusted output.
    result = subprocess.run(argv, cwd='/', env=ENV, stdin=subprocess.DEVNULL,
                            capture_output=True, timeout=5)
    absence_supported = (argv[0] == '/usr/sbin/lsof' or argv == DISCOVERY or
                         argv[:3] == ['/bin/ps', '-ww', '-p'])
    empty = absence_supported and result.returncode == 1 and not result.stdout
    if absence_supported and result.returncode == 0 and not result.stdout:
        raise ValueError('Successful observation returned no records')
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
    def discover():
        rows = run(DISCOVERY).splitlines()
        if (len(rows) > 32 or any(not re.fullmatch(r'[1-9][0-9]*', row) for row in rows) or
                len(set(rows)) != len(rows)):
            raise ValueError('Ambiguous Container process discovery')
        return {int(row) for row in rows}

    discovered = discover()
    requested = discovered | {entry['pid'] for entry in entries}
    if len(requested) > 32:
        raise ValueError('Container process observation exceeds budget')
    text = run(['/bin/ps', '-ww', '-p', ','.join(map(str, sorted(requested))),
                '-o', 'pid=,uid=,lstart=,comm='])
    found = []
    for number, row in enumerate(text.splitlines(), 1):
        fields = row.split(maxsplit=7)
        if (len(fields) != 8 or not re.fullmatch(r'[1-9][0-9]*', fields[0]) or
                not re.fullmatch(r'[0-9]+', fields[1]) or not Path(fields[7]).is_absolute()):
            raise ValueError(f'Ambiguous targeted process row {number}: {len(fields)} fields or invalid PID/UID/path')
        pid, uid = int(fields[0]), int(fields[1])
        started = ' '.join(fields[2:7])
        try:
            datetime.strptime(started, '%a %b %d %H:%M:%S %Y')
        except ValueError:
            raise ValueError(f'Invalid birth time for targeted PID {pid}') from None
        if pid not in requested or any(p['pid'] == pid for p in found):
            raise ValueError('Unexpected/duplicate targeted process row')
        found.append({'pid': pid, 'uid': uid, 'started': started, 'executable': fields[7]})
    if discovered != discover() or not discovered.issubset({p['pid'] for p in found}):
        raise ValueError('Container process set changed or observation incomplete')
    if any(p['pid'] not in discovered for p in found):
        raise ValueError('PID discovery failed to account for an observed service process')
    return sorted(found, key=lambda p: p['pid'])


def verify_processes(observed, entries):
    if len(observed) != len(entries) or {p['pid'] for p in observed} != {e['pid'] for e in entries}:
        raise ValueError('Setup process set differs; expected PIDs ' + str(sorted(e['pid'] for e in entries)) +
                         ', observed PIDs ' + str(sorted(p['pid'] for p in observed)))
    for entry in entries:
        process = next(p for p in observed if p['pid'] == entry['pid'])
        if (process['uid'] != entry['process_uid'] or process['started'] != entry['process_started'] or
                not identity.same_path(process['executable'], entry['identity']['executable'])):
            raise ValueError(f'Process executable/owner/birth identity differs for PID {entry["pid"]}; no removal')


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
    if hashlib.sha256(JOURNAL.with_name('recovery-setup-v2-01.jsonl').read_bytes()).hexdigest() != plan['previous_recovery_journal_sha256']:
        raise ValueError('Previous recovery journal identity changed')
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
            verify_processes(current_processes, entries)
            ports = listeners(run)
            foreign = [item for item in ports if item['pid'] not in {e['pid'] for e in entries}]
            emit({'phase': 'PREFLIGHT', 'services': before, 'processes': current_processes, 'listeners': ports})
            for entry in entries:
                verify_registrations(registrations(run), [e for e in entries if e['target'] not in removed])
                current = inspect_service(entry, run)
                observed_processes = processes(entries, run)
                verify_processes(observed_processes, [e for e in entries if e['target'] not in removed])
                process = [p for p in observed_processes if p['pid'] == entry['pid']]
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
    if sys.argv[1:] != ['recover-setup-v2-02']:
        raise SystemExit('Separate approval required: recover-setup-v2-02')
    raise SystemExit(recover())
