"""Host-owned subprocesses and synthetic launchd output; never registers jobs or VMs."""
import importlib.util
import json
import os
from pathlib import Path
import signal
import subprocess
import tempfile
import time
import unittest
from unittest.mock import patch

SOURCE = Path(__file__).resolve().parents[1] / 'qualification/apple_container_guardian_calibration_v1.py'
SPEC = importlib.util.spec_from_file_location('calibration', SOURCE)
c = importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(c)


class CalibrationTests(unittest.TestCase):
    def test_wal_interruption_replays_original_deadline_before_action(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp).resolve() / 'journal'; identity = {'pid': 7, 'uid': 501, 'birth': 'fixed', 'executable': str(c.PYTHON)}
            plan = {'armed_monotonic': 1, 'deadline_monotonic': 11}; alive = [True]; calls = []
            def action(operation): calls.append(operation); alive[0] = False
            def interrupted(operation): raise KeyboardInterrupt('synthetic guardian death after intent')
            with self.assertRaises(KeyboardInterrupt):
                c.watch(plan, path, lambda: identity, lambda _: identity, interrupted, lambda: 12)
            self.assertEqual(c.events(path)[-1]['event'], 'BOOTOUT_INTENT')
            c.watch(plan, path, lambda: identity if alive[0] else None, lambda _: identity if alive[0] else None,
                    action, lambda: 12, lambda _: self.fail('Must not arm a new deadline'))
            self.assertEqual(calls, ['bootout']); self.assertEqual(c.events(path)[-1]['event'], 'TERMINATED')
            c.watch(plan, path, lambda: self.fail('Terminal replay must be inert'), None, None)

    def test_identity_replacement_and_unregistered_live_pid_are_untouched(self):
        for change in ('replacement', 'unregistered'):
            with self.subTest(change=change), tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp).resolve() / 'journal'; old = {'pid': 7, 'uid': 501, 'birth': 'old', 'executable': str(c.PYTHON)}
                c.emit(path, {'event': 'OWNED', 'identity': old})
                value = {**old, 'birth': 'new'} if change == 'replacement' else None
                with self.assertRaises(ValueError):
                    c.watch({'armed_monotonic': 1, 'deadline_monotonic': 11}, path, lambda: value, lambda _: old,
                            lambda _: self.fail('Uncertain identity must not be killed'), lambda: 12)

    def test_torn_journal_invalid_deadline_and_clock_reset_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp).resolve() / 'journal'; path.write_text('{"event":'); path.chmod(0o600)
            with self.assertRaises(ValueError): c.events(path)
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp).resolve(); victim=root/'victim';victim.write_text('unchanged')
            link=root/'journal';link.symlink_to(victim)
            with self.assertRaises(ValueError):c.emit(link,{'event':'FORBIDDEN'})
            self.assertEqual(victim.read_text(),'unchanged')
            fifo=root/'fifo';os.mkfifo(fifo,0o600)
            with self.assertRaises(ValueError):c.events(fifo)
        for armed, deadline, now in ((1, 12, 2), (5, 10, 1), (1, float('nan'), 2), (1, float('inf'), 2)):
            with tempfile.TemporaryDirectory() as tmp, self.assertRaises(ValueError):
                c.watch({'armed_monotonic': armed, 'deadline_monotonic': deadline}, Path(tmp).resolve()/'journal',
                        lambda: self.fail('Invalid plan observed live owner'), None, None, lambda: now)

    def test_timeout_fallback_and_independent_absence_both_required(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp).resolve() / 'journal'; identity = {'pid': 7, 'uid': 501, 'birth': 'fixed', 'executable': str(c.PYTHON)}
            alive = [True]; calls = []
            def act(operation):
                calls.append(operation)
                if operation == 'bootout': raise subprocess.TimeoutExpired('synthetic', 1)
                alive[0] = False
            c.watch({'armed_monotonic': 1, 'deadline_monotonic': 11}, path,
                    lambda: identity if alive[0] else None, lambda _: identity if alive[0] else None,
                    act, lambda: 12, lambda _: None)
            self.assertEqual(calls, ['bootout', 'kill'])
            self.assertTrue(c.events(path)[-1]['independent_pid_absent'])
            self.assertTrue(c.events(path)[-1]['registration_absent'])

    def test_exact_launchd_plist_and_origin_argv_pid_validation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve(); label = c.PREFIX + 'coordinator-loss.fixture'; path = root/(label+'.plist')
            config = c.job(label, 'fixture', root/'plan.json'); path.write_bytes(c.plistlib.dumps(config)); path.chmod(0o400)
            plan = {'directory':str(root),'fixture_label':label,'fixture_plist_sha256':c.digest(path),
                    'source_sha256':c.digest(c.SOURCE),'python_sha256':c.digest(c.PYTHON)}
            text = c.DOMAIN+'/'+label+' = {\n\tpath = '+str(path)+'\n\tprogram = '+str(c.PYTHON)+'\n\targuments = {\n'+''.join('\t\t'+a+'\n' for a in config['ProgramArguments'])+'\t}\n\tpid = 7\n}\n'
            identity = {'pid':7,'uid':501,'birth':'fixed','executable':str(c.PYTHON)}
            with patch.object(c,'registered',return_value=True), patch.object(c,'process',return_value=identity):
                with patch.object(c,'command',return_value=text): self.assertEqual(c.observe(plan,'fixture')['pid'],7)
                for bad in (text.replace(str(path),'/foreign/job.plist'), text.replace('\tpid = 7','\tpid = 8\n\tpid = 7'), text.replace('\t\tfixture\n','\t\tforeign\n')):
                    with patch.object(c,'command',return_value=bad), self.assertRaises(ValueError): c.observe(plan,'fixture')
                with patch.object(c,'command',return_value=text.replace('\tpid = 7\n','')):
                    self.assertIsNone(c.observe(plan,'fixture',stopped=True)['pid'])
            job=c.job('exact.guardian','guardian',root/'plan.json')
            self.assertEqual(job['KeepAlive'],{'SuccessfulExit':False}); self.assertEqual(job['ThrottleInterval'],1)
            self.assertTrue(job['RunAtLoad']); self.assertNotIn('KeepAlive',config)

    def test_real_coordinator_interruption_and_separate_guardian_recovery(self):
        fixture_source = "import sys,time,signal;from pathlib import Path;signal.alarm(8);p=Path(sys.argv[1]);exec('while p.exists(): time.sleep(.01)')"
        driver = '''import importlib.util,json,os,signal,sys
from pathlib import Path
spec=importlib.util.spec_from_file_location('c',sys.argv[1]);c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
root=Path(sys.argv[2]);plan=json.loads((root/'plan').read_text());identity=plan['identity']
def pid(n):return identity if (root/'alive').exists() else None
def owner():return identity if pid(identity['pid']) is not None else None
def action(operation):
 if pid(identity['pid'])!={k:identity[k] for k in ('pid','uid','birth','executable')}:raise ValueError('Fixture identity changed')
 (root/'alive').unlink()
c.watch(plan,root/'journal',owner,pid,action)
'''
        for restart in (False, True):
            with self.subTest(restart=restart), tempfile.TemporaryDirectory() as tmp:
                root=Path(tmp).resolve(); children=[]
                try:
                    (root/'alive').write_text('synthetic owner registration and PID observation')
                    fixture=subprocess.Popen([str(c.PYTHON),'-I','-B','-c',fixture_source,str(root/'alive')]);children.append(fixture)
                    coordinator=subprocess.Popen([str(c.PYTHON),'-I','-B','-c','import time;time.sleep(8)']);children.append(coordinator)
                    fixture_identity={'pid':fixture.pid,'uid':501,'birth':'synthetic fixture token','executable':str(c.PYTHON)}
                    armed=time.monotonic(); plan={'armed_monotonic':armed,'deadline_monotonic':armed+2,'identity':fixture_identity}
                    (root/'plan').write_text(json.dumps(plan))
                    def start():
                        p=subprocess.Popen([str(c.PYTHON),'-I','-B','-c',driver,str(SOURCE),str(root)]); children.append(p); return p
                    guardian=start()
                    c.wait_for(lambda:any(e['event']=='OWNED' for e in c.events(root/'journal')),armed+1)
                    coordinator.kill();coordinator.wait(timeout=1)
                    if restart:
                        guardian.kill();guardian.wait(timeout=1);guardian=start()
                    guardian.wait(timeout=5);self.assertEqual(guardian.returncode,0)
                    fixture.wait(timeout=1);self.assertEqual(fixture.returncode,0)
                    history=c.events(root/'journal');self.assertEqual(history[-1]['event'],'TERMINATED')
                    self.assertGreaterEqual(history[-1]['monotonic'],armed+2)
                    self.assertLess(history[-1]['monotonic'],armed+5)
                    starts=[e for e in history if e['event']=='GUARDIAN_STARTED']
                    self.assertEqual(len({e['writer_pid'] for e in starts}),2 if restart else 1)
                    self.assertEqual({e['deadline_monotonic'] for e in starts},{plan['deadline_monotonic']})
                finally:
                    for child in children:
                        if child.poll() is None:child.kill()
                        child.wait(timeout=2)


if __name__ == '__main__': unittest.main()
