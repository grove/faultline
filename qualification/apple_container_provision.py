"""One separately approved worker/kernel provisioning attempt. Never starts a VM."""

import errno
import gzip
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import signal
import stat
import subprocess
import sys
import tarfile

HERE = Path(__file__).resolve().parent
BUNDLE = Path('/private/tmp/faultline-apple-positive-v2')
DEST = BUNDLE / 'provision-v1'
RUNTIME = BUNDLE / 'setup-v4/runtime'
RECEIPT_SHA = '7366b677973d26db9b16efbfc1cae563e262de59d4fb1d695ed79d56f73b584c'
SETUP_SHA = '82a20ecffdedef478b72fe4b3b9a384cb8e35ad9b407b7e61c510a596b21f101'
WORKER = 'docker.io/library/python@sha256:55432fc4ef6d07e33c10449312f0ec00071bbb310bb9bd7ba626a31fbbc2cb0d'
MANIFEST = WORKER.split('@')[1]
CONFIG = 'sha256:da841a7026abc0089180121604f6d0ba4324998e2d133eccae13f22707055dc1'
LAYERS = [('c75f989a229d12b2d2613a5997de9ff3546f664c22da9248720033a2410220f6', 28137179),
          ('aa08835651e777794bde3e8c99bee012c418f60d0d164df22497fa01dc72aca5', 3176232),
          ('7b2df2902dddd1a4510670c4d3a6d61b4458fa3e7c1ae0b262d75bde1349ab14', 14748696),
          ('32020fed7f2a057b9cee7fdbfa3ea9fc394149118d7a951c462c7055c3cd3f56', 250)]
KERNEL_URL = 'https://github.com/kata-containers/kata-containers/releases/download/3.32.0/kata-static-3.32.0-arm64.tar.zst'
ARCHIVE_SHA = '8736c054d9223974735394f822000823baef509e1c33405ec798240fa9b6e4b5'
ARCHIVE_SIZE = 696573576
MEMBER = 'opt/kata/share/kata-containers/vmlinux-6.18.35-197-debug'
KERNEL = DEST / 'vmlinux-6.18.35-197-debug'
ARCHIVE = DEST / 'kata-static-3.32.0-arm64.tar.zst'
CLI = '/usr/local/bin/container'
ENV = {'HOME': '/Users/grove', 'PATH': '/usr/bin:/bin', 'LC_ALL': 'C', 'TZ': 'Europe/Oslo',
       'CONTAINER_APP_ROOT': str(RUNTIME), 'CONTAINER_INSTALL_ROOT': '/usr/local',
       'XDG_CONFIG_HOME': str(BUNDLE / 'setup-v4/config-home')}
PULL = [CLI, 'image', 'pull', '--platform', 'linux/arm64/v8', '--scheme', 'https',
        '--progress', 'plain', '--max-concurrent-downloads', '1', WORKER]
DOWNLOAD = ['/usr/bin/curl', '-q', '--fail', '--silent', '--show-error', '--location',
            '--proto', '=https', '--proto-redir', '=https', '--max-redirs', '5',
            '--connect-timeout', '10', '--max-time', '300', '--max-filesize', str(ARCHIVE_SIZE),
            '--output', str(ARCHIVE), KERNEL_URL]


def digest(path):
    with path.open('rb') as source:
        return hashlib.file_digest(source, 'sha256').hexdigest()


def regular(path, maximum):
    if path.is_symlink() or any(p.is_symlink() for p in path.parents):
        raise ValueError('Linked artifact path')
    info = path.lstat()
    if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or not 0 < info.st_size <= maximum:
        raise ValueError('Artifact kind/link/size exceeds scope: ' + str(path))
    return info


def metadata(path):
    regular(path, 1048576)
    return json.loads(path.read_bytes())


def elf(header):
    if header[:6] != b'\x7fELF\x02\x01' or int.from_bytes(header[18:20], 'little') != 183:
        raise ValueError('Expected a little-endian AArch64 ELF binary')


