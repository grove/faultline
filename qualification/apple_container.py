"""Prepare/observe synthetic fixtures. Deliberately contains no runtime launcher."""

import argparse
from datetime import datetime, timezone
import hashlib
from itertools import islice
import json
import os
from pathlib import Path
import platform
import shutil
import stat
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SOURCES = (
    "qualification/apple_container.py", "qualification/apple_container_guest.py",
    "qualification/APPLE_CONTAINER.md", "qualification/macos_canaries.py",
    "qualification/2026-10-18-macos.json",
    "qualification/2026-10-18-apple-container-preflight.json",
    "faultline-audit/SKILL.md", "experiments/lost-acknowledgement.md",
)
CONTROLS = (
    "positive", "source-write", "test-write", "source-rename", "receipt-write",
    "private-read", "unrelated-read", "symlink-write", "symlink-read",
    "hardlink-write", "dotdot-write", "root-write",
    "external-tcp4", "external-udp4", "external-tcp6", "external-udp6",
    "dns-udp", "dns-tcp", "host-tcp4", "host-udp4", "host-tcp6", "host-udp6",
    "host-unix-socket", "memory", "cpu", "process-count", "output", "storage", "timeout",
    "detached-descendants", "normal-cleanup", "timeout-cleanup", "interrupt-cleanup",
)


def digest(path):
    value = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(65536), b""):
            value.update(chunk)
    return value.hexdigest()


def manifest(path):
    """Record directory identities without following links or opening special files."""
    result = {}

    def visit(item, name):
        if len(result) >= 64 or name.count("/") > 8:
            raise ValueError("Protected fixture exceeds manifest budget")
        info = item.lstat()
        entry = {"mode": stat.S_IMODE(info.st_mode), "device": info.st_dev,
                 "inode": info.st_ino, "links": info.st_nlink}
        if stat.S_ISLNK(info.st_mode):
            entry.update(kind="symlink", target=os.readlink(item))
        elif stat.S_ISREG(info.st_mode):
            if info.st_size > 1048576:
                raise ValueError("Protected fixture exceeds one MiB")
            entry.update(kind="file", bytes=info.st_size, sha256=digest(item))
        elif stat.S_ISDIR(info.st_mode):
            entry["kind"] = "directory"
            result[name] = entry
            children = list(islice(item.iterdir(), 65))
            if len(children) > 64:
                raise ValueError("Protected fixture exceeds manifest budget")
            for child in sorted(children):
                visit(child, name + "/" + child.name)
        else:
            raise ValueError("Special file in protected fixture: " + name)
        result[name] = entry

    visit(path, ".")
    return result


def write_new(path, value):
    # Exclusive creation preserves earlier receipts; never replace evidence.
    with path.open("x", encoding="utf-8") as output:
        json.dump(value, output, indent=2, sort_keys=True)
        output.write("\n")


def inspect_host():
    """Request client help/version only; never request daemon startup or downloads."""
    cli = shutil.which("container")
    if cli is None:
        cli = next((p for p in ("/usr/local/bin/container", "/opt/homebrew/bin/container")
                    if Path(p).is_file()), None)
    report = {"observed_at_utc": datetime.now(timezone.utc).isoformat(),
              "kind": "CLIENT_INSPECTION_ONLY", "schema": 1,
              "invocation": sys.orig_argv, "cwd": os.getcwd(),
              "source_sha256": {name: digest(ROOT / name) for name in SOURCES},
              "host": {"system": platform.system(), "release": platform.release(),
                       "macos": platform.mac_ver()[0], "machine": platform.machine()},
              "python": sys.version, "cli": cli, "observations": [],
              "decision": "UNAVAILABLE", "qualification_granted": False,
              "boundary_launches": 0, "controls": [
                  {"name": name, "status": "NOT_RUN"} for name in CONTROLS]}
    commands = [["/usr/bin/sw_vers"]] if platform.system() == "Darwin" else []
    if cli:
        report["cli_sha256"] = digest(Path(cli))
        commands += [[cli, "--version"], [cli, "run", "--help"],
                     [cli, "inspect", "--help"], [cli, "stop", "--help"],
                     [cli, "delete", "--help"], [cli, "image", "inspect", "--help"]]
    for argv in commands:
        try:
            result = subprocess.run(argv, cwd="/", env={"PATH": "/usr/bin:/bin", "LC_ALL": "C"},
                                    stdin=subprocess.DEVNULL, capture_output=True, timeout=5)
            report["observations"].append({"argv": argv, "cwd": "/",
                "environment": {"PATH": "/usr/bin:/bin", "LC_ALL": "C"},
                "returncode": result.returncode,
                "stdout": result.stdout[:65536].decode(errors="replace"),
                "stderr": result.stderr[:65536].decode(errors="replace"),
                "truncated": max(len(result.stdout), len(result.stderr)) > 65536})
        except (OSError, subprocess.TimeoutExpired) as error:
            report["observations"].append({"argv": argv, "error": type(error).__name__})
    report["reason"] = "Client inspection only; version-matched review and runtime controls pending."
    return report


