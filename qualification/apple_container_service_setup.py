"""Single approved service-setup attempt; never launches a VM or workload."""

from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import plistlib
import re
import shutil
import stat
import subprocess
import sys
import time
import tomllib


HERE = Path(__file__).resolve().parent
BUNDLE = Path("/private/tmp/faultline-apple-positive-v2")
ATTEMPT = "setup-v4"
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
ENV = {"HOME": "/Users/grove", "PATH": "/usr/bin:/bin", "LC_ALL": "C", "TZ": "Europe/Oslo",
       "XDG_CONFIG_HOME": str(SETUP / "config-home"),
       "CONTAINER_APP_ROOT": str(SETUP / "runtime"),
       "CONTAINER_INSTALL_ROOT": "/usr/local"}
START = [CLI, "system", "start", "--app-root", ENV["CONTAINER_APP_ROOT"],
         "--install-root", "/usr/local", "--disable-kernel-install", "--timeout", "15"]
PULL = [CLI, "image", "pull", "--platform", "linux/arm64/v8", "--scheme", "https",
        "--progress", "plain", "--max-concurrent-downloads", "1", INIT]
SERVICE_PROGRAMS = {
    "com.apple.container.apiserver": "/usr/local/bin/container-apiserver",
    "com.apple.container.machine-apiserver": "/usr/local/libexec/container/plugins/machine-apiserver/bin/machine-apiserver",
    "com.apple.container.container-core-images": "/usr/local/libexec/container/plugins/container-core-images/bin/container-core-images",
    "com.apple.container.container-network-vmnet.default": "/usr/local/libexec/container/plugins/container-network-vmnet/bin/container-network-vmnet",
}

OBSERVER_SHA256 = "c86e1c77332d4d9bb8785c5136dedbf1d258a2aba0623a2d9d38e78c9317b6a0"
CONFIG_SHA256 = "ec039793064339b1c438630aaa4a81b03717d96a6ca6b7a19a945c6f85c0883e"
BINARY_SHA256 = {
    "/usr/local/bin/container-apiserver": "0d05388259e73b63f84680968fa5fa39feeef4219cce45c5655d29d3172a63b9",
    "/usr/local/libexec/container/plugins/machine-apiserver/bin/machine-apiserver": "1d3f53f6979d92d0bb9f343cc16782bad9a4b23bb380619f4b0d87d9d6df449c",
    "/usr/local/libexec/container/plugins/container-core-images/bin/container-core-images": "dc88d9aeb67f8258c3697f8485b6ee77018d63b86b6dc3ba9905fb88f01cb6eb",
    "/usr/local/libexec/container/plugins/container-network-vmnet/bin/container-network-vmnet": "bfb0c8b002946071df4428c5fa8e1d3bcb86d9798ae2e25dab1a1388e84c7270",
    "/usr/local/bin/container": "8cc619377e8978a0ce9f22a3e864dcd4445f2bc38fb64c5197bb69a1bab42463"
}
MACH = {
    "com.apple.container.apiserver": "com.apple.container.apiserver",
    "com.apple.container.machine-apiserver": "com.apple.container.core.machine-apiserver",
    "com.apple.container.container-core-images": "com.apple.container.core.container-core-images",
    "com.apple.container.container-network-vmnet.default": "com.apple.container.network.container-network-vmnet.default",
}


def same_path(left, right):
    try:
        return Path(left).is_absolute() and Path(right).is_absolute() and Path(left).samefile(right)
    except (OSError, TypeError, ValueError):
        return False


def storage(root):
    """Phase-boundary admission checks, not a live quota on launchd services."""
    def unreadable(error):
        raise error

    logical = allocated = count = 0
    for directory, dirs, files in os.walk(root, followlinks=False, onerror=unreadable):
        if len(Path(directory).relative_to(root).parts) > 16:
            raise ValueError("Setup storage nesting exceeds budget")
        for name in dirs + files:
            info = (Path(directory) / name).lstat()
            count += 1
            if count > 4096 or not (stat.S_ISREG(info.st_mode) or stat.S_ISDIR(info.st_mode)):
                raise ValueError("Unexpected file kind/count in setup storage")
            logical += info.st_size
            allocated += info.st_blocks * 512
            if max(logical, allocated) > 1024**3:
                raise ValueError("Setup exceeds one GiB storage admission budget")
    free = shutil.disk_usage(root).free
    if free < 2 * 1024**3:
        raise ValueError("Setup requires two GiB free space")
    return {"logical_bytes": logical, "allocated_bytes": allocated, "free_bytes": free}


