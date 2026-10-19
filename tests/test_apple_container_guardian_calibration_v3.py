"""V2 safety regressions plus exact Background-session admission; no live launchd."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


SOURCE = Path(__file__).resolve().parents[1] / 'qualification/apple_container_guardian_calibration_v3.py'
c = module('calibration_v3', SOURCE)
previous = module('calibration_v2_tests', Path(__file__).with_name('test_apple_container_guardian_calibration_v2.py'))


class CalibrationV3Tests(previous.CalibrationTests):
    def setUp(self):
        for name, value in (('c', c), ('SOURCE', SOURCE)):
            replacement = patch.object(previous, name, value)
            replacement.start()
            self.addCleanup(replacement.stop)

    def test_all_four_exact_plists_require_background_session(self):
        self.assertEqual(c.DOMAIN, 'user/501')
        self.assertEqual(c.BASE, Path('/private/tmp/faultline-guardian-calibration-v3'))
        for case in ('coordinator-loss', 'guardian-restart'):
            for role in ('guardian', 'fixture'):
                label = 'dev.faultline.guardian-calibration-v3.' + case + '.' + role
                plan = c.BASE / case / 'plan.json'
                expected = {
                    'Label': label,
                    'ProgramArguments': [str(c.PYTHON), '-I', '-B', str(SOURCE), role, str(plan)],
                    'WorkingDirectory': '/',
                    'EnvironmentVariables': {'PATH': '/usr/bin:/bin', 'LC_ALL': 'C', 'TZ': 'Europe/Oslo'},
                    'RunAtLoad': True, 'ProcessType': 'Background',
                    'LimitLoadToSessionType': 'Background', 'ExitTimeOut': 1,
                }
                if role == 'guardian':
                    expected.update(KeepAlive={'SuccessfulExit': False}, ThrottleInterval=1)
                self.assertEqual(c.PREFIX + case + '.' + role, label)
                self.assertEqual(c.plistlib.loads(c.plistlib.dumps(c.job(label, role, plan))), expected)

    def test_wrong_or_missing_sessions_rejected_even_with_matching_hash(self):
        for role in ('guardian', 'fixture'):
            for session in (None, 'Aqua', 'StandardIO', ['Background'], ['Background', 'Aqua'], ''):
                with self.subTest(role=role, session=session), tempfile.TemporaryDirectory() as tmp:
                    root = Path(tmp).resolve()
                    plan = self.bootstrap_fixture(root)
                    path = root / (plan[role + '_label'] + '.plist')
                    config = c.plistlib.loads(path.read_bytes())
                    if session is None:
                        del config['LimitLoadToSessionType']
                    else:
                        config['LimitLoadToSessionType'] = session
                    path.chmod(0o600)
                    path.write_bytes(c.plistlib.dumps(config))
                    path.chmod(0o400)
                    plan[role + '_plist_sha256'] = c.digest(path)
                    with patch.object(c, 'load', return_value=plan), patch.object(c, 'registered', return_value=False), patch.object(c.subprocess, 'Popen') as launch:
                        with self.assertRaisesRegex(ValueError, 'Changed bootstrap plist'):
                            c.bootstrap(plan, role)
                        launch.assert_not_called()
                    self.assertFalse((root / (role + '-bootstrap-intent.json')).exists())
                    with patch.object(c, 'registered', return_value=True), patch.object(c, 'command') as command:
                        with self.assertRaisesRegex(ValueError, 'plist/session/arguments'):
                            c.observe(plan, role)
                        command.assert_not_called()

    def test_observe_rejects_extra_plist_key_with_matching_hash(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            plan = self.bootstrap_fixture(root)
            path = root / (plan['fixture_label'] + '.plist')
            config = c.plistlib.loads(path.read_bytes())
            config['Disabled'] = True
            path.chmod(0o600)
            path.write_bytes(c.plistlib.dumps(config))
            path.chmod(0o400)
            plan['fixture_plist_sha256'] = c.digest(path)
            with patch.object(c, 'registered', return_value=True), patch.object(c, 'command') as command:
                with self.assertRaisesRegex(ValueError, 'plist/session/arguments'):
                    c.observe(plan, 'fixture', stopped=True)
                command.assert_not_called()

    def test_existing_root_or_exact_label_refuses_new_attempt(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            with patch.object(c, 'BASE', root), patch.object(c, 'digest', return_value=c.RECEIPT_SHA), patch.object(c, 'command', return_value='Background'), patch.object(c, 'registered', return_value=True), patch.object(c.subprocess, 'Popen') as launch:
                with self.assertRaisesRegex(ValueError, 'Consumed/colliding label'):
                    c.install()
                launch.assert_not_called()
            with patch.object(c, 'BASE', root), patch.object(c, 'PYTHON_PINS', {}), patch.object(c, 'digest', return_value=c.RECEIPT_SHA), patch.object(c, 'command', return_value='Background'), patch.object(c, 'registered', return_value=False), patch.object(c, 'process', return_value={'pid': 1}), patch.object(c.subprocess, 'Popen') as launch:
                with self.assertRaises(FileExistsError):
                    c.install()
                launch.assert_not_called()
            self.assertEqual(list(root.iterdir()), [])


if __name__ == '__main__':
    unittest.main()
