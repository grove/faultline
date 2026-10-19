"""Future positive-only launchd watchdog. Not installed or authorized by provisioning."""

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import plistlib
import re
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
RUNTIME = Path('/private/tmp/faultline-apple-positive-v2/setup-v4/runtime')
NAME = 'faultline-apple-positive-v3'
ROOT = RUNTIME / 'containers' / NAME
LABEL = 'com.apple.container.container-runtime-linux.' + NAME
MACH = 'com.apple.container.runtime.container-runtime-linux.' + NAME
TARGET = 'user/501/' + LABEL
PROGRAM = '/usr/local/libexec/container/plugins/container-runtime-linux/bin/container-runtime-linux'
PROGRAM_SHA = 'e8bee184cc1f6b53982f9cc4ecb02085ebe238b8834112f71f8972c0d488511a'
ENV = {'PATH': '/usr/bin:/bin', 'LC_ALL': 'C', 'TZ': 'Europe/Oslo'}


def command(argv, timeout=1):
    result = subprocess.run(argv, cwd='/', env=ENV, stdin=subprocess.DEVNULL,
                            capture_output=True, timeout=timeout)
    if len(result.stdout) > 4194304 or result.stderr or result.returncode not in (0, 1):
        raise ValueError('Incomplete guardian observation/action')
    if result.returncode and (argv[0] != '/bin/ps' or result.stdout):
        raise ValueError('Guardian command failed')
    return result.stdout.decode('utf-8', 'strict')


def process(pid, run=command):
    rows = run(['/bin/ps', '-ww', '-p', str(pid), '-o', 'pid=,uid=,lstart=,comm=']).splitlines()
    if not rows:
        return None
    if len(rows) != 1:
        raise ValueError('Ambiguous VM-owner process')
    fields = rows[0].split(maxsplit=7)
    if len(fields) != 8 or fields[:2] != [str(pid), '501'] or fields[7] != PROGRAM:
        raise ValueError('VM-owner PID/executable/UID changed')
    return {'pid': pid, 'uid': 501, 'birth': ' '.join(fields[2:7]), 'executable': fields[7]}


def observe(setup, run=command):
    names = setup.domain_names(run(['/bin/launchctl', 'print', 'user/501']), 'user/501')
    if LABEL not in names['services']:
        if MACH in names['endpoints']:
            raise ValueError('Orphan runtime endpoint')
        return None
    text = run(['/bin/launchctl', 'print', TARGET])
    paths = re.findall(r'^\tpath = (.+)$', text, re.M)
    programs = re.findall(r'^\tprogram = (.+)$', text, re.M)
    pids = re.findall(r'^\tpid = ([1-9][0-9]*)$', text, re.M)
    path = ROOT / 'service.plist'
    if paths != [str(path)] or programs != [PROGRAM] or len(pids) != 1 or path.is_symlink():
        raise ValueError('Runtime origin/process differs')
    for parent in path.parents:
        if parent.is_symlink():
            raise ValueError('Linked runtime origin')
    raw = path.read_bytes()
    if len(raw) > 65536:
        raise ValueError('Runtime plist exceeds budget')
    plist = plistlib.loads(raw)
    if (plist.get('Label') != LABEL or plist.get('Program') is not None or
            plist.get('ProgramArguments') != [PROGRAM, 'start', '--root', str(ROOT), '--uuid', NAME] or
            plist.get('EnvironmentVariables', {}).get('CONTAINER_APP_ROOT', '').rstrip('/') != str(RUNTIME) or
            plist.get('EnvironmentVariables', {}).get('CONTAINER_INSTALL_ROOT', '').rstrip('/') != '/usr/local'):
        raise ValueError('Runtime arguments/roots differ')
    with Path(PROGRAM).open('rb') as executable:
        if hashlib.file_digest(executable, 'sha256').hexdigest() != PROGRAM_SHA:
            raise ValueError('Runtime executable bytes changed')
    identity = process(int(pids[0]), run)
    if identity is None:
        raise ValueError('Runtime process disappeared during binding')
    return {**identity, 'target': TARGET, 'plist_sha256': hashlib.sha256(raw).hexdigest(),
            'origin': str(path), 'binary_sha256': PROGRAM_SHA, 'container_id': NAME}


