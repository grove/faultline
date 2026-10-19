"""Synthetic Images/archives only; no service, network or real provisioning calls."""

from contextlib import ExitStack
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import stat
import tarfile
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('provision_v3', ROOT / 'qualification/apple_container_provision_v3.py')
v = importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(v)
p = v.p


def image():
    data = bytearray(1024)
    data[:16] = bytes.fromhex('4d5a40fa196058140000000000000000')
    data[16:24] = (4096).to_bytes(8, 'little')
    data[24:32] = (10).to_bytes(8, 'little')
    data[56:60] = b'ARMd'; data[60:64] = (64).to_bytes(4, 'little')
    data[64:70] = b'PE\x00\x00\x64\xaa'
    return bytes(data)


def archive(path, data, kind='valid'):
    from compression import zstd
    raw = io.BytesIO()
    with tarfile.open(fileobj=raw, mode='w') as tar:
        for _ in range(2 if kind == 'duplicate' else 1):
            entry = tarfile.TarInfo('absent' if kind == 'missing' else p.MEMBER)
            entry.size = len(data)
            if kind == 'symlink': entry.type = tarfile.SYMTYPE; entry.linkname = '/unrelated'
            tar.addfile(entry, io.BytesIO(data) if entry.isfile() else None)
    path.write_bytes(zstd.compress(raw.getvalue()))


