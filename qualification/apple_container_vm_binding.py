"""Offline configuration/participant binding. No VM, launchd or execution entrypoint."""
import hashlib
import json
import math
import os
from pathlib import Path
import stat
from urllib.parse import unquote, urlsplit

HERE = Path(__file__).resolve().parent
NAME = 'faultline-apple-positive-v3'
ROOT = Path('/private/tmp/faultline-apple-positive-v2/setup-v4/runtime/containers') / NAME
PROGRAM = '/usr/local/libexec/container/plugins/container-runtime-linux/bin/container-runtime-linux'
TARGET = 'user/501/com.apple.container.container-runtime-linux.' + NAME
WORKER = 'docker.io/library/python@sha256:55432fc4ef6d07e33c10449312f0ec00071bbb310bb9bd7ba626a31fbbc2cb0d'
ROLES = {'kernel', 'initfs', 'rootfs', 'runtime_binary', 'python_launcher', 'python_process',
         'guardian_source', 'coordinator_source', 'guest_fixture', 'candidate', 'test_input', 'provision_receipt'}
FIXED_PINS = {
    'kernel': 'fb2cfb79eb1ae19447a85d75682d7fa5cfec97e24beb2609a492b806e8072c8d',
    'initfs': 'd5c6f80f42dfb49fabc4ad7c6867d8df37686f6514d90f4eeacda0428c84f20b',
    'rootfs': 'af7e906cc24b34138962ebd6f000f68fbb9a7194d530a149c0fca87d4b6507f4',
    'runtime_binary': 'e8bee184cc1f6b53982f9cc4ecb02085ebe238b8834112f71f8972c0d488511a',
    'python_launcher': '1955899cb535256cfa477d926d016819e52e747984722c44f76e39a4950fee0e',
    'python_process': '409ddb09021ac53577e7658de9ec09c899655c77a38744679ef73be9af21ecd5',
    'guest_fixture': 'bb20d238a7834551147efc6f3e15fc3ea56f844a5c506ad6aeaa2a0ffb752412',
    'candidate': 'f411dcca00abd8af2a0c1d450e8755fcf83edb3fdcb6b8d7dab8f45f462672ac',
    'test_input': 'f5773301b62d21d78fa932af611c3d284830456cb1032279f4ffaebf96be6401',
    'provision_receipt': 'e082359d42a2d24690c10cd16d220cb55783d2f6b68c5d9210333d5a4dafdea0',
}
UNAVAILABLE = ('external_instance_vm_liveness', 'vm_backend_auxiliary_ownership',
               'independent_instance_teardown_after_owner_loss')


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def metadata(path):
    path = Path(path)
    if not path.is_absolute() or path != Path(os.path.normpath(path)) or any(p.is_symlink() for p in (path, *path.parents)):
        raise ValueError('Noncanonical/linked path')
    info = path.lstat()
    if not stat.S_ISREG(info.st_mode) or info.st_uid != 501 or info.st_nlink != 1 or info.st_mode & 0o022:
        raise ValueError('File kind/owner/links/access differs')
    return {'path': str(path), 'device': info.st_dev, 'inode': info.st_ino, 'bytes': info.st_size,
            'mode': stat.S_IMODE(info.st_mode), 'uid': info.st_uid, 'gid': info.st_gid,
            'mtime_ns': info.st_mtime_ns, 'ctime_ns': info.st_ctime_ns}


def fingerprint(path, sparse=False):
    before = metadata(path)
    if sparse:
        # Reuse the frozen bounded sparse verifier; never read 512 GiB of holes.
        helper = HERE / 'apple_container_provision.py'; raw = helper.read_bytes()
        if sha(raw) != '2da6578d3c1cb49798ccc0f82db8f6e54c357c4a5c671736dfe556e2104dd67c':
            raise ValueError('Sparse verifier changed')
        scope = {'__name__': 'frozen_sparse_verifier', '__file__': str(helper)}
        exec(compile(raw, str(helper), 'exec'), scope)
        content = scope['snapshot_digest'](Path(path))['extent_map_and_data_sha256']
    else:
        if not 0 < before['bytes'] <= 640 * 1024**2: raise ValueError('File exceeds hash budget')
        with Path(path).open('rb') as source: content = hashlib.file_digest(source, 'sha256').hexdigest()
    if before != metadata(path): raise ValueError('File changed while hashing')
    return {**before, 'hash_kind': 'sparse_extents_and_data' if sparse else 'sha256', 'digest': content}


