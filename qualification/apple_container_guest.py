"""Fixed filesystem fixture; guest diagnostics are never authoritative receipts.

NOT RUN. Only execute in a separately approved, pinned Apple Container launch.
No imports, discovery, shell commands, downloads or target-project code.
"""

import json
from pathlib import Path
import sys


def main():
    action = sys.argv[1]
    targets = json.loads(Path("/inputs/targets.json").read_text())
    targets.update({
        "source-write": "/original/candidate.txt",
        "test-write": "/original/test_candidate.txt",
        "source-rename": "/original/candidate.txt",
        "symlink-write": "/inputs/source-link",
        "symlink-read": "/inputs/private-link",
        "hardlink-write": "/inputs/source-hardlink",
        "dotdot-write": "/inputs/../original/candidate.txt",
        "root-write": "/forbidden.txt",
    })
    print(json.dumps({"started": True, "action": action}), flush=True)
    try:
        if action == "positive":
            assert Path("/original/candidate.txt").read_bytes() == b"synthetic-source\n"
            assert Path("/inputs/test_candidate.txt").read_bytes() == b"synthetic-selected-test\n"
            Path("/scratch/output.txt").write_bytes(b"synthetic-approved-output\n")
            print(json.dumps({"effect": "allowed"}))
            return
        target = Path(targets[action])
        if action in ("private-read", "unrelated-read", "symlink-read"):
            target.read_bytes()  # Never print even synthetic private bytes.
        elif action == "source-rename":
            target.rename("/original/renamed.txt")
        else:
            target.write_bytes(b"synthetic-forbidden-write\n")
        print(json.dumps({"effect": "allowed"}))
    except OSError as error:
        print(json.dumps({"effect": "error", "errno": error.errno}))


if __name__ == "__main__":
    main()
