"""Synthetic files/identities only; never imports or invokes the guest fixture."""
import copy
import importlib.util
import json
import os
from pathlib import Path
import plistlib
import tempfile
import unittest
from unittest.mock import patch

SOURCE = Path(__file__).resolve().parents[1] / 'qualification/apple_container_vm_binding.py'
spec = importlib.util.spec_from_file_location('vm_binding', SOURCE)
b = importlib.util.module_from_spec(spec); spec.loader.exec_module(b)


class BindingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve() / b.NAME; self.root.mkdir(mode=0o700)
        replacement = patch.object(b, 'ROOT', self.root); replacement.start(); self.addCleanup(replacement.stop)
        self.artifacts = {}
        for role in b.ROLES:
            p = self.root / role; p.write_bytes((role + '\n').encode()); p.chmod(0o400)
            pin = b.fingerprint(p, role == 'rootfs')
            self.artifacts[role] = {'path': str(p), 'digest': pin['digest']}
        replacement = patch.object(b, 'FIXED_PINS', {role: pin['digest'] for role, pin in self.artifacts.items() if role in b.FIXED_PINS})
        replacement.start(); self.addCleanup(replacement.stop)
        replacement = patch.object(b, 'PROGRAM', self.artifacts['runtime_binary']['path']); replacement.start(); self.addCleanup(replacement.stop)
        self.configuration = self.root / 'runtime-configuration.json'
        self.config = {'path': self.root.as_uri(),
                      'containerConfiguration': {'id': b.NAME, 'image': {'reference': b.WORKER},
                        'networks': [], 'publishedPorts': [], 'publishedSockets': [], 'readOnly': True,
                        'runtimeHandler': 'container-runtime-linux', 'ssh': False, 'rosetta': False, 'virtualization': False},
                      'kernel': {'path': Path(self.artifacts['kernel']['path']).as_uri()},
                      'initialFilesystem': {'source': self.artifacts['initfs']['path']},
                      'containerRootFilesystem': {'source': self.artifacts['rootfs']['path'], 'options': []}}
        self.configuration.write_bytes(b.encoded(self.config)); self.configuration.chmod(0o400)
        self.plan, self.sha = self.seal()
        self.plan_path = self.root / 'offline-plan.json'

    def seal(self):
        return b.seal(self.configuration, b.sha(self.configuration.read_bytes()), self.artifacts, 'synthetic boot', 100)

    def identity(self, role):
        return {'pid': 7, 'uid': 501, 'birth': 'synthetic birth', 'executable': self.artifacts['python_process']['path'],
                'argv': [self.artifacts['python_launcher']['path'], '-I', '-B',
                         self.artifacts[role + '_source']['path'], str(self.plan_path), self.sha]}

    def test_exact_configuration_and_both_participants_share_one_seal(self):
        for role in ('guardian', 'coordinator'):
            identity = self.identity(role)
            receipt = b.participant(self.plan, self.sha, role, identity, self.plan_path, 'synthetic boot', 101)
            b.check_readiness(self.plan, self.sha, receipt, identity)
            self.assertEqual(receipt['deadline_monotonic'], 110)
            for key, value in (('birth', ''), ('executable', '/foreign'), ('argv', ['wrong'])):
                with self.subTest(role=role, key=key), self.assertRaises(ValueError):
                    b.participant(self.plan, self.sha, role, {**identity, key: value}, self.plan_path, 'synthetic boot', 101)
            with self.assertRaises(ValueError): b.check_readiness(self.plan, self.sha, receipt, {**identity, 'pid': 8})

    def test_exclusive_durable_plan_and_detached_readiness_identity(self):
        b.write_seal(self.plan_path, self.plan, self.sha)
        self.assertEqual(self.plan_path.stat().st_mode & 0o777, 0o400)
        self.assertEqual(b.sha(b.encoded(json.loads(self.plan_path.read_bytes()))), self.sha)
        with self.assertRaises(FileExistsError): b.write_seal(self.plan_path, self.plan, self.sha)
        with self.assertRaises(ValueError): b.write_seal(self.root / 'bad-plan', self.plan, 'wrong')
        identity = self.identity('guardian')
        receipt = b.participant(self.plan, self.sha, 'guardian', identity, self.plan_path, 'synthetic boot', 101)
        identity['birth'] = 'reused'
        with self.assertRaises(ValueError): b.check_readiness(self.plan, self.sha, receipt, identity)
        self.assertEqual(receipt['identity']['birth'], 'synthetic birth')

    def test_replaced_plan_boot_source_deadline_and_clock_rejected(self):
        for change in ('plan', 'boot', 'deadline', 'clock', 'source'):
            plan = copy.deepcopy(self.plan); expected = self.sha; boot = 'synthetic boot'; now = 101
            if change == 'plan': plan['files']['kernel']['digest'] = 'foreign'
            if change == 'boot': boot = 'another boot'
            if change == 'deadline': plan['deadline_monotonic'] = 120; expected = b.sha(b.encoded(plan))
            if change == 'clock': now = 99
            if change == 'source': plan['binding_source_sha256'] = 'foreign'; expected = b.sha(b.encoded(plan))
            with self.subTest(change=change), self.assertRaises(ValueError): b.verify(plan, expected, boot, now)
        for now in (float('nan'), float('inf')):
            with self.assertRaises(ValueError): b.verify(self.plan, self.sha, 'synthetic boot', now)

    def test_each_artifact_and_configuration_replacement_invalidates_binding(self):
        for role in (*b.ROLES, 'configuration'):
            path = self.configuration if role == 'configuration' else Path(self.artifacts[role]['path'])
            original = path.read_bytes(); path.chmod(0o600); path.write_bytes(original + b'changed'); path.chmod(0o400)
            with self.subTest(role=role), self.assertRaises(ValueError): b.verify(self.plan, self.sha, 'synthetic boot', 101)
            path.chmod(0o600); path.write_bytes(original); path.chmod(0o400)
            self.plan, self.sha = self.seal()

    def test_unreviewed_bytes_references_missing_pins_and_unsafe_scope_refused(self):
        with self.assertRaises(ValueError): b.seal(self.configuration, 'unreviewed', self.artifacts, 'boot', 100)
        for field, value in (('networks', [{}]), ('publishedSockets', [{}]), ('readOnly', False), ('ssh', True), ('id', 'foreign')):
            config = copy.deepcopy(self.config); config['containerConfiguration'][field] = value
            self.configuration.chmod(0o600); self.configuration.write_bytes(b.encoded(config)); self.configuration.chmod(0o400)
            with self.subTest(field=field), self.assertRaises(ValueError): self.seal()
        self.configuration.chmod(0o600); self.configuration.write_bytes(b.encoded(self.config)); self.configuration.chmod(0o400)
        broken = {k: v for k, v in self.artifacts.items() if k != 'coordinator_source'}
        with self.assertRaises(ValueError): b.seal(self.configuration, b.sha(self.configuration.read_bytes()), broken, 'boot', 100)
        self.config['kernel']['path'] = (self.root / 'different-kernel').as_uri()
        self.configuration.chmod(0o600); self.configuration.write_bytes(b.encoded(self.config)); self.configuration.chmod(0o400)
        with self.assertRaisesRegex(ValueError, 'references'): self.seal()

    def test_links_fifos_wrong_owner_and_group_writable_files_refused(self):
        path = self.root / 'linked'; path.symlink_to(self.configuration)
        with self.assertRaises(ValueError): b.fingerprint(path)
        path.unlink(); os.mkfifo(path, 0o600)
        with self.assertRaises(ValueError): b.fingerprint(path)
        self.configuration.chmod(0o440)
        b.fingerprint(self.configuration)
        self.configuration.chmod(0o460)
        with self.assertRaises(ValueError): b.fingerprint(self.configuration)
        self.configuration.chmod(0o400)
        info = list(self.configuration.lstat()); info[4] = 999
        with patch.object(b.Path, 'lstat', return_value=os.stat_result(info)):
            with self.assertRaises(ValueError): b.fingerprint(self.configuration)

    def test_later_bundle_copies_bind_original_configuration_and_artifacts(self):
        for filename, role in (('kernel.bin', 'kernel'), ('initfs.ext4', 'initfs'), ('rootfs.ext4', 'rootfs')):
            target = self.root / filename; target.write_bytes(Path(self.artifacts[role]['path']).read_bytes()); target.chmod(0o400)
        values = {'config.json': self.config['containerConfiguration'],
                  'kernel.json': {**self.config['kernel'], 'path': (self.root / 'kernel.bin').as_uri()},
                  'rootfs.json': {'source': str(self.root / 'rootfs.ext4'), 'options': ['ro']}}
        for name, value in values.items():
            path = self.root / name; path.write_bytes(b.encoded(value)); path.chmod(0o400)
        bound = b.bootstrap_bundle(self.plan, self.sha, 'synthetic boot', 101)
        b.bootstrap_bundle(self.plan, self.sha, 'synthetic boot', 102, bound)
        path = self.root / 'rootfs.json'; path.chmod(0o600)
        path.write_bytes(b.encoded({'source': str(self.root / 'rootfs.ext4'), 'options': []})); path.chmod(0o400)
        with self.assertRaises(ValueError): b.bootstrap_bundle(self.plan, self.sha, 'synthetic boot', 102, bound)
        path.chmod(0o600); path.write_bytes(b.encoded(values['rootfs.json'])); path.chmod(0o400)
        path = self.root / 'kernel.bin'; path.chmod(0o600); path.write_bytes(b'changed kernel'); path.chmod(0o400)
        with self.assertRaises(ValueError): b.bootstrap_bundle(self.plan, self.sha, 'synthetic boot', 102)

    def runtime(self):
        origin = self.root / 'service.plist'
        config = {'Label': b.TARGET.removeprefix('user/501/'),
                  'ProgramArguments': [b.PROGRAM, 'start', '--root', str(self.root), '--uuid', b.NAME],
                  'EnvironmentVariables': {'CONTAINER_APP_ROOT': str(self.root.parent.parent), 'CONTAINER_INSTALL_ROOT': '/usr/local'}}
        origin.write_bytes(plistlib.dumps(config)); origin.chmod(0o400)
        basic = {'pid': 42, 'uid': 501, 'birth': 'synthetic runtime birth', 'executable': b.PROGRAM}
        return {**basic, 'origin': str(origin), 'target': b.TARGET, 'container_id': b.NAME,
                'plist_sha256': b.fingerprint(origin)['digest'], 'binary_sha256': self.plan['files']['runtime_binary']['digest']}, basic

    def test_runtime_owner_binds_plan_configuration_plist_and_independent_pid(self):
        identity, pid = self.runtime()
        bound = b.runtime_owner(self.plan, self.sha, identity, pid, 'synthetic boot', 101)
        self.assertEqual(bound['configuration'], self.plan['configuration'])
        b.runtime_owner(self.plan, self.sha, identity, pid, 'synthetic boot', 102, bound)
        for field, value in (('pid', 99), ('target', 'user/501/foreign'), ('origin', '/foreign'), ('binary_sha256', 'wrong')):
            with self.subTest(field=field), self.assertRaises(ValueError):
                b.runtime_owner(self.plan, self.sha, {**identity, field: value}, pid, 'synthetic boot', 102, bound)
        changed = {**identity, 'birth': 'reused'}; changed_pid = {**pid, 'birth': 'reused'}
        with self.assertRaisesRegex(ValueError, 'replaced'):
            b.runtime_owner(self.plan, self.sha, changed, changed_pid, 'synthetic boot', 102, bound)

    def test_loss_restart_deadline_and_owner_absence_never_claim_vm_teardown(self):
        for event in ('COORDINATOR_LOST', 'GUARDIAN_LOST', 'DEADLINE_EXPIRED', 'RUNTIME_OWNER_ABSENT', 'TEARDOWN_INCOMPLETE'):
            journal = b.encoded({'event': event, 'plan_sha256': self.sha, 'deadline_monotonic': 110, 'monotonic': 111}) + b'\n'
            result = b.disposition(self.plan, self.sha, journal, 'synthetic boot', 112)
            self.assertEqual(result['original_deadline_monotonic'], 110)
            self.assertEqual(result['decision'], 'TERMINAL_NO_GO'); self.assertFalse(result['teardown_proven'])
            self.assertEqual(result['host_actions'], []); self.assertFalse(result['execution_authorized'])
        with self.assertRaises(ValueError): b.participant(self.plan, self.sha, 'guardian', self.identity('guardian'), self.plan_path, 'synthetic boot', 110)

    def test_torn_tampered_journal_and_invented_success_fail_closed(self):
        row = {'event': 'ARMED', 'plan_sha256': self.sha, 'deadline_monotonic': 110, 'monotonic': 100}
        for bad in (b'{', b.encoded(row), b.encoded({**row, 'event': 'VM_TERMINATED'}) + b'\n',
                    b.encoded({**row, 'deadline_monotonic': 120}) + b'\n', b.encoded({**row, 'plan_sha256': 'wrong'}) + b'\n'):
            with self.subTest(bad=bad), self.assertRaises(ValueError): b.disposition(self.plan, self.sha, bad, 'synthetic boot', 112)


if __name__ == '__main__': unittest.main()
