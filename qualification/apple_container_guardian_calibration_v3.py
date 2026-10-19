"""Prepared host-fixture launchd calibration. Never invokes Container or a VM."""
import base64
import hashlib
import json
import math
import os
from pathlib import Path
import plistlib
import re
import selectors
import signal
import stat
import subprocess
import sys
import time

SOURCE = Path(__file__).resolve()
BASE = Path('/private/tmp/faultline-guardian-calibration-v3')
PYTHON = Path('/opt/homebrew/bin/python3').resolve()
PROCESS_PYTHON = PYTHON.parents[1] / 'Resources/Python.app/Contents/MacOS/Python'
PYTHON_PINS = {str(PYTHON): '1955899cb535256cfa477d926d016819e52e747984722c44f76e39a4950fee0e',
               str(PROCESS_PYTHON): '409ddb09021ac53577e7658de9ec09c899655c77a38744679ef73be9af21ecd5'}
DOMAIN = 'user/501'
ENV = {'PATH': '/usr/bin:/bin', 'LC_ALL': 'C', 'TZ': 'Europe/Oslo'}
PREFIX = 'dev.faultline.guardian-calibration-v3.'
RECEIPT = Path('/private/tmp/faultline-apple-positive-v2/evidence/provision-v3.json')
RECEIPT_SHA = 'e082359d42a2d24690c10cd16d220cb55783d2f6b68c5d9210333d5a4dafdea0'
TERMINAL = {'TERMINATED', 'INCOMPLETE_STOP_AND_REVIEW'}


def digest(path):
    with path.open('rb') as source:
        return hashlib.file_digest(source, 'sha256').hexdigest()


def safe(path, mode=None):
    if path.is_symlink() or any(p.is_symlink() for p in path.parents):
        raise ValueError('Linked host path')
    info = path.stat()
    if info.st_uid != 501 or (mode is not None and stat.S_IMODE(info.st_mode) != mode):
        raise ValueError('Host ownership/mode changed')
    if not (stat.S_ISDIR(info.st_mode) if mode == 0o700 else stat.S_ISREG(info.st_mode)):
        raise ValueError('Host evidence type changed')
    if stat.S_ISREG(info.st_mode) and (info.st_nlink != 1 or info.st_size > 1048576):
        raise ValueError('Host evidence kind/link/size changed')


def write(path, value):
    with path.open('x') as out:
        os.fchmod(out.fileno(), 0o400)
        json.dump(value, out, sort_keys=True, indent=2); out.write('\n')
        out.flush(); os.fsync(out.fileno())
    fsync_dir(path.parent)


def fsync_dir(path):
    fd = os.open(path, os.O_RDONLY)
    try: os.fsync(fd)
    finally: os.close(fd)


def command(argv):
    result = subprocess.run(argv, cwd='/', env=ENV, stdin=subprocess.DEVNULL,
                            capture_output=True, timeout=1)
    if len(result.stdout) + len(result.stderr) > 1048576:
        raise ValueError('Command output budget exceeded')
    if result.returncode or result.stderr:
        # Only a successful domain inventory or ps absence can establish absence.
        if argv[0] == '/bin/ps' and result.returncode == 1 and not result.stdout and not result.stderr:
            return ''
        raise ValueError('Command failed: ' + repr(argv))
    return result.stdout.decode('utf-8', 'strict')


def access_snapshot(paths):
    """Effective caller access is a preflight observation, not launchd acceptance."""
    rows = []
    for path in sorted({p for leaf in paths for p in (leaf, *leaf.parents)}):
        info = path.lstat()
        if path.is_symlink() or not (stat.S_ISDIR(info.st_mode) or stat.S_ISREG(info.st_mode)):
            raise ValueError('Unexpected bootstrap path type: ' + str(path))
        required = os.X_OK if path.is_dir() else os.R_OK
        if path in (PYTHON, PROCESS_PYTHON): required |= os.X_OK
        if not os.access(path, required): raise ValueError('Inaccessible bootstrap path: ' + str(path))
        rows.append({'path': str(path), 'uid': info.st_uid, 'gid': info.st_gid,
                     'mode': oct(stat.S_IMODE(info.st_mode)), 'flags': info.st_flags,
                     'required_access': required, 'caller_access': True})
    return rows