class ReadBudget:
    def __init__(self, source, maximum):
        self.source, self.remaining = source, maximum

    def read(self, count):
        data = self.source.read(min(count, self.remaining + 1))
        self.remaining -= len(data)
        if self.remaining < 0:
            raise ValueError('Decompressed archive exceeds read budget')
        return data


def extract_kernel(archive, destination):
    regular(archive, ARCHIVE_SIZE)
    if archive.stat().st_size != ARCHIVE_SIZE or digest(archive) != ARCHIVE_SHA:
        raise ValueError('Kata archive size/digest mismatch')
    from compression import zstd
    found = False
    with zstd.open(archive, 'rb') as source, tarfile.open(fileobj=ReadBudget(source, 8 * 1024**3), mode='r|') as entries:
        for count, member in enumerate(entries, 1):
            if count > 100000:
                raise ValueError('Kata archive member count exceeds budget')
            if member.name.removeprefix('./') != MEMBER:
                continue
            if found or not member.isfile() or not 0 < member.size <= 128 * 1024**2:
                raise ValueError('Duplicate, nonregular or oversized kernel member')
            found = True
            with entries.extractfile(member) as data, destination.open('xb') as output:
                shutil.copyfileobj(data, output, 65536)
                output.flush()
                os.fsync(output.fileno())
    if not found:
        raise ValueError('Pinned kernel member absent')
    regular(destination, 128 * 1024**2)
    with destination.open('rb') as source:
        elf(source.read(64))
    destination.chmod(0o444)
    return {'path': str(destination), 'sha256': digest(destination), 'bytes': destination.stat().st_size,
            'archive_sha256': ARCHIVE_SHA, 'member': MEMBER}


def snapshot_digest(path):
    """Hash data extents plus holes/length, without reading 512 GiB of sparse zeros."""
    info = regular(path, 513 * 1024**3)
    value = hashlib.sha256(str(info.st_size).encode() + b'\n')
    position = read = 0
    extents = []
    with path.open('rb', buffering=0) as source:
        while position < info.st_size:
            try:
                start = os.lseek(source.fileno(), position, os.SEEK_DATA)
            except OSError as error:
                if error.errno == errno.ENXIO:
                    break
                raise
            end = os.lseek(source.fileno(), start, os.SEEK_HOLE)
            if not position <= start < end <= info.st_size or len(extents) >= 8192:
                raise ValueError('Invalid/excessive sparse extents')
            read += end - start
            if read > 8 * 1024**3:
                raise ValueError('Snapshot data extents exceed eight GiB read budget')
            extents.append([start, end])
            value.update(f'{start}:{end}\n'.encode())
            source.seek(start)
            remaining = end - start
            while remaining:
                block = source.read(min(remaining, 65536))
                if not block:
                    raise ValueError('Short snapshot read')
                value.update(block)
                remaining -= len(block)
            position = end
    return {'path': str(path), 'logical_bytes': info.st_size, 'allocated_bytes': info.st_blocks * 512,
            'data_bytes_read': read, 'extents': extents, 'extent_map_and_data_sha256': value.hexdigest(),
            'check': 'SPARSE_DATA_AND_STRUCTURE_NOT_FSCK_OR_GUEST_BOOT'}


