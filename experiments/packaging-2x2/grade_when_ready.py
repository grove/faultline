"""Grade each completed packet once, while the remaining audits continue."""

import time
import run


for identity in run.PROTOCOL["order"]:
    cell = next(c for c in run.PROTOCOL["cells"] if c["id"] == identity)
    deadline = time.monotonic() + 2400
    while not (run.OUT / "audits" / identity / "packet.json").exists():
        if time.monotonic() > deadline:
            raise TimeoutError("Audit packet not ready; no retry")
        time.sleep(1)
    run.run_grade(cell)
