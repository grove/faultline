"""One-off paired source-only evaluation, reusing the PR #21 event collector."""

import importlib.util
import json
from pathlib import Path
import shutil
import sys


OUT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("collector", OUT.parent / "packaging-2x2/run.py")
collector = importlib.util.module_from_spec(spec)
spec.loader.exec_module(collector)
collector.OUT = OUT
collector.PROTOCOL = protocol = json.loads((OUT / "protocol.json").read_text())


def run(identity):
    entry = next(r for r in protocol["runs"] if r["id"] == identity)
    stage = Path(protocol["stage"]) / entry["case"]
    # Only this evaluator-owned disposable directory is replaced between sessions.
    if stage.exists():
        shutil.rmtree(stage)
    shutil.copytree(OUT / "curation/packets" / entry["case"], stage / "project")
    shutil.copyfile(OUT / "instructions" / (entry["arm"] + ".md"), stage / "SKILL.md")
    before = collector.inventory(stage)
    case = next(c for c in protocol["cases"] if c["id"] == entry["case"])
    assert {k.removeprefix("project/"): v for k, v in before.items()
            if k.startswith("project/")} == case["files"]
    assert before["SKILL.md"] == protocol["instructions_sha256"][entry["arm"]]
    prompt = ((OUT / "audit-prompt.txt").read_text()
              .replace("{scope}", case["scope"]).replace("{stage}", str(stage)))
    output = OUT / "audits" / identity
    error = None
    try:
        collector.observe(prompt, stage / "project", output)
    except RuntimeError as exc:
        error = str(exc)
    assert collector.inventory(stage) == before, "staged source changed"
    (output / "packet.json").write_text(json.dumps(before, indent=2) + "\n")
    if error:
        (output / "failure.txt").write_text(error + "\n")


if __name__ == "__main__":
    for identity in protocol["order"] if len(sys.argv) == 1 else sys.argv[1:]:
        run(identity)
