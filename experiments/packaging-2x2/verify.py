"""Verify archived evaluation evidence without rerunning models or target code."""

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def digest(data):
    return hashlib.sha256(data).hexdigest()


def check():
    protocol = json.loads((ROOT / "protocol.json").read_text())
    results = json.loads((ROOT / "results.json").read_text())["cells"]
    source = json.loads((ROOT / "source-manifest.json").read_text())["files"]
    assert len(source) == 43
    for file, key in [("run.py", "collector_sha256"),
                      ("grading-rubric.md", "grading_rubric_sha256"),
                      ("audit-prompt.txt", "audit_prompt_sha256"),
                      ("grade-prompt.txt", "grade_prompt_sha256")]:
        assert digest((ROOT / file).read_bytes()) == protocol[key], file
    for cell in protocol["cells"]:
        for role in ("audits", "grades"):
            folder = ROOT / role / cell["id"]
            raw = [json.loads(line) for line in (folder / "stdout.jsonl").read_text().splitlines()]
            events = [json.loads(line) for line in (folder / "events.jsonl").read_text().splitlines()]
            assert raw == [e["event"] for e in events]
            assert events[-1]["event"]["type"] == "turn.completed"
            assert [e["received_seconds"] for e in events] == sorted(e["received_seconds"] for e in events)
            messages = [e["item"]["text"] for e in raw if e["type"] == "item.completed"
                        and e.get("item", {}).get("type") == "agent_message"]
            assert (folder / "response.md").read_text() == messages[-1] + "\n"
            timing = json.loads((folder / "timing.json").read_text())
            assert timing["complete_response_captured"] and timing["returncode"] == 0
            prompt = (folder / "prompt.txt").read_bytes()
            assert digest(prompt) == protocol["audit_prompt_sha256" if role == "audits" else "grade_prompt_sha256"]
            packet = json.loads((folder / "packet.json").read_text())
            staged = {k.removeprefix("project/"): v for k, v in packet.items()
                      if k.startswith("project/") and k != "project/docs/pep-0440.rst"}
            assert staged == source
            spec = packet.get("project/docs/pep-0440.rst")
            assert spec == (protocol["specification_sha256"] if cell["specification"] == "present" else None)
            if role == "audits":
                assert packet["SKILL.md"] == protocol["instructions_sha256"][cell["instructions"]]
            else:
                assert not any("SKILL" in name or "protocol" in name for name in packet)
                assert packet["report.md"] == digest((ROOT / "audits" / cell["id"] / "response.md").read_bytes())
                assert packet["rubric.md"] == protocol["grading_rubric_sha256"]
                grade = json.loads((folder / "response.md").read_text())
                result = next(r for r in results if r["id"] == cell["id"])
                assert result["grade_sha256"] == digest((folder / "response.md").read_bytes())
                assert result["counts"] == grade["counts"]
                assert result["detection"] == grade["detection"]
                claims = [c for f in grade["findings"] for c in f["claims"]]
                assert grade["counts"] == {"findings": len(grade["findings"]), "claims": len(claims),
                                           "unsupported_claims": sum(c["unsupported"] for c in claims),
                                           "false_positive_claims": sum(c["classification"] == "false_positive" for c in claims)}
                for finding in grade["findings"]:
                    classes = {c["classification"] for c in finding["claims"]}
                    expected = next(c for c in ("false_positive", "unresolved", "accepted_gap", "duplicate", "out_of_scope") if c in classes)
                    assert finding["classification"] == expected
    visibility = json.loads((ROOT / "read-visibility.json").read_text())
    for identity, probes in visibility["cells"].items():
        events = [json.loads(line)["event"] for line in
                  (ROOT / "audits" / identity / "events.jsonl").read_text().splitlines()]
        outputs = {e["item"]["id"]: e["item"].get("aggregated_output", "") for e in events
                   if e["type"] == "item.completed" and e.get("item", {}).get("type") == "command_execution"}
        for name, bindings in probes.items():
            assert bool(bindings) == (name != "normative_rule" or identity in ("B", "D"))
            for binding in bindings:
                output = outputs[binding["item_id"]]
                assert visibility["probes"][name] in output
                assert digest(output.encode()) == binding["output_sha256"]
    manifest = ROOT / "artifact-manifest.json"
    if manifest.exists():
        for name, expected in json.loads(manifest.read_text()).items():
            assert digest((ROOT / name).read_bytes()) == expected, name
    print("PASS: four audits and four independent grades; frozen inputs, raw traces, packet identities and grade accounting")


if __name__ == "__main__":
    check()