def write_seal(path, plan, expected_sha256):
    """Exclusive offline receipt only; never creates a runtime root or replaces old evidence."""
    path = Path(path)
    if sha(encoded(plan)) != expected_sha256: raise ValueError('Plan digest differs')
    parent = path.parent.lstat()
    if (any(p.is_symlink() for p in (path, *path.parents)) or not stat.S_ISDIR(parent.st_mode) or
            parent.st_uid != 501 or stat.S_IMODE(parent.st_mode) != 0o700):
        raise ValueError('Unsafe seal directory')
    with path.open('xb') as out:
        os.fchmod(out.fileno(), 0o400); out.write(encoded(plan) + b'\n'); out.flush(); os.fsync(out.fileno())
    fd = os.open(path.parent, os.O_RDONLY)
    try: os.fsync(fd)
    finally: os.close(fd)


def file_url(value):
    parsed = urlsplit(value)
    if parsed.scheme != 'file' or parsed.netloc or parsed.query or parsed.fragment:
        raise ValueError('Expected local file URL')
    return unquote(parsed.path, errors='strict')


def seal(configuration, reviewed_sha256, artifacts, boot_identity, armed_monotonic):
    """Bind actual serialized create output to separately reviewed bytes and artifact pins."""
    configuration = Path(configuration)
    if configuration != ROOT / 'runtime-configuration.json': raise ValueError('Foreign runtime root')
    config_identity = fingerprint(configuration)
    if config_identity['bytes'] > 1048576: raise ValueError('Configuration exceeds one MiB')
    raw = configuration.read_bytes()
    if sha(raw) != reviewed_sha256 or sha(raw) != config_identity['digest']:
        raise ValueError('Configuration bytes not reviewed')
    config = json.loads(raw); container = config['containerConfiguration']
    if (file_url(config['path']) != str(ROOT) or container['id'] != NAME or
            container['image']['reference'] != WORKER or container['networks'] != [] or
            container['publishedPorts'] != [] or container['publishedSockets'] != [] or
            container['readOnly'] is not True or container['runtimeHandler'] != 'container-runtime-linux' or
            any(container[key] is not False for key in ('ssh', 'rosetta', 'virtualization'))):
        raise ValueError('Reviewed configuration violates fixed positive scope')
    if set(artifacts) != ROLES: raise ValueError('Incomplete artifact/source pins')
    files = {}
    for role, pin in artifacts.items():
        files[role] = fingerprint(pin['path'], role == 'rootfs')
        if (files[role]['digest'] != pin['digest'] or
                role in FIXED_PINS and pin['digest'] != FIXED_PINS[role]):
            raise ValueError('Artifact pin differs: ' + role)
    references = {'kernel': file_url(config['kernel']['path']),
                  'initfs': config['initialFilesystem']['source'],
                  'rootfs': config['containerRootFilesystem']['source']}
    if any(files[role]['path'] != path for role, path in references.items()):
        raise ValueError('Artifact references do not bind configured files')
    if files['runtime_binary']['path'] != PROGRAM: raise ValueError('Foreign runtime program')
    if not boot_identity or not math.isfinite(armed_monotonic): raise ValueError('Missing boot/clock identity')
    plan = {'schema': 'OFFLINE_VM_BINDING_V1', 'root': str(ROOT), 'target': TARGET,
            'configuration': config_identity, 'files': files, 'boot_identity': boot_identity,
            'armed_monotonic': armed_monotonic, 'deadline_monotonic': armed_monotonic + 10,
            'binding_source_sha256': sha(Path(__file__).read_bytes())}
    return plan, sha(encoded(plan))


