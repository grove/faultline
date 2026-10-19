"""Separately authorized offline verification/extraction; no service or network calls."""

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import signal
import stat
import sys

HERE = Path(__file__).resolve().parent
HELPER_SHA = '2da6578d3c1cb49798ccc0f82db8f6e54c357c4a5c671736dfe556e2104dd67c'
helper = HERE / 'apple_container_provision.py'
if hashlib.sha256(helper.read_bytes()).hexdigest() != HELPER_SHA:
    raise ValueError('Frozen provision-v1 helper changed')
spec = importlib.util.spec_from_file_location('frozen_provision_v1', helper)
p = importlib.util.module_from_spec(spec); spec.loader.exec_module(p)

V1_SHA = 'ad1949e4a3fb2dbc70ebcb5a34bf12b0a40a2581ac7fb667c85e5383707259e2'
CONFIG_SHA = 'ec039793064339b1c438630aaa4a81b03717d96a6ca6b7a19a945c6f85c0883e'
STATE_SHA = 'e20ab71a03fb61bc86129a28e6b75d0d1a4f53799df0d04758b63048c1e4e94f'
DEST = p.BUNDLE / 'provision-v2'
MAX_KERNEL = 128 * 1024**2
MAX_LOGICAL = 515 * 1024**3


def storage(reserve=0):
    logical = allocated = count = 0
    def unreadable(error):
        raise error
    for root in (p.BUNDLE / 'setup-v4', p.DEST, DEST):
        if root.is_symlink() or not root.is_dir():
            raise ValueError('Storage root missing or linked')
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
    free = shutil.disk_usage(p.BUNDLE).free
    if logical + reserve > MAX_LOGICAL or allocated + reserve > 8 * 1024**3 or free - reserve < 16 * 1024**3:
        raise ValueError('Storage phase admission failed')
    return {'logical_bytes': logical, 'allocated_bytes': allocated, 'free_bytes': free,
            'reserved_kernel_bytes': reserve}


def verify_archive():
    info = p.regular(p.ARCHIVE, p.ARCHIVE_SIZE)
    value = p.digest(p.ARCHIVE)
    if info.st_size != p.ARCHIVE_SIZE or value != p.ARCHIVE_SHA:
        raise ValueError('Existing Kata archive size/digest mismatch')
    return {'path': str(p.ARCHIVE), 'bytes': info.st_size, 'sha256': value}


def provision():
    report = {'kind': 'WORKER_KERNEL_PROVISION_V2', 'result': 'FAILED', 'qualification_granted': False,
              'vm_launches': 0, 'service_commands': [], 'retrieval_commands': [],
              'provision_v1_receipt_sha256': V1_SHA, 'setup_v4_receipt_sha256': p.RECEIPT_SHA,
              'source_sha256': {Path(__file__).name: p.digest(Path(__file__)), helper.name: HELPER_SHA}}
    with (p.BUNDLE / 'evidence/provision-v2.json').open('x') as evidence:
        def checkpoint():
            evidence.seek(0); json.dump(report, evidence, indent=2, sort_keys=True); evidence.write('\n')
            evidence.truncate(); evidence.flush(); os.fsync(evidence.fileno())

        def expired(*_):
            raise TimeoutError('600-second verification/extraction deadline')

        previous = signal.signal(signal.SIGALRM, expired); signal.alarm(600)
        try:
            if DEST.exists() or DEST.is_symlink():
                raise ValueError('Consumed provision-v2 destination')
            old_path = p.BUNDLE / 'evidence/provision-v1.json'
            old = p.metadata(old_path)
            if p.digest(old_path) != V1_SHA or p.digest(p.BUNDLE / 'evidence/setup-v4.json') != p.RECEIPT_SHA:
                raise ValueError('Original evidence changed')
            config = p.RUNTIME / 'config/config.toml'
            if (p.digest(config) != CONFIG_SHA or p.kernel_store() != old['kernel_store_before'] or
                    p.digest(p.RUNTIME / 'state.json') != STATE_SHA):
                raise ValueError('Runtime config/default kernel state changed')
            state = p.metadata(p.RUNTIME / 'state.json')
            # Pin the accepted init entry and the locally generated worker index too.
            setup = p.metadata(p.BUNDLE / 'evidence/setup-v4.json')
            init = setup['init_verification']['reference']
            if (set(state) != {init, p.WORKER} or
                    state[init]['digest'] != setup['init_verification']['blobs'][0]['digest']):
                raise ValueError('Existing image state differs')
            report['archive'] = verify_archive(); checkpoint()
            report['worker'] = p.verify_worker()
            if report['worker'] != old['worker']:
                raise ValueError('Worker content/snapshot differs from provision-v1')
            checkpoint()
            DEST.mkdir(mode=0o700)
            report['storage_before_extract'] = storage(MAX_KERNEL); checkpoint()
            report['kernel'] = p.extract_kernel(p.ARCHIVE, DEST / p.KERNEL.name); checkpoint()
            report['storage_after_extract'] = storage(); checkpoint()
            if (p.digest(old_path) != V1_SHA or p.digest(config) != CONFIG_SHA or
                    p.metadata(p.RUNTIME / 'state.json') != state or
                    p.kernel_store() != old['kernel_store_before'] or
                    verify_archive() != report['archive'] or p.verify_worker() != old['worker']):
                raise ValueError('Preserved evidence/artifact/runtime state changed')
            report['result'] = 'WORKER_AND_DEDICATED_KERNEL_VERIFIED_NO_VM'
        except (Exception, KeyboardInterrupt) as error:
            report['error'] = type(error).__name__ + ': ' + str(error)
            report['failure_policy'] = 'PRESERVE_SERVICES_AND_ALL_PARTIAL_STATE; NO_RETRY_OR_CLEANUP'
        finally:
            signal.alarm(0); signal.signal(signal.SIGALRM, previous); checkpoint()
    return 0 if report['result'] == 'WORKER_AND_DEDICATED_KERNEL_VERIFIED_NO_VM' else 1


if __name__ == '__main__':
    if sys.argv[1:] != ['provision-v2']:
        raise SystemExit('Separate authorization required; exact argument: provision-v2')
    raise SystemExit(provision())
