"""Mocked launchd setup and ownership recovery; no service or guest executes."""

from contextlib import ExitStack
import hashlib
import importlib.util
import json
from pathlib import Path
import plistlib
import subprocess
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("service_setup", ROOT / "qualification/apple_container_service_setup.py")
service = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(service)
API = "com.apple.container.apiserver"
IMAGE = "com.apple.container.container-core-images"
NETWORK = "com.apple.container.container-network-vmnet.default"
MACHINE = "com.apple.container.machine-apiserver"
LABELS = (API, MACHINE, IMAGE, NETWORK)
DOMAINS = ("system", "user/501", "gui/501")


def domain_output(domain, labels=(), endpoints=()):
    return (domain + " = {\n\tservices = {\n" +
            "".join("\t\t123 - " + label + "\n" for label in labels) +
            "\t}\n\tendpoints = {\n" +
            "".join("\t\t0x123 M A " + label + "\n" for label in endpoints) +
            "\t}\n\tenvironment = {\n\t\tSYNTHETIC_PRIVATE = not-retained\n\t}\n}\n").encode()


class ServiceSetupTests(unittest.TestCase):
    def attempt(self, manager="Background", failure=None, collision=None, foreign=False, drift=False,
                domain_error=False, bootout_error=False, trailing=False, wrong_program=False, lingering=False, process_collision=False,
                endpoint_after=False, missing_init=False, process_denied=False, replaced=False, binary_drift=False,
                existing_directory=False, config_drift=False, observer_drift=False, bootout_timeout=False,
                pull_failure=None, verification_failure=False, low_space=False):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        bundle = Path(temporary.name).resolve()
        (bundle / "evidence").mkdir()
        (bundle / "evidence/setup-v1.json").write_bytes(b"original receipt\n")
        (bundle / "evidence/setup-v2.json").write_bytes(b"preserved setup-v2 receipt\n")
        (bundle / "evidence/setup-v3.json").write_bytes(b"preserved setup-v3 receipt\n")
        setup = bundle / "setup-v4"
        if existing_directory:
            setup.mkdir()
            (setup / "sentinel").write_bytes(b"preserve existing attempt")
        plugins = bundle / "plugins"
        (plugins / "images").mkdir(parents=True)
        (plugins / "images/config.toml").write_bytes(b"synthetic plugin metadata")
        pins = {"images": hashlib.sha256(b"synthetic plugin metadata").hexdigest()}
        env = {**service.ENV, "CONTAINER_APP_ROOT": str(setup / "runtime"),
               "XDG_CONFIG_HOME": str(setup / "config-home")}
        start = [service.CLI, "system", "start", "--app-root", env["CONTAINER_APP_ROOT"],
                 "--install-root", "/usr/local", "--disable-kernel-install", "--timeout", "15"]
        domain = "gui/501" if manager == "Aqua" else "user/501"
        live = {}
        inspections = {}
        programs = {}
        for label in LABELS:
            program = bundle / (label + ".executable")
            program.write_bytes(b"synthetic executable identity; never executed")
            programs[label] = str(program)

        binary_pins = {path: hashlib.sha256(Path(path).read_bytes()).hexdigest() for path in programs.values()}
        if binary_drift:
            Path(programs[API]).write_bytes(b"changed executable identity")
        pids = {label: 701 + index for index, label in enumerate(LABELS)}
        processes_seen = 0

        def respond(argv, **kwargs):
            output = b""
            code = 0
            if argv == ["/bin/launchctl", "managername"]:
                output = (manager + "\n").encode()
            elif argv[:2] == ["/bin/launchctl", "print"] and argv[2] in DOMAINS:
                if domain_error:
                    return subprocess.CompletedProcess(argv, 1, b"", b"Permission denied")
                labels = tuple(live) if argv[2] == domain else ()
                endpoints = tuple(service.MACH[label] for label in labels)
                if endpoint_after and live and argv[2] == "system":
                    endpoints = ("com.apple.container.foreign",)
                if collision and argv[2] == collision[0]:
                    if collision[1] == "services":
                        labels = ("com.apple.container.unrelated",)
                    else:
                        endpoints = ("com.apple.container.unrelated",)
                output = domain_output(argv[2], labels, endpoints)
            elif argv == start:
                copied = setup / "runtime/config"
                copied.mkdir(parents=True)
                (copied / "config.toml").write_bytes((service.HERE / "apple-container-service.toml").read_bytes())
                for label in LABELS:
                    path = setup / "runtime" / (label + ".plist")
                    roots = {**env, "CONTAINER_APP_ROOT": env["CONTAINER_APP_ROOT"] + ("/" if trailing else ""),
                             "CONTAINER_INSTALL_ROOT": "/usr/local/" if trailing else "/usr/local"}
                    path.write_bytes(plistlib.dumps({"Label": label, "EnvironmentVariables": roots,
                                                    "ProgramArguments": [programs[label], "start"]}))
                    live[label] = path
                if isinstance(failure, Exception):
                    raise failure
                code = 1 if failure else 0
            elif argv[:2] == ["/bin/launchctl", "print"]:
                target = argv[2]
                label = target.rsplit("/", 1)[1]
                path = live[label]
                inspections[label] = inspections.get(label, 0) + 1
                if foreign:
                    path = bundle / "unrelated.plist"
                    path.write_bytes(b"unrelated; never remove")
                if drift and inspections[label] == 2:
                    config = plistlib.loads(path.read_bytes())
                    config["changed"] = True
                    path.write_bytes(plistlib.dumps(config))
                program = "/bin/sh" if wrong_program else programs[label]
                output = (target + " = {\n\tpath = " + str(path) + "\n\tprogram = " + program +
                          "\n\tpid = " + str(pids[label]) + "\n\tstate = running\n" +
                          "\t\tCONTAINER_APP_ROOT => " + env["CONTAINER_APP_ROOT"] + "/\n" +
                          "\t\tCONTAINER_INSTALL_ROOT => /usr/local/\n}\n").encode()
            elif argv[:2] == ["/bin/launchctl", "bootout"]:
                if bootout_timeout:
                    del live[argv[2].rsplit("/", 1)[1]]
                    raise subprocess.TimeoutExpired(argv, 5)
                if bootout_error:
                    code = 1
                else:
                    del live[argv[2].rsplit("/", 1)[1]]
            elif argv == [service.CLI, "system", "status", "--format", "json"]:
                output = json.dumps({"status": "running", "paths": {
                    "appRoot": env["CONTAINER_APP_ROOT"] + ("/" if trailing else ""),
                    "installRoot": "/usr/local/" if trailing else "/usr/local"},
                    "server": {"version": "1.5.0", "commit": "d265d669ecae041bf338cb3b39c4118316d138f0"}}).encode()
            elif argv == [service.CLI, "image", "inspect", service.INIT]:
                output = b"[]"
                if missing_init:
                    return subprocess.CompletedProcess(argv, 1, b"", b"image not found")
            elif argv == service.PULL:
                self.assertEqual(len(live), 4)
                checkpoint = json.loads((bundle / "evidence/setup-v4.json").read_text())
                self.assertEqual(len(checkpoint["process_plan"]), 4)
                self.assertTrue(checkpoint["provisioning_attempted"])
                if isinstance(pull_failure, Exception):
                    raise pull_failure
                if pull_failure:
                    return subprocess.CompletedProcess(argv, 1, b"partial pull", b"explicit retrieval failed")
            elif argv[:3] == ["/usr/bin/pgrep", "-u", "501"] or argv[0] == "/bin/ps":
                if process_denied:
                    return subprocess.CompletedProcess(argv, 1, b"", b"Operation not permitted")
                active = list(live)
                if lingering and not active and (setup / "runtime").exists():
                    active = [API]
                if argv[0] == "/usr/bin/pgrep":
                    output = ("999\n" if process_collision and not active else "".join(str(pids[label]) + "\n" for label in active)).encode()
                else:
                    nonlocal processes_seen
                    processes_seen += 1
                    started = "23:31:23" if not replaced or processes_seen == 1 else "23:59:59"
                    output = "".join(f"{pids[label]} 501 Sun Oct 18 {started} 2026 {programs[label]}\n" for label in active).encode()
                code = 0 if output else 1
            elif argv[0] == "/usr/sbin/lsof":
                output = b"p701\nf14\nPUDP\nn127.0.0.1:2053\n" if API in live else b""
                code = 0 if output else 1
            else:
                raise AssertionError("Unexpected command: " + str(argv))
            stderr = b"Launching container-apiserver...\n" if argv == start else b""
            return subprocess.CompletedProcess(argv, code, output, stderr)

        with ExitStack() as stack:
            for name, value in (("BUNDLE", bundle), ("SETUP", setup), ("PLUGIN_ROOT", plugins),
                                ("PLUGIN_CONFIGS", pins), ("CUSTOM_PLUGINS", bundle / "no-custom-plugins"),
                                ("ENV", env), ("START", start), ("SERVICE_PROGRAMS", programs), ("BINARY_SHA256", binary_pins)):
                stack.enter_context(patch.object(service, name, value))
            if config_drift:
                stack.enter_context(patch.object(service, "CONFIG_SHA256", "wrong"))
            if observer_drift:
                stack.enter_context(patch.object(service, "OBSERVER_SHA256", "wrong"))
            stack.enter_context(patch.object(service.os, "getuid", return_value=501))
            stack.enter_context(patch.object(service.time, "sleep"))
            if low_space:
                stack.enter_context(patch.object(service.shutil, "disk_usage", return_value=SimpleNamespace(free=0)))
            stack.enter_context(patch.object(service, "verify_init", side_effect=ValueError("bad blob/snapshot")
                                              if verification_failure else None, return_value={"synthetic": True}))
            run = stack.enter_context(patch.object(service.subprocess, "run", side_effect=respond))
            code = service.setup()
            calls = [call.args[0] for call in run.call_args_list]
        raw = (bundle / "evidence/setup-v4.json").read_text()
        self.assertNotIn("not-retained", raw)
        self.assertEqual((bundle / "evidence/setup-v1.json").read_bytes(), b"original receipt\n")
        self.assertEqual((bundle / "evidence/setup-v2.json").read_bytes(), b"preserved setup-v2 receipt\n")
        self.assertEqual((bundle / "evidence/setup-v3.json").read_bytes(), b"preserved setup-v3 receipt\n")
        self.assertFalse(any(cmd[:3] == [service.CLI, "system", "stop"] for cmd in calls))
        if existing_directory:
            self.assertEqual((setup / "sentinel").read_bytes(), b"preserve existing attempt")
        return code, calls, json.loads(raw), bundle

    def test_aqua_and_background_select_only_the_source_matched_domain(self):
        for manager, expected in (("Aqua", "gui/501"), ("Background", "user/501")):
            with self.subTest(manager=manager):
                code, calls, report, _ = self.attempt(manager)
                self.assertEqual(code, 0)
                self.assertEqual(report["launchd_domain"], expected)
                self.assertEqual(set(report["owned_services"]), set(LABELS))
                self.assertEqual(calls[1:4], [["/bin/launchctl", "print", d] for d in DOMAINS])
                self.assertFalse(any(c[1] == "bootout" for c in calls))

    def test_service_or_endpoint_collision_in_any_domain_blocks_start_and_stop(self):
        for domain in DOMAINS:
            for kind in ("services", "endpoints"):
                with self.subTest(domain=domain, kind=kind):
                    code, calls, report, bundle = self.attempt(collision=(domain, kind))
                    self.assertEqual(code, 1)
                    self.assertFalse(report["startup_attempted"])
                    self.assertTrue(all(c[0] == "/bin/launchctl" and c[1] in ("managername", "print") for c in calls))
                    self.assertFalse((bundle / "setup-v4").exists())

    def test_unreadable_domain_or_unsupported_manager_blocks_without_fallback(self):
        for kwargs in ({"domain_error": True}, {"manager": "System"}):
            code, _, report, _ = self.attempt(**kwargs)
            self.assertEqual(code, 1)
            self.assertFalse(report["startup_attempted"])

    def test_startup_exit_or_timeout_recovers_exact_owned_services_in_both_domains(self):
        for manager in ("Aqua", "Background"):
            for failure in ("nonzero", subprocess.TimeoutExpired(service.START, 120, output=b"partial")):
                with self.subTest(manager=manager, failure=failure):
                    code, calls, report, _ = self.attempt(manager, failure=failure)
                    self.assertEqual(code, 1)
                    domain = report["launchd_domain"]
                    self.assertEqual([c for c in calls if c[1] == "bootout"], [
                        ["/bin/launchctl", "bootout", domain + "/" + label] for label in LABELS])
                    self.assertEqual(report["recovery"], "SCOPED_RECOVERY_OBSERVED")

    def test_foreign_origin_or_changed_identity_is_never_removed(self):
        for kwargs in ({"foreign": True}, {"drift": True}):
            code, calls, report, _ = self.attempt(failure="nonzero", **kwargs)
            self.assertEqual(code, 1)
            self.assertIn("INCOMPLETE_STOP_AND_REVIEW", report["recovery"])
            self.assertFalse(any(c[1] == "bootout" for c in calls))

    def test_bootout_failure_is_incomplete_and_never_uses_prefix_stop(self):
        code, _, report, _ = self.attempt(failure="nonzero", bootout_error=True)
        self.assertEqual(code, 1)
        self.assertIn("INCOMPLETE_STOP_AND_REVIEW", report["recovery"])

    def test_repeated_v4_refuses_before_service_contact(self):
        _, _, _, bundle = self.attempt()
        with patch.object(service, "BUNDLE", bundle), patch.object(service.subprocess, "run") as run:
            with self.assertRaises(FileExistsError):
                service.setup()
            run.assert_not_called()

    def test_unrecognized_domain_output_is_not_empty_namespace_evidence(self):
        valid = domain_output("user/501").decode()
        for text in ("", valid.replace("\tendpoints = {", "\tunknown = {"),
                     valid.replace("\tservices = {", "\tservices = {\ninvalid-row")):
            with self.assertRaises(ValueError):
                service.domain_names(text, "user/501")

    def test_endpoint_names_with_spaces_are_preserved_as_names(self):
        text = domain_output("user/501", endpoints=("locale unrelated-endpoint", API)).decode()
        self.assertEqual(service.domain_names(text, "user/501")["endpoints"], [API])

    def test_trailing_status_and_network_root_slashes_keep_strict_identity(self):
        code, _, report, _ = self.attempt(trailing=True)
        self.assertEqual(code, 0)
        self.assertIn(NETWORK, report["owned_services"])

    def test_foreign_live_executable_is_not_removed(self):
        code, calls, report, _ = self.attempt(failure="nonzero", wrong_program=True)
        self.assertEqual(code, 1)
        self.assertIn("INCOMPLETE", report["recovery"])
        self.assertFalse(any(c[1] == "bootout" for c in calls))

    def test_existing_directory_or_changed_source_pins_refuse_before_contact(self):
        for kwargs in ({"existing_directory": True}, {"config_drift": True}, {"observer_drift": True}):
            with self.subTest(kwargs=kwargs):
                code, calls, report, _ = self.attempt(**kwargs)
                self.assertEqual(code, 1)
                self.assertFalse(report["startup_attempted"])
                self.assertEqual(calls, [])

    def test_fresh_attempt_records_exact_sources_and_does_not_repeat_prerequisites(self):
        code, calls, report, _ = self.attempt(trailing=True)
        self.assertEqual(code, 0)
        self.assertEqual(service.ATTEMPT, "setup-v4")
        self.assertEqual(report["source_sha256"]["apple_container_recover_setup_v2.py"], service.OBSERVER_SHA256)
        self.assertEqual(report["source_sha256"]["apple-container-service.toml"], service.CONFIG_SHA256)
        self.assertEqual(len(report["process_plan"]), 4)
        self.assertFalse(any(c[0] in ("/usr/bin/codesign", "/usr/sbin/sysctl") for c in calls))
        container_calls = [c for c in calls if c[0] == service.CLI]
        self.assertEqual([c[1:3] for c in container_calls], [
            ["system", "start"], ["system", "status"], ["image", "pull"], ["image", "inspect"]])
        self.assertTrue(all(c[3] == service.INIT for c in container_calls if c[1:3] == ["image", "inspect"]))

    def test_missing_init_metadata_causes_owned_only_recovery(self):
        code, calls, report, _ = self.attempt(missing_init=True)
        self.assertEqual(code, 1)
        self.assertEqual(report["recovery"], "SCOPED_RECOVERY_OBSERVED")
        self.assertEqual(len([c for c in calls if c[1] == "bootout"]), 4)
        self.assertEqual(report["removed"], report["attempted"])

    def test_explicit_pull_failure_timeout_or_bad_payload_preserves_failure_and_recovers(self):
        for kwargs in ({"pull_failure": "nonzero"},
                       {"pull_failure": subprocess.TimeoutExpired(service.PULL, 180, output=b"partial", stderr=b"pull timeout")},
                       {"verification_failure": True}):
            with self.subTest(kwargs=kwargs):
                code, calls, report, _ = self.attempt(**kwargs)
                self.assertEqual(code, 1)
                self.assertTrue(report["provisioning_attempted"])
                self.assertEqual(report["result"], "FAILED")
                self.assertEqual(report["recovery"], "SCOPED_RECOVERY_OBSERVED")
                pull = next(o for o in report["observations"] if o["argv"] == service.PULL)
                if "pull_failure" in kwargs:
                    self.assertIn("partial", pull["stdout"])
                    self.assertTrue(pull["stderr"])
                self.assertEqual(len([c for c in calls if c[1] == "bootout"]), 4)

    def test_insufficient_disk_space_blocks_start_pull_and_recovery(self):
        code, calls, report, _ = self.attempt(low_space=True)
        self.assertEqual(code, 1)
        self.assertFalse(report["startup_attempted"])
        self.assertIn("two GiB free", report["error"])
        self.assertFalse(any(c[0] == service.CLI or c[1] == "bootout" for c in calls))

    def test_binary_drift_or_lingering_preexisting_process_blocks_start(self):
        for kwargs in ({"binary_drift": True}, {"process_collision": True}, {"process_denied": True}):
            with self.subTest(kwargs=kwargs):
                code, calls, report, _ = self.attempt(**kwargs)
                self.assertEqual(code, 1)
                self.assertFalse(report["startup_attempted"])
                self.assertFalse(any(c[0] == service.CLI or c[1] == "bootout" for c in calls))

    def test_endpoint_in_other_domain_or_replaced_process_stops_recovery(self):
        for kwargs in ({"endpoint_after": True}, {"replaced": True}):
            with self.subTest(kwargs=kwargs):
                code, calls, report, _ = self.attempt(failure="nonzero", **kwargs)
                self.assertEqual(code, 1)
                self.assertIn("INCOMPLETE_STOP_AND_REVIEW", report["recovery"])
                self.assertFalse(any(c[1] == "bootout" for c in calls))

    def test_timed_out_bootout_preserves_ambiguous_attempt_and_stops(self):
        code, calls, report, _ = self.attempt(failure="nonzero", bootout_timeout=True)
        self.assertEqual(code, 1)
        self.assertIn("INCOMPLETE_STOP_AND_REVIEW", report["recovery"])
        self.assertEqual(len(report["attempted"]), 1)
        self.assertEqual(report["removed"], [])
        self.assertEqual(len(report["incomplete_postcheck"]["processes"]), 3)
        self.assertEqual(len([c for c in calls if c[1] == "bootout"]), 1)

    def test_partial_removal_with_lingering_process_cannot_report_success(self):
        code, calls, report, _ = self.attempt(failure="nonzero", lingering=True)
        self.assertEqual(code, 1)
        self.assertIn("INCOMPLETE_STOP_AND_REVIEW", report["recovery"])
        self.assertTrue(report["incomplete_postcheck"]["processes"])
        self.assertTrue(report["attempted"])
        self.assertEqual(len([c for c in calls if c[1] == "bootout"]), 4)