def verify_init(root, reference=INIT):
    """Check pinned local OCI content and fresh snapshot without mounting or executing it."""
    checked = []

    def regular(path, limit):
        relative = path.relative_to(root)
        for parent in (relative, *relative.parents):
            if (root / parent).is_symlink():
                raise ValueError("Symlink in init storage")
        info = path.lstat()
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or not 0 < info.st_size <= limit:
            raise ValueError("Invalid init file kind, links or size: " + str(relative))
        return info

    def metadata(path):
        regular(path, 1048576)
        return json.loads(path.read_bytes())

    def blob(descriptor, limit):
        digest = descriptor["digest"]
        if not re.fullmatch(r"sha256:[0-9a-f]{64}", digest):
            raise ValueError("Invalid init content digest")
        path = root / "content/blobs/sha256" / digest[7:]
        info = regular(path, limit)
        if type(descriptor["size"]) is not int or descriptor["size"] != info.st_size:
            raise ValueError("Init blob size mismatch")
        with path.open("rb") as source:
            if hashlib.file_digest(source, "sha256").hexdigest() != digest[7:]:
                raise ValueError("Init blob digest mismatch")
        checked.append({"path": str(path), **descriptor})
        return path

    pin = reference.rsplit("@", 1)[1]
    state = metadata(root / "state.json")
    if set(state) != {reference}:
        raise ValueError("Unexpected image references in dedicated runtime")
    index = metadata(blob(state[reference], 1048576))
    if index["schemaVersion"] != 2 or len(index["manifests"]) != 1:
        raise ValueError("Expected one init platform descriptor")
    descriptor = index["manifests"][0]
    platform = descriptor["platform"]
    if (descriptor["digest"] != pin or platform["os"] != "linux" or platform["architecture"] != "arm64" or
            platform.get("variant", "v8") != "v8"):
        raise ValueError("Init platform/pinned manifest differs")
    manifest = metadata(blob(descriptor, 1048576))
    if manifest["schemaVersion"] != 2 or not 1 <= len(manifest["layers"]) <= 8:
        raise ValueError("Init manifest/layer count exceeds scope")
    config = metadata(blob(manifest["config"], 1048576))
    if config["os"] != "linux" or config["architecture"] != "arm64" or config.get("variant", "v8") != "v8":
        raise ValueError("Init configuration platform differs")
    if sum(d["size"] for d in manifest["layers"]) > 256 * 1024**2:
        raise ValueError("Init compressed layers exceed 256 MiB")
    for layer in manifest["layers"]:
        blob(layer, 256 * 1024**2)
    directory = root / "snapshots" / pin[7:]
    snapshot = directory / "snapshot"
    info = regular(snapshot, 640 * 1024**2)
    description = metadata(directory / "snapshot-info")
    if (description["type"]["block"]["format"] != "ext4" or description["destination"] != "/" or
            description["source"] != str(snapshot) or description["options"] != []):
        raise ValueError("Init snapshot metadata differs")
    for ingest in (root / "content/ingest", root / "snapshots/ingest"):
        if not ingest.is_dir() or any(ingest.iterdir()):
            raise ValueError("Incomplete init ingest remains")
    with snapshot.open("rb") as source:
        source.seek(1024)
        superblock = source.read(1024)
        log_block_size = int.from_bytes(superblock[24:28], "little")
        blocks = int.from_bytes(superblock[4:8], "little") + (int.from_bytes(superblock[336:340], "little") << 32)
        if (superblock[56:58] != b"\x53\xef" or log_block_size > 6 or
                not 512 * 1024**2 <= blocks * (1024 << log_block_size) <= info.st_size):
            raise ValueError("Init snapshot EXT4 geometry is invalid")
        source.seek(0)
        digest = hashlib.file_digest(source, "sha256").hexdigest()
    return {"reference": reference, "blobs": checked, "snapshot": {
        "path": str(snapshot), "bytes": info.st_size, "allocated_bytes": info.st_blocks * 512,
        "sha256": digest, "metadata": description,
        "check": "STRUCTURE_AND_UNPACK_EXIT_ONLY; NOT_FSCK_OR_GUEST_BOOT"}}


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
    programs = [line.removeprefix("\tprogram = ") for line in lines if line.startswith("\tprogram = ")]
    if not lines or lines[0] != target + " = {" or len(paths) != 1 or len(programs) != 1:
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
    label = target.rsplit("/", 1)[1]
    arguments = config.get("ProgramArguments", [])
    expected = SERVICE_PROGRAMS.get(label)
    if (config.get("Label") != label or config.get("Program") is not None or not arguments or
            not same_path(env.get("CONTAINER_APP_ROOT"), ENV["CONTAINER_APP_ROOT"]) or
            not same_path(env.get("CONTAINER_INSTALL_ROOT"), "/usr/local") or
            not same_path(arguments[0], expected) or not same_path(programs[0], expected)):
        raise ValueError("Service ownership differs; leave it untouched")
    return {"path": str(path.resolve(strict=True)), "sha256": hashlib.sha256(data).hexdigest(),
            "executable": str(Path(expected).resolve(strict=True))}