def verify(plan, expected_sha256, boot_identity, now):
    if sha(encoded(plan)) != expected_sha256 or plan['schema'] != 'OFFLINE_VM_BINDING_V1':
        raise ValueError('Sealed plan changed')
    if (plan['root'] != str(ROOT) or plan['target'] != TARGET or
            plan['binding_source_sha256'] != sha(Path(__file__).read_bytes()) or
            plan['boot_identity'] != boot_identity or not math.isfinite(now) or
            not math.isfinite(plan['armed_monotonic']) or not math.isfinite(plan['deadline_monotonic']) or
            plan['deadline_monotonic'] != plan['armed_monotonic'] + 10 or now < plan['armed_monotonic']):
        raise ValueError('Scope/source/boot/original deadline changed')
    if fingerprint(plan['configuration']['path']) != plan['configuration']:
        raise ValueError('Configuration identity changed')
    if set(plan['files']) != ROLES: raise ValueError('Incomplete bound files')
    for role, expected in plan['files'].items():
        if fingerprint(expected['path'], role == 'rootfs') != expected:
            raise ValueError('Bound artifact/source changed: ' + role)


def participant(plan, expected_sha256, role, identity, plan_path, boot_identity, now):
    """Shared guardian/coordinator readiness contract, not a process observer."""
    verify(plan, expected_sha256, boot_identity, now)
    if role not in ('guardian', 'coordinator') or now >= plan['deadline_monotonic']:
        raise ValueError('Invalid participant or expired original budget')
    expected_argv = [plan['files']['python_launcher']['path'], '-I', '-B',
                     plan['files'][role + '_source']['path'], str(plan_path), expected_sha256]
    if (set(identity) != {'pid', 'uid', 'birth', 'executable', 'argv'} or
            type(identity['pid']) is not int or identity['pid'] <= 0 or identity['uid'] != 501 or
            not isinstance(identity['birth'], str) or not identity['birth'] or
            identity['executable'] != plan['files']['python_process']['path'] or identity['argv'] != expected_argv):
        raise ValueError('Participant identity/arguments differ')
    return {'role': role, 'identity': json.loads(encoded(identity)), 'plan_sha256': expected_sha256,
            'deadline_monotonic': plan['deadline_monotonic'], 'observed_monotonic': now}


def check_readiness(plan, expected_sha256, receipt, current_identity):
    role = receipt['role']
    if (sha(encoded(plan)) != expected_sha256 or role not in ('guardian', 'coordinator') or receipt['plan_sha256'] != expected_sha256 or
            receipt['deadline_monotonic'] != plan['deadline_monotonic'] or
            not plan['armed_monotonic'] <= receipt['observed_monotonic'] < plan['deadline_monotonic'] or
            receipt['identity'] != current_identity):
        raise ValueError('Readiness/replacement/original deadline differs')


def bootstrap_bundle(plan, expected_sha256, boot_identity, now, previous=None):
    """Check the runtime's later copies against sealed create output; no VM is contacted."""
    verify(plan, expected_sha256, boot_identity, now)
    config = json.loads(Path(plan['configuration']['path']).read_bytes())
    kernel = {**config['kernel'], 'path': (ROOT / 'kernel.bin').as_uri()}
    rootfs = {**config['containerRootFilesystem'], 'source': str(ROOT / 'rootfs.ext4')}
    rootfs['options'] = list(rootfs['options'])
    if 'ro' not in rootfs['options']: rootfs['options'].append('ro')
    expected_json = {'config.json': config['containerConfiguration'], 'kernel.json': kernel, 'rootfs.json': rootfs}
    files = {}
    for name, expected in expected_json.items():
        path = ROOT / name; files[name] = fingerprint(path)
        raw = path.read_bytes()
        if len(raw) > 1048576 or json.loads(raw) != expected or files[name] != fingerprint(path):
            raise ValueError('Bootstrapped configuration/reference changed')
    for name, role in (('kernel.bin', 'kernel'), ('initfs.ext4', 'initfs'), ('rootfs.ext4', 'rootfs')):
        files[name] = fingerprint(ROOT / name, role == 'rootfs')
        if files[name]['digest'] != plan['files'][role]['digest']:
            raise ValueError('Bootstrapped artifact content/sparse structure changed')
    binding = {'plan_sha256': expected_sha256, 'files': files, 'original_deadline_monotonic': plan['deadline_monotonic']}
    if previous is not None and previous != binding: raise ValueError('Bootstrapped bundle replaced')
    return binding