class InitContentTests(unittest.TestCase):
    def fixture(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name).resolve()
        blobs = root / "content/blobs/sha256"
        blobs.mkdir(parents=True)

        def blob(data):
            raw = data if isinstance(data, bytes) else json.dumps(data).encode()
            digest = hashlib.sha256(raw).hexdigest()
            (blobs / digest).write_bytes(raw)
            return {"digest": "sha256:" + digest, "size": len(raw)}

        layer = blob(b"synthetic layer bytes, never unpacked or executed")
        config = blob({"os": "linux", "architecture": "arm64"})
        manifest = blob({"schemaVersion": 2, "config": config, "layers": [layer]})
        reference = "ghcr.io/apple/containerization/vminit@" + manifest["digest"]
        descriptor = {**manifest, "platform": {"os": "linux", "architecture": "arm64"}}
        index = blob({"schemaVersion": 2, "manifests": [descriptor]})
        (root / "state.json").write_text(json.dumps({reference: index}))
        snapshot = root / "snapshots" / manifest["digest"][7:] / "snapshot"
        snapshot.parent.mkdir(parents=True)
        header = bytearray(1024)
        header[4:8] = (131072).to_bytes(4, "little")
        header[24:28] = (2).to_bytes(4, "little")
        header[56:58] = b"\x53\xef"
        with snapshot.open("wb") as output:
            output.seek(1024)
            output.write(header)
            output.truncate(512 * 1024**2)
        (snapshot.parent / "snapshot-info").write_text(json.dumps({
            "type": {"block": {"format": "ext4"}}, "source": str(snapshot), "destination": "/", "options": []}))
        for directory in (root / "content/ingest", root / "snapshots/ingest"):
            directory.mkdir()
        return root, reference, blobs / layer["digest"][7:], snapshot

    def test_complete_blob_graph_and_structural_snapshot_are_recorded_without_execution(self):
        root, reference, _, snapshot = self.fixture()
        with patch.object(service.subprocess, "run") as run:
            result = service.verify_init(root, reference)
        run.assert_not_called()
        self.assertEqual(len(result["blobs"]), 4)
        self.assertEqual(result["snapshot"]["bytes"], 512 * 1024**2)
        self.assertEqual(len(result["snapshot"]["sha256"]), 64)
        self.assertIn("NOT_FSCK_OR_GUEST_BOOT", result["snapshot"]["check"])
        self.assertTrue(snapshot.exists())

    def test_corrupt_missing_linked_or_wrong_sized_blob_is_rejected(self):
        for kind in ("corrupt", "missing", "symlink", "hardlink", "size"):
            with self.subTest(kind=kind):
                root, reference, layer, _ = self.fixture()
                original = layer.read_bytes()
                if kind == "corrupt":
                    layer.write_bytes(b"x" * len(original))
                elif kind == "missing":
                    layer.unlink()
                elif kind == "symlink":
                    target = root / "foreign"
                    target.write_bytes(original)
                    layer.unlink()
                    layer.symlink_to(target)
                elif kind == "hardlink":
                    (root / "alias").hardlink_to(layer)
                else:
                    layer.write_bytes(original + b"extra")
                with self.assertRaises((OSError, ValueError)):
                    service.verify_init(root, reference)

    def test_wrong_pin_platform_incomplete_ingest_or_snapshot_is_rejected(self):
        for kind in ("pin", "platform", "ingest", "metadata", "geometry", "snapshot-link"):
            with self.subTest(kind=kind):
                root, reference, _, snapshot = self.fixture()
                if kind == "pin":
                    wrong = reference.rsplit("@", 1)[0] + "@sha256:" + "0" * 64
                    state = json.loads((root / "state.json").read_text())
                    (root / "state.json").write_text(json.dumps({wrong: state[reference]}))
                    reference = wrong
                elif kind == "platform":
                    state = json.loads((root / "state.json").read_text())
                    path = root / "content/blobs/sha256" / state[reference]["digest"][7:]
                    index = json.loads(path.read_text())
                    index["manifests"][0]["platform"]["architecture"] = "amd64"
                    raw = json.dumps(index).encode()
                    digest = hashlib.sha256(raw).hexdigest()
                    (path.parent / digest).write_bytes(raw)
                    (root / "state.json").write_text(json.dumps({reference: {"digest": "sha256:" + digest, "size": len(raw)}}))
                elif kind == "ingest":
                    (root / "snapshots/ingest/partial").mkdir()
                elif kind == "metadata":
                    path = snapshot.parent / "snapshot-info"
                    metadata = json.loads(path.read_text())
                    metadata["source"] = "/unrelated/snapshot"
                    path.write_text(json.dumps(metadata))
                elif kind == "snapshot-link":
                    snapshot.unlink()
                    snapshot.symlink_to("/unrelated/snapshot")
                else:
                    with snapshot.open("r+b") as output:
                        output.seek(1080)
                        output.write(b"xx")
                with self.assertRaises((OSError, ValueError)):
                    service.verify_init(root, reference)

    def test_storage_admission_rejects_oversize_or_symlinks_without_deleting(self):
        for kind in ("oversize", "symlink"):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                path = root / "retained"
                if kind == "symlink":
                    path.symlink_to("/unrelated")
                else:
                    with path.open("wb") as output:
                        output.truncate(1024**3 + 1)
                with self.assertRaises(ValueError):
                    service.storage(root)
                self.assertTrue(path.exists() or path.is_symlink())


if __name__ == "__main__":
    unittest.main()
