"""One-off read-only model evaluation; never imports or executes staged source."""

import hashlib
import json
import os
from pathlib import Path
import selectors
import shutil
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone


OUT = Path(__file__).resolve().parent
BASE = OUT.parents[2]
STAGE = BASE / "stage"
PROTOCOL = json.loads((OUT / "protocol.json").read_text())


def digest(data):
    return hashlib.sha256(data).hexdigest()


def inventory(folder):
    return {str(p.relative_to(folder)): digest(p.read_bytes())
            for p in sorted(folder.rglob("*")) if p.is_file()}


def observe(prompt, cwd, output):
    output.mkdir(parents=True, exist_ok=False)
    (output / "prompt.txt").write_text(prompt)
    command = ["/opt/homebrew/bin/codex", "exec", "--ignore-user-config",
               "--ephemeral", "--json", "--sandbox", "read-only",
               "--skip-git-repo-check", "--color", "never", "-C", str(cwd),
               "-m", PROTOCOL["model"], "-c", 'model_reasoning_effort="xhigh"',
               "-c", 'approval_policy="never"', "-c", 'web_search="disabled"',
               "-c", "features.multi_agent=false", "-"]
    terminal = None
    last_message = None
    buffer = b""
    events = 0
    start_utc = datetime.now(timezone.utc).isoformat()
    start = time.monotonic_ns()
    with (output / "stderr.txt").open("wb") as err, \
            (output / "stdout.jsonl").open("wb") as raw, \
            (output / "events.jsonl").open("w") as ledger:
        process = subprocess.Popen(command, stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE, stderr=err,
                                   start_new_session=True)
        process.stdin.write(prompt.encode())
        process.stdin.close()
        selector = selectors.DefaultSelector()
        selector.register(process.stdout, selectors.EVENT_READ)
        while terminal is None:
            remaining = PROTOCOL["timeout_seconds"] - (time.monotonic_ns() - start) / 1e9
            if remaining <= 0:
                terminal = "timeout"
                break
            if not selector.select(min(remaining, 0.1)):
                continue
            chunk = os.read(process.stdout.fileno(), 65536)
            if not chunk:
                terminal = "stream_closed_without_completion"
                break
            raw.write(chunk)
            raw.flush()
            buffer += chunk
            while b"\n" in buffer:
                line, buffer = buffer.split(b"\n", 1)
                if not line.strip():
                    continue
                received = time.monotonic_ns()
                event = json.loads(line)
                ledger.write(json.dumps({"received_seconds": (received - start) / 1e9,
                                         "event": event}) + "\n")
                ledger.flush()
                events += 1
                if event.get("type") == "item.completed" and event.get("item", {}).get("type") == "agent_message":
                    last_message = event["item"]["text"]
                if event.get("type") in ("turn.completed", "turn.failed"):
                    terminal = event["type"]
                    break
        end = time.monotonic_ns()
        selector.close()
        if terminal != "turn.completed" and process.poll() is None:
            os.killpg(process.pid, signal.SIGTERM)
        try:
            code = process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            code = process.wait()
    if last_message is not None:
        (output / "response.md").write_text(last_message + "\n")
    record = {"start_utc": start_utc, "terminal": terminal,
              "elapsed_seconds": (end - start) / 1e9, "returncode": code,
              "complete_response_captured": terminal == "turn.completed" and last_message is not None,
              "event_count": events, "command": command,
              "prompt_sha256": digest(prompt.encode()),
              "timing": "monotonic before Popen through terminal-event handling; descriptive only"}
    (output / "timing.json").write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps({"run": str(output.relative_to(OUT)), **record}), flush=True)
    if not record["complete_response_captured"] or code != 0:
        raise RuntimeError("Incomplete evaluation retained; no automatic retry")


def run_audit(cell):
    instructions = (OUT / "instructions" / (cell["instructions"] + ".md")).read_bytes()
    (STAGE / "SKILL.md").write_bytes(instructions)
    spec = STAGE / "project/docs/pep-0440.rst"
    if cell["specification"] == "present":
        spec.write_bytes((OUT / "specification/pep-0440.rst").read_bytes())
    else:
        spec.unlink(missing_ok=True)
    before = inventory(STAGE)
    expected = json.loads((OUT / "source-manifest.json").read_text())["files"]
    actual = {k.removeprefix("project/"): v for k, v in before.items()
              if k.startswith("project/") and k != "project/docs/pep-0440.rst"}
    assert actual == expected
    assert before["SKILL.md"] == PROTOCOL["instructions_sha256"][cell["instructions"]]
    prompt = (OUT / "audit-prompt.txt").read_text()
    assert digest(prompt.encode()) == PROTOCOL["audit_prompt_sha256"]
    output = OUT / "audits" / cell["id"]
    observe(prompt, STAGE / "project", output)
    after = inventory(STAGE)
    assert before == after, "staged input changed"
    (output / "packet.json").write_text(json.dumps(before, indent=2) + "\n")


def run_grade(cell):
    folder = BASE / "grading"
    if folder.exists():
        shutil.rmtree(folder)
    shutil.copytree(STAGE / "project", folder / "project")
    spec = folder / "project/docs/pep-0440.rst"
    if cell["specification"] == "present":
        spec.write_bytes((OUT / "specification/pep-0440.rst").read_bytes())
    else:
        spec.unlink(missing_ok=True)
    (folder / "report.md").write_bytes((OUT / "audits" / cell["id"] / "response.md").read_bytes())
    (folder / "rubric.md").write_bytes((OUT / "grading-rubric.md").read_bytes())
    prompt = (OUT / "grade-prompt.txt").read_text()
    before = inventory(folder)
    output = OUT / "grades" / cell["id"]
    observe(prompt, folder, output)
    assert inventory(folder) == before
    (output / "packet.json").write_text(json.dumps(before, indent=2) + "\n")


if __name__ == "__main__":
    assert sys.argv[1] in ("audit", "grade")
    assert digest((OUT / "grading-rubric.md").read_bytes()) == PROTOCOL["grading_rubric_sha256"]
    for identity in PROTOCOL["order"]:
        cell = next(c for c in PROTOCOL["cells"] if c["id"] == identity)
        (run_audit if sys.argv[1] == "audit" else run_grade)(cell)
