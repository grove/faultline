"""Separately authorized offline ARM64 Image verification/copy; no service or network calls."""

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
V2_SHA = 'c56a7cdf32130e60142adc66ecb43bfa034191ec867dad43cf3682dab17727c6'
CONFIG_SHA = 'ec039793064339b1c438630aaa4a81b03717d96a6ca6b7a19a945c6f85c0883e'
STATE_SHA = 'e20ab71a03fb61bc86129a28e6b75d0d1a4f53799df0d04758b63048c1e4e94f'
EXISTING = p.BUNDLE / 'provision-v2' / p.KERNEL.name
DEST = p.BUNDLE / 'provision-v3'
KERNEL_BYTES = 30423552
KERNEL_SHA = 'fb2cfb79eb1ae19447a85d75682d7fa5cfec97e24beb2609a492b806e8072c8d'
MAX_KERNEL = 128 * 1024**2
MAX_LOGICAL = 515 * 1024**3


def image_header(header, file_size):
    if len(header) != 64 or header[:4] == b'\x7fELF' or header[56:60] != b'ARMd':
        raise ValueError('Expected a raw ARM64 Linux Image header')
    offset, size, flags = [int.from_bytes(header[i:i+8], 'little') for i in (8, 16, 24)]
    pe_offset = int.from_bytes(header[60:64], 'little')
    if (not 64 <= file_size <= size <= MAX_KERNEL or offset > MAX_KERNEL or offset % 4096 or
            flags & 1 or flags & ~15 or any(header[32:56]) or
            (pe_offset and (pe_offset < 64 or pe_offset % 4 or pe_offset > file_size - 24))):
        raise ValueError('Unsupported ARM64 Image size/offset/endianness/flags/reserved fields')
    return {'format': 'LINUX_ARM64_IMAGE', 'text_offset': offset, 'image_size': size,
            'flags': flags, 'endianness': 'little', 'page_size': (None, 4096, 16384, 65536)[(flags >> 1) & 3],
            'physical_placement_anywhere': bool(flags & 8), 'pe_header_offset': pe_offset}


def verify_existing(path):
    info = p.regular(path, MAX_KERNEL)
    if info.st_size != KERNEL_BYTES or p.digest(path) != KERNEL_SHA:
        raise ValueError('Existing kernel size/digest differs')
    with path.open('rb') as source:
        header = image_header(source.read(64), info.st_size)
    return {'path': str(path), 'bytes': info.st_size, 'sha256': KERNEL_SHA, 'header': header}


def compare_member(existing):
    """Compare bytes without extracting anything; consume the bounded archive scan."""
    import tarfile
    from compression import zstd
    result = verify_existing(existing)
    info = p.regular(p.ARCHIVE, p.ARCHIVE_SIZE)
    if info.st_size != p.ARCHIVE_SIZE or p.digest(p.ARCHIVE) != p.ARCHIVE_SHA:
        raise ValueError('Kata archive size/digest mismatch')
    found = False
    with zstd.open(p.ARCHIVE, 'rb') as source, tarfile.open(fileobj=p.ReadBudget(source, 8 * 1024**3), mode='r|') as entries:
        for count, member in enumerate(entries, 1):
            if count > 100000:
                raise ValueError('Kata archive member count exceeds budget')
            if member.name.removeprefix('./') != p.MEMBER:
                continue
            if found or not member.isfile() or member.size != KERNEL_BYTES:
                raise ValueError('Duplicate, nonregular or wrong-size kernel member')
            found = True
            value = hashlib.sha256()
            with entries.extractfile(member) as data, existing.open('rb') as local:
                for block in iter(lambda: data.read(65536), b''):
                    if block != local.read(len(block)):
                        raise ValueError('Existing kernel differs from archive member')
                    value.update(block)
                if local.read(1) or value.hexdigest() != KERNEL_SHA:
                    raise ValueError('Archive member length/digest differs')
    if not found:
        raise ValueError('Pinned kernel member absent')
    if verify_existing(existing) != result:
        raise ValueError('Existing kernel changed during comparison')
    return {**result, 'archive_sha256': p.ARCHIVE_SHA, 'member': p.MEMBER, 'comparison': 'BYTE_FOR_BYTE'}


def copy_kernel(existing, destination):
    verify_existing(existing)
    with existing.open('rb') as source, destination.open('xb') as output:
        shutil.copyfileobj(p.ReadBudget(source, KERNEL_BYTES), output, 65536)
        output.flush(); os.fsync(output.fileno())
    result = verify_existing(destination)
    destination.chmod(0o444)
    return {**result, 'archive_sha256': p.ARCHIVE_SHA, 'member': p.MEMBER, 'copied_from': str(existing)}


