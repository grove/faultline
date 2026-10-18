"""Positive-v2 preparation and separately authorized service inventory. No launcher."""

import argparse
from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("preparation", HERE / "apple_container.py")
preparation = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(preparation)
CLI = "/usr/local/bin/container"
ENV = {"HOME": "/Users/grove", "PATH": "/usr/bin:/bin", "LC_ALL": "C"}
APP_ROOT = Path("/Users/grove/Library/Application Support/com.apple.container")


def prepare(directory):
    directory = directory.parent.resolve(strict=True) / directory.name
    directory.mkdir(mode=0o700)
    for name in ("original", "inputs", "evidence"):
        (directory / name).mkdir()
    (directory / "original/candidate.txt").write_bytes(b"synthetic-source\n")
    (directory / "inputs/test_candidate.txt").write_bytes(b"synthetic-selected-test\n")
    shutil.copyfile(HERE / "apple_container_positive_v2.py", directory / "inputs/positive-v2.py")
    report = {
        "schema": 2, "kind": "POSITIVE_V2_PREPARED_NOT_EXECUTED",
        "observed_at_utc": datetime.now(timezone.utc).isoformat(),
        "directory": str(directory), "boundary_launches": 0,
        "qualification_granted": False,
        "previous_prepared_sha256": "3349e3c1e401afa9c32de55ecd385cd65afc46b01fcfbb7660d1c0f763f4426d",
        "source_sha256": {name: preparation.digest(HERE.parent / name) for name in (
            *preparation.SOURCES, "qualification/apple_container_smoke.py",
            "qualification/apple_container_positive_v2.py", "qualification/APPLE_CONTAINER_NEXT.md")},
        "before": {name: preparation.manifest(directory / name) for name in ("original", "inputs")},
        "positive": "NOT_RUN", "negative_controls": "NOT_RUN",
    }
    preparation.write_new(directory / "evidence/prepared-v2.json", report)
    return directory


def inventory(directory):
    """Contacts registered services; this action needs separate operator approval."""
    directory = directory.resolve(strict=True)
    destination = directory / "evidence/inventory.json"
    # Reserve before service contact; a repeat must never overwrite prior evidence.
    with destination.open("x", encoding="utf-8") as output:
        report = {"kind": "SERVICE_INVENTORY_ONLY", "boundary_launches": 0,
                  "observed_at_utc": datetime.now(timezone.utc).isoformat(),
                  "qualification_granted": False, "observations": [],
                  "cwd": "/", "environment": ENV, "kernel": "NOT_INSPECTED"}
        try:
            for args in (("system", "status", "--format", "json"),
                         ("image", "list", "--format", "json")):
                argv = [CLI, *args]
                # shortcut: trusted CLI capture has no live byte quota; stream before accepting untrusted output.
                result = subprocess.run(argv, cwd="/", env=ENV, stdin=subprocess.DEVNULL,
                                        capture_output=True, timeout=15)
                observation = {"argv": argv, "returncode": result.returncode,
                               "stdout": result.stdout[:65536].decode("utf-8", "replace"),
                               "stderr": result.stderr[:65536].decode("utf-8", "replace"),
                               "truncated": len(result.stdout) > 65536 or len(result.stderr) > 65536}
                report["observations"].append(observation)
                if result.returncode or observation["truncated"]:
                    raise ValueError("Service inventory failed or exceeded retention budget; stop")
                if args[0] == "system":
                    status = json.loads(result.stdout)
                    if status.get("status") != "running" or status["paths"]["appRoot"] != str(APP_ROOT):
                        raise ValueError("Unexpected service state/app root; stop without startup")
            kernel = APP_ROOT / "kernels/default.kernel-arm64"
            if not kernel.exists():
                report["kernel"] = "MISSING_AT_DEFAULT_PATH"
            else:
                resolved = kernel.resolve(strict=True)
                if resolved.parent != (APP_ROOT / "kernels").resolve(strict=True) or not resolved.is_file():
                    raise ValueError("Kernel points outside approved kernel store; stop")
                if resolved.stat().st_size > 128 * 1024 * 1024:
                    raise ValueError("Kernel exceeds 128 MiB inventory read budget; stop")
                report["kernel"] = {"path": str(resolved), "sha256": preparation.digest(resolved)}
        except (OSError, ValueError, KeyError, subprocess.TimeoutExpired) as error:
            report["error"] = type(error).__name__ + ": " + str(error)
            if isinstance(error, subprocess.TimeoutExpired):
                report["timeout_stdout"] = (error.stdout or b"")[:65536].decode("utf-8", "replace")
                report["timeout_stderr"] = (error.stderr or b"")[:65536].decode("utf-8", "replace")
        finally:
            json.dump(report, output, indent=2, sort_keys=True)
            output.write("\n")
    return "error" not in report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("prepare", "inventory"))
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    if args.action == "prepare":
        print(prepare(args.directory))
        return 0
    return 0 if inventory(args.directory) else 1


if __name__ == "__main__":
    raise SystemExit(main())
