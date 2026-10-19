"""Check archived evaluation data; never import or execute fixture code."""

import ast
from datetime import datetime
import hashlib
import json
from pathlib import Path
import statistics
import unittest


ROOT = Path(__file__).resolve().parents[1] / "experiments/audit-evaluation"


class AuditEvaluationTests(unittest.TestCase):
    def test_fixture_manifest_preserves_source_data(self):
        manifest = json.loads((ROOT / "fixture-manifest.json").read_text())
        files = {str(p.relative_to(ROOT)) for p in (ROOT / "fixtures").rglob("*")
                 if p.is_file()}
        self.assertEqual(files, set(manifest))
        for name, digest in manifest.items():
            with self.subTest(name=name):
                path = ROOT / name
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), digest)
                if path.suffix == ".py":
                    ast.parse(path.read_text(), filename=name)

    def test_reports_grades_and_timing_denominators_reconcile(self):
        expected = json.loads((ROOT / "expectations.json").read_text())
        protocol = json.loads((ROOT / "protocol.json").read_text())
        results = json.loads((ROOT / "results.json").read_text())
        runs, summary = results["runs"], results["summary"]
        self.assertEqual(len(runs), len(expected))
        self.assertEqual({run["case"] for run in runs}, set(expected))
        self.assertEqual(set(protocol["cases"]), set(expected))
        self.assertEqual(protocol["expectations_sha256"],
                         hashlib.sha256((ROOT / "expectations.json").read_bytes()).hexdigest())
        self.assertEqual(summary["baseline_runs"], len(runs))
        self.assertEqual(summary["expected_weakness_cases"],
                         sum(case["weakness"] for case in expected.values()))
        self.assertEqual(summary["audit_checkpoint_seconds_median"],
                         statistics.median(run["audit_checkpoint_seconds"] for run in runs))
        for field in ("missed_findings", "false_positives", "unclear_explanations"):
            self.assertEqual(summary[field + "_manual"],
                             sum(len(run["grading"][field]) for run in runs))
        for run in runs:
            with self.subTest(case=run["case"]):
                report = ROOT / run["report"]
                self.assertEqual(hashlib.sha256(report.read_bytes()).hexdigest(),
                                 run["report_sha256"])
                self.assertIn("**Tests were not run.**", report.read_text())
                times = [datetime.fromisoformat(run[key].replace("Z", "+00:00"))
                         for key in ("start_utc", "pre_final_utc", "completion_observed_before_utc")]
                self.assertLessEqual(times[0], times[1])
                self.assertLessEqual(times[1], times[2])
                self.assertEqual((times[1] - times[0]).total_seconds(),
                                 run["audit_checkpoint_seconds"])
                self.assertEqual((times[2] - times[0]).total_seconds(),
                                 run["completion_upper_bound_seconds"])
                # Grading is human judgment; the test protects recorded accounting,
                # not a claim that future model responses will match this baseline.
                grading = run["grading"]
                self.assertEqual(bool(grading["missed_findings"]),
                                 expected[run["case"]]["weakness"] and not grading["found_weakness"])
                self.assertEqual(bool(grading["false_positives"]),
                                 not expected[run["case"]]["weakness"] and grading["found_weakness"])


if __name__ == "__main__":
    unittest.main()
