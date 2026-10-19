"""Recovery tests use only mocked commands and temporary host evidence."""

from contextlib import ExitStack
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('recovery', ROOT / 'qualification/apple_container_recover_setup_v2.py')
r = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(r)
BASE = json.loads(r.PLAN.read_text())


class RecoveryTests(unittest.TestCase):
    def attempt(self, fail_second=False, deny_ps=False, lingering=False, changed=False, foreign_listener=False,
                ambiguous_first=False, process_fault=None, replaced_late=False, new_lingering=False):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        plan = copy.deepcopy(BASE)
        for number, entry in enumerate(plan['services'], 101):
            entry['pid'] = number
            executable = root / Path(entry['identity']['executable']).name
            executable.write_bytes(b'synthetic executable identity; never executed')
            entry['identity']['executable'] = str(executable)
        previous = root / 'recovery-setup-v2-01.jsonl'
        previous.write_bytes(b'preserved failed recovery')
        plan['previous_recovery_journal_sha256'] = hashlib.sha256(previous.read_bytes()).hexdigest()
        plan['setup_receipt_sha256'] = hashlib.sha256(b'original receipt').hexdigest()
        plan_file = root / 'plan.json'
        plan_file.write_text(json.dumps(plan))
        (root / 'setup-v2.json').write_bytes(b'original receipt')
        journal = root / 'recovery.jsonl'
        entries = plan['services']
        remaining = [entry['target'] for entry in entries]
        calls = []
        inspected = {}
        ps_calls = 0

        def run(argv):
            calls.append(argv)
            if argv[:2] == ['/bin/launchctl', 'print']:
                domain = argv[2]
                active = [e for e in entries if e['target'] in remaining] if domain == 'user/501' else []
                return (domain + ' = {\n\tservices = {\n' +
                        ''.join('\t\t123 - ' + e['target'].split('/')[-1] + '\n' for e in active) +
                        '\t}\n\tendpoints = {\n' +
                        ''.join('\t\t0x123 M A ' + name + '\n' for e in active for name in e['mach_services']) +
                        '\t}\n}\n')
            if argv[:2] == ['/bin/launchctl', 'bootout']:
                if ambiguous_first and len(remaining) == 4:
                    remaining.remove(argv[2])
                    raise TimeoutError('bootout timed out after an unknown effect')
                if fail_second and len(remaining) == 3:
                    raise ValueError('simulated second bootout failure')
                remaining.remove(argv[2])
                return ''
            def active_processes():
                active = [e for e in entries if e['target'] in remaining]
                if lingering and not active:
                    active = entries[:1]
                if new_lingering and not active:
                    active = [{**entries[0], 'pid': 200}]
                if process_fault == 'missing':
                    active = active[1:]
                if process_fault == 'stale_pid' and active:
                    active = [{**active[0], 'pid': 200}] + active[1:]
                if process_fault == 'unexpected':
                    active = active + [{**entries[0], 'pid': 200}]
                return active
            if argv == r.DISCOVERY:
                return ''.join(str(e['pid']) + '\n' for e in active_processes())
            if argv[0] == '/bin/ps':
                nonlocal ps_calls
                ps_calls += 1
                if deny_ps:
                    raise PermissionError('process inspection unavailable')
                self.assertEqual(argv[:3], ['/bin/ps', '-ww', '-p'])
                self.assertEqual(argv[4:], ['-o', 'pid=,uid=,lstart=,comm='])
                output = []
                for e in active_processes():
                    uid = 502 if process_fault == 'uid' else 501
                    program = '/bin/sh' if process_fault == 'executable' else e['identity']['executable']
                    started = e['process_started']
                    if process_fault == 'birth' or (replaced_late and ps_calls > 1):
                        started = 'Sun Oct 18 23:59:59 2026'
                    output.append(f"{e['pid']} {uid} {started} {program}\n")
                return ''.join(output)
            if argv[0] == '/usr/sbin/lsof':
                output = 'p101\nf14\nPUDP\nn127.0.0.1:2053\n' if entries[0]['target'] in remaining else ''
                return output + ('p999\nf3\nPUDP\nn127.0.0.1:1053\n' if foreign_listener else '')
            raise AssertionError('Unexpected command ' + str(argv))

        def inspect(entry, run):
            target = entry['target']
            inspected[target] = inspected.get(target, 0) + 1
            if changed and inspected[target] > 1:
                raise ValueError('identity changed before removal')
            return {'target': target, 'pid': entry['pid'], 'identity': entry['identity']}

        with ExitStack() as stack:
            for name, value in (('PLAN', plan_file), ('PLAN_SHA256', hashlib.sha256(plan_file.read_bytes()).hexdigest()),
                                ('JOURNAL', journal)):
                stack.enter_context(patch.object(r, name, value))
            stack.enter_context(patch.object(r.os, 'getuid', return_value=501))
            stack.enter_context(patch.object(r, 'inspect_service', side_effect=inspect))
            code = r.recover(run=run, pause=lambda _: None)
        records = [json.loads(line) for line in journal.read_text().splitlines()]
        self.assertEqual((root / 'setup-v2.json').read_bytes(), b'original receipt')
        self.assertEqual(previous.read_bytes(), b'preserved failed recovery')
        self.assertFalse(any(c[0].endswith('/container') for c in calls))
        return code, calls, records, remaining

    def test_scoped_recovery_revalidates_and_checks_all_observers(self):
        code, calls, records, remaining = self.attempt()
        self.assertEqual(code, 0)
        self.assertFalse(remaining)
        self.assertEqual([c[2] for c in calls if c[1] == 'bootout'], [e['target'] for e in BASE['services']])
        self.assertEqual(sum(item['phase'] == 'BEFORE_BOOTOUT' for item in records), 4)
        self.assertEqual(records[-1]['result'], 'SCOPED_RECOVERY_OBSERVED')
        self.assertTrue(any(c[0] == '/bin/ps' for c in calls))
        self.assertTrue(any(c[0] == '/usr/sbin/lsof' for c in calls))

    def test_partial_cleanup_stops_and_records_remaining_state(self):
        code, calls, records, remaining = self.attempt(fail_second=True)
        self.assertEqual(code, 1)
        self.assertEqual(len(remaining), 3)
        self.assertEqual(sum(c[1] == 'bootout' for c in calls), 2)
        self.assertEqual(records[-1]['phase'], 'PARTIAL_POSTCHECK')
        self.assertEqual(len(records[-1]['processes']), 3)
        self.assertFalse(any(item.get('phase') == 'COMPLETE' for item in records))

    def test_denied_process_observation_and_changed_identity_prevent_removal(self):
        for kwargs in ({'deny_ps': True}, {'changed': True}):
            with self.subTest(kwargs=kwargs):
                code, calls, _, remaining = self.attempt(**kwargs)
                self.assertEqual(code, 1)
                self.assertEqual(len(remaining), 4)
                self.assertFalse(any(c[1] == 'bootout' for c in calls))

    def test_lingering_process_is_incomplete_after_registrations_disappear(self):
        code, _, records, remaining = self.attempt(lingering=True)
        self.assertEqual(code, 1)
        self.assertFalse(remaining)
        self.assertEqual(records[-2]['phase'], 'INCOMPLETE_STOP_AND_REVIEW')

    def test_existing_foreign_listener_is_preserved(self):
        code, calls, records, _ = self.attempt(foreign_listener=True)
        self.assertEqual(code, 0)
        self.assertEqual(records[-2]['listeners'][0]['pid'], 999)
        self.assertTrue(all(c[2].startswith('user/501/com.apple.container.') for c in calls if c[1] == 'bootout'))

    def test_ambiguous_first_bootout_still_collects_partial_state(self):
        code, calls, records, remaining = self.attempt(ambiguous_first=True)
        self.assertEqual(code, 1)
        self.assertEqual(len(remaining), 3)
        failure = next(item for item in records if item['phase'] == 'INCOMPLETE_STOP_AND_REVIEW')
        self.assertEqual(len(failure['attempted']), 1)
        self.assertEqual(failure['removed'], [])
        self.assertEqual(records[-1]['phase'], 'PARTIAL_POSTCHECK')
        self.assertEqual(sum(c[1] == 'bootout' for c in calls), 1)

    def test_missing_or_replaced_processes_and_extra_helpers_block_before_removal(self):
        for fault in ('missing', 'stale_pid', 'uid', 'executable', 'birth', 'unexpected'):
            with self.subTest(fault=fault):
                code, calls, _, remaining = self.attempt(process_fault=fault)
                self.assertEqual(code, 1)
                self.assertEqual(len(remaining), 4)
                self.assertFalse(any(c[1] == 'bootout' for c in calls))
        code, calls, _, _ = self.attempt(replaced_late=True)
        self.assertEqual(code, 1)
        self.assertFalse(any(c[1] == 'bootout' for c in calls))

    def test_new_pid_lingering_after_bootout_is_not_mistaken_for_cleanup(self):
        code, _, records, _ = self.attempt(new_lingering=True)
        self.assertEqual(code, 1)
        self.assertEqual(records[-1]['processes'][0]['pid'], 200)
        self.assertFalse(any(record['phase'] == 'COMPLETE' for record in records))

    def test_foreign_plist_hash_is_not_accepted_by_live_revalidation(self):
        entry = BASE['services'][0]
        text = (entry['target'] + ' = {\n\tpid = ' + str(entry['pid']) +
                '\n\tstate = running\n\t\tCONTAINER_APP_ROOT => ' + r.identity.ENV['CONTAINER_APP_ROOT'] +
                '/\n\t\tCONTAINER_INSTALL_ROOT => /usr/local/\n}\n')
        foreign = {**entry['identity'], 'sha256': 'foreign'}
        with patch.object(r.identity, 'owned_plist', return_value=foreign):
            with self.assertRaisesRegex(ValueError, 'identity changed'):
                r.inspect_service(entry, run=lambda _: text)


