"""One-off blinded grades; uses the same collector and never executes targets."""

import importlib.util
import json
from pathlib import Path
import shutil
import sys

OUT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("trial", OUT / "run.py")
trial = importlib.util.module_from_spec(spec)
spec.loader.exec_module(trial)
collector, protocol = trial.collector, trial.protocol


plan = json.loads((OUT / "grading-plan.json").read_text())


def grade(identity):
    entry = next(r for r in plan["runs"] if r["id"] == identity)
    audit = next(r for r in protocol["runs"] if r["id"] == entry["audit"])
    stage = Path("/private/tmp/faultline-counterexample-grading") / identity
    stage.mkdir(parents=True, exist_ok=False)
    shutil.copytree(OUT / "curation/packets" / audit["case"], stage / "project")
    shutil.copyfile(OUT / "audits" / entry["audit"] / "response.md", stage / "report.md")
    shutil.copyfile(OUT / "curation/sealed/cases" / (audit["case"] + ".json"), stage / "oracle.json")
    shutil.copyfile(OUT / "curation/sealed/grading-rubric.json", stage / "rubric.json")
    before = collector.inventory(stage)
    output = OUT / "grades" / identity
    try:
        collector.observe((OUT / "grade-prompt.txt").read_text(), stage, output)
    finally:
        assert collector.inventory(stage) == before, "grading packet changed"
        (output / "packet.json").write_text(json.dumps(before, indent=2) + "\n")


if __name__ == "__main__":
    for identity in sys.argv[1:]:
        grade(identity)
