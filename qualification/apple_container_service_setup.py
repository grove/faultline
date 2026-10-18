"""Single approved service-setup attempt; never launches a VM or workload."""

import hashlib
import json
import os
from pathlib import Path
import plistlib
import subprocess
import sys
import time
import tomllib


HERE = Path(__file__).resolve().parent
BUNDLE = Path("/private/tmp/faultline-apple-positive-v2")
ATTEMPT = "setup-v2"
SETUP = BUNDLE / ATTEMPT
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


def domain_names(text, domain):
    """Accept only the reviewed host's service/endpoint table shape; retain no environment."""
    lines = text.splitlines()
    if not lines or lines[0] != domain + " = {" or lines[-1] != "}":
        raise ValueError("Unrecognized launchd domain output")
    names = {}
    for section, columns in (("services", 3), ("endpoints", 4)):
        heading = "\t" + section + " = {"
        if lines.count(heading) != 1:
            raise ValueError("Missing or ambiguous launchd " + section + " table")
        start = lines.index(heading) + 1
        try:
            end = lines.index("\t}", start)
        except ValueError:
            raise ValueError("Unterminated launchd table") from None
        names[section] = []
        for row in lines[start:end]:
            fields = row.split(maxsplit=columns - 1)
            if not row.startswith("\t\t") or len(fields) != columns:
                raise ValueError("Unrecognized launchd table row")
            if fields[-1].startswith("com.apple.container."):
                names[section].append(fields[-1])
        if len(names[section]) > 16:
            raise ValueError("Container launchd inventory exceeds setup budget")
    return names


def owned_plist(text, target):
    lines = text.splitlines()
    paths = [line.removeprefix("\tpath = ") for line in lines if line.startswith("\tpath = ")]
    if not lines or lines[0] != target + " = {" or len(paths) != 1:
        raise ValueError("Cannot identify launchd service origin")
    path = Path(paths[0])
    if path.is_symlink() or not path.resolve(strict=True).is_relative_to(SETUP / "runtime"):
        raise ValueError("Service plist is outside this setup; leave it untouched")
    with path.open("rb") as source:
        data = source.read(65537)
    if len(data) > 65536:
        raise ValueError("Service plist exceeds setup budget")
    config = plistlib.loads(data)
    env = config.get("EnvironmentVariables", {})
    if (config.get("Label") != target.rsplit("/", 1)[1] or
            env.get("CONTAINER_APP_ROOT") != ENV["CONTAINER_APP_ROOT"] or
            env.get("CONTAINER_INSTALL_ROOT") != "/usr/local"):
        raise ValueError("Service ownership differs; leave it untouched")
    return {"path": str(path), "sha256": hashlib.sha256(data).hexdigest()}


def setup():
    started = time.monotonic()
    config_bytes = (HERE / "apple-container-service.toml").read_bytes()
    report = {"kind": "SERVICE_SETUP_ONLY", "boundary_launches_requested": 0,
              "qualification_granted": False, "cwd": "/", "environment": ENV,
              "source_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                                for p in (Path(__file__), HERE / "apple-container-service.toml")},
              "observations": [], "result": "FAILED", "startup_attempted": False}
    with (BUNDLE / ("evidence/" + ATTEMPT + ".json")).open("x", encoding="utf-8") as evidence:
        def run(argv, timeout, view=None):
            entry = {"argv": argv, "timeout_seconds": timeout}
            report["observations"].append(entry)
            try:
                # shortcut: capture assumes finite trusted CLI metadata; stream before accepting untrusted output.
                result = subprocess.run(argv, cwd="/", env=ENV, stdin=subprocess.DEVNULL,
                                        capture_output=True, timeout=timeout)
            except subprocess.TimeoutExpired as error:
                entry.update(timed_out=True,
                             stdout="NOT_RETAINED" if view else (error.stdout or b"")[:65536].decode("utf-8", "replace"),
                             stderr=(error.stderr or b"")[:65536].decode("utf-8", "replace"))
                raise
            text = result.stdout.decode("utf-8", "replace")
            entry.update(returncode=result.returncode, stdout="NOT_RETAINED" if view else text[:65536],
                         stderr=result.stderr[:65536].decode("utf-8", "replace"))
            if result.returncode or len(result.stdout) > (4194304 if view else 65536) or len(result.stderr) > 65536:
                raise ValueError("Setup command failed or exceeded retention bound")
            if view:
                value = domain_names(text, argv[2]) if view == "domain" else owned_plist(text, argv[2])
                entry["observed"] = value
                return value
            return text

        def inspect_domains():
            return {target: run(["/bin/launchctl", "print", target], 5, "domain") for target in domains}

        def owners(inventory):
            if any(rows["services"] for target, rows in inventory.items() if target != domain):
                raise ValueError("Container services appeared in another domain; no automatic recovery")
            return {label: run(["/bin/launchctl", "print", domain + "/" + label], 5, "service")
                    for label in inventory[domain]["services"]}

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
            manager = run(["/bin/launchctl", "managername"], 5).strip()
            if manager not in ("Aqua", "Background") or os.getuid() == 0:
                raise ValueError("Unsupported launchd session; no domain fallback")
            domains = ("system", f"user/{os.getuid()}", f"gui/{os.getuid()}")
            domain = domains[2] if manager == "Aqua" else domains[1]
            report.update(manager=manager, launchd_domain=domain)
            before = inspect_domains()
            if any(rows[section] for rows in before.values() for section in ("services", "endpoints")):
                raise ValueError("Existing Container services/endpoints; do not register or stop them")
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
            report["owned_services"] = owners(inspect_domains())
            if "com.apple.container.apiserver" not in report["owned_services"]:
                raise ValueError("Owned API service missing from selected domain")
            report["result"] = "SERVICES_STARTED_INIT_METADATA_PRESENT"
        except (Exception, KeyboardInterrupt) as error:
            report["error"] = type(error).__name__ + ": " + str(error)
            if report["startup_attempted"]:
                try:
                    plan = owners(inspect_domains())
                    report["recovery_plan"] = plan
                    for label, identity in plan.items():
                        target = domain + "/" + label
                        if run(["/bin/launchctl", "print", target], 5, "service") != identity:
                            raise ValueError("Service ownership changed; no bootout")
                        run(["/bin/launchctl", "bootout", target], 5)
                    remaining = inspect_domains()
                    report["recovery"] = "NO_CONTAINER_REGISTRATIONS_OBSERVED" if not any(
                        rows[section] for rows in remaining.values() for section in ("services", "endpoints")
                    ) else "INCOMPLETE_STOP_AND_REVIEW"
                except (Exception, KeyboardInterrupt) as recovery_error:
                    report["recovery"] = "INCOMPLETE_STOP_AND_REVIEW: " + str(recovery_error)
        finally:
            report["elapsed_seconds"] = time.monotonic() - started
            json.dump(report, evidence, indent=2, sort_keys=True)
            evidence.write("\n")
    return 0 if report["result"] == "SERVICES_STARTED_INIT_METADATA_PRESENT" else 1


if __name__ == "__main__":
    if sys.argv[1:] != [ATTEMPT]:
        raise SystemExit("New authorization required; exact argument: " + ATTEMPT)
    raise SystemExit(setup())
