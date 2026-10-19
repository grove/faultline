"""V2 safety regressions plus coordinator startup/diagnostics; no live registrations."""
import base64
from contextlib import contextmanager
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import time
import unittest
from unittest.mock import Mock, patch


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec); spec.loader.exec_module(value)
    return value


SOURCE = Path(__file__).resolve().parents[1] / 'qualification/apple_container_guardian_calibration_v4.py'
c = module('calibration_v4', SOURCE)
previous = module('v4_inherited_tests', Path(__file__).with_name('test_apple_container_guardian_calibration_v2.py'))


class CalibrationV4Tests(previous.CalibrationTests):
    def setUp(self):
        for name, value in (('c', c), ('SOURCE', SOURCE)):
            replacement = patch.object(previous, name, value); replacement.start(); self.addCleanup(replacement.stop)

    def test_v4_exact_session_and_attempt_scope(self):
        self.assertEqual(c.BASE, Path('/private/tmp/faultline-guardian-calibration-v4'))
        self.assertEqual(c.DOMAIN, 'user/501')
        for case in ('coordinator-loss', 'guardian-restart'):
            for role in ('fixture', 'guardian'):
                job = c.job(c.PREFIX + case + '.' + role, role, c.BASE / case / 'plan.json')
                self.assertEqual(job['LimitLoadToSessionType'], 'Background')
                self.assertEqual(job['ProgramArguments'][3], str(SOURCE))

    def inject(self, root, mode):
        path = root / 'plan.json'; path.write_text('{}'); path.chmod(0o400)
        plan = {'deadline_monotonic': time.monotonic() + (5.1 if mode == 'never-ready' else 10)}
        identity = {'pid': 7, 'uid': 501, 'birth': 'fixed', 'executable': str(c.PROCESS_PYTHON)}
        child = Mock(pid=7); child.returncode = -c.signal.SIGKILL
        samples = []
        @contextmanager
        def spawn(_):
            def sample(stage, allow_exit=False):
                samples.append(stage)
                if mode == 'exit': raise ValueError('Coordinator premature exit: 1')
                if mode == 'never-ready': return {'identity': identity}
                if stage == 'startup':
                    if samples.count('startup') == 1: return {'identity': {**identity, 'executable': str(c.PYTHON)}}
                    ready = {'identity': identity, 'plan_sha256': c.digest(path)}
                    if mode == 'ready-mismatch': ready['identity'] = {**identity, 'birth': 'foreign'}
                    c.write(root / 'coordinator-ready.json', ready)
                if stage == 'waiting-for-fixture':
                    c.write(root / 'coordinator-bootstrap-complete.json', {'plan_sha256': c.digest(path)})
                    if mode == 'bound-mismatch': return {'identity': {**identity, 'birth': 'reused'}}
                if stage == 'before-sigkill' and mode == 'late': plan['deadline_monotonic'] = time.monotonic() + 2
                return {'identity': identity}
            yield child, sample
        with patch.object(c, 'coordinator_child', spawn), patch.object(c, 'events', return_value=[{'event': 'OWNED'}]), patch.object(c, 'process', return_value=None):
            if mode in ('exit', 'ready-mismatch', 'bound-mismatch', 'late', 'never-ready'):
                with self.assertRaises((ValueError, TimeoutError)): c.inject_coordinator_loss(path, plan)
                child.kill.assert_not_called()
                self.assertFalse((root / 'operator.jsonl').exists())
            else:
                c.inject_coordinator_loss(path, plan)
                child.kill.assert_called_once(); child.wait.assert_called_once_with(timeout=1)
                self.assertEqual(samples[:2], ['startup', 'startup'])
                self.assertIn('COORDINATOR_SIGKILL_INTENT', (root / 'operator.jsonl').read_text())

    def test_startup_transition_before_binding_and_exact_identity_after_binding(self):
        for mode in ('success', 'exit', 'ready-mismatch', 'bound-mismatch', 'late', 'never-ready'):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as tmp:
                self.inject(Path(tmp).resolve(), mode)

    def test_coordinator_ready_and_bootstrap_completion_are_sealed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve(); path = root / 'plan.json'; c.write(path, {})
            c.write(root / 'ready.json', {'plan_sha256': c.digest(path)})
            identity = {'pid': 7, 'uid': 501, 'birth': 'fixed', 'executable': str(c.PROCESS_PYTHON)}
            plan = {'directory': str(root), 'fixture_label': 'exact', 'deadline_monotonic': time.monotonic() + 10}
            def bootstrap(*_):
                self.assertTrue((root / 'coordinator-ready.json').exists())
                self.assertFalse((root / 'coordinator-bootstrap-complete.json').exists())
            with patch.object(c, 'load', return_value=plan), patch.object(c, 'observe', return_value=identity), patch.object(c, 'registered', return_value=False), patch.object(c, 'process', return_value=identity), patch.object(c, 'bootstrap', side_effect=bootstrap), patch.object(c.signal, 'alarm'), patch.object(c.time, 'sleep'):
                c.coordinator(path)
            for name in ('coordinator-ready.json', 'coordinator-bootstrap-complete.json'):
                self.assertEqual((root / name).stat().st_mode & 0o777, 0o400)
                self.assertEqual(json.loads((root / name).read_bytes())['plan_sha256'], c.digest(path))

    def test_real_premature_exit_retains_binary_output_and_returncode(self):
        popen = subprocess.Popen
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve(); path = root / 'plan.json'; c.write(path, {})
            def spawn(argv, **kwargs):
                return popen([str(c.PYTHON), '-I', '-B', '-c', "import os;os.write(1,b'out\\xff');os.write(2,b'failure\\xfe');raise SystemExit(7)"], **kwargs)
            with patch.object(c.subprocess, 'Popen', side_effect=spawn), patch.object(c, 'process', return_value=None):
                with self.assertRaisesRegex(ValueError, 'premature exit'):
                    with c.coordinator_child(path) as (child, sample):
                        child.wait(timeout=2); sample('exited')
            result = json.loads((root / 'coordinator-result.json').read_bytes())
            self.assertEqual(result['returncode'], 7)
            self.assertEqual(base64.b64decode(result['stdout_base64']), b'out\xff')
            self.assertEqual(base64.b64decode(result['stderr_base64']), b'failure\xfe')
            self.assertEqual(c.events(root / 'coordinator.jsonl')[-1]['returncode'], 7)

    def test_poll_recorded_even_on_identity_inspection_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp).resolve() / 'plan.json'; c.write(path, {})
            child = Mock(pid=7, stdout=None, stderr=None); child.poll.return_value = 9
            # Empty real pipes avoid launching any helper.
            import os
            r1, w1 = os.pipe(); r2, w2 = os.pipe(); os.close(w1); os.close(w2)
            child.stdout = os.fdopen(r1, 'rb'); child.stderr = os.fdopen(r2, 'rb')
            with patch.object(c.subprocess, 'Popen', return_value=child), patch.object(c, 'process', side_effect=ValueError('foreign executable')):
                with self.assertRaisesRegex(ValueError, 'observation/output'):
                    with c.coordinator_child(path): self.fail('Must fail closed')
            event = c.events(path.parent / 'coordinator.jsonl')[0]
            self.assertEqual(event['returncode'], 9); self.assertIn('foreign executable', event['identity_error'])
            child.kill.assert_not_called()

    def test_output_overflow_is_bounded_and_fails_without_uncertain_kill(self):
        popen = subprocess.Popen
        children = []
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp).resolve() / 'plan.json'; c.write(path, {})
            def spawn(argv, **kwargs):
                child = popen([str(c.PYTHON), '-I', '-B', '-c', "import os,time;os.write(1,b'x'*200000);time.sleep(3)"], **kwargs)
                children.append(child); return child
            try:
                with patch.object(c.subprocess, 'Popen', side_effect=spawn), patch.object(c, 'process', return_value={'pid': 7}):
                    with self.assertRaisesRegex(ValueError, 'observation/output'):
                        with c.coordinator_child(path) as (child, sample):
                            until = time.monotonic() + 2
                            while time.monotonic() < until: sample('output'); time.sleep(.01)
                            self.fail('Overflow must fail')
                result = json.loads((path.parent / 'coordinator-result.json').read_bytes())
                self.assertTrue(result['output_limit'])
                self.assertEqual(len(base64.b64decode(result['stdout_base64'])), 65536)
            finally:
                for child in children:
                    if child.poll() is None: child.kill()
                    child.wait(timeout=2)

    def test_failed_shutdown_never_records_termination(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp).resolve() / 'journal'
            identity = {'pid': 7, 'uid': 501, 'birth': 'fixed', 'executable': str(c.PROCESS_PYTHON)}
            actions = []
            with self.assertRaisesRegex(ValueError, 'not independently observed'):
                c.watch({'armed_monotonic': 1, 'deadline_monotonic': 11}, path, lambda: identity,
                        lambda _: identity, actions.append, lambda: 12, lambda _: None)
            self.assertEqual(actions, ['bootout', 'kill'])
            self.assertFalse(any(e['event'] == 'TERMINATED' for e in c.events(path)))


if __name__ == '__main__': unittest.main()
