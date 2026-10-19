"""Offline fixtures only: no registry, installed CLI, service or VM calls."""

from contextlib import ExitStack
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import tarfile
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('provision', ROOT / 'qualification/apple_container_provision.py')
p = importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(p)


def elf():
    header = bytearray(64); header[:6] = b'\x7fELF\x02\x01'; header[18:20] = (183).to_bytes(2, 'little')
    return bytes(header)


class ProvisionTests(unittest.TestCase):
    def test_kernel_archive_pin_regular_member_and_dedicated_output(self):
        from compression import zstd
        for kind in ('valid', 'digest', 'symlink', 'duplicate'):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary).resolve(); archive = root / 'kernel.tar.zst'; output = root / 'kernel'
                raw = io.BytesIO()
                with tarfile.open(fileobj=raw, mode='w') as tar:
                    for _ in range(2 if kind == 'duplicate' else 1):
                        info = tarfile.TarInfo(p.MEMBER); info.size = len(elf())
                        if kind == 'symlink': info.type = tarfile.SYMTYPE; info.linkname = '/unrelated'
                        tar.addfile(info, io.BytesIO(elf()) if info.isfile() else None)
                archive.write_bytes(zstd.compress(raw.getvalue()))
                with patch.object(p, 'ARCHIVE_SIZE', archive.stat().st_size), patch.object(p, 'ARCHIVE_SHA',
                        '0' * 64 if kind == 'digest' else p.digest(archive)):
                    if kind == 'valid':
                        result = p.extract_kernel(archive, output)
                        self.assertEqual(output.read_bytes(), elf())
                        self.assertEqual(result['sha256'], hashlib.sha256(elf()).hexdigest())
                        with self.assertRaises(FileExistsError): p.extract_kernel(archive, output)
                    else:
                        with self.assertRaises(ValueError): p.extract_kernel(archive, output)

    def test_sparse_snapshot_hash_changes_when_data_changes(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary).resolve() / 'sparse'
            with path.open('wb') as output:
                output.write(b'first'); output.truncate(1024**2)
            before = p.snapshot_digest(path)
            with path.open('r+b') as output: output.write(b'other')
            after = p.snapshot_digest(path)
            self.assertNotEqual(before['extent_map_and_data_sha256'], after['extent_map_and_data_sha256'])
            self.assertLessEqual(before['data_bytes_read'], 1024**2)
            self.assertEqual(before['logical_bytes'], 1024**2)

    def test_worker_blob_graph_interpreter_and_snapshot(self):
        for corrupt in (False, True):
            with self.subTest(corrupt=corrupt), tempfile.TemporaryDirectory() as temporary, ExitStack() as stack:
                root = Path(temporary).resolve(); blobs = root / 'content/blobs/sha256'; blobs.mkdir(parents=True)
                def blob(data):
                    raw = data if isinstance(data, bytes) else json.dumps(data).encode()
                    digest = hashlib.sha256(raw).hexdigest(); (blobs / digest).write_bytes(raw)
                    return {'digest': 'sha256:' + digest, 'size': len(raw)}
                stream = io.BytesIO()
                with tarfile.open(fileobj=stream, mode='w:gz') as tar:
                    info = tarfile.TarInfo('usr/local/bin/python3'); info.type = tarfile.SYMTYPE; info.linkname = 'python3.13'; tar.addfile(info)
                    info = tarfile.TarInfo('usr/local/bin/python3.13'); info.mode = 0o755; info.size = len(elf()); tar.addfile(info, io.BytesIO(elf()))
                layer = blob(stream.getvalue()); config = blob({'os': 'linux', 'architecture': 'arm64'})
                manifest = blob({'config': config, 'layers': [layer]}); reference = 'docker.io/library/python@' + manifest['digest']
                index = blob({'manifests': [{**manifest, 'platform': {'os': 'linux', 'architecture': 'arm64'}}]}); (root / 'state.json').write_text(json.dumps({reference: index}))
                directory = root / 'snapshots' / manifest['digest'][7:]; directory.mkdir(parents=True)
                snapshot = directory / 'snapshot'
                with snapshot.open('wb') as output:
                    output.seek(1024); sb = bytearray(1024); sb[4:8] = (134217728).to_bytes(4, 'little'); sb[24:28] = (2).to_bytes(4, 'little'); sb[56:58] = b'\x53\xef'
                    output.write(sb); output.truncate(512 * 1024**3)
                (directory / 'snapshot-info').write_text(json.dumps({'source': str(snapshot), 'destination': '/', 'type': {'block': {'format': 'ext4'}}}))
                (root / 'content/ingest').mkdir(); (root / 'snapshots/ingest').mkdir()
                for name, value in [('RUNTIME', root), ('WORKER', reference), ('MANIFEST', manifest['digest']), ('CONFIG', config['digest']), ('LAYERS', [(layer['digest'][7:], layer['size'])])]:
                    stack.enter_context(patch.object(p, name, value))
                stack.enter_context(patch.object(p.subprocess, 'run', side_effect=AssertionError('No live command allowed')))
                if corrupt:
                    (blobs / layer['digest'][7:]).write_bytes(b'wrong')
                    with self.assertRaises(ValueError): p.verify_worker()
                else:
                    result = p.verify_worker()
                    self.assertEqual(result['interpreter']['sha256'], hashlib.sha256(elf()).hexdigest())

    def test_decompression_and_storage_admission_fail_without_cleanup(self):
        with self.assertRaises(ValueError): p.ReadBudget(io.BytesIO(b'12345'), 4).read(5)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve(); (root / 'setup-v4').mkdir(); (root / 'provision-v1').mkdir()
            with patch.object(p, 'BUNDLE', root), patch.object(p, 'DEST', root / 'provision-v1'), patch.object(p.shutil, 'disk_usage') as usage:
                usage.return_value.free = 0
                with self.assertRaises(ValueError): p.storage()
                self.assertTrue((root / 'provision-v1').exists())

    def test_existing_provision_identity_never_contacts_services(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve(); (root / 'evidence').mkdir(); (root / 'provision-v1').mkdir()
            with patch.object(p, 'BUNDLE', root), patch.object(p, 'DEST', root / 'provision-v1'), patch.object(p.subprocess, 'run') as run:
                self.assertEqual(p.provision(), 1); run.assert_not_called()
            report = json.loads((root / 'evidence/provision-v1.json').read_text())
            self.assertEqual(report['result'], 'FAILED')
            before = (root / 'evidence/provision-v1.json').read_bytes()
            with patch.object(p, 'BUNDLE', root):
                with self.assertRaises(FileExistsError): p.provision()
            self.assertEqual((root / 'evidence/provision-v1.json').read_bytes(), before)

    def test_provision_sequence_and_failure_preserve_preexisting_services(self):
        import subprocess
        for failure in (False, True):
            with self.subTest(failure=failure), tempfile.TemporaryDirectory() as temporary, ExitStack() as stack:
                root = Path(temporary).resolve(); runtime = root / 'setup-v4/runtime'; (runtime / 'config').mkdir(parents=True); (runtime / 'kernels').mkdir(); (root / 'evidence').mkdir()
                config = b'synthetic pinned config'; (runtime / 'config/config.toml').write_bytes(config)
                init = 'synthetic-init'; state = {init: {'digest': 'old'}}; (runtime / 'state.json').write_text(json.dumps(state))
                target = 'user/501/synthetic-service'; identity = {'path': 'synthetic-owned-plist'}
                baseline = {'binary_sha256': {}, 'process_plan': [{'target': target, 'pid': 42, 'identity': identity}],
                            'init_verification': {'blobs': [{'digest': 'old'}]}}
                receipt = root / 'evidence/setup-v4.json'; receipt.write_text(json.dumps(baseline))
                setup = SimpleNamespace(OBSERVER_SHA256=p.digest(p.HERE / 'apple_container_recover_setup_v2.py'),
                    CONFIG_SHA256=hashlib.sha256(config).hexdigest(), INIT=init,
                    owned_plist=lambda *_: identity, same_path=lambda a, b: Path(a)==Path(b))
                observer = SimpleNamespace(processes=lambda entries, run: [], verify_processes=lambda *_: None)
                spec = SimpleNamespace(loader=SimpleNamespace(exec_module=lambda _: None))
                calls = []
                def run(argv, **kwargs):
                    calls.append(argv)
                    if argv == p.PULL:
                        self.assertEqual(list((runtime / 'kernels').iterdir()), [])
                        (runtime / 'state.json').write_text(json.dumps({**state, p.WORKER: {'digest': 'new'}}))
                        if failure: return subprocess.CompletedProcess(argv, 1, b'partial worker pull', b'explicit failure')
                    if argv[:3] == [p.CLI, 'system', 'status']:
                        value = {'status': 'running', 'paths': {'appRoot': str(runtime), 'installRoot': '/usr/local'},
                            'server': {'version': '1.5.0', 'commit': 'd265d669ecae041bf338cb3b39c4118316d138f0'}, 'resources': {'containersTotal': 0}}
                        return subprocess.CompletedProcess(argv, 0, json.dumps(value).encode(), b'')
                    if argv[:2] == ['/bin/launchctl', 'print']:
                        text = f'\tpid = 42\n\t\tCONTAINER_APP_ROOT => {runtime}\n\t\tCONTAINER_INSTALL_ROOT => /usr/local\n'
                        return subprocess.CompletedProcess(argv, 0, text.encode(), b'')
                    if argv not in (p.PULL, p.DOWNLOAD): self.fail('Unexpected action: '+str(argv))
                    return subprocess.CompletedProcess(argv, 0, b'', b'')
                for name,value in [('BUNDLE', root), ('RUNTIME', runtime), ('DEST', root / 'provision-v1'), ('RECEIPT_SHA', p.digest(receipt)),
                                   ('ENV', {**p.ENV, 'CONTAINER_APP_ROOT': str(runtime)})]:
                    stack.enter_context(patch.object(p, name, value))
                stack.enter_context(patch.object(p.importlib.util, 'spec_from_file_location', return_value=spec))
                stack.enter_context(patch.object(p.importlib.util, 'module_from_spec', side_effect=[setup, observer]))
                stack.enter_context(patch.object(p, 'storage', return_value={'synthetic': True}))
                stack.enter_context(patch.object(p, 'verify_worker', return_value={'verified': True}))
                stack.enter_context(patch.object(p, 'extract_kernel', return_value={'verified': True}))
                stack.enter_context(patch.object(p.subprocess, 'run', side_effect=run))
                self.assertEqual(p.provision(), 1 if failure else 0)
                report = json.loads((root / 'evidence/provision-v1.json').read_text())
                self.assertEqual((runtime / 'config/config.toml').read_bytes(), config)
                self.assertEqual(json.loads((runtime / 'state.json').read_text())[init], state[init])
                self.assertFalse(any('bootout' in command or 'stop' in command or 'start' in command for command in calls))
                self.assertEqual(p.DOWNLOAD in calls, not failure)
                if failure:
                    self.assertIn('partial worker pull', json.dumps(report))
                    self.assertIn('PRESERVE_SERVICES', report['failure_policy'])
                else: self.assertEqual(report['result'], 'WORKER_AND_DEDICATED_KERNEL_VERIFIED_NO_VM')


if __name__ == '__main__': unittest.main()
