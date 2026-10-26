"""Check six source-only regression packets, never execute their code.

These checks protect the examples and maintainer expectations. They do not run
Audit or establish that a model follows the skill, improves detection, or is fast.
"""

import ast
import json
from pathlib import Path
import unittest


FIXTURE = Path(__file__).resolve().parent / "fixtures" / "impact-first.json"


class ImpactFirstFixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bundle = json.loads(FIXTURE.read_text(encoding="utf-8"))
        cls.cases = cls.bundle["cases"]

    def source(self, case, name):
        return "\n".join(self.cases[case]["files"][name]) + "\n"

    def symbol(self, case, name, symbol):
        node = ast.parse(self.source(case, name), filename=f"{case}/{name}")
        for part in symbol.split("."):
            node = next(child for child in node.body
                        if isinstance(child, (ast.ClassDef, ast.FunctionDef))
                        and child.name == part)
        return node

    def calls(self, node):
        return [ast.unparse(child.func) for child in ast.walk(node)
                if isinstance(child, ast.Call)]

    def test_packets_are_parseable_and_expectations_cite_real_symbols(self):
        self.assertEqual(set(self.cases), set("ABCDEF"))
        self.assertEqual(self.bundle["status"],
                         "NOT RUN: maintainer expectations, not observed model behavior")
        for case, packet in self.cases.items():
            with self.subTest(case=case):
                for name in packet["files"]:
                    if name.endswith(".py"):
                        ast.parse(self.source(case, name), filename=f"{case}/{name}")
                for reference in packet["expectation"]["evidence"]:
                    name, separator, symbol = reference.partition(":")
                    self.assertIn(name, packet["files"])
                    if separator:
                        self.symbol(case, name, symbol)

    def test_weak_case_acknowledges_before_durability_and_only_tests_success(self):
        calls = self.calls(self.symbol("A", "journal.py", "Journal.save"))
        self.assertLess(calls.index("self.disk.write"), calls.index("acknowledge"))
        self.assertLess(calls.index("acknowledge"), calls.index("self.disk.sync"))
        happy = self.symbol("A", "test_journal.py", "test_successful_save")
        self.assertIn("journal.save", self.calls(happy))
        self.assertNotIn("disk.power_loss", self.calls(happy))
        self.assertTrue(any(isinstance(node, ast.Assert) for node in happy.body))
        self.assertIn("complete value are durable", self.source("A", "CONTRACT.md"))

    def test_disk_boundaries_copy_nested_records_without_shared_mutable_values(self):
        # Keep aliasing bugs out of the controlled durability examples. A crash
        # discards buffered writes; neither callers nor reads can change durable data.
        boundaries = {
            "write": "self.buffered[key] = deepcopy(value)",
            "sync": "self.durable = deepcopy(self.buffered)",
            "power_loss": "self.buffered = deepcopy(self.durable)",
            "read_all": "return deepcopy(self.durable)",
        }
        for case in "ABCDE":
            with self.subTest(case=case):
                tree = ast.parse(self.source(case, "disk.py"))
                self.assertEqual(ast.unparse(tree.body[0]), "from copy import deepcopy")
                for method, statement in boundaries.items():
                    node = self.symbol(case, "disk.py", f"Disk.{method}")
                    self.assertEqual([ast.unparse(item) for item in node.body], [statement])

    def test_protected_case_interrupts_at_ack_and_compares_full_recovered_state(self):
        calls = self.calls(self.symbol("B", "journal.py", "Journal.save"))
        self.assertLess(calls.index("self.disk.sync"), calls.index("acknowledge"))
        test = self.symbol("B", "test_journal.py",
                           "JournalTests.test_confirmed_values_survive_power_loss")
        callback = next(node for node in test.body if isinstance(node, ast.FunctionDef))
        self.assertEqual(self.calls(callback),
                         ["acknowledged.append", "disk.power_loss", "PowerLoss"])
        self.assertIsInstance(callback.body[-1], ast.Raise)
        self.assertIn("self.assertRaises", self.calls(test))
        assertions = [node.value for node in test.body
                      if isinstance(node, ast.Expr)
                      and isinstance(node.value, ast.Call)
                      and ast.unparse(node.value.func) == "self.assertEqual"]
        # Reopen the same disk, not a fresh empty backing store or the old Journal.
        recovery = next(call for call in assertions
                        if ast.unparse(call.args[0]) == "Journal(disk).recover()")
        self.assertEqual(ast.literal_eval(recovery.args[1]),
                         {"existing": {"amount": 4}, "new": {"amount": 7}})
        self.assertEqual(self.cases["B"]["expectation"]["result"],
                         "No actionable finding in the reviewed scope.")

    def test_mixed_scope_keeps_integrity_and_formatting_consequences_separate(self):
        for name in ("disk.py", "journal.py", "test_journal.py"):
            self.assertEqual(self.source("C", name), self.source("A", name))
        test = self.symbol("C", "test_display.py", "test_error_label")
        self.assertIsInstance(test.body[0].test.ops[0], ast.In)
        self.assertIn("no storage effect", self.source("C", "CONTRACT.md"))
        self.assertEqual(self.cases["C"]["expectation"]["first_finding"],
                         "The acknowledgement-before-sync recovery gap from case A.")

    def test_unsettled_promise_has_conditional_expectations_for_same_source_path(self):
        self.assertEqual(self.source("D", "journal.py"), self.source("A", "journal.py"))
        self.assertIn("progress indicator", self.source("D", "CONTRACT.md"))
        expectation = self.cases["D"]["expectation"]
        self.assertEqual(expectation["result"], "contract question")
        self.assertIn("If acknowledgement promises durability", expectation["smallest_test"])
        self.assertIn("If it means accepted in memory", expectation["smallest_test"])

    def test_constructed_error_checks_display_but_never_exercises_storage(self):
        test = self.symbol("E", "test_display.py", "test_error_message")
        self.assertEqual(self.calls(test), ["OSError", "error_message"])
        self.assertIsInstance(test.body[-1].test.ops[0], ast.Eq)
        self.assertEqual(self.source("E", "journal.py"), self.source("A", "journal.py"))
        self.assertIn("display test remains useful", self.cases["E"]["expectation"]["distinction"])

    def test_negative_control_has_exact_checks_for_its_limited_promise(self):
        self.assertEqual(set(self.cases["F"]["files"]),
                         {"CONTRACT.md", "display.py", "test_display.py"})
        test = self.symbol("F", "test_display.py", "test_error_message")
        loop = test.body[0]
        self.assertIsInstance(loop, ast.For)
        self.assertIsInstance(loop.body[0].test.ops[0], ast.Eq)
        self.assertEqual([item.elts[1].value for item in loop.iter.elts],
                         ["Save failed: offline", "Save failed: "])
        self.assertEqual(self.cases["F"]["expectation"]["result"],
                         "No actionable finding in the reviewed scope.")


if __name__ == "__main__":
    unittest.main()