def verify_worker():
    def blob(desc, limit):
        if not re.fullmatch(r'sha256:[0-9a-f]{64}', desc['digest']):
            raise ValueError('Malformed worker digest')
        path = RUNTIME / 'content/blobs/sha256' / desc['digest'][7:]
        info = regular(path, limit)
        if info.st_size != desc['size'] or digest(path) != desc['digest'][7:]:
            raise ValueError('Worker blob size/digest mismatch')
        return path

    state = metadata(RUNTIME / 'state.json')
    index = metadata(blob(state[WORKER], 1048576))
    if len(index['manifests']) != 1 or index['manifests'][0]['digest'] != MANIFEST:
        raise ValueError('Worker index differs')
    platform = index['manifests'][0]['platform']
    if platform['os'] != 'linux' or platform['architecture'] != 'arm64' or platform.get('variant', 'v8') != 'v8':
        raise ValueError('Worker index platform differs')
    manifest = metadata(blob(index['manifests'][0], 1048576))
    if manifest['config']['digest'] != CONFIG or [(d['digest'][7:], d['size']) for d in manifest['layers']] != LAYERS:
        raise ValueError('Worker descriptors differ')
    config = metadata(blob(manifest['config'], 1048576))
    if config['os'] != 'linux' or config['architecture'] != 'arm64' or config.get('variant', 'v8') != 'v8':
        raise ValueError('Worker platform differs')
    interpreter = {}
    for desc in manifest['layers']:
        path = blob(desc, 32 * 1024**2)
        with gzip.open(path, 'rb') as source, tarfile.open(fileobj=ReadBudget(source, 512 * 1024**2), mode='r|') as entries:
            for count, member in enumerate(entries, 1):
                if count > 40000:
                    raise ValueError('Worker layer member budget exceeded')
                name = member.name.removeprefix('./')
                if name in ('usr/.wh..wh..opq', 'usr/local/.wh..wh..opq', 'usr/local/bin/.wh..wh..opq',
                            'usr/local/bin/.wh.python3', 'usr/local/bin/.wh.python3.13'):
                    raise ValueError('Interpreter whiteout requires review')
                if name == 'usr/local/bin/python3':
                    if not member.issym() or member.linkname != 'python3.13':
                        raise ValueError('Unexpected python3 link')
                    interpreter['link'] = member.linkname
                if name == 'usr/local/bin/python3.13':
                    if not member.isfile() or not 0 < member.size <= 64 * 1024**2 or not member.mode & 0o111:
                        raise ValueError('Unexpected Python interpreter file')
                    with entries.extractfile(member) as data:
                        header = data.read(64)
                        elf(header)
                        value = hashlib.sha256(header)
                        for block in iter(lambda: data.read(65536), b''):
                            value.update(block)
                    interpreter.update(sha256=value.hexdigest(), bytes=member.size)
    if set(interpreter) != {'link', 'sha256', 'bytes'}:
        raise ValueError('Interpreter files not verified')
    directory = RUNTIME / 'snapshots' / MANIFEST[7:]
    snapshot = directory / 'snapshot'
    description = metadata(directory / 'snapshot-info')
    if description['source'] != str(snapshot) or description['destination'] != '/' or description['type']['block']['format'] != 'ext4':
        raise ValueError('Worker snapshot metadata differs')
    regular(snapshot, 513 * 1024**3)
    with snapshot.open('rb') as source:
        source.seek(1024)
        sb = source.read(1024)
    shift = int.from_bytes(sb[24:28], 'little')
    if sb[56:58] != b'\x53\xef' or shift > 6 or not 512 * 1024**3 <= int.from_bytes(sb[4:8], 'little') * (1024 << shift) <= snapshot.stat().st_size:
        raise ValueError('Worker EXT4 geometry differs')
    for path in (RUNTIME / 'content/ingest', RUNTIME / 'snapshots/ingest'):
        if path.is_symlink() or not path.is_dir() or any(path.iterdir()):
            raise ValueError('Incomplete image ingest remains')
    return {'reference': WORKER, 'manifest': manifest, 'interpreter': interpreter,
            'snapshot': snapshot_digest(snapshot)}


def storage():
    logical = allocated = count = 0
    def unreadable(error):
        raise error
    for root in (BUNDLE / 'setup-v4', DEST):
        for directory, dirs, files in os.walk(root, followlinks=False, onerror=unreadable):
            if len(Path(directory).relative_to(root).parts) > 16:
                raise ValueError('Storage depth exceeded')
            for name in dirs + files:
                info = (Path(directory) / name).lstat()
                count += 1
                if count > 8192 or not (stat.S_ISREG(info.st_mode) or stat.S_ISDIR(info.st_mode)):
                    raise ValueError('Storage kind/count exceeded')
                logical += info.st_size
                allocated += info.st_blocks * 512
    free = shutil.disk_usage(BUNDLE).free
    if logical > 514 * 1024**3 or allocated > 8 * 1024**3 or free < 16 * 1024**3:
        raise ValueError('Storage phase admission failed')
    return {'logical_bytes': logical, 'allocated_bytes': allocated, 'free_bytes': free}