def bootstrap(plan, role):
    """One exact bootstrap; persist intent and bounded raw result even on failure."""
    directory = Path(plan['directory']); plan_path = directory / 'plan.json'
    if role not in ('guardian', 'fixture') or load(plan_path) != plan:
        raise ValueError('Changed bootstrap plan/role')
    label = plan[role + '_label']; path = directory / (label + '.plist')
    safe(path, 0o400)
    if digest(path) != plan[role + '_plist_sha256'] or plistlib.loads(path.read_bytes()) != job(label, role, plan_path):
        raise ValueError('Changed bootstrap plist/arguments')
    if registered(label): raise ValueError('Bootstrap label collision')
    access = access_snapshot([SOURCE, PYTHON, PROCESS_PYTHON, plan_path, path])
    command(['/usr/bin/plutil', '-lint', str(path)])
    if plan['deadline_monotonic'] - time.monotonic() < (5 if role == 'fixture' else 3):
        raise ValueError('Insufficient original bootstrap budget')
    argv = ['/bin/launchctl', 'bootstrap', DOMAIN, str(path)]
    write(directory / (role + '-bootstrap-intent.json'), {'argv': argv, 'access': access,
          'plan_sha256': digest(plan_path), 'plist_sha256': digest(path), 'monotonic': time.monotonic()})
    streams = {'stdout': bytearray(), 'stderr': bytearray()}
    result = {'argv': argv, 'returncode': None, 'timeout': False, 'output_limit': False,
              'output_bytes_observed': 0, 'start_error': None, 'started_monotonic': time.monotonic()}
    child = None
    try:
        if plan['deadline_monotonic'] - time.monotonic() < (5 if role == 'fixture' else 3):
            raise ValueError('Original bootstrap budget elapsed after intent')
        child = subprocess.Popen(argv, cwd='/', env=ENV, stdin=subprocess.DEVNULL,
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        with selectors.DefaultSelector() as selector:
            for name, pipe in (('stdout', child.stdout), ('stderr', child.stderr)):
                os.set_blocking(pipe.fileno(), False); selector.register(pipe, selectors.EVENT_READ, name)
            deadline = result['started_monotonic'] + 1
            while selector.get_map():
                if time.monotonic() >= deadline:
                    result['timeout'] = True; break
                for key, _ in selector.select(max(0, deadline - time.monotonic())):
                    chunk = os.read(key.fd, 4096)
                    if not chunk:
                        selector.unregister(key.fileobj); continue
                    remaining = 65536 - sum(map(len, streams.values()))
                    streams[key.data].extend(chunk[:remaining])
                    result['output_bytes_observed'] += len(chunk)
                    if len(chunk) > remaining:
                        result['output_limit'] = True; break
                if result['output_limit']: break
            if result['timeout'] or result['output_limit']:
                child.kill()
            try: child.wait(timeout=max(.001, deadline - time.monotonic()))
            except subprocess.TimeoutExpired:
                result['timeout'] = True; child.kill(); child.wait(timeout=1)
            result['returncode'] = child.returncode
    except OSError as error:
        result['start_error'] = repr(error)
    finally:
        if child is not None:
            try:
                if child.poll() is None: child.kill()
                child.wait(timeout=1)
            except (OSError, subprocess.TimeoutExpired) as error:
                result['cleanup_error'] = repr(error)
            result['returncode'] = child.returncode
            for pipe in (child.stdout, child.stderr): pipe.close()
        result.update({name + '_base64': base64.b64encode(raw).decode('ascii') for name, raw in streams.items()})
        result['finished_monotonic'] = time.monotonic()
        write(directory / (role + '-bootstrap-result.json'), result)
    if (result['returncode'] != 0 or streams['stderr'] or result['start_error'] or result.get('cleanup_error') or
            result['timeout'] or result['output_limit']):
        raise ValueError('Bootstrap incomplete; preserve bootstrap intent/result and review; no retry')


def registered(label):
    text = command(['/bin/launchctl', 'print', DOMAIN])
    section = re.findall(r'^\tservices = \{\n(.*?)^\t\}', text, re.M | re.S)
    if not text.startswith(DOMAIN + ' = {\n') or len(section) != 1:
        raise ValueError('Incomplete launchd inventory')
    names = []
    for row in section[0].splitlines():
        fields = row.split(maxsplit=2)
        if len(fields) != 3 or not row.startswith('\t\t'):
            raise ValueError('Unrecognized launchd service row')
        names.append(fields[-1])
    return label in names


def process(pid):
    text = command(['/bin/ps', '-ww', '-p', str(pid), '-o', 'pid=,uid=,lstart=,comm='])
    if not text.strip(): return None
    rows = text.splitlines(); fields = rows[0].split(maxsplit=7)
    if len(rows) != 1 or len(fields) != 8 or fields[:2] != [str(pid), '501'] or str(Path(fields[7]).resolve()) not in PYTHON_PINS:
        raise ValueError('Host fixture PID/UID/executable changed')
    return {'pid': pid, 'uid': 501, 'birth': ' '.join(fields[2:7]), 'executable': str(Path(fields[7]).resolve())}


def observe(plan, role, stopped=False):
    label = plan[role + '_label']; target = DOMAIN + '/' + label
    if not registered(label): return None
    path = Path(plan['directory']) / (label + '.plist'); safe(path, 0o400)
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != plan[role + '_plist_sha256']:
        raise ValueError('Host job plist changed')
    config = plistlib.loads(raw)
    if config != job(label, role, Path(plan['directory']) / 'plan.json'):
        raise ValueError('Changed host job plist/session/arguments')
    text = command(['/bin/launchctl', 'print', target])
    paths = re.findall(r'^\tpath = (.+)$', text, re.M)
    programs = re.findall(r'^\tprogram = (.+)$', text, re.M)
    args = re.findall(r'^\targuments = \{\n(.*?)^\t\}', text, re.M | re.S)
    pids = re.findall(r'^\tpid = ([1-9][0-9]*)$', text, re.M)
    if (not text.startswith(target + ' = {\n') or paths != [str(path)] or programs != [str(PYTHON)] or
            len(args) != 1 or [line.strip() for line in args[0].splitlines()] != config['ProgramArguments'] or len(pids) > 1 or (not pids and not stopped)):
        raise ValueError('Host job registration/argv/origin changed or process unavailable')
    if any(digest(Path(p)) != h for p, h in PYTHON_PINS.items()) or digest(SOURCE) != plan['source_sha256']:
        raise ValueError('Host executable/source bytes changed')
    if not pids:
        return {'target': target, 'origin': str(path), 'plist_sha256': plan[role + '_plist_sha256'], 'pid': None}
    identity = process(int(pids[0]))
    if identity is None: raise ValueError('Host job disappeared during ownership binding')
    return {**identity, 'target': target, 'origin': str(path), 'plist_sha256': plan[role + '_plist_sha256']}


def events(path):
    if not path.exists(): return []
    safe(path, 0o600)
    raw = path.read_bytes()
    if raw and not raw.endswith(b'\n'): raise ValueError('Torn journal; preserve and review')
    return [json.loads(line) for line in raw.splitlines()]


def emit(path, event):
    safe(path.parent, 0o700)
    if path.exists() or path.is_symlink(): safe(path, 0o600)
    event = {**event, 'monotonic': time.monotonic(), 'writer_pid': os.getpid()}
    with path.open('a') as out:
        os.fchmod(out.fileno(), 0o600)
        out.write(json.dumps(event, sort_keys=True) + '\n'); out.flush(); os.fsync(out.fileno())
    fsync_dir(path.parent)


def watch(plan, journal, owner, pid, action, clock=time.monotonic, pause=time.sleep):
    """Restart replays ownership; repeated exact-target actions are identity checked."""
    history = events(journal)
    if any(e['event'] in TERMINAL for e in history): return
    if (not all(math.isfinite(plan[k]) for k in ('deadline_monotonic', 'armed_monotonic')) or
            not 0 < plan['deadline_monotonic'] - plan['armed_monotonic'] <= 10 or clock() < plan['armed_monotonic']):
        raise ValueError('Invalid original deadline/clock')
    if any(e['deadline_monotonic'] != plan['deadline_monotonic'] for e in history if e['event'] == 'GUARDIAN_STARTED'):
        raise ValueError('Original journal deadline changed')
    owned = next((e['identity'] for e in history if e['event'] == 'OWNED'), None)
    emit(journal, {'event': 'GUARDIAN_STARTED', 'deadline_monotonic': plan['deadline_monotonic']})
    def current():
        nonlocal owned
        value = owner()
        if value is not None:
            if owned is None:
                owned = value; emit(journal, {'event': 'OWNED', 'identity': owned})
            elif value != owned: raise ValueError('Replacement identity; no action')
        return value
    while clock() < plan['deadline_monotonic']:
        current(); pause(min(.05, max(0, plan['deadline_monotonic'] - clock())))
    for operation in ('bootout', 'kill'):
        value = current()
        if owned is None: raise ValueError('No fixture owner observed; calibration incomplete')
        actual = pid(owned['pid'])
        expected = {k: owned[k] for k in ('pid', 'uid', 'birth', 'executable')}
        if value is None and actual is None:
            emit(journal, {'event': 'TERMINATED', 'registration_absent': True, 'independent_pid_absent': True}); return
        if value != owned or actual != expected: raise ValueError('Unregistered live/replaced PID; no action')
        emit(journal, {'event': operation.upper() + '_INTENT', 'identity': owned})
        try: action(operation)
        except (OSError, ValueError, subprocess.TimeoutExpired) as error:
            emit(journal, {'event': 'ACTION_ERROR', 'operation': operation, 'error': str(error)})
        # Allow launchd teardown to complete before considering the exact-target fallback.
        for _ in range(5):
            if owner() is None and pid(owned['pid']) is None:
                emit(journal, {'event': 'TERMINATED', 'registration_absent': True, 'independent_pid_absent': True}); return
            pause(.1)
    raise ValueError('Termination not independently observed')


def load(path):
    path = Path(path); safe(path, 0o400); safe(path.parent, 0o700)
    plan = json.loads(path.read_bytes())
    if (path != BASE / plan['case'] / 'plan.json' or plan['directory'] != str(path.parent) or plan['case'] not in ('coordinator-loss', 'guardian-restart') or
            plan['source_sha256'] != digest(SOURCE) or plan['python_sha256'] != PYTHON_PINS or
            any(digest(Path(p)) != h for p, h in PYTHON_PINS.items()) or
            plan['boot_identity'] != command(['/usr/sbin/sysctl', '-n', 'kern.boottime'])):
        raise ValueError('Plan scope/source/boot identity changed')
    for role in ('fixture', 'guardian'):
        if plan[role + '_label'] != PREFIX + plan['case'] + '.' + role: raise ValueError('Foreign label')
    ready = path.parent / 'ready.json'
    if ready.exists() or ready.is_symlink():
        safe(ready, 0o400)
        if json.loads(ready.read_bytes())['plan_sha256'] != digest(path):
            raise ValueError('Original ready plan changed')
    return plan


def guardian(path):
    path = Path(path)
    if path not in [BASE / case / 'plan.json' for case in ('coordinator-loss', 'guardian-restart')]:
        return
    directory = path.parent; safe(directory, 0o700); journal = directory / 'guardian.jsonl'
    try:
        plan = load(path)
        history = events(journal)
        if history and (history[0]['event'] != 'ARMED' or history[0].get('plan_sha256') != digest(path)):
            raise ValueError('Original armed plan changed')
        if not history:
            if registered(plan['fixture_label']): raise ValueError('Fixture existed before arming')
            emit(journal, {'event': 'ARMED', 'plan_sha256': digest(path)})
        if not (directory / 'ready.json').exists(): write(directory / 'ready.json', {'plan_sha256': digest(Path(path))})
        target = DOMAIN + '/' + plan['fixture_label']
        watch(plan, journal, lambda: observe(plan, 'fixture'), process,
              lambda operation: command(['/bin/launchctl', 'bootout', target] if operation == 'bootout' else
                                        ['/bin/launchctl', 'kill', 'SIGKILL', target]))
    except Exception as error:
        emit(journal, {'event': 'INCOMPLETE_STOP_AND_REVIEW', 'error': str(error)})


def coordinator(path):
    plan = load(path); directory = Path(plan['directory'])
    safe(directory / 'ready.json', 0o400)
    if json.loads((directory / 'ready.json').read_bytes())['plan_sha256'] != digest(Path(path)):
        raise ValueError('Wrong guardian readiness')
    if plan['deadline_monotonic'] - time.monotonic() < 5: raise ValueError('Insufficient original budget')
    if observe(plan, 'guardian') is None or registered(plan['fixture_label']): raise ValueError('Guardian missing/fixture collision')
    bootstrap(plan, 'fixture')
    time.sleep(30)


def job(label, role, plan_path):
    value = {'Label': label, 'ProgramArguments': [str(PYTHON), '-I', '-B', str(SOURCE), role, str(plan_path)],
             'WorkingDirectory': '/', 'EnvironmentVariables': ENV, 'RunAtLoad': True,
             'ProcessType': 'Background', 'LimitLoadToSessionType': 'Background', 'ExitTimeOut': 1}
    if role == 'guardian': value.update(KeepAlive={'SuccessfulExit': False}, ThrottleInterval=1)
    return value


def wait_for(check, deadline):
    while time.monotonic() < deadline:
        value = check()
        if value: return value
        time.sleep(.05)
    raise TimeoutError('Calibration observation budget exhausted')


def install():
    if os.getuid() != 501 or digest(RECEIPT) != RECEIPT_SHA: raise ValueError('Wrong host/provision receipt')
    if command(['/bin/launchctl', 'managername']).strip() != 'Background': raise ValueError('Require user/501 Background manager')
    # Check every attempt identity before creating any new host state.
    for case in ('coordinator-loss', 'guardian-restart'):
        for role in ('fixture', 'guardian'):
            if registered(PREFIX + case + '.' + role): raise ValueError('Consumed/colliding label')
    if any(digest(Path(p)) != h for p, h in PYTHON_PINS.items()) or process(os.getpid()) is None:
        raise ValueError('Host interpreter/process observations unavailable')
    BASE.mkdir(mode=0o700); fsync_dir(BASE.parent)
    write(BASE / 'attempt.json', {'source_sha256': digest(SOURCE), 'provision_v3_receipt_sha256': RECEIPT_SHA})
    for case in ('coordinator-loss', 'guardian-restart'):
        directory = BASE / case; directory.mkdir(mode=0o700); plan_path = directory / 'plan.json'
        plan = {'case': case, 'directory': str(directory), 'source_sha256': digest(SOURCE),
                'python_sha256': PYTHON_PINS, 'boot_identity': command(['/usr/sbin/sysctl', '-n', 'kern.boottime'])}
        for role in ('fixture', 'guardian'):
            label = PREFIX + case + '.' + role; plan[role + '_label'] = label
            path = directory / (label + '.plist')
            with path.open('xb') as out:
                os.fchmod(out.fileno(), 0o400); out.write(plistlib.dumps(job(label, role, plan_path)))
                out.flush(); os.fsync(out.fileno())
            plan[role + '_plist_sha256'] = digest(path)
        plan['armed_monotonic'] = time.monotonic(); plan['deadline_monotonic'] = plan['armed_monotonic'] + 10
        write(plan_path, plan)
        bootstrap(plan, 'guardian')
        wait_for(lambda: (directory / 'ready.json').exists(), plan['armed_monotonic'] + 3)
        child = subprocess.Popen([str(PYTHON), '-I', '-B', str(SOURCE), 'coordinator', str(plan_path)],
                                 cwd='/', env=ENV, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        child_identity = process(child.pid)
        if child_identity is None: raise ValueError('Coordinator disappeared')
        wait_for(lambda: any(e['event'] == 'OWNED' for e in events(directory / 'guardian.jsonl')),
                 plan['deadline_monotonic'] - 3)
        if process(child.pid) != child_identity or child.poll() is not None: raise ValueError('Coordinator identity changed')
        emit(directory / 'operator.jsonl', {'event': 'COORDINATOR_SIGKILL_INTENT', 'identity': child_identity})
        child.kill(); child.wait(timeout=1)
        if process(child.pid) is not None: raise ValueError('Coordinator still present')
        if case == 'guardian-restart':
            identity = observe(plan, 'guardian')
            if identity is None or observe(plan, 'guardian') != identity: raise ValueError('Guardian identity unavailable/changed')
            emit(directory / 'operator.jsonl', {'event': 'GUARDIAN_SIGKILL_INTENT', 'identity': identity})
            command(['/bin/launchctl', 'kill', 'SIGKILL', identity['target']])
        history = wait_for(lambda: (h if any(e['event'] in TERMINAL for e in h) else None)
                           if (h := events(directory / 'guardian.jsonl')) else None, plan['armed_monotonic'] + 25)
        if history[-1]['event'] != 'TERMINATED': raise ValueError('Guardian incomplete; preserve and review')
        starts = [e for e in history if e['event'] == 'GUARDIAN_STARTED']
        if case == 'guardian-restart' and (len(starts) < 2 or len({e['writer_pid'] for e in starts}) < 2):
            raise ValueError('Independent launchd restart not observed')
        owned = next(e['identity'] for e in history if e['event'] == 'OWNED')
        if registered(plan['fixture_label']) or process(owned['pid']) is not None: raise ValueError('Independent final stop check failed')
        def guardian_stopped():
            registration = observe(plan, 'guardian', stopped=True)
            if registration is not None and registration['pid'] is not None: return False
            return all(process(e['writer_pid']) is None for e in starts)
        wait_for(guardian_stopped, plan['armed_monotonic'] + 25)
        registration = observe(plan, 'guardian', stopped=True)
        if registration is not None:
            if registration['pid'] is not None: raise ValueError('Guardian restarted unexpectedly')
            emit(directory / 'operator.jsonl', {'event': 'GUARDIAN_BOOTOUT_INTENT', 'registration': registration})
            command(['/bin/launchctl', 'bootout', registration['target']])
        wait_for(lambda: not registered(plan['guardian_label']), plan['armed_monotonic'] + 25)
        write(directory / 'result.json', {'result': 'SYNTHETIC_HOST_LIFETIME_ONLY', 'deadline_monotonic': plan['deadline_monotonic'],
              'termination_monotonic': history[-1]['monotonic'], 'vm_launches': 0, 'qualification_granted': False})
    write(BASE / 'result.json', {'result': 'CALIBRATED_HOST_FIXTURES_ONLY', 'execution': 'NO_GO / UNAVAILABLE', 'vm_descendant_containment': 'UNQUALIFIED'})


if __name__ == '__main__':
    if sys.argv[1:] == ['install-calibrate-v3']:
        if BASE.exists() or BASE.is_symlink(): raise SystemExit('Consumed calibration-v3 root; no retry')
        try: install()
        except Exception as error:
            if BASE.exists() and not (BASE / 'failure.json').exists():
                write(BASE / 'failure.json', {'result': 'INCOMPLETE_STOP_AND_REVIEW', 'error': str(error), 'retry': False})
            raise SystemExit(str(error))
    elif len(sys.argv) == 3 and sys.argv[1] == 'guardian': guardian(sys.argv[2])
    elif len(sys.argv) == 3 and sys.argv[1] == 'coordinator': coordinator(sys.argv[2])
    elif len(sys.argv) == 3 and sys.argv[1] == 'fixture':
        load(sys.argv[2]); signal.alarm(30); time.sleep(30)
    else: raise SystemExit('Separate approval required: install-calibrate-v3')