class ImageTests(unittest.TestCase):
    def test_valid_image_effective_size_can_exceed_file_length(self):
        for effective_size in (1024, 4096):
            for flags in (0, 2, 4, 6, 8, 10, 12, 14):
                header = bytearray(image()[:64]); header[16:24] = effective_size.to_bytes(8, 'little')
                header[24:32] = flags.to_bytes(8, 'little')
                result = v.image_header(header, 1024)
                self.assertEqual(result['image_size'], effective_size)
                self.assertEqual(result['endianness'], 'little')
        header[60:64] = bytes(4)
        self.assertEqual(v.image_header(header, 1024)['pe_header_offset'], 0)
        header[8:16] = (0x80000).to_bytes(8, 'little')
        self.assertEqual(v.image_header(header, 1024)['text_offset'], 0x80000)

    def test_malformed_headers_and_elf_are_rejected_but_worker_still_uses_elf(self):
        bad = [image()[:63]]
        for start, data in ((0, b'\x7fELF'), (56, b'dMRA'), (16, bytes(8)),
                            (16, (1023).to_bytes(8, 'little')), (16, (v.MAX_KERNEL+1).to_bytes(8, 'little')),
                            (16, (4096).to_bytes(8, 'big')), (24, (1).to_bytes(8, 'little')),
                            (24, (16).to_bytes(8, 'little')), (8, (1).to_bytes(8, 'little')),
                            (8, (v.MAX_KERNEL+4096).to_bytes(8, 'little')), (32, b'\x01'),
                            (40, b'\x01'), (48, b'\x01'), (60, (60).to_bytes(4, 'little')),
                            (60, (65).to_bytes(4, 'little')), (60, (1024).to_bytes(4, 'little'))):
            header = bytearray(image()[:64]); header[start:start+len(data)] = data; bad.append(header)
        for header in bad:
            with self.subTest(header=bytes(header).hex()), self.assertRaises(ValueError): v.image_header(header, 1024)
        with self.assertRaises(ValueError): v.image_header(image()[:64], 63)
        with self.assertRaises(ValueError): v.image_header(image()[:64], v.MAX_KERNEL+1)
        with self.assertRaises(ValueError): p.elf(image()[:64])
        elf = bytearray(64); elf[:6] = b'\x7fELF\x02\x01'; elf[18:20] = (183).to_bytes(2, 'little')
        p.elf(elf)
        with self.assertRaises(ValueError): v.image_header(elf, 1024)

    def test_pinned_archive_member_comparison_and_exclusive_readonly_copy(self):
        for kind in ('valid', 'changed_local', 'changed_member', 'size', 'archive_hash', 'duplicate', 'symlink', 'missing', 'truncated'):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as temporary, ExitStack() as stack:
                root = Path(temporary).resolve(); source = root / 'existing'; source.write_bytes(image())
                packed = root / 'archive'; member = image()
                if kind == 'changed_member': member = member[:-1] + b'X'
                if kind == 'size': member = member[:-1]
                archive(packed, member, kind)
                if kind == 'truncated': packed.write_bytes(packed.read_bytes()[:len(packed.read_bytes())//2])
                for obj, name, value in ((p, 'ARCHIVE', packed), (p, 'ARCHIVE_SIZE', packed.stat().st_size),
                        (p, 'ARCHIVE_SHA', '0'*64 if kind == 'archive_hash' else p.digest(packed)),
                        (v, 'KERNEL_BYTES', len(image())), (v, 'KERNEL_SHA', hashlib.sha256(image()).hexdigest())):
                    stack.enter_context(patch.object(obj, name, value))
                if kind == 'changed_local': source.write_bytes(image()[:-1] + b'X')
                before = source.read_bytes(); output = root / 'accepted'
                if kind != 'valid':
                    with self.assertRaises(Exception): v.compare_member(source)
                    self.assertFalse(output.exists())
                else:
                    self.assertEqual(v.compare_member(source)['comparison'], 'BYTE_FOR_BYTE')
                    self.assertEqual(v.copy_kernel(source, output)['sha256'], v.KERNEL_SHA)
                    self.assertEqual(output.read_bytes(), image())
                    self.assertEqual(stat.S_IMODE(output.stat().st_mode), 0o444)
                    with self.assertRaises(FileExistsError): v.copy_kernel(source, output)
                self.assertEqual(source.read_bytes(), before)

    def test_partial_copy_remains_and_wrong_content_is_not_accepted(self):
        with tempfile.TemporaryDirectory() as temporary, ExitStack() as stack:
            root = Path(temporary).resolve(); source = root / 'old'; source.write_bytes(image())
            stack.enter_context(patch.object(v, 'KERNEL_BYTES', len(image())))
            stack.enter_context(patch.object(v, 'KERNEL_SHA', p.digest(source)))
            def partial(reader, output, size):
                output.write(reader.read(32)); raise OSError('Synthetic interrupted extraction/copy')
            with patch.object(v.shutil, 'copyfileobj', side_effect=partial):
                with self.assertRaises(OSError): v.copy_kernel(source, root / 'partial')
            self.assertEqual((root / 'partial').read_bytes(), image()[:32])
            def changed(reader, output, size): output.write(b'X' * len(image()))
            with patch.object(v.shutil, 'copyfileobj', side_effect=changed):
                with self.assertRaises(ValueError): v.copy_kernel(source, root / 'wrong')
            self.assertEqual(source.read_bytes(), image())

    def test_all_previous_roots_count_and_original_physical_guards_remain(self):
        with tempfile.TemporaryDirectory() as temporary, ExitStack() as stack:
            root = Path(temporary).resolve()
            for name in ('setup-v2', 'setup-v3', 'setup-v4', 'provision-v1', 'provision-v2', 'provision-v3', 'evidence'):
                (root / name).mkdir(); (root / name / 'data').write_bytes(b'x')
            stack.enter_context(patch.object(p, 'BUNDLE', root))
            usage = stack.enter_context(patch.object(v.shutil, 'disk_usage', return_value=SimpleNamespace(free=32*1024**3)))
            observed = v.storage(); self.assertGreaterEqual(observed['logical_bytes'], 7)
            with (root / 'setup-v2/data').open('wb') as output: output.truncate(515*1024**3)
            with self.assertRaises(ValueError): v.storage()
            (root / 'setup-v2/data').write_bytes(b'x')
            usage.return_value.free = 16*1024**3
            with self.assertRaises(ValueError): v.storage()
            usage.return_value.free = 32*1024**3
            with patch.object(Path, 'lstat', return_value=SimpleNamespace(st_mode=0o100600, st_size=1, st_blocks=8*1024**3//512)):
                with self.assertRaises(ValueError): v.storage()
            (root / 'link').symlink_to(root / 'setup-v2/data')
            with self.assertRaises(ValueError): v.storage()

    def test_preserved_receipts_worker_runtime_and_kernel_are_revalidated(self):
        with tempfile.TemporaryDirectory() as temporary, ExitStack() as stack:
            root = Path(temporary).resolve(); runtime = root / 'setup-v4/runtime'
            (runtime / 'config').mkdir(parents=True); (root / 'evidence').mkdir()
            old1 = root / 'evidence/provision-v1.json'; old2 = root / 'evidence/provision-v2.json'
            setup = root / 'evidence/setup-v4.json'; config = runtime / 'config/config.toml'; state = runtime / 'state.json'
            source = root / 'existing'; source.write_bytes(image())
            worker = {'verified': True}
            old1.write_text(json.dumps({'kernel_store_before': None, 'worker': worker}))
            old2.write_text(json.dumps({'worker': worker}))
            for path in (setup, config, state): path.write_bytes(b'pinned fixture')
            for obj, name, value in ((p, 'BUNDLE', root), (p, 'RUNTIME', runtime), (p, 'RECEIPT_SHA', p.digest(setup)),
                    (v, 'V1_SHA', p.digest(old1)), (v, 'V2_SHA', p.digest(old2)), (v, 'CONFIG_SHA', p.digest(config)),
                    (v, 'STATE_SHA', p.digest(state)), (v, 'EXISTING', source), (v, 'KERNEL_BYTES', len(image())),
                    (v, 'KERNEL_SHA', p.digest(source))):
                stack.enter_context(patch.object(obj, name, value))
            stack.enter_context(patch.object(p, 'kernel_store', return_value=None))
            checked = stack.enter_context(patch.object(p, 'verify_worker', return_value=worker))
            self.assertEqual(v.verify_preserved(), worker)
            for path in (old1, old2, setup, config, state, source):
                before = path.read_bytes(); path.write_bytes(before + b'changed')
                with self.subTest(path=path), self.assertRaises(ValueError): v.verify_preserved()
                path.write_bytes(before)
            checked.return_value = {'changed': True}
            with self.assertRaises(ValueError): v.verify_preserved()
            with patch.object(p, 'kernel_store', return_value={'changed': True}):
                with self.assertRaises(ValueError): v.verify_preserved()

    def test_orchestration_fails_closed_and_consumes_only_fresh_v3_identity(self):
        for failure in ('none', 'preserved', 'compare', 'space', 'partial', 'destination', 'after_copy'):
            with self.subTest(failure=failure), tempfile.TemporaryDirectory() as temporary, ExitStack() as stack:
                root = Path(temporary).resolve(); (root / 'evidence').mkdir(); (root / 'provision-v2').mkdir()
                old = root / 'provision-v2/kernel'; old.write_bytes(image())
                receipt2 = root / 'evidence/provision-v2.json'; receipt2.write_bytes(b'original receipt')
                stack.enter_context(patch.object(p, 'BUNDLE', root)); stack.enter_context(patch.object(v, 'EXISTING', old))
                stack.enter_context(patch.object(v, 'DEST', root / 'provision-v3'))
                stack.enter_context(patch.object(p.subprocess, 'run', side_effect=AssertionError('No live call allowed')))
                stack.enter_context(patch.object(v, 'verify_preserved', side_effect=ValueError('Changed preserved state') if failure == 'preserved' else None, return_value={}))
                stack.enter_context(patch.object(v, 'compare_member', side_effect=ValueError('Changed archive member') if failure == 'compare' else None, return_value={}))
                check_storage = stack.enter_context(patch.object(v, 'storage', side_effect=ValueError('No space') if failure == 'space' else None, return_value={}))
                def copy(existing, destination):
                    self.assertEqual(existing, old); self.assertEqual(destination.parent, v.DEST)
                    destination.write_bytes(image()[:32] if failure == 'partial' else image())
                    if failure == 'partial': raise OSError('Interrupted copy')
                    destination.chmod(0o444)
                    return {'sha256': hashlib.sha256(image()).hexdigest()}
                copier = stack.enter_context(patch.object(v, 'copy_kernel', side_effect=copy))
                if failure == 'after_copy':
                    check_storage.side_effect = [{}, {}, ValueError('Final admission failed')]
                if failure == 'destination': v.DEST.mkdir()
                self.assertEqual(v.provision(), 0 if failure == 'none' else 1)
                receipt = root / 'evidence/provision-v3.json'; before = receipt.read_bytes(); result = json.loads(before)
                self.assertEqual(result['vm_launches'], 0); self.assertFalse(result['qualification_granted'])
                self.assertEqual(result['service_commands'], []); self.assertEqual(result['retrieval_commands'], [])
                self.assertEqual(stat.S_IMODE(receipt.stat().st_mode), 0o444)
                self.assertEqual(old.read_bytes(), image()); self.assertEqual(receipt2.read_bytes(), b'original receipt')
                self.assertEqual(copier.call_count, int(failure in ('none', 'partial', 'after_copy')))
                if failure == 'none':
                    self.assertEqual(stat.S_IMODE(v.DEST.stat().st_mode), 0o500)
                    v.DEST.chmod(0o700)  # Synthetic fixture teardown only.
                else: self.assertEqual(result['result'], 'FAILED')
                with self.assertRaises(FileExistsError): v.provision()
                self.assertEqual(receipt.read_bytes(), before)


if __name__ == '__main__': unittest.main()