def watch(plan, events, emit, observe_owner, observe_pid, act, clock=time.monotonic, pause=time.sleep):
    """No coordinator heartbeat can extend this fixed host-clock deadline."""
    owned = next((e['identity'] for e in events if e['event'] == 'OWNED'), None)
    if not 0 < plan['deadline_monotonic'] - plan['armed_monotonic'] <= 10:
        raise ValueError('Guardian deadline exceeds ten seconds')
    if clock() < plan['armed_monotonic']:
        raise ValueError('Host clock reset; no automatic action')
    while True:
        current = observe_owner()
        if current is not None:
            if owned is None:
                owned = current; emit({'event': 'OWNED', 'identity': owned})
            elif current != owned:
                raise ValueError('VM-owner identity replaced; no action')
        elif owned is not None:
            actual = observe_pid(owned['pid'])
            if actual is None:
                emit({'event': 'TERMINATED', 'independent_pid_absent': True, 'runtime_registration_absent': True})
                return
            if actual != {k: owned[k] for k in ('pid', 'uid', 'birth', 'executable')}:
                raise ValueError('Unregistered VM-owner PID identity changed')
        if clock() >= plan['deadline_monotonic']:
            break
        pause(min(0.1, max(0, plan['deadline_monotonic'] - clock())))
    if owned is None:
        emit({'event': 'NO_VM_OWNER_OBSERVED'})
        return
    for operation in ('bootout', 'kill'):
        current = observe_owner()
        actual = observe_pid(owned['pid'])
        if current is None and actual is None:
            emit({'event': 'TERMINATED', 'independent_pid_absent': True, 'runtime_registration_absent': True})
            return
        if current is None:
            break
        if current != owned or actual != {k: owned[k] for k in ('pid', 'uid', 'birth', 'executable')}:
            raise ValueError('VM-owner identity changed before termination')
        if any(e['event'] == operation.upper() for e in events):
            continue
        emit({'event': operation.upper(), 'target': TARGET})
        try:
            act(['/bin/launchctl', 'bootout', TARGET] if operation == 'bootout' else ['/bin/launchctl', 'kill', 'SIGKILL', TARGET])
        except (OSError, ValueError, subprocess.TimeoutExpired):
            pass
    for _ in range(10):
        if observe_owner() is None and observe_pid(owned['pid']) is None:
            emit({'event': 'TERMINATED', 'independent_pid_absent': True, 'runtime_registration_absent': True})
            return
        pause(0.1)
    raise ValueError('VM-owner termination not independently observed')


def job(plan_path, plan_sha):
    return {'Label': 'dev.faultline.positive-v3-guardian', 'ProgramArguments': [
        '/opt/homebrew/bin/python3', '-I', '-B', str(HERE / 'apple_container_guardian.py'), str(plan_path), plan_sha],
        'WorkingDirectory': '/', 'EnvironmentVariables': ENV, 'RunAtLoad': True,
        'KeepAlive': {'SuccessfulExit': False}, 'ThrottleInterval': 1, 'ProcessType': 'Background'}


def main(plan_path, expected):
    path = Path(plan_path)
    raw = path.read_bytes()
    if path.is_symlink() or len(raw) > 65536 or hashlib.sha256(raw).hexdigest() != expected or os.getuid() != 501:
        raise ValueError('Unapproved guardian plan')
    plan = json.loads(raw)
    if plan['container_id'] != NAME or plan['target'] != TARGET or plan['source_sha256'] != hashlib.sha256(Path(__file__).read_bytes()).hexdigest():
        raise ValueError('Guardian scope/source changed')
    setup_path = HERE / 'apple_container_service_setup.py'
    if hashlib.sha256(setup_path.read_bytes()).hexdigest() != '82a20ecffdedef478b72fe4b3b9a384cb8e35ad9b407b7e61c510a596b21f101':
        raise ValueError('Namespace parser bytes changed')
    spec = importlib.util.spec_from_file_location('setup', setup_path)
    setup = importlib.util.module_from_spec(spec); spec.loader.exec_module(setup)
    journal = path.parent / 'guardian.jsonl'
    if journal.is_symlink() or (journal.exists() and journal.stat().st_size > 1048576):
        raise ValueError('Invalid guardian journal')
    events = [json.loads(line) for line in journal.read_text().splitlines()] if journal.exists() else []
    if any(e['event'] in ('TERMINATED', 'INCOMPLETE_STOP_AND_REVIEW', 'NO_VM_OWNER_OBSERVED') for e in events):
        return
    with journal.open('a') as output:
        def emit(event):
            event['monotonic'] = time.monotonic(); events.append(event)
            output.write(json.dumps(event, sort_keys=True) + '\n'); output.flush(); os.fsync(output.fileno())
        try:
            if not events:
                if observe(setup) is not None:
                    raise ValueError('Runtime existed before guardian armed')
                emit({'event': 'ARMED', 'plan_sha256': expected})
                with (path.parent / 'guardian-ready.json').open('x') as ready:
                    json.dump({'plan_sha256': expected, 'deadline_monotonic': plan['deadline_monotonic']}, ready)
                    ready.flush(); os.fsync(ready.fileno())
            watch(plan, events, emit, lambda: observe(setup), process, command)
        except Exception as error:
            emit({'event': 'INCOMPLETE_STOP_AND_REVIEW', 'error': str(error)})


if __name__ == '__main__':
    if len(sys.argv) != 3:
        raise SystemExit('Future positive-stage authorization and exact plan/hash required')
    main(*sys.argv[1:])
