"""Single approved service-setup attempt; never launches a VM or workload."""

import hashlib
import json
import os
from pathlib import Path
import subprocess
import time
import tomllib


HERE = Path(__file__).resolve().parent
BUNDLE = Path("/private/tmp/faultline-apple-positive-v2")
SETUP = BUNDLE / "setup-v1"
CLI = "/usr/local/bin/container"
PLUGIN_ROOT = Path("/usr/local/libexec/container/plugins")
CUSTOM_PLUGINS = Path("/usr/local/libexec/container-plugins")
PLUGIN_CONFIGS = {
    "container-core-images": "89ebf5415177298d36f4c67c8c03db26fac1377b428f30a5ccf96407d8f63f9d",
    "container-network-vmnet": "7ec0d522dcf9c9bc78b1e0843916bd0a98cfec45ef5b35f04fb8407ecda3db3e",
    "container-runtime-linux": "d609af652f3e0224cb7f0cef315f873081506d010d2d1a8ff33508980e3427a7",
    "k8s": "4b190947dd6fdadb9463b0210d19c25b1d086ddff00a0685027d29e99facab95",
    "machine-apiserver": "819edb0d3c20517e8a56e11a9623b3804c6821d3920da3fa66d989f766103b6a",
}
INIT = "ghcr.io/apple/containerization/vminit@sha256:c5c20071df2a9f249f82c9c2940539bd568360540559921a29f9f8b78df67ade"
ENV = {"HOME": "/Users/grove", "PATH": "/usr/bin:/bin", "LC_ALL": "C",
       "XDG_CONFIG_HOME": str(SETUP / "config-home"),
       "CONTAINER_APP_ROOT": str(SETUP / "runtime"),
       "CONTAINER_INSTALL_ROOT": "/usr/local"}
START = [CLI, "system", "start", "--app-root", ENV["CONTAINER_APP_ROOT"],
         "--install-root", "/usr/local", "--disable-kernel-install", "--timeout", "15"]
STOP = [CLI, "system", "stop", "--prefix", "com.apple.container."]


def setup():
    started = time.monotonic()
    config_bytes = (HERE / "apple-container-service.toml").read_bytes()
    report = {"kind": "SERVICE_SETUP_ONLY", "boundary_launches_requested": 0,
              "qualification_granted": False, "cwd": "/", "environment": ENV,
              "source_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                                for p in (Path(__file__), HERE / "apple-container-service.toml")},
              "observations": [], "result": "FAILED", "startup_attempted": False}
    with (BUNDLE / "evidence/setup-v1.json").open("x", encoding="utf-8") as evidence:
        def run(argv, timeout, labels_only=False):
            entry = {"argv": argv, "timeout_seconds": timeout}
            report["observations"].append(entry)
            try:
                # shortcut: capture assumes finite trusted CLI metadata; stream before accepting untrusted output.
                result = subprocess.run(argv, cwd="/", env=ENV, stdin=subprocess.DEVNULL,
                                        capture_output=True, timeout=timeout)
            except subprocess.TimeoutExpired as error:
                entry.update(timed_out=True,
                             stdout=(error.stdout or b"")[:65536].decode("utf-8", "replace"),
                             stderr=(error.stderr or b"")[:65536].decode("utf-8", "replace"))
                raise
            text = result.stdout.decode("utf-8", "replace")
            if labels_only:
                text = "\n".join(line for line in text.splitlines()
                                 if len(line.split()) == 3 and line.split()[2].startswith("com.apple.container."))
            entry.update(returncode=result.returncode, stdout=text[:65536],
                         stderr=result.stderr[:65536].decode("utf-8", "replace"))
            if result.returncode or len(text.encode()) > 65536 or len(result.stderr) > 65536:
                raise ValueError("Setup command failed or exceeded retention bound")
            return text

        try:
            if tomllib.loads(config_bytes.decode())["vminit"]["image"] != INIT:
                raise ValueError("Init configuration pin changed")
            if CUSTOM_PLUGINS.is_symlink() or (CUSTOM_PLUGINS.exists() and any(CUSTOM_PLUGINS.iterdir())):
                raise ValueError("Unreviewed custom plugins; stop before service contact")
            if {p.name for p in PLUGIN_ROOT.iterdir()} != set(PLUGIN_CONFIGS):
                raise ValueError("Installed plugin inventory changed")
            for name, expected in PLUGIN_CONFIGS.items():
                if hashlib.sha256((PLUGIN_ROOT / name / "config.toml").read_bytes()).hexdigest() != expected:
                    raise ValueError("Installed plugin configuration changed: " + name)
            report["plugin_config_sha256"] = PLUGIN_CONFIGS
            if run(["/bin/launchctl", "managername"], 5).strip() != "Aqua":
                raise ValueError("Use the approved normal Terminal session; no domain fallback")
            if run(["/bin/launchctl", "list"], 5, labels_only=True).strip():
                raise ValueError("Existing Container services; do not register or stop them")
            SETUP.mkdir(mode=0o700)
            config = SETUP / "config-home/container"
            config.mkdir(parents=True)
            (config / "config.toml").write_bytes(config_bytes)
            report["startup_attempted"] = True
            run(START, 120)
            status = json.loads(run([CLI, "system", "status", "--format", "json"], 15))
            if status.get("status") != "running" or status["paths"]["appRoot"] != ENV["CONTAINER_APP_ROOT"]:
                raise ValueError("Unexpected post-start service state/root")
            if (status["paths"]["installRoot"] != "/usr/local" or
                    status["server"]["version"] != "1.5.0" or
                    not status["server"]["commit"].startswith("d265d66")):
                raise ValueError("Service installation/source identity differs")
            copied = SETUP / "runtime/config/config.toml"
            if copied.read_bytes() != (config / "config.toml").read_bytes():
                raise ValueError("Effective startup configuration differs")
            if not json.loads(run([CLI, "image", "inspect", INIT], 15)):
                raise ValueError("Init metadata missing after startup")
            run(["/bin/launchctl", "list"], 5, labels_only=True)
            report["result"] = "SERVICES_STARTED_INIT_METADATA_PRESENT"
        except (Exception, KeyboardInterrupt) as error:
            report["error"] = type(error).__name__ + ": " + str(error)
            if report["startup_attempted"]:
                try:
                    run(STOP, 35)
                    remaining = run(["/bin/launchctl", "list"], 5, labels_only=True)
                    report["recovery"] = "NO_CONTAINER_LABELS" if not remaining.strip() else "INCOMPLETE_STOP_AND_REVIEW"
                except (Exception, KeyboardInterrupt) as recovery_error:
                    report["recovery"] = "INCOMPLETE_STOP_AND_REVIEW: " + str(recovery_error)
        finally:
            report["elapsed_seconds"] = time.monotonic() - started
            json.dump(report, evidence, indent=2, sort_keys=True)
            evidence.write("\n")
    return 0 if report["result"] == "SERVICES_STARTED_INIT_METADATA_PRESENT" else 1


if __name__ == "__main__":
    raise SystemExit(setup())
