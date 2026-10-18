"""Maintainer-only synthetic observations, never a project runner or qualification grant."""

import errno
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import signal
import subprocess
import tempfile
import time


CHILD = r'''
import errno, json, os, socket, sys, time
from pathlib import Path
print(json.dumps({"started": True}), flush=True)
action, target = sys.argv[1:]
try:
    if action == "read":
        Path(target).read_bytes()
    elif action == "write":
        Path(target).write_text("changed\n")
    elif action == "network":
        with socket.socket() as connection:
            connection.settimeout(0.2)
            connection.connect(("192.0.2.1", 9))
    elif action == "timeout":
        time.sleep(10)
    print(json.dumps({"effect": "allowed"}))
except OSError as error:
    print(json.dumps({"effect": "error", "errno": error.errno}))
'''


def observe(argv, cwd, env, timeout=2):
    """Only fixed, bounded synthetic children; not safe for arbitrary test output."""
    started = time.monotonic()
    try:
        process = subprocess.Popen(argv, cwd=cwd, env=env, start_new_session=True,
                                   stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
    except OSError as error:
        return {"status": "UNAVAILABLE", "launch_errno": error.errno}
    timed_out = False
    try:
        stdout, stderr = process.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        timed_out = True
        stdout = stderr = b""
    finally:
        # Kill the created group even if its leader exited; never kill by name.
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    if timed_out:
        # A second finite wait prevents a descendant-held pipe from hanging us.
        try:
            stdout, stderr = process.communicate(timeout=1)
        except subprocess.TimeoutExpired:
            process.stdout.close()
            process.stderr.close()
    return {"status": "INCONCLUSIVE" if timed_out else "OBSERVED",
            "returncode": process.returncode, "timed_out": timed_out,
            "elapsed_seconds": round(time.monotonic() - started, 3),
            "stdout": stdout[:4096].decode(errors="replace"),
            "stderr": stderr[:4096].decode(errors="replace")}


def effect_status(result):
    if result["status"] != "OBSERVED":
        return result["status"]
    try:
        messages = [json.loads(line) for line in result["stdout"].splitlines()]
    except ValueError:
        return "UNAVAILABLE"
    if (result["returncode"] != 0 or len(messages) != 2
            or messages[0] != {"started": True}):
        return "UNAVAILABLE"
    effect = messages[1]
    if effect.get("effect") == "allowed":
        return "ALLOWED"
    if effect.get("errno") in (errno.EACCES, errno.EPERM):
        return "DENIED"
    return "INCONCLUSIVE"


def hashes(paths):
    return {name: hashlib.sha256(path.read_bytes()).hexdigest()
            for name, path in paths.items()}


def main():
    report = {"schema": 1, "decision": "UNAVAILABLE", "project_execution": "NOT_RUN",
              "observed_at_utc": datetime.now(timezone.utc).isoformat(),
              "coordinator_python": platform.python_version(),
              "host": {"system": platform.system(), "release": platform.release(),
                       "macos": platform.mac_ver()[0], "machine": platform.machine()},
              "probe_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "limits": {"per_probe_seconds": 2, "cleanup_wait_seconds": 1,
                         "total_seconds": 30, "retained_output_bytes_per_stream": 4096},
              "controls": [], "qualification_granted": False}
    if platform.system() != "Darwin":
        report["reason"] = "Only the macOS native sandbox-exec mechanism is considered."
        print(json.dumps(report, indent=2))
        return
    deadline = time.monotonic() + 30
    with tempfile.TemporaryDirectory(prefix="faultline-issue2-") as temporary:
        root = Path(temporary).resolve()
        for directory in ("original", "protected", "private", "baseline", "mutant"):
            (root / directory).mkdir()
        protected = {"candidate": root / "original/candidate.py",
                     "tests": root / "original/test_candidate.py",
                     "receipt": root / "protected/receipt.txt",
                     "private": root / "private/token.txt"}
        for name, path in protected.items():
            path.write_text("synthetic-" + name + "\n")
        for directory in ("baseline", "mutant"):
            for name in ("candidate", "tests"):
                (root / directory / protected[name].name).write_bytes(protected[name].read_bytes())
        (root / "mutant/source-alias").symlink_to(protected["candidate"])
        (root / "mutant/private-alias").symlink_to(protected["private"])
        (root / "mutant/receipt-hardlink").hardlink_to(protected["receipt"])
        profile = '''(version 1)
(deny default)
(allow process-exec)
(allow sysctl-read)
(allow file-read*
    (subpath "/System") (subpath "/usr")
    (subpath "/Library/Developer/CommandLineTools")
    (subpath "{root}/original")
    (subpath "{root}/baseline") (subpath "{root}/mutant"))
(allow file-write* (subpath "{root}/baseline") (subpath "{root}/mutant"))
'''.format(root=root)
        # This allowlist is a probe policy, not an approved project execution policy.
        report.update({"synthetic_root": str(root), "profile": profile,
                       "environment": {"PATH": "/usr/bin:/bin", "HOME": str(root / "mutant"),
                                       "TMPDIR": str(root / "mutant")},
                       "before": hashes(protected)})
        prefix = ["/usr/bin/sandbox-exec", "-p", profile,
                  "/usr/bin/python3", "-I", "-S", "-B", "-c", CHILD]
        report["argv_prefix"] = prefix
        controls = [
            ("positive-read", "read", protected["candidate"]),
            ("positive-write", "write", root / "mutant/output.txt"),
            ("source-write", "write", protected["candidate"]),
            ("test-write", "write", protected["tests"]),
            ("receipt-write", "write", protected["receipt"]),
            ("private-read", "read", protected["private"]),
            ("symlink-write", "write", root / "mutant/source-alias"),
            ("symlink-read", "read", root / "mutant/private-alias"),
            ("hardlink-write", "write", root / "mutant/receipt-hardlink"),
            ("dotdot-write", "write", root / "mutant/../original/candidate.py"),
            ("outbound-tcp", "network", "192.0.2.1:9"),
            ("timeout", "timeout", "unused"),
        ]
        for name, action, target in controls:
            suffix = [action, str(target)]
            if time.monotonic() >= deadline:
                result = {"status": "UNAVAILABLE", "reason": "Total budget exhausted."}
            else:
                result = observe(prefix + suffix, root / "mutant", report["environment"],
                                 timeout=min(2, deadline - time.monotonic()))
            result["effect_status"] = effect_status(result)
            result.update({"name": name, "argv_suffix": suffix, "after": hashes(protected)})
            result["protected_unchanged"] = result["after"] == report["before"]
            report["controls"].append(result)
            if not result["protected_unchanged"]:
                break
        report["after"] = hashes(protected)
        report["reason"] = (
            "No execution grant: require positive controls, observed denials, immutable "
            "originals, network telemetry and host-owned descendant/resource containment. "
            "This probe does not establish all of these; see ISOLATION.md."
        )
    report["synthetic_root_removed"] = not root.exists()
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
