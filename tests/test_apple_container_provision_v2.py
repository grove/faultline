"""Offline continuation fixtures; all extraction uses synthetic data or mocks."""

from contextlib import ExitStack
import importlib.util
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('provision_v2', ROOT / 'qualification/apple_container_provision_v2.py')
v = importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(v)
p = v.p


class ContinuationTests(unittest.TestCase):
    def test_reuse_only_success_and_failures_preserve_v1_and_services(self):
        for failure in ('none', 'receipt', 'archive', 'worker', 'state', 'space', 'extract', 'drift', 'destination'):
            with self.subTest(failure=failure), tempfile.TemporaryDirectory() as temporary, ExitStack() as stack:
                root = Path(temporary).resolve(); runtime = root / 'setup-v4/runtime'
                (runtime / 'config').mkdir(parents=True); (runtime / 'kernels').mkdir()
                (root / 'evidence').mkdir(); old_dest = root / 'provision-v1'; old_dest.mkdir()
                archive = old_dest / 'archive'; archive.write_bytes(b'pinned synthetic archive')
                config = runtime / 'config/config.toml'; config.write_bytes(b'pinned config')
                state = runtime / 'state.json'; state.write_text(json.dumps({'init': {'digest': 'init-pin'}, p.WORKER: {}}))
                setup = root / 'evidence/setup-v4.json'
                setup.write_text(json.dumps({'init_verification': {'reference': 'init', 'blobs': [{'digest': 'init-pin'}]}}))
                worker = {'content': 'same', 'snapshot': {'extent_map_and_data_sha256': 'same'}}
                old = root / 'evidence/provision-v1.json'
                old.write_text(json.dumps({'worker': worker, 'kernel_store_before': None}))
                frozen = {x: x.read_bytes() for x in (old, archive, config, state, setup)}
                for name, value in [('BUNDLE', root), ('RUNTIME', runtime), ('DEST', old_dest), ('ARCHIVE', archive),
                                    ('ARCHIVE_SIZE', archive.stat().st_size), ('ARCHIVE_SHA', p.digest(archive)),
                                    ('RECEIPT_SHA', p.digest(setup))]:
                    stack.enter_context(patch.object(p, name, value))
                for name, value in [('DEST', root / 'provision-v2'), ('V1_SHA', p.digest(old)),
                                    ('CONFIG_SHA', p.digest(config)), ('STATE_SHA', p.digest(state))]:
                    stack.enter_context(patch.object(v, name, value))
                stack.enter_context(patch.object(p, 'kernel_store', return_value=None))
                stack.enter_context(patch.object(p.shutil, 'disk_usage', return_value=SimpleNamespace(free=0 if failure == 'space' else 32 * 1024**3)))
                stack.enter_context(patch.object(p.subprocess, 'run', side_effect=AssertionError('No service/network/VM command allowed')))
                checked = stack.enter_context(patch.object(p, 'verify_worker', return_value={'changed': True} if failure == 'worker' else worker))
                def extract(source, destination):
                    self.assertEqual(source, archive)
                    self.assertEqual(destination, v.DEST / p.KERNEL.name)
                    destination.write_bytes(b'synthetic kernel')
                    if failure == 'extract': raise ValueError('Synthetic extraction failure')
                    if failure == 'drift': state.write_bytes(b'changed externally')
                    return {'path': str(destination), 'bytes': destination.stat().st_size}
                extracted = stack.enter_context(patch.object(p, 'extract_kernel', side_effect=extract))
                if failure == 'receipt': stack.enter_context(patch.object(v, 'V1_SHA', '0' * 64))
                if failure == 'archive': stack.enter_context(patch.object(p, 'ARCHIVE_SHA', '0' * 64))
                if failure == 'state': stack.enter_context(patch.object(v, 'STATE_SHA', '0' * 64))
                if failure == 'destination': v.DEST.mkdir()
                self.assertEqual(v.provision(), 0 if failure == 'none' else 1)
                receipt = root / 'evidence/provision-v2.json'; raw = receipt.read_bytes(); report = json.loads(raw)
                self.assertEqual(report['qualification_granted'], False)
                self.assertEqual(report['vm_launches'], 0)
                self.assertEqual(report['service_commands'], [])
                self.assertEqual(report['retrieval_commands'], [])
                self.assertEqual(extracted.call_count, int(failure in ('none', 'extract', 'drift')))
                self.assertEqual(list(old_dest.iterdir()), [archive])
                for path, data in frozen.items():
                    if failure == 'drift' and path == state: continue
                    self.assertEqual(path.read_bytes(), data)
                if failure == 'none':
                    self.assertEqual(checked.call_count, 2)
                    self.assertEqual(report['storage_before_extract']['reserved_kernel_bytes'], v.MAX_KERNEL)
                    self.assertEqual(report['result'], 'WORKER_AND_DEDICATED_KERNEL_VERIFIED_NO_VM')
                else:
                    self.assertEqual(report['result'], 'FAILED')
                    self.assertIn('PRESERVE_SERVICES', report['failure_policy'])
                with self.assertRaises(FileExistsError): v.provision()
                self.assertEqual(receipt.read_bytes(), raw)

    def test_combined_logical_budget_reserves_kernel_and_keeps_physical_guards(self):
        with tempfile.TemporaryDirectory() as temporary, ExitStack() as stack:
            root = Path(temporary).resolve()
            for name in ('setup-v4', 'provision-v1', 'provision-v2'): (root / name).mkdir()
            stack.enter_context(patch.object(p, 'BUNDLE', root))
            stack.enter_context(patch.object(p, 'DEST', root / 'provision-v1'))
            stack.enter_context(patch.object(v, 'DEST', root / 'provision-v2'))
            usage = stack.enter_context(patch.object(v.shutil, 'disk_usage', return_value=SimpleNamespace(free=32 * 1024**3)))
            with (root / 'setup-v4/snapshot').open('wb') as output: output.truncate(551615977941)
            with (root / 'provision-v1/archive').open('wb') as output: output.truncate(696573576)
            self.assertEqual(v.storage(v.MAX_KERNEL)['logical_bytes'], 552312551517)
            with (root / 'provision-v2/extra').open('wb') as output: output.truncate(530270116)
            with self.assertRaises(ValueError): v.storage(v.MAX_KERNEL)
            (root / 'provision-v2/extra').write_bytes(b'')
            usage.return_value.free = 16 * 1024**3
            with self.assertRaises(ValueError): v.storage(v.MAX_KERNEL)
            usage.return_value.free = 32 * 1024**3
            with patch.object(Path, 'lstat', return_value=SimpleNamespace(st_mode=0o100600, st_size=1, st_blocks=(8 * 1024**3)//512)):
                with self.assertRaises(ValueError): v.storage()


if __name__ == '__main__': unittest.main()
