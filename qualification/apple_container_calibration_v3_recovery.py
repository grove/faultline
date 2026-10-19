"""Exact stopped-v3-registration inspection/recovery; never touches fixture processes."""
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import time

ROOT = Path('/private/tmp/faultline-guardian-calibration-v3')
RECOVERY = Path('/private/tmp/faultline-guardian-calibration-v3-recovery-01')
SOURCE = Path('/Users/grove/projects/faultline/qualification/apple_container_guardian_calibration_v3.py')
SOURCE_SHA = '2c431ec7b99a6424eee8b7b7fcbff1eaf1c2b28fa2503b8a804ef587827ecc02'
MANIFEST = Path(__file__).resolve().with_name('2026-10-19-apple-container-guardian-calibration-v3-original-manifest.json')
MANIFEST_SHA = 'ecad961b9adff940d15d1be59a3dc683c0abc4d4cc015819d1ff913317dc9545'
TARGET = 'user/501/dev.faultline.guardian-calibration-v3.coordinator-loss.guardian'


def helper():
    raw = SOURCE.read_bytes()
    if hashlib.sha256(raw).hexdigest() != SOURCE_SHA: raise ValueError('Original source changed')
    scope = {'__file__': str(SOURCE), '__name__': 'frozen_v3_recovery_observer'}
    exec(compile(raw, str(SOURCE), 'exec'), scope)
    return scope


def verify_originals(c):
    raw = MANIFEST.read_bytes()
    if hashlib.sha256(raw).hexdigest() != MANIFEST_SHA: raise ValueError('Recovery manifest changed')
    manifest = json.loads(raw)
    paths = sorted(str(p.relative_to(ROOT)) for p in (ROOT, *ROOT.rglob('*')))
    if paths != sorted(r['path'] for r in manifest['entries']): raise ValueError('Original tree changed')
    for row in manifest['entries']:
        path = ROOT / row['path']; c['safe'](path, int(row['mode'], 8)); info = path.lstat()
        for name, actual in (('uid', info.st_uid), ('gid', info.st_gid), ('inode', info.st_ino),
                             ('device', info.st_dev), ('nlink', info.st_nlink), ('flags', info.st_flags),
                             ('mtime_ns', info.st_mtime_ns), ('ctime_ns', info.st_ctime_ns)):
            if actual != row[name]: raise ValueError('Original metadata changed: ' + row['path'] + '/' + name)
        if row['kind'] == 'file' and c['digest'](path) != row['sha256']:
            raise ValueError('Original bytes changed')


def inspect(c):
    if os.getuid() != 501: raise ValueError('Wrong UID')
    verify_originals(c)
    plan = c['load'](ROOT / 'coordinator-loss/plan.json')
    journal = c['events'](ROOT / 'coordinator-loss/guardian.jsonl')
    owned = next(e['identity'] for e in journal if e['event'] == 'OWNED')
    guardian_pids = sorted({e['writer_pid'] for e in journal})
    if guardian_pids != [16954] or owned['pid'] != 16969 or journal[-1]['event'] != 'TERMINATED':
        raise ValueError('Unexpected original lifecycle')
    # A stopped registration and an unregistered live process are different states.
    processes = {str(pid): c['process'](pid) for pid in [16954, 16969]}
    if any(v is not None for v in processes.values()): raise ValueError('Captured PID is present')
    for case in ('coordinator-loss', 'guardian-restart'):
        for role in ('fixture', 'guardian'):
            label = c['PREFIX'] + case + '.' + role
            if 'user/501/' + label != TARGET and c['registered'](label):
                raise ValueError('Unexpected fixture/second-case registration')
    registration = c['observe'](plan, 'guardian', stopped=True)
    raw = None
    if registration is not None:
        raw = c['command'](['/bin/launchctl', 'print', TARGET])
        if (registration['target'] != TARGET or registration['pid'] is not None or
                re.findall(r'^\tstate = (.+)$', raw, re.M) != ['not running'] or
                re.findall(r'^\tdomain = (.+)$', raw, re.M) != ['user/501']):
            raise ValueError('Registration is not the exact stopped job')
    return {'monotonic': time.monotonic(), 'wall_ns': time.time_ns(), 'registration': registration,
            'raw_launchctl_print': raw, 'captured_pid_observations': processes,
            'fixture_and_second_case_registrations_absent': True, 'original_manifest_verified': True}


def recover():
    c = helper()
    before = inspect(c)
    # Exclusive receipt identity is consumed even if revalidation fails. No deletion or retry.
    RECOVERY.mkdir(mode=0o700); c['fsync_dir'](RECOVERY.parent)
    c['write'](RECOVERY / 'before.json', before)
    try:
        if before['registration'] is None:
            c['write'](RECOVERY / 'result.json', {'result': 'ALREADY_ABSENT_NO_ACTION'})
            return
        current = inspect(c)
        if current['registration'] != before['registration']: raise ValueError('Recovery identity changed')
        argv = ['/bin/launchctl', 'bootout', TARGET]
        c['write'](RECOVERY / 'intent.json', {'argv': argv, 'before': current, 'monotonic': time.monotonic()})
        # One exact bootout; preserve raw status/streams even if the command fails.
        import base64
        action = {'returncode': None, 'timeout': False, 'start_error': None}
        stdout = stderr = b''
        try:
            result = c['subprocess'].run(argv, cwd='/', env=c['ENV'], stdin=c['subprocess'].DEVNULL,
                                         capture_output=True, timeout=1)
            stdout, stderr = result.stdout, result.stderr; action['returncode'] = result.returncode
        except c['subprocess'].TimeoutExpired as error:
            stdout, stderr = error.stdout or b'', error.stderr or b''; action['timeout'] = True
        except OSError as error: action['start_error'] = repr(error)
        action.update({'stdout_base64': base64.b64encode(stdout[:65536]).decode('ascii'),
            'stderr_base64': base64.b64encode(stderr[:max(0, 65536-len(stdout))]).decode('ascii'),
            'output_truncated': len(stdout) + len(stderr) > 65536, 'monotonic': time.monotonic()})
        c['write'](RECOVERY / 'action.json', action)
        after = inspect(c); c['write'](RECOVERY / 'after.json', after)
        if (action['returncode'] != 0 or stderr or action['timeout'] or action['start_error'] or
                action['output_truncated'] or after['registration'] is not None):
            raise ValueError('Recovery not independently complete')
        c['write'](RECOVERY / 'result.json', {'result': 'EXACT_STOPPED_REGISTRATION_REMOVED',
                  'originals_preserved': True, 'fixture_pid_absent': True, 'guardian_pid_absent': True})
    except BaseException as error:
        c['write'](RECOVERY / 'failure.json', {'error': repr(error), 'retry': False})
        raise


if __name__ == '__main__':
    if sys.argv[1:] == ['recover-stopped-v3-once']: recover()
    elif sys.argv[1:] == ['inspect-v3']: print(json.dumps(inspect(helper()), indent=2, sort_keys=True))
    else: raise SystemExit('Only inspect-v3 or separately approved recover-stopped-v3-once')
