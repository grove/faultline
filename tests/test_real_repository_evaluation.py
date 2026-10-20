"""Protect pilot evidence and accounting; never load or execute target projects."""

from collections import Counter
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
import statistics
import unittest


ROOT = Path(__file__).resolve().parents[1] / "experiments/real-repository-pilot"
CASES = {"r1", "r2", "r3", "r4"}


def read_json(name):
    return json.loads((ROOT / name).read_text())


class RealRepositoryEvaluationTests(unittest.TestCase):
    def test_frozen_inputs_and_published_evidence_identities(self):
        freeze = read_json("freeze.json")
        self.assertEqual(set(freeze["cases"]), CASES)
        for name in ("expectations", "source-manifest"):
            self.assertEqual(hashlib.sha256((ROOT / f"{name}.json").read_bytes()).hexdigest(),
                             freeze[name.replace("-", "_") + "_sha256"])
        for name, digest in read_json("artifact-manifest.json").items():
            with self.subTest(name=name):
                self.assertEqual(hashlib.sha256((ROOT / name).read_bytes()).hexdigest(), digest)
        for case, identity in read_json("published-inputs.json").items():
            prompt = (ROOT / f"inputs/{case}.txt").read_bytes()
            self.assertEqual(hashlib.sha256(prompt).hexdigest(), identity["published_prompt_sha256"])
            self.assertEqual(identity["original_prompt_sha256"], freeze["cases"][case]["prompt_sha256"])
            self.assertNotIn(b"expectations.json", prompt)
        sources = read_json("source-manifest.json")
        self.assertEqual({source["case"] for source in sources}, CASES)
        self.assertEqual(sum(len(source["files"]) for source in sources), 254)
        for source in sources:
            self.assertRegex(source["commit"], r"^[0-9a-f]{40}$")
            for name, digest in source["files"].items():
                self.assertIn(Path(name).parts[0], {"src", "tests", "docs"})
                self.assertRegex(digest, r"^[0-9a-f]{64}$")

    def test_end_to_end_times_end_after_captured_final_responses(self):
        freeze = read_json("freeze.json")
        for case in CASES:
            with self.subTest(case=case):
                timing = read_json(f"timings/audit-{case}.json")
                events = [json.loads(line) for line in (ROOT / timing["events"]).read_text().splitlines()]
                self.assertEqual(events[-1]["type"], "turn.completed")
                self.assertEqual(timing["terminal_event"], "turn.completed")
                self.assertTrue(timing["complete_response_captured"])
                self.assertEqual(timing["elapsed_seconds"], events[-1]["received_seconds"])
                self.assertEqual([e["received_seconds"] for e in events],
                                 sorted(e["received_seconds"] for e in events))
                messages = [e for e in events if e.get("item_type") == "agent_message"
                            and e["type"] == "item.completed"]
                response = (ROOT / timing["response"]).read_bytes()
                # The observer appends one newline when persisting the captured message.
                self.assertEqual(hashlib.sha256(response[:-1]).hexdigest(), messages[-1]["text_sha256"])
                self.assertLess(messages[-1]["received_seconds"], timing["elapsed_seconds"])
                self.assertEqual(hashlib.sha256(response).hexdigest(), timing["response_sha256"])
                self.assertIn(b"**Tests were not run.**", response)
                self.assertLess(datetime.fromisoformat(freeze["frozen_utc"]),
                                datetime.fromisoformat(timing["start_utc"]))
                for event in events:
                    command = event.get("command", "")
                    self.assertNotIn("expectations.json", command)
                    self.assertNotIn("/EVALUATION", command)

    def test_finding_and_claim_denominators_keep_misses_and_uncertainty(self):
        results = read_json("results.json")
        summary, runs = results["summary"], results["runs"]
        self.assertEqual({run["case"] for run in runs}, CASES)
        self.assertEqual(summary["audits_assigned"], len(runs))
        for key, count_key, total_key in (("finding_units", "finding_counts", "emitted_findings"),
                                          ("claim_units", "claim_counts", "substantive_claims")):
            actual = Counter(unit["classification"] for unit in results[key])
            self.assertEqual(len(results[key]), summary[total_key])
            self.assertEqual(sum(summary[count_key].values()), summary[total_key])
            for classification, count in summary[count_key].items():
                self.assertEqual(actual[classification], count)
        for case in CASES:
            grade = read_json(f"grades/{case}.json")
            self.assertEqual(len([c for c in results["claim_units"] if c["case"] == case]),
                             len(grade["findings"]))
            emitted = {"F" + number for number in re.findall(
                r"(?m)^(?:\*\*)?([1-3])\.\s", (ROOT / f"audits/{case}.md").read_text())}
            units = [u for u in results["finding_units"] if u["case"] == case]
            self.assertEqual({u["id"] for u in units}, emitted)
            self.assertEqual({claim for u in units for claim in u["raw_grade_claims"]},
                             {f["id"] for f in grade["findings"]})
        mixed = next(u for u in results["finding_units"] if (u["case"], u["id"]) == ("r2", "F2"))
        self.assertEqual(mixed["classification"], read_json("reviews/click.json")["original_finding_2_unit_classification"])
        self.assertEqual(mixed["raw_grade_claims"], ["F2a", "F2b"])
        self.assertEqual(summary["historical_gaps_found"], sum(r["historical_gap_found"] is True for r in runs))
        self.assertEqual(summary["historical_gaps_missed"], sum(r["historical_gap_missed"] is True for r in runs))
        fp = summary["false_positives_among_adjudicated"]
        counts = summary["finding_counts"]
        self.assertEqual(fp["denominator"], counts["accepted_gap"] + counts["false_positive"])
        self.assertEqual(fp["numerator"], counts["false_positive"])
        self.assertEqual(fp["fraction"], fp["numerator"] / fp["denominator"])
        times = [read_json(run["timing"])["elapsed_seconds"] for run in runs]
        self.assertEqual(summary["latency_seconds_median"], statistics.median(times))
        self.assertEqual(summary["latency_seconds_min"], min(times))
        self.assertEqual(summary["latency_seconds_max"], max(times))


if __name__ == "__main__":
    unittest.main()