def setup():
    started = time.monotonic()
    config_bytes = (HERE / "apple-container-service.toml").read_bytes()
    report = {"kind": "SERVICE_SETUP_AND_PINNED_INIT_ONLY", "boundary_launches_requested": 0,
              "started_at_utc": datetime.now(timezone.utc).isoformat(),
              "qualification_granted": False, "cwd": "/", "environment": ENV,
              "source_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                                for p in (Path(__file__), HERE / "apple-container-service.toml",
                                          HERE / "apple_container_recover_setup_v2.py")},
              "observations": [], "result": "FAILED", "startup_attempted": False}
    with (BUNDLE / ("evidence/" + ATTEMPT + ".json")).open("x", encoding="utf-8") as evidence:
        def checkpoint():
            evidence.seek(0)
            json.dump(report, evidence, indent=2, sort_keys=True)
            evidence.write("\n")
            evidence.truncate()
            evidence.flush()
            os.fsync(evidence.fileno())

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
            absence = (argv == observer.DISCOVERY or argv[:3] == ["/bin/ps", "-ww", "-p"] or
                       argv[0] == "/usr/sbin/lsof")
            empty = absence and result.returncode == 1 and not result.stdout and not result.stderr
            if ((result.returncode and not empty) or (absence and not result.returncode and not result.stdout) or
                    len(result.stdout) > (4194304 if view else 65536) or len(result.stderr) > 65536 or (absence and result.stderr)):
                raise ValueError("Setup command failed or exceeded retention bound")
            if view:
                value = domain_names(text, argv[2]) if view == "domain" else owned_plist(text, argv[2])
                if view == "service":
                    pids = re.findall(r"^\tpid = ([1-9][0-9]*)$", text, re.M)
                    if len(pids) != 1 or re.findall(r"^\tstate = (.+)$", text, re.M) != ["running"]:
                        raise ValueError("Ambiguous/nonrunning service process identity")
                    for name in ("CONTAINER_APP_ROOT", "CONTAINER_INSTALL_ROOT"):
                        roots = re.findall(r"^\t\t" + name + r" => (.+)$", text, re.M)
                        if len(roots) != 1 or not same_path(roots[0], ENV[name]):
                            raise ValueError("Effective service root differs")
                    with Path(value["executable"]).open("rb") as source:
                        digest = hashlib.file_digest(source, "sha256").hexdigest()
                    if digest != BINARY_SHA256[value["executable"]]:
                        raise ValueError("Service executable bytes changed")
                    value = {"identity": value, "pid": int(pids[0]), "executable_sha256": digest,
                             "target": argv[2]}
                entry["observed"] = value
                return value
            return text

        def inspect_domains():
            return {target: run(["/bin/launchctl", "print", target], 5, "domain") for target in domains}

        def owners(inventory):
            if any(names for target, rows in inventory.items() if target != domain for names in rows.values()):
                raise ValueError("Container service/endpoint appeared in another domain; no automatic recovery")
            labels = inventory[domain]["services"]
            if (not set(labels).issubset(SERVICE_PROGRAMS) or
                    not set(inventory[domain]["endpoints"]).issubset({MACH[label] for label in labels})):
                raise ValueError("Unknown service/endpoint ownership; no automatic recovery")
            return {label: run(["/bin/launchctl", "print", domain + "/" + label], 5, "service")
                    for label in SERVICE_PROGRAMS if label in labels}

        def observe(argv):
            return run(argv, 5)

        def process_plan(owned):
            entries = list(owned.values())
            processes = observer.processes(entries, observe) if entries else []
            if not entries and observe(observer.DISCOVERY):
                raise ValueError("Unowned Container processes remain")
            for entry in entries:
                matches = [p for p in processes if p["pid"] == entry["pid"]]
                if len(matches) != 1:
                    raise ValueError("Missing/ambiguous setup process")
                entry.update(process_uid=501, process_started=matches[0]["started"])
            observer.verify_processes(processes, entries)
            return entries

        try:
            if SETUP.exists() or SETUP.is_symlink():
                raise ValueError("Setup-v4 directory already exists; do not reuse the attempt")
            if report["source_sha256"]["apple_container_recover_setup_v2.py"] != OBSERVER_SHA256:
                raise ValueError("Reviewed process observer bytes changed")
            spec = importlib.util.spec_from_file_location("setup_process_observer", HERE / "apple_container_recover_setup_v2.py")
            observer = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(observer)
            if hashlib.sha256(config_bytes).hexdigest() != CONFIG_SHA256:
                raise ValueError("Reviewed configuration bytes changed")
            for name, expected in BINARY_SHA256.items():
                with Path(name).open("rb") as source:
                    if hashlib.file_digest(source, "sha256").hexdigest() != expected:
                        raise ValueError("Installed executable bytes changed: " + name)
            report["binary_sha256"] = BINARY_SHA256
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
            if manager not in ("Aqua", "Background") or os.getuid() != 501:
                raise ValueError("Unsupported launchd session; no domain fallback")
            domains = ("system", f"user/{os.getuid()}", f"gui/{os.getuid()}")
            domain = domains[2] if manager == "Aqua" else domains[1]
            report.update(manager=manager, launchd_domain=domain)
            before = inspect_domains()
            if any(rows[section] for rows in before.values() for section in ("services", "endpoints")):
                raise ValueError("Existing Container services/endpoints; do not register or stop them")
            if run(observer.DISCOVERY, 5):
                raise ValueError("Existing Container processes; do not start or stop them")
            before_ports = observer.listeners(observe)
            SETUP.mkdir(mode=0o700)
            config = SETUP / "config-home/container"
            config.mkdir(parents=True)
            (config / "config.toml").write_bytes(config_bytes)
            report["storage_before_start"] = storage(SETUP)
            report["startup_attempted"] = True
            checkpoint()
            run(START, 120)
            status = json.loads(run([CLI, "system", "status", "--format", "json"], 15))
            if status.get("status") != "running" or not same_path(status["paths"]["appRoot"], ENV["CONTAINER_APP_ROOT"]):
                raise ValueError("Unexpected post-start service state/root")
            if (not same_path(status["paths"]["installRoot"], "/usr/local") or
                    status["server"]["version"] != "1.5.0" or
                    status["server"]["commit"] != "d265d669ecae041bf338cb3b39c4118316d138f0"):
                raise ValueError("Service installation/source identity differs")
            copied = SETUP / "runtime/config/config.toml"
            if copied.read_bytes() != (config / "config.toml").read_bytes():
                raise ValueError("Effective startup configuration differs")
            after = inspect_domains()
            report["owned_services"] = owners(after)
            if (set(report["owned_services"]) != set(SERVICE_PROGRAMS) or
                    set(after[domain]["endpoints"]) != set(MACH.values())):
                raise ValueError("Expected startup services missing")
            report["process_plan"] = process_plan(report["owned_services"])
            report["listeners"] = observer.listeners(observe)
            report["storage_before_pull"] = storage(SETUP)
            report["provisioning_attempted"] = True
            checkpoint()
            run(PULL, 180)
            report["storage_after_pull"] = storage(SETUP)
            # ImageInspect intentionally filters the configured init; [] with exit 0 is expected.
            run([CLI, "image", "inspect", INIT], 15)
            report["init_verification"] = verify_init(SETUP / "runtime")
            if owners(inspect_domains()) != {
                    label: {k: v for k, v in entry.items() if k not in ("process_uid", "process_started")}
                    for label, entry in report["owned_services"].items()}:
                raise ValueError("Service identity changed during provisioning")
            observer.verify_processes(observer.processes(report["process_plan"], observe), report["process_plan"])
            report["result"] = "SERVICES_STARTED_INIT_CONTENT_SNAPSHOT_CHECKED"
        except (Exception, KeyboardInterrupt) as error:
            report["error"] = type(error).__name__ + ": " + str(error)
            if report["startup_attempted"]:
                try:
                    plan = owners(inspect_domains())
                    entries = process_plan(plan)
                    report["recovery_plan"] = entries
                    report["removed"] = []
                    report["attempted"] = []
                    checkpoint()
                    for entry in entries:
                        remaining = [e for e in entries if e["target"] not in report["removed"]]
                        current = owners(inspect_domains())
                        if {e["target"] for e in current.values()} != {e["target"] for e in remaining}:
                            raise ValueError("Service set changed before recovery")
                        live = current[entry["target"].rsplit("/", 1)[1]]
                        if live != {k: v for k, v in entry.items() if k not in ("process_uid", "process_started")}:
                            raise ValueError("Service ownership changed; no bootout")
                        observer.verify_processes(observer.processes(entries, observe), remaining)
                        report["attempted"].append(entry["target"])
                        checkpoint()
                        run(["/bin/launchctl", "bootout", entry["target"]], 5)
                        report["removed"].append(entry["target"])
                        checkpoint()
                    for attempt in range(5):
                        registrations = inspect_domains()
                        processes = observer.processes(entries, observe) if entries else []
                        if not entries and observe(observer.DISCOVERY):
                            raise ValueError("Unowned Container processes remain")
                        ports = observer.listeners(observe)
                        report["recovery_postcheck"] = {"registrations": registrations,
                                                       "processes": processes, "listeners": ports}
                        checkpoint()
                        if not any(names for rows in registrations.values() for names in rows.values()) and not processes and ports == before_ports:
                            report["recovery"] = "SCOPED_RECOVERY_OBSERVED"
                            break
                        if attempt < 4:
                            time.sleep(1)
                    else:
                        raise ValueError("Registrations/processes/bindings remain after recovery")
                except (Exception, KeyboardInterrupt) as recovery_error:
                    report["recovery"] = "INCOMPLETE_STOP_AND_REVIEW: " + str(recovery_error)
                    try:
                        entries = report.get("recovery_plan", [])
                        report["incomplete_postcheck"] = {
                            "registrations": inspect_domains(),
                            "processes": observer.processes(entries, observe) if entries else "NOT_VERIFIED",
                            "listeners": observer.listeners(observe),
                        }
                    except (Exception, KeyboardInterrupt) as observation_error:
                        report["incomplete_observation_error"] = str(observation_error)
        finally:
            report["elapsed_seconds"] = time.monotonic() - started
            checkpoint()
    return 0 if report["result"] == "SERVICES_STARTED_INIT_CONTENT_SNAPSHOT_CHECKED" else 1


if __name__ == "__main__":
    if sys.argv[1:] != [ATTEMPT]:
        raise SystemExit("New authorization required; exact argument: " + ATTEMPT)
    raise SystemExit(setup())
