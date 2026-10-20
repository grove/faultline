"""Check derived pilot accounting without executing any target project or audit."""

import importlib.util
import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
DIAGNOSTIC = ROOT / "experiments/audit-quality-diagnostics"
spec = importlib.util.spec_from_file_location("audit_latency", DIAGNOSTIC / "analyze_latency.py")
analysis = importlib.util.module_from_spec(spec)
spec.loader.exec_module(analysis)


def sample():
    return [
        {"type": "turn.started", "received_seconds": 1},
        {"type": "item.started", "item_type": "command_execution", "item_id": "a", "received_seconds": 2},
        {"type": "item.started", "item_type": "command_execution", "item_id": "b", "received_seconds": 3},
        {"type": "item.completed", "item_type": "command_execution", "item_id": "a", "received_seconds": 5,
         "command": "cat source", "output_bytes": 4},
        {"type": "item.completed", "item_type": "command_execution", "item_id": "b", "received_seconds": 7,
         "command": "cat source", "output_bytes": 4},
        {"type": "item.completed", "item_type": "agent_message", "received_seconds": 9},
        {"type": "turn.completed", "received_seconds": 10, "usage": {"input_tokens": 12}},
    ]


class AuditDiagnosticTests(unittest.TestCase):
    def test_overlapping_event_spans_and_full_response_endpoint(self):
        result = analysis.summarize(sample())
        self.assertEqual(result["observed_command_event_span_union_seconds"], 5)
        self.assertEqual(result["exact_repeat_commands"], 1)
        self.assertEqual(result["captured_output_bytes_with_repeats"], 8)
        self.assertEqual(result["usage_as_reported"], {"input_tokens": 12})
        self.assertEqual([result[key] for key in (
            "submission_to_turn_started_seconds", "turn_started_to_last_read_seconds",
            "last_read_to_full_final_message_seconds", "full_final_message_to_turn_completed_seconds")],
                         [1, 6, 2, 1])
        self.assertEqual(result["end_to_end_seconds"], 10)

    def test_incomplete_or_misordered_traces_do_not_become_latency_measurements(self):
        cases = [[], sample()[:-1], list(reversed(sample()))]
        bad_order = sample()
        message = {"type": "item.completed", "item_type": "agent_message", "received_seconds": 6}
        bad_order = bad_order[:4] + [message, bad_order[4], bad_order[-1]]
        cases.append(bad_order)
        for events in cases:
            with self.subTest(events=events), self.assertRaises(ValueError):
                analysis.summarize(events)

    def test_archived_derivation_reconciles_with_original_pilot(self):
        saved = json.loads((DIAGNOSTIC / "latency.json").read_text())
        self.assertEqual(analysis.derive(), saved)
        for run in saved["runs"]:
            original = json.loads((analysis.PILOT / f"timings/audit-{run['case']}.json").read_text())
            self.assertEqual(run["end_to_end_seconds"], original["elapsed_seconds"])
            total = sum(run[key] for key in (
                "submission_to_turn_started_seconds", "turn_started_to_last_read_seconds",
                "last_read_to_full_final_message_seconds", "full_final_message_to_turn_completed_seconds"))
            self.assertAlmostEqual(total, run["end_to_end_seconds"])
            self.assertEqual(run["read_commands"], original["read_command_count"])

    def test_evidence_bindings_and_execution_fences_remain_intact(self):
        saved = json.loads((DIAGNOSTIC / "preservation.json").read_text())
        skill = (ROOT / "faultline-audit/SKILL.md").read_bytes()
        sections = {"release_boundary": skill.split(b"**Release boundary: advice-only.**")[1].split(b"## Find weak tests")[0],
                    "verification_gate": skill.split(b"## Verify this finding?")[1]}
        for name, data in sections.items():
            self.assertEqual(hashlib.sha256(data).hexdigest(), saved["sections_sha256"][name])
        for name, key in (("REPORT.md", "pilot_report_sha256"),
                          ("artifact-manifest.json", "pilot_artifact_manifest_sha256")):
            self.assertEqual(hashlib.sha256((analysis.PILOT / name).read_bytes()).hexdigest(), saved[key])
        visibility = json.loads((DIAGNOSTIC / "visibility.json").read_text())
        events = [json.loads(line) for line in (analysis.PILOT / "events/audit-r1.jsonl").read_text().splitlines()]
        outputs = {event["item_id"]: event for event in events
                   if event["type"] == "item.completed" and event.get("item_type") == "command_execution"}
        for signal in visibility["r1_signals"]:
            self.assertEqual(signal["output_sha256"], outputs[signal["item_id"]]["output_sha256"])
            self.assertEqual(signal["received_seconds"], outputs[signal["item_id"]]["received_seconds"])
        for message in json.loads((DIAGNOSTIC / "commentary.json").read_text()):
            events = [json.loads(line) for line in
                      (analysis.PILOT / f"events/audit-{message['case']}.jsonl").read_text().splitlines()]
            event = next(event for event in events if event.get("item_id") == message["item_id"]
                         and event["type"] == "item.completed")
            self.assertEqual(hashlib.sha256(message["text"].encode()).hexdigest(), event["text_sha256"])
            self.assertEqual(message["received_seconds"], event["received_seconds"])


if __name__ == "__main__":
    unittest.main()