def prepare(directory):
    # Resolve the parent once; the leaf must be new and cannot be a supplied symlink.
    directory = directory.parent.resolve(strict=True) / directory.name
    directory.mkdir(mode=0o700)
    for name in ("original", "protected", "private", "unrelated", "inputs", "evidence"):
        (directory / name).mkdir()
    for name, content in {
        "original/candidate.txt": "synthetic-source\n",
        "original/test_candidate.txt": "synthetic-selected-test\n",
        "original/.git": "synthetic git identity only\n",
        "protected/receipt.txt": "synthetic-protected-receipt\n",
        "private/token.txt": "synthetic-private-token\n",
        "unrelated/token.txt": "synthetic-unrelated-token\n",
    }.items():
        (directory / name).write_text(content, encoding="utf-8")
    inputs = directory / "inputs"
    for name in ("candidate.txt", "test_candidate.txt"):
        shutil.copyfile(directory / "original" / name, inputs / name)
    (inputs / "source-link").symlink_to("/original/candidate.txt")
    (inputs / "private-link").symlink_to(str(directory / "private/token.txt"))
    (inputs / "source-hardlink").hardlink_to(directory / "original/candidate.txt")
    shutil.copyfile(ROOT / "qualification/apple_container_guest.py", inputs / "guest.py")
    # Only synthetic absolute host paths are disclosed, never the actual home or secrets.
    (inputs / "targets.json").write_text(json.dumps({
        "private-read": str(directory / "private/token.txt"),
        "unrelated-read": str(directory / "unrelated/token.txt"),
        "receipt-write": str(directory / "protected/receipt.txt"),
    }, sort_keys=True) + "\n", encoding="utf-8")
    report = {"schema": 1, "kind": "PREPARED_NOT_EXECUTED", "directory": str(directory),
              "observed_at_utc": datetime.now(timezone.utc).isoformat(),
              "source_sha256": {name: digest(ROOT / name) for name in SOURCES},
              "before": {name: manifest(directory / name) for name in
                         ("original", "protected", "private", "unrelated", "inputs")},
              "controls": [{"name": name, "status": "NOT_RUN"} for name in CONTROLS],
              "decision": "UNAVAILABLE", "qualification_granted": False,
              "blockers": ["Installed version/help and matching documentation not reviewed.",
                           "No independently observed network denial or resource/lifetime containment."]}
    write_new(directory / "evidence/prepared.json", report)
    return directory


def verify(directory, control, expected_prepared_sha256):
    """Host observation only; unchanged state is never classified as a denial."""
    directory = directory.resolve(strict=True)
    evidence = directory / "evidence"
    prepared = evidence / "prepared.json"
    if prepared.is_symlink() or digest(prepared) != expected_prepared_sha256:
        raise ValueError("Trusted prepared receipt identity changed; stop")
    before = json.loads(prepared.read_text(encoding="utf-8"))
    after = {name: manifest(directory / name) for name in before["before"]}
    source_after = {name: digest(ROOT / name) for name in SOURCES}
    unchanged = after == before["before"] and source_after == before["source_sha256"]
    result = {"control": control, "observed_at_utc": datetime.now(timezone.utc).isoformat(),
              "prepared_sha256": digest(prepared), "after": after,
              "source_sha256": source_after, "protected_unchanged": unchanged,
              "decision": "UNAVAILABLE" if unchanged else "NO_GO",
              "qualification_granted": False,
              "reason": "Host manifest comparison only; no independent denial/cleanup telemetry."}
    write_new(evidence / (control + ".json"), result)
    return unchanged


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    sub.add_parser("inspect")
    sub.add_parser("prepare").add_argument("directory", type=Path)
    check = sub.add_parser("verify")
    check.add_argument("directory", type=Path)
    check.add_argument("control", choices=CONTROLS)
    check.add_argument("--expected-prepared-sha256", required=True)
    args = parser.parse_args()
    if args.action == "inspect":
        print(json.dumps(inspect_host(), indent=2))
    elif args.action == "prepare":
        print(prepare(args.directory))
    else:
        return 0 if verify(args.directory, args.control, args.expected_prepared_sha256) else 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
