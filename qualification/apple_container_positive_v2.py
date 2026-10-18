"""Frozen positive-only guest fixture. Run only with separate VM authorization."""

import os
from pathlib import Path
import signal
import sys


def main():
    if sys.argv[1:] != ["positive-v2"]:
        raise ValueError("Only the frozen positive-v2 operation is supported")
    signal.alarm(8)
    if Path("/original/candidate.txt").read_bytes() != b"synthetic-source\n":
        raise ValueError("Synthetic source changed")
    if Path("/inputs/test_candidate.txt").read_bytes() != b"synthetic-selected-test\n":
        raise ValueError("Synthetic test input changed")
    with Path("/scratch/output.txt").open("xb") as output:
        output.write(b"synthetic-approved-output\n")
        output.flush()
        os.fsync(output.fileno())
    # Keep tmpfs alive until the host has copied and verified the marker.
    if sys.stdin.buffer.readline(64) != b"faultline-positive-v2-ok\n":
        raise ValueError("Missing host acknowledgement")
    signal.alarm(0)


if __name__ == "__main__":
    main()
