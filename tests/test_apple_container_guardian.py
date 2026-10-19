"""Mocked watchdog state transitions; never installs a job or launches a VM."""

import importlib.util
from pathlib import Path
import unittest

SPEC = importlib.util.spec_from_file_location('guardian', Path(__file__).resolve().parents[1] / 'qualification/apple_container_guardian.py')
g = importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(g)


class GuardianTests(unittest.TestCase):
    def test_deadline_survives_coordinator_absence_and_uses_exact_fallback(self):
        clock = [0.0]; identity = {'pid': 42, 'uid': 501, 'birth': 'fixed', 'executable': g.PROGRAM}
        alive = [True]; actions = []; events = []
        def act(argv):
            actions.append(argv)
            if argv[1] == 'bootout': raise TimeoutError('hung command')
            alive[0] = False
        # TimeoutExpired is the actual subprocess failure used by the watchdog.
        import subprocess
        def action(argv):
            try: act(argv)
            except TimeoutError: raise subprocess.TimeoutExpired(argv, 1)
        g.watch({'armed_monotonic': 0, 'deadline_monotonic': 10}, events, events.append,
                lambda: identity if alive[0] else None, lambda _: identity if alive[0] else None,
                action, lambda: clock[0], lambda seconds: clock.__setitem__(0, clock[0] + seconds))
        self.assertGreaterEqual(clock[0], 10)
        self.assertEqual(actions, [['/bin/launchctl', 'bootout', g.TARGET], ['/bin/launchctl', 'kill', 'SIGKILL', g.TARGET]])
        self.assertEqual(events[-1]['event'], 'TERMINATED')

    def test_restart_retains_original_deadline_and_identity(self):
        identity = {'pid': 42, 'uid': 501, 'birth': 'fixed', 'executable': g.PROGRAM}
        events = [{'event': 'OWNED', 'identity': identity}, {'event': 'BOOTOUT'}]; actions = []; alive = [True]
        def action(argv): actions.append(argv); alive[0] = False
        g.watch({'armed_monotonic': 0, 'deadline_monotonic': 10}, events, events.append,
                lambda: identity if alive[0] else None, lambda _: identity if alive[0] else None, action,
                lambda: 12, lambda _: self.fail('No new ten-second period'))
        self.assertEqual(actions, [['/bin/launchctl', 'kill', 'SIGKILL', g.TARGET]])
        self.assertEqual(events[-1]['event'], 'TERMINATED')

    def test_replaced_owner_or_unregistered_live_pid_never_gets_killed(self):
        old = {'pid': 42, 'uid': 501, 'birth': 'fixed', 'executable': g.PROGRAM}
        for owner in ({**old, 'birth': 'reused'}, None):
            events = [{'event': 'OWNED', 'identity': old}]
            with self.assertRaises(ValueError):
                g.watch({'armed_monotonic': 0, 'deadline_monotonic': 10}, events, events.append,
                        lambda: owner, lambda _: old, lambda _: self.fail('Foreign/uncertain action'), lambda: 12)

    def test_launchd_supervision_is_independent_and_not_installed(self):
        job = g.job(Path('/future/plan.json'), 'a' * 64)
        self.assertEqual(job['KeepAlive'], {'SuccessfulExit': False})
        self.assertTrue(job['RunAtLoad'])
        self.assertEqual(job['ProgramArguments'][-1], 'a' * 64)


if __name__ == '__main__': unittest.main()
