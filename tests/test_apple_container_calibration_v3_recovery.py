"""Recovery is one stopped exact target only; all host observations are synthetic."""
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import Mock, patch

HERE = Path(__file__).resolve().parents[1]


def module(name, filename):
    spec = importlib.util.spec_from_file_location(name, HERE / 'qualification' / filename)
    value = importlib.util.module_from_spec(spec); spec.loader.exec_module(value); return value


r = module('v3_recovery', 'apple_container_calibration_v3_recovery.py')
c = module('recovery_file_helpers', 'apple_container_guardian_calibration_v3.py')


class RecoveryTests(unittest.TestCase):
    def observer(self):
        return {'load': Mock(return_value={}), 'events': Mock(return_value=[{'event': 'OWNED', 'writer_pid': 16954, 'identity': {'pid': 16969}}, {'event': 'TERMINATED', 'writer_pid': 16954}]),
                'process': Mock(return_value=None), 'registered': Mock(return_value=False), 'PREFIX': c.PREFIX,
                'observe': Mock(return_value={'target': r.TARGET, 'pid': None}),
                'command': Mock(return_value=r.TARGET + ' = {\n\tstate = not running\n\tdomain = user/501\n}\n')}

    def test_only_exact_stopped_registration_with_absent_captured_pids(self):
        for bad in ('none', 'live-pid', 'fixture-registration', 'running', 'domain', 'guardian-pid', 'foreign-target', 'absent'):
            with self.subTest(bad=bad):
                observer = self.observer()
                if bad == 'live-pid': observer['process'].return_value = {'pid': 16969}
                if bad == 'fixture-registration': observer['registered'].return_value = True
                if bad == 'running': observer['command'].return_value = observer['command'].return_value.replace('not running', 'running')
                if bad == 'domain': observer['command'].return_value = observer['command'].return_value.replace('\tdomain = user/501', '\tdomain = gui/501')
                if bad == 'guardian-pid': observer['observe'].return_value['pid'] = 16954
                if bad == 'foreign-target': observer['observe'].return_value['target'] = 'user/501/foreign'
                if bad == 'absent': observer['observe'].return_value = None
                with patch.object(r, 'verify_originals'), patch.object(r.os, 'getuid', return_value=501):
                    if bad in ('none', 'absent'):
                        result = r.inspect(observer)
                        self.assertEqual(result['captured_pid_observations'], {'16954': None, '16969': None})
                    else:
                        with self.assertRaises(ValueError): r.inspect(observer)

    def test_one_bootout_exact_target_and_exclusive_receipts(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve() / 'recovery'
            before = {'registration': {'target': r.TARGET, 'pid': None}}
            after = {'registration': None}
            run = Mock(return_value=subprocess.CompletedProcess([], 0, b'', b''))
            helpers = {'fsync_dir': c.fsync_dir, 'write': c.write, 'ENV': c.ENV,
                       'subprocess': Mock(run=run, DEVNULL=subprocess.DEVNULL)}
            with patch.object(r, 'RECOVERY', root), patch.object(r, 'helper', return_value=helpers), patch.object(r, 'inspect', side_effect=[before, before, after]):
                r.recover()
            self.assertEqual(run.call_args.args[0], ['/bin/launchctl', 'bootout', r.TARGET])
            run.assert_called_once()
            self.assertEqual(json.loads((root / 'result.json').read_bytes())['result'], 'EXACT_STOPPED_REGISTRATION_REMOVED')
            with patch.object(r, 'RECOVERY', root), patch.object(r, 'helper', return_value=helpers), patch.object(r, 'inspect', return_value=before), self.assertRaises(FileExistsError): r.recover()
            run.assert_called_once()

    def test_absent_or_uncertain_never_invokes_bootout(self):
        for bad in ('absent', 'uncertain', 'changed'):
            with self.subTest(bad=bad), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp).resolve() / 'recovery'; run = Mock()
                before = {'registration': {'target': r.TARGET, 'pid': None}}
                values = [{'registration': None}] if bad == 'absent' else ValueError('uncertain') if bad == 'uncertain' else [before, {'registration': {'pid': 7}}]
                helpers = {'fsync_dir': c.fsync_dir, 'write': c.write, 'subprocess': Mock(run=run)}
                with patch.object(r, 'RECOVERY', root), patch.object(r, 'helper', return_value=helpers), patch.object(r, 'inspect', side_effect=values):
                    if bad == 'absent': r.recover()
                    else:
                        with self.assertRaises(ValueError): r.recover()
                run.assert_not_called()
                self.assertFalse((root / 'intent.json').exists())

    def test_failed_bootout_preserves_failure_and_no_retry(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve() / 'recovery'; before = {'registration': {'target': r.TARGET, 'pid': None}}
            run = Mock(return_value=subprocess.CompletedProcess([], 5, b'partial', b'failed'))
            helpers = {'fsync_dir': c.fsync_dir, 'write': c.write, 'ENV': c.ENV, 'subprocess': Mock(run=run, DEVNULL=subprocess.DEVNULL)}
            with patch.object(r, 'RECOVERY', root), patch.object(r, 'helper', return_value=helpers), patch.object(r, 'inspect', return_value=before):
                with self.assertRaises(ValueError): r.recover()
            self.assertTrue((root / 'action.json').exists()); self.assertTrue((root / 'failure.json').exists())
            self.assertFalse((root / 'result.json').exists()); run.assert_called_once()


if __name__ == '__main__': unittest.main()