class TargetedProcessTests(unittest.TestCase):
    RAW = (ROOT / 'qualification/2026-10-19-apple-container-operator-processes.txt').read_text()

    def observe(self, raw=None, discovery=None):
        raw = self.RAW if raw is None else raw
        pids = sorted(e['pid'] for e in BASE['services'])
        discovery = iter([pids, pids] if discovery is None else discovery)
        calls = []
        def run(argv):
            calls.append(argv)
            if argv == r.DISCOVERY:
                return ''.join(str(pid) + '\n' for pid in next(discovery))
            self.assertEqual(argv, ['/bin/ps', '-ww', '-p', ','.join(map(str, pids)),
                                    '-o', 'pid=,uid=,lstart=,comm='])
            return raw
        return r.processes(BASE['services'], run), calls

    def test_actual_operator_rows_parse_and_match_every_frozen_birth_identity(self):
        observed, calls = self.observe()
        r.verify_processes(observed, BASE['services'])
        self.assertEqual([p['pid'] for p in observed], [70913, 70921, 70924, 70925])
        self.assertEqual(len(calls), 3)
        self.assertFalse(any('-axo' in call or '-f' in call for call in calls))

    def test_ambiguous_relevant_rows_are_never_ignored(self):
        for raw in ('70913 501 - /usr/local/bin/container-apiserver\n',
                    self.RAW + self.RAW.splitlines()[0] + '\n',
                    self.RAW.replace('70913', '99999', 1),
                    self.RAW.replace('/usr/local/bin/container-apiserver', '<defunct>'),
                    self.RAW.replace('23:31:23', '99:31:23')):
            with self.subTest(raw=raw[:20]), self.assertRaises(ValueError):
                self.observe(raw=raw)

    def test_disappearing_or_unaccounted_candidate_prevents_complete_observation(self):
        pids = sorted(e['pid'] for e in BASE['services'])
        for scans in ([pids, pids[1:]], [pids[1:], pids[1:]]):
            with self.subTest(scans=scans), self.assertRaises(ValueError):
                self.observe(discovery=scans)

    def test_no_match_exit_is_distinguished_from_denial_and_unknown_failure(self):
        ps = ['/bin/ps', '-ww', '-p', '70913', '-o', 'pid=,uid=,lstart=,comm=']
        for argv in (ps, r.DISCOVERY):
            for code, stdout, stderr, accepted in ((1, b'', b'', True),
                                                  (1, b'', b'Operation not permitted', False),
                                                  (3, b'', b'', False),
                                                  (0, b'', b'', False)):
                result = SimpleNamespace(returncode=code, stdout=stdout, stderr=stderr)
                with self.subTest(argv=argv[0], code=code, stderr=stderr):
                    with patch.object(r.subprocess, 'run', return_value=result) as native:
                        if accepted:
                            self.assertEqual(r.command(argv), '')
                        else:
                            with self.assertRaises(ValueError):r.command(argv)
                        self.assertEqual(native.call_args.kwargs['env']['TZ'], 'Europe/Oslo')


if __name__ == '__main__':
    unittest.main()
