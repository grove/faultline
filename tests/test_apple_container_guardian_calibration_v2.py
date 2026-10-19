"""Host-owned subprocesses and synthetic launchd output; never registers jobs or VMs."""
import importlib.util
import base64
import json
import os
from pathlib import Path
import signal
import subprocess
import tempfile
import time
import unittest
from unittest.mock import patch

SOURCE = Path(__file__).resolve().parents[1] / 'qualification/apple_container_guardian_calibration_v2.py'
SPEC = importlib.util.spec_from_file_location('calibration', SOURCE)
c = importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(c)


class CalibrationTests(unittest.TestCase):
    def bootstrap_fixture(self, root, role='guardian'):
        plan = {'directory': str(root), 'deadline_monotonic': time.monotonic() + 10}
        (root/'plan.json').write_text('{}'); (root/'plan.json').chmod(0o400)
        for name in ('guardian', 'fixture'):
            label = c.PREFIX + 'coordinator-loss.' + name
            path = root/(label+'.plist')
            path.write_bytes(c.plistlib.dumps(c.job(label, name, root/'plan.json'))); path.chmod(0o400)
            plan[name+'_label'] = label; plan[name+'_plist_sha256'] = c.digest(path)
        return plan

    def test_bootstrap_records_raw_streams_exit_timeout_and_output_limit(self):
        popen = subprocess.Popen
        cases = [
            ('success', "import os;os.write(1,b'accepted\\xff')", 0),
            ('failure', "import os;os.write(1,b'out');os.write(2,b'bootstrap error\\xff');raise SystemExit(5)", 5),
            ('stderr', "import os;os.write(2,b'warning')", 0),
            ('timeout', "import os,time;os.write(2,b'partial');time.sleep(5)", -signal.SIGKILL),
            ('limit', "import os,time;os.write(1,b'x'*200000);time.sleep(5)", -signal.SIGKILL),
        ]
        for name, source, code in cases:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp).resolve(); plan = self.bootstrap_fixture(root)
                def synthetic(argv, **kwargs):
                    self.assertEqual(argv, ['/bin/launchctl','bootstrap',c.DOMAIN,str(root/(plan['guardian_label']+'.plist'))])
                    self.assertTrue((root/'guardian-bootstrap-intent.json').exists())
                    self.assertEqual(kwargs['env'], c.ENV); self.assertEqual(kwargs['cwd'], '/')
                    return popen([str(c.PYTHON),'-I','-B','-c',source], **kwargs)
                with patch.object(c,'load',return_value=plan), patch.object(c,'registered',return_value=False), patch.object(c,'command',return_value='OK'), patch.object(c.subprocess,'Popen',side_effect=synthetic):
                    if name == 'success': c.bootstrap(plan,'guardian')
                    else:
                        with self.assertRaises(ValueError): c.bootstrap(plan,'guardian')
                result = json.loads((root/'guardian-bootstrap-result.json').read_bytes())
                self.assertEqual(result['returncode'], code)
                stdout = base64.b64decode(result['stdout_base64']); stderr = base64.b64decode(result['stderr_base64'])
                self.assertLessEqual(len(stdout)+len(stderr),65536)
                self.assertEqual(result['timeout'], name == 'timeout'); self.assertEqual(result['output_limit'],name == 'limit')
                if name == 'success': self.assertEqual(stdout,b'accepted\xff')
                if name == 'failure': self.assertEqual((stdout,stderr),(b'out',b'bootstrap error\xff'))
                if name == 'timeout': self.assertEqual(stderr,b'partial')
                if name == 'limit': self.assertEqual(len(stdout),65536)
                self.assertEqual((root/'guardian-bootstrap-result.json').stat().st_mode & 0o777,0o400)
                # Consumed intent refuses a second invocation before a new subprocess.
                with patch.object(c,'load',return_value=plan), patch.object(c,'registered',return_value=False), patch.object(c,'command',return_value='OK'), patch.object(c.subprocess,'Popen') as launch:
                    plan['deadline_monotonic'] = time.monotonic()+10
                    with self.assertRaises(FileExistsError): c.bootstrap(plan,'guardian')
                    launch.assert_not_called()

    def test_bootstrap_spawn_error_and_exact_fixture_receipt(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp).resolve(); plan=self.bootstrap_fixture(root)
            with patch.object(c,'load',return_value=plan), patch.object(c,'registered',return_value=False), patch.object(c,'command',return_value='OK'), patch.object(c.subprocess,'Popen',side_effect=PermissionError('synthetic denial')):
                with self.assertRaises(ValueError): c.bootstrap(plan,'fixture')
            result=json.loads((root/'fixture-bootstrap-result.json').read_bytes())
            self.assertIsNone(result['returncode']); self.assertIn('synthetic denial',result['start_error'])
            self.assertEqual(result['argv'][2], 'user/501')

    def test_bootstrap_preflight_rejects_tamper_collision_and_spent_budget(self):
        for bad in ('plist','collision','budget','access','plan','lint'):
            with self.subTest(bad=bad), tempfile.TemporaryDirectory() as tmp:
                root=Path(tmp).resolve(); plan=self.bootstrap_fixture(root)
                if bad=='plist': plan['guardian_plist_sha256']='foreign'
                if bad=='budget': plan['deadline_monotonic']=time.monotonic()+2
                with patch.object(c,'load',return_value={} if bad=='plan' else plan), patch.object(c,'registered',return_value=bad=='collision'), patch.object(c,'command',side_effect=ValueError('lint failed') if bad=='lint' else None), patch.object(c.os,'access',return_value=bad!='access'), patch.object(c.subprocess,'Popen') as launch:
                    with self.assertRaises(ValueError): c.bootstrap(plan,'guardian')
                    launch.assert_not_called()
                self.assertFalse((root/'guardian-bootstrap-intent.json').exists())

    def test_access_snapshot_rejects_symlink_and_unsearchable_parent(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp).resolve(); leaf=root/'file';leaf.write_text('host fixture')
            link=root/'linked';link.symlink_to(leaf)
            with self.assertRaises(ValueError): c.access_snapshot([link])
            access=os.access
            with patch.object(c.os,'access',side_effect=lambda p,m:False if p==root else access(p,m)):
                with self.assertRaises(ValueError): c.access_snapshot([leaf])

    def test_restart_refuses_changed_deadline_and_armed_plan(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp).resolve(); journal=root/'journal'
            c.emit(journal,{'event':'GUARDIAN_STARTED','deadline_monotonic':10})
            with self.assertRaisesRegex(ValueError,'deadline changed'):
                c.watch({'armed_monotonic':2,'deadline_monotonic':12},journal,
                        lambda:self.fail('Changed deadline observed owner'),None,None,lambda:13)
            case=root/'coordinator-loss';case.mkdir(mode=0o700);plan_path=case/'plan.json'
            plan_path.write_text('{}');plan_path.chmod(0o400)
            c.emit(case/'guardian.jsonl',{'event':'ARMED','plan_sha256':'old plan hash'})
            with patch.object(c,'BASE',root),patch.object(c,'load',return_value={}),patch.object(c,'watch') as watch:
                c.guardian(plan_path);watch.assert_not_called()
            self.assertEqual(c.events(case/'guardian.jsonl')[-1]['event'],'INCOMPLETE_STOP_AND_REVIEW')
            self.assertFalse((case/'ready.json').exists())

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
