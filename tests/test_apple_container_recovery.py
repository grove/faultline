"""Recovery tests use only mocked commands and temporary host evidence."""

from contextlib import ExitStack
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('recovery', ROOT / 'qualification/apple_container_recover_setup_v2.py')
r = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(r)
BASE = json.loads(r.PLAN.read_text())


class RecoveryTests(unittest.TestCase):
    def attempt(self, fail_second=False, deny_ps=False, lingering=False, changed=False, foreign_listener=False,
                ambiguous_first=False):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        plan = copy.deepcopy(BASE)
        for number, entry in enumerate(plan['services'], 101):
            entry['pid'] = number
            executable = root / Path(entry['identity']['executable']).name
            executable.write_bytes(b'synthetic executable identity; never executed')
            entry['identity']['executable'] = str(executable)
        plan['setup_receipt_sha256'] = hashlib.sha256(b'original receipt').hexdigest()
        plan_file = root / 'plan.json'
        plan_file.write_text(json.dumps(plan))
        (root / 'setup-v2.json').write_bytes(b'original receipt')
        journal = root / 'recovery.jsonl'
        entries = plan['services']
        remaining = [entry['target'] for entry in entries]
        calls = []
        inspected = {}

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
            if argv[0] == '/bin/ps':
                if deny_ps:
                    raise PermissionError('process inspection unavailable')
                active = [e for e in entries if e['target'] in remaining]
                if lingering and not active:
                    active = entries[:1]
                return ''.join(str(e['pid']) + ' 501 Sun Oct 18 20:00:00 2026 ' + e['identity']['executable'] + '\n' for e in active)
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

    def test_foreign_plist_hash_is_not_accepted_by_live_revalidation(self):
        entry = BASE['services'][0]
        text = (entry['target'] + ' = {\n\tpid = ' + str(entry['pid']) +
                '\n\tstate = running\n\t\tCONTAINER_APP_ROOT => ' + r.identity.ENV['CONTAINER_APP_ROOT'] +
                '/\n\t\tCONTAINER_INSTALL_ROOT => /usr/local/\n}\n')
        foreign = {**entry['identity'], 'sha256': 'foreign'}
        with patch.object(r.identity, 'owned_plist', return_value=foreign):
            with self.assertRaisesRegex(ValueError, 'identity changed'):
                r.inspect_service(entry, run=lambda _: text)


if __name__ == '__main__':
    unittest.main()