def runtime_owner(plan, expected_sha256, identity, independent_pid, boot_identity, now, previous=None):
    """Bind a verified runtime observation to this plan, never to an inferred VM backend."""
    verify(plan, expected_sha256, boot_identity, now)
    basic = {key: identity[key] for key in ('pid', 'uid', 'birth', 'executable')}
    origin = ROOT / 'service.plist'; plist = fingerprint(origin)
    if (identity['target'] != TARGET or identity['container_id'] != NAME or
            identity['origin'] != str(origin) or identity['plist_sha256'] != plist['digest'] or
            identity['binary_sha256'] != plan['files']['runtime_binary']['digest'] or
            identity['executable'] != PROGRAM or identity['uid'] != 501 or
            type(identity['pid']) is not int or identity['pid'] <= 0 or not identity['birth'] or
            basic != independent_pid):
        raise ValueError('Runtime registration/PID binding differs')
    import plistlib
    config = plistlib.loads(origin.read_bytes())
    if (config.get('Label') != TARGET.removeprefix('user/501/') or config.get('Program') is not None or
            config.get('ProgramArguments') != [PROGRAM, 'start', '--root', str(ROOT), '--uuid', NAME] or
            config.get('EnvironmentVariables', {}).get('CONTAINER_APP_ROOT', '').rstrip('/') != str(ROOT.parent.parent) or
            config.get('EnvironmentVariables', {}).get('CONTAINER_INSTALL_ROOT', '').rstrip('/') != '/usr/local'):
        raise ValueError('Runtime source/arguments/roots differ')
    if plist != fingerprint(origin): raise ValueError('Runtime plist changed during binding')
    binding = {'plan_sha256': expected_sha256, 'runtime_identity': json.loads(encoded(identity)), 'plist': plist,
               'configuration': plan['configuration'], 'original_deadline_monotonic': plan['deadline_monotonic']}
    if previous is not None and previous != binding: raise ValueError('Runtime owner replaced')
    return binding


def disposition(plan, expected_sha256, journal, boot_identity, now):
    """Replay never rearms. No supplied journal can make the unsupported VM oracle pass."""
    verify(plan, expected_sha256, boot_identity, now)
    if journal and not journal.endswith(b'\n'): raise ValueError('Interrupted journal')
    if len(journal) > 1048576: raise ValueError('Journal exceeds budget')
    previous = plan['armed_monotonic']; last = 'PREPARED'
    allowed = {'ARMED', 'GUARDIAN_READY', 'COORDINATOR_READY', 'RUNTIME_OWNER_BOUND',
               'COORDINATOR_LOST', 'GUARDIAN_LOST', 'DEADLINE_EXPIRED', 'RUNTIME_OWNER_ABSENT',
               'TEARDOWN_INCOMPLETE', 'STOP_AND_REVIEW'}
    for line in journal.splitlines():
        event = json.loads(line)
        if (event['event'] not in allowed or event['plan_sha256'] != expected_sha256 or
                event['deadline_monotonic'] != plan['deadline_monotonic'] or
                not math.isfinite(event['monotonic']) or not previous <= event['monotonic'] <= now):
            raise ValueError('Journal provenance/clock/unsupported success claim')
        previous = event['monotonic']; last = event['event']
    return {'decision': 'TERMINAL_NO_GO', 'execution_authorized': False, 'host_actions': [],
            'unavailable': list(UNAVAILABLE), 'last_event': last,
            'deadline_expired': now >= plan['deadline_monotonic'],
            'original_deadline_monotonic': plan['deadline_monotonic'],
            'teardown_proven': False, 'preserve_evidence': True, 'retry': False}


if __name__ == '__main__':
    raise SystemExit('Offline binding only; no VM/guardian/coordinator execution entrypoint')