def kernel_store():
    path = RUNTIME / 'kernels'
    if path.is_symlink():
        raise ValueError('Linked kernel store; leave it untouched')
    if not path.exists():
        return None
    if not path.is_dir() or any(path.iterdir()):
        raise ValueError('Nonempty kernel store; leave it untouched')
    info = path.stat()
    return {'device': info.st_dev, 'inode': info.st_ino, 'mode': info.st_mode}


def provision():
    report = {'kind': 'WORKER_KERNEL_PROVISION_V1', 'result': 'FAILED', 'qualification_granted': False,
              'vm_launches': 0, 'observations': [], 'environment': ENV, 'cwd': '/', 'setup_v4_receipt_sha256': RECEIPT_SHA}
    with (BUNDLE / 'evidence/provision-v1.json').open('x') as evidence:
        def checkpoint():
            evidence.seek(0); json.dump(report, evidence, indent=2, sort_keys=True); evidence.write('\n')
            evidence.truncate(); evidence.flush(); os.fsync(evidence.fileno())

        def run(argv, timeout, private=False):
            entry = {'argv': argv, 'timeout_seconds': timeout}; report['observations'].append(entry); checkpoint()
            try:
                # shortcut: finite trusted CLI output is captured, not a hard live stream quota.
                result = subprocess.run(argv, cwd='/', env=ENV, stdin=subprocess.DEVNULL, capture_output=True, timeout=timeout)
            except subprocess.TimeoutExpired as error:
                entry.update(timed_out=True, stdout='NOT_RETAINED' if private else (error.stdout or b'')[:65536].decode(errors='replace'),
                             stderr=(error.stderr or b'')[:65536].decode(errors='replace'))
                raise
            entry.update(returncode=result.returncode, stdout='NOT_RETAINED' if private else result.stdout[:65536].decode(errors='replace'), stderr=result.stderr[:65536].decode(errors='replace'))
            checkpoint()
            if result.returncode or len(result.stdout) > (4194304 if private else 65536) or len(result.stderr) > 65536:
                raise ValueError('Provision command failed or output exceeded retention bound')
            return result.stdout.decode()

        def expired(*_):
            raise TimeoutError('600-second provisioning coordinator deadline')

        previous = signal.signal(signal.SIGALRM, expired); signal.alarm(600)
        try:
            if DEST.exists() or DEST.is_symlink() or digest(BUNDLE / 'evidence/setup-v4.json') != RECEIPT_SHA:
                raise ValueError('Consumed provision identity or changed setup receipt')
            if digest(HERE / 'apple_container_service_setup.py') != SETUP_SHA:
                raise ValueError('Consumed setup helper bytes changed')
            spec = importlib.util.spec_from_file_location('setup_v4', HERE / 'apple_container_service_setup.py')
            setup = importlib.util.module_from_spec(spec); spec.loader.exec_module(setup)
            if digest(HERE / 'apple_container_recover_setup_v2.py') != setup.OBSERVER_SHA256:
                raise ValueError('Observer bytes changed')
            baseline = json.loads((BUNDLE / 'evidence/setup-v4.json').read_bytes())
            report['source_sha256'] = {name: digest(HERE / name) for name in
                                       ('apple_container_provision.py', 'apple_container_service_setup.py', 'apple_container_recover_setup_v2.py')}
            for name, expected in baseline['binary_sha256'].items():
                if digest(Path(name)) != expected:
                    raise ValueError('Provisioning executable bytes changed')
            spec = importlib.util.spec_from_file_location('process_observer', HERE / 'apple_container_recover_setup_v2.py')
            observer = importlib.util.module_from_spec(spec); spec.loader.exec_module(observer)
            state = metadata(RUNTIME / 'state.json')
            if set(state) != {setup.INIT}:
                raise ValueError('Unexpected existing image state; no retry')
            if state[setup.INIT]['digest'] != baseline['init_verification']['blobs'][0]['digest']:
                raise ValueError('Accepted init reference changed')
            config = (RUNTIME / 'config/config.toml').read_bytes()
            if hashlib.sha256(config).hexdigest() != setup.CONFIG_SHA256:
                raise ValueError('Runtime config changed')
            kernels_before = kernel_store()
            report['kernel_store_before'] = kernels_before
            identities = {}
            for entry in baseline['process_plan']:
                text = run(['/bin/launchctl', 'print', entry['target']], 5, True)
                if setup.owned_plist(text, entry['target']) != entry['identity'] or re.findall(r'^\tpid = ([0-9]+)$', text, re.M) != [str(entry['pid'])]:
                    raise ValueError('Setup-v4 service ownership changed; preserve services')
                for key in ('CONTAINER_APP_ROOT', 'CONTAINER_INSTALL_ROOT'):
                    values = re.findall(r'^\t\t' + key + r' => (.+)$', text, re.M)
                    if len(values) != 1 or not setup.same_path(values[0], ENV[key]):
                        raise ValueError('Live service root changed')
                identities[entry['target']] = entry['identity']
            observer.verify_processes(observer.processes(baseline['process_plan'], lambda argv: run(argv, 5)), baseline['process_plan'])
            status = json.loads(run([CLI, 'system', 'status', '--format', 'json'], 15))
            if (status['status'] != 'running' or not setup.same_path(status['paths']['appRoot'], RUNTIME) or
                    not setup.same_path(status['paths']['installRoot'], '/usr/local') or
                    status['server']['version'] != '1.5.0' or status['server']['commit'] != 'd265d669ecae041bf338cb3b39c4118316d138f0' or
                    status['resources']['containersTotal'] != 0):
                raise ValueError('Existing service/root/source/VM state differs')
            DEST.mkdir(mode=0o700)
            report['storage_before_worker'] = storage(); checkpoint()
            run(PULL, 180)
            report['storage_after_worker'] = storage(); checkpoint()
            if metadata(RUNTIME / 'state.json') != {**state, WORKER: metadata(RUNTIME / 'state.json')[WORKER]}:
                raise ValueError('Unrelated image state changed')
            report['worker'] = verify_worker(); checkpoint()
            run(DOWNLOAD, 310)
            report['storage_after_download'] = storage(); checkpoint()
            report['kernel'] = extract_kernel(ARCHIVE, KERNEL)
            report['storage_after_extract'] = storage()
            if (RUNTIME / 'config/config.toml').read_bytes() != config or kernel_store() != kernels_before:
                raise ValueError('Runtime config/default kernel state changed')
            for entry in baseline['process_plan']:
                if setup.owned_plist(run(['/bin/launchctl', 'print', entry['target']], 5, True), entry['target']) != identities[entry['target']]:
                    raise ValueError('Existing service ownership changed')
            observer.verify_processes(observer.processes(baseline['process_plan'], lambda argv: run(argv, 5)), baseline['process_plan'])
            report['result'] = 'WORKER_AND_DEDICATED_KERNEL_VERIFIED_NO_VM'
        except (Exception, KeyboardInterrupt) as error:
            report['error'] = type(error).__name__ + ': ' + str(error)
            report['failure_policy'] = 'PRESERVE_SERVICES_AND_ALL_PARTIAL_STATE; NO_RETRY_OR_CLEANUP'
        finally:
            signal.alarm(0); signal.signal(signal.SIGALRM, previous); checkpoint()
    return 0 if report['result'] == 'WORKER_AND_DEDICATED_KERNEL_VERIFIED_NO_VM' else 1


if __name__ == '__main__':
    if sys.argv[1:] != ['provision-v1']:
        raise SystemExit('Separate authorization required; exact argument: provision-v1')
    raise SystemExit(provision())
