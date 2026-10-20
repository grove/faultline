"""Protect source-only trial evidence, not future model compliance."""

from datetime import datetime
import hashlib
import json
from pathlib import Path
import statistics
import unittest


REPO = Path(__file__).resolve().parents[1]
ROOT = REPO / "experiments/counterexample-audit"


def read(name):
    return json.loads((ROOT / name).read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class CounterexampleAuditTests(unittest.TestCase):
    def test_frozen_skill_source_and_execution_boundaries(self):
        protocol = read("protocol.json")
        baseline = (ROOT / "instructions/baseline.md").read_bytes()
        revised = (ROOT / "instructions/revised.md").read_bytes()
        self.assertEqual(revised, (REPO / "faultline-audit/SKILL.md").read_bytes())
        # Only the internal reasoning steps change; ordinary output and fences stay.
        for data in (baseline, revised):
            self.assertEqual(data.split(b"## Find weak tests")[0],
                             baseline.split(b"## Find weak tests")[0])
            self.assertEqual(data.split(b"## Explain each finding")[1],
                             baseline.split(b"## Explain each finding")[1])
        for arm, expected in protocol["instructions_sha256"].items():
            self.assertEqual(sha(ROOT / f"instructions/{arm}.md"), expected)
        for name, expected in protocol["frozen_artifacts_sha256"].items():
            self.assertEqual(sha(ROOT / name), expected, name)
        self.assertEqual(sha(ROOT.parent / "packaging-2x2/run.py"), protocol["collector_sha256"])
        self.assertEqual(sha(ROOT / "curation/sealed/expectations.json"),
                         protocol["sealed_expectations_sha256"])
        for name, expected in read("artifact-manifest.json").items():
            self.assertEqual(sha(ROOT / name), expected, name)
        for name, expected in read("grading-freeze.json")["files"].items():
            self.assertEqual(sha(ROOT / name), expected, name)
        for case in protocol["cases"]:
            folder = ROOT / "curation/packets" / case["id"]
            files = {str(p.relative_to(folder)): sha(p)
                     for p in folder.rglob("*") if p.is_file()}
            self.assertEqual(files, case["files"])
        known = read("known-case-protocol.json")
        self.assertTrue(known["prior_answer_exposure"])
        self.assertEqual({k.removeprefix("project/"): v for k, v in known["frozen_packet"].items()
                          if k.startswith("project/") and k != "project/docs/pep-0440.rst"},
                         read("../packaging-2x2/source-manifest.json")["files"])
        self.assertNotIn("packaging", json.dumps(protocol["cases"]).lower())

    def test_paired_first_responses_use_identical_evidence_and_settings(self):
        protocol = read("protocol.json")
        self.assertEqual(len(protocol["runs"]), 12)
        self.assertEqual(set(protocol["order"]), {r["id"] for r in protocol["runs"]})
        self.assertEqual(protocol["retries"], 0)
        for case in protocol["cases"]:
            pair = [r for r in protocol["runs"] if r["case"] == case["id"]]
            self.assertEqual({r["arm"] for r in pair}, {"baseline", "revised"})
            prompts, packets, commands = [], [], []
            for run in pair:
                folder = f"audits/{run['id']}"
                timing = read(f"{folder}/timing.json")
                self.assertGreaterEqual(datetime.fromisoformat(timing["start_utc"]),
                                        datetime.fromisoformat(protocol["frozen_utc"]))
                events = read_events(f"{folder}/events.jsonl")
                raw = read_events(f"{folder}/stdout.jsonl")
                self.assertEqual(raw, [e["event"] for e in events])
                if timing["complete_response_captured"]:
                    self.assertEqual(raw[-1]["type"], "turn.completed")
                    messages = [e["item"]["text"] for e in raw
                                if e["type"] == "item.completed"
                                and e.get("item", {}).get("type") == "agent_message"]
                    self.assertEqual((ROOT / folder / "response.md").read_text(),
                                     messages[-1] + "\n")
                    self.assertGreaterEqual(timing["elapsed_seconds"], events[-1]["received_seconds"])
                else:
                    self.assertTrue((ROOT / folder / "failure.txt").is_file())
                prompts.append((ROOT / folder / "prompt.txt").read_bytes())
                packet = read(f"{folder}/packet.json")
                self.assertEqual(packet.pop("SKILL.md"),
                                 protocol["instructions_sha256"][run["arm"]])
                packets.append(packet)
                commands.append(timing["command"])
            self.assertEqual(prompts[0], prompts[1])
            self.assertEqual(packets[0], packets[1])
            self.assertEqual(commands[0], commands[1])

    def test_every_claim_failure_control_and_latency_stays_in_accounting(self):
        protocol, results = read("protocol.json"), read("results.json")
        self.assertEqual({r["id"] for r in results["runs"]}, set(protocol["order"]))
        for arm, summary in results["summary"].items():
            runs = [r for r in results["runs"] if r["arm"] == arm]
            self.assertEqual(len(runs), 6)
            self.assertEqual(summary["completed"], sum(r["complete"] for r in runs))
            self.assertEqual(summary["median_seconds"], statistics.median(
                r["elapsed_seconds"] for r in runs if r["complete"]))
            for key in ("unsupported_claims", "false_positive_claims"):
                self.assertEqual(summary[key], sum(r["counts"][key] for r in runs))
            self.assertEqual(summary["control_alarms"], sum(r["control_alarm"] for r in runs))
            self.assertEqual(summary["supported_contradictions"], sum(
                r["role"] == "defective" and r["detection"]["kind"] == "supported_contradiction"
                for r in runs))
            for run in runs:
                if not run["complete"]:
                    self.assertEqual(run["detection"]["kind"], "miss")
                    continue
                grade = read(run["grade"])
                self.assertEqual(run["counts"], grade["counts"])
                self.assertEqual(run["detection"], grade["detection"])
                folder = Path(run["grade"]).parent
                raw = read_events(str(folder / "stdout.jsonl"))
                events = read_events(str(folder / "events.jsonl"))
                self.assertEqual(raw, [e["event"] for e in events])
                self.assertEqual(raw[-1]["type"], "turn.completed")
                messages = [e["item"]["text"] for e in raw if e["type"] == "item.completed"
                            and e.get("item", {}).get("type") == "agent_message"]
                self.assertEqual((ROOT / run["grade"]).read_text(), messages[-1] + "\n")
                packet = read(str(Path(run["grade"]).parent / "packet.json"))
                expected = {"project/" + p: h for p, h in next(
                    c["files"] for c in protocol["cases"] if c["id"] == run["case"]).items()}
                self.assertEqual({k: v for k, v in packet.items() if k.startswith("project/")}, expected)
                self.assertEqual(set(packet) - set(expected), {"report.md", "oracle.json", "rubric.json"})
                self.assertEqual(packet["oracle.json"], sha(ROOT / f"curation/sealed/cases/{run['case']}.json"))
                self.assertEqual(packet["report.md"], sha(ROOT / f"audits/{run['id']}/response.md"))
                self.assertEqual(packet["rubric.json"], protocol["sealed_rubric_sha256"])
                claims = [c for f in grade["findings"] for c in f["claims"]
                          if c["classification"] != "duplicate"]
                self.assertEqual(grade["counts"], {
                    "findings": len(grade["findings"]), "claims": len(claims),
                    "unsupported_claims": sum(c["unsupported"] for c in claims),
                    "false_positive_claims": sum(c["classification"] == "false_positive" for c in claims)})


def read_events(name):
    return [json.loads(line) for line in (ROOT / name).read_text().splitlines()]


if __name__ == "__main__":
    unittest.main()