def storage(reserve=0):
    logical = allocated = count = 0
    def unreadable(error):
        raise error
    if p.BUNDLE.is_symlink() or not p.BUNDLE.is_dir():
        raise ValueError('Storage root missing or linked')
    for directory, dirs, files in os.walk(p.BUNDLE, followlinks=False, onerror=unreadable):
        if len(Path(directory).relative_to(p.BUNDLE).parts) > 16:
            raise ValueError('Storage depth exceeded')
        for name in dirs + files:
            info = (Path(directory) / name).lstat()
            count += 1
            if count > 8192 or not (stat.S_ISREG(info.st_mode) or stat.S_ISDIR(info.st_mode)):
                raise ValueError('Storage kind/count exceeded')
            logical += info.st_size
            allocated += info.st_blocks * 512
    free = shutil.disk_usage(p.BUNDLE).free
    # Reserve receipt growth as well as the prospective kernel, within the same caps.
    reserved = reserve + 1024**2
    if logical + reserved > MAX_LOGICAL or allocated + reserved > 8 * 1024**3 or free - reserved < 16 * 1024**3:
        raise ValueError('Storage phase admission failed')
    return {'root': str(p.BUNDLE), 'logical_bytes': logical, 'allocated_bytes': allocated,
            'free_bytes': free, 'reserved_kernel_bytes': reserve, 'reserved_receipt_bytes': 1024**2}


def verify_preserved():
    for path, expected in ((p.BUNDLE / 'evidence/provision-v1.json', V1_SHA),
                           (p.BUNDLE / 'evidence/provision-v2.json', V2_SHA),
                           (p.BUNDLE / 'evidence/setup-v4.json', p.RECEIPT_SHA),
                           (p.RUNTIME / 'config/config.toml', CONFIG_SHA),
                           (p.RUNTIME / 'state.json', STATE_SHA)):
        p.regular(path, 1024**2)
        if p.digest(path) != expected:
            raise ValueError('Preserved evidence/runtime state changed: ' + str(path))
    old = p.metadata(p.BUNDLE / 'evidence/provision-v1.json')
    previous = p.metadata(p.BUNDLE / 'evidence/provision-v2.json')
    if p.kernel_store() != old['kernel_store_before']:
        raise ValueError('Default kernel store changed')
    worker = p.verify_worker()
    if worker != old['worker'] or worker != previous['worker']:
        raise ValueError('Worker content/snapshot changed')
    verify_existing(EXISTING)
    return worker


def provision():
    report = {'kind': 'WORKER_KERNEL_PROVISION_V3', 'result': 'FAILED', 'qualification_granted': False,
              'vm_launches': 0, 'service_commands': [], 'retrieval_commands': [],
              'provision_v1_receipt_sha256': V1_SHA, 'provision_v2_receipt_sha256': V2_SHA,
              'source_sha256': {Path(__file__).name: p.digest(Path(__file__)), helper.name: HELPER_SHA}}
    with (p.BUNDLE / 'evidence/provision-v3.json').open('x') as evidence:
        def checkpoint():
            data = json.dumps(report, indent=2, sort_keys=True) + '\n'
            if len(data.encode()) > 1024**2:
                raise ValueError('Receipt exceeds one MiB bound')
            evidence.seek(0); evidence.write(data); evidence.truncate(); evidence.flush(); os.fsync(evidence.fileno())

        def expired(*_):
            raise TimeoutError('600-second verification/copy deadline')

        previous = signal.signal(signal.SIGALRM, expired); signal.alarm(600)
        try:
            if DEST.exists() or DEST.is_symlink():
                raise ValueError('Consumed provision-v3 destination')
            report['storage_before_verify'] = storage(MAX_KERNEL); checkpoint()
            report['worker'] = verify_preserved(); checkpoint()
            report['existing_kernel'] = compare_member(EXISTING); checkpoint()
            DEST.mkdir(mode=0o700)
            report['storage_before_copy'] = storage(MAX_KERNEL); checkpoint()
            report['kernel'] = copy_kernel(EXISTING, DEST / p.KERNEL.name); checkpoint()
            verify_preserved()
            report['existing_kernel_after'] = compare_member(EXISTING)
            report['storage_after_copy'] = storage()
            DEST.chmod(0o500)
            report['result'] = 'WORKER_AND_DEDICATED_KERNEL_VERIFIED_NO_VM'
        except (Exception, KeyboardInterrupt) as error:
            report['error'] = type(error).__name__ + ': ' + str(error)
            report['failure_policy'] = 'PRESERVE_SERVICES_AND_ALL_PARTIAL_STATE; NO_RETRY_OR_CLEANUP'
        finally:
            signal.alarm(0); signal.signal(signal.SIGALRM, previous); checkpoint()
            os.fchmod(evidence.fileno(), 0o444); os.fsync(evidence.fileno())
    return 0 if report['result'] == 'WORKER_AND_DEDICATED_KERNEL_VERIFIED_NO_VM' else 1


if __name__ == '__main__':
    if sys.argv[1:] != ['provision-v3']:
        raise SystemExit('Separate authorization required; exact argument: provision-v3')
    raise SystemExit(provision())
