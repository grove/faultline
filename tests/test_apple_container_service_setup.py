"""Mocked launchd setup and ownership recovery; no service or guest executes."""

from contextlib import ExitStack
import hashlib
import importlib.util
import json
from pathlib import Path
import plistlib
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("service_setup", ROOT / "qualification/apple_container_service_setup.py")
service = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(service)
API = "com.apple.container.apiserver"
IMAGE = "com.apple.container.core.container-core-images"
DOMAINS = ("system", "user/501", "gui/501")


def domain_output(domain, labels=(), endpoints=()):
    return (domain + " = {\n\tservices = {\n" +
            "".join("\t\t123 - " + label + "\n" for label in labels) +
            "\t}\n\tendpoints = {\n" +
            "".join("\t\t0x123 M A " + label + "\n" for label in endpoints) +
            "\t}\n\tenvironment = {\n\t\tSYNTHETIC_PRIVATE = not-retained\n\t}\n}\n").encode()


class ServiceSetupTests(unittest.TestCase):
    def attempt(self, manager="Background", failure=None, collision=None, foreign=False, drift=False,
                domain_error=False, bootout_error=False):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        bundle = Path(temporary.name).resolve()
        (bundle / "evidence").mkdir()
        (bundle / "evidence/setup-v1.json").write_bytes(b"original receipt\n")
        setup = bundle / "setup-v2"
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

        def respond(argv, **kwargs):
            output = b""
            code = 0
            if argv == ["/bin/launchctl", "managername"]:
                output = (manager + "\n").encode()
            elif argv[:2] == ["/bin/launchctl", "print"] and argv[2] in DOMAINS:
                if domain_error:
                    return subprocess.CompletedProcess(argv, 1, b"", b"Permission denied")
                labels = tuple(live) if argv[2] == domain else ()
                endpoints = ()
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
                for label in (API, IMAGE):
                    path = setup / "runtime" / (label + ".plist")
                    path.write_bytes(plistlib.dumps({"Label": label, "EnvironmentVariables": env}))
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
                output = (target + " = {\n\tpath = " + str(path) + "\n}\n").encode()
            elif argv[:2] == ["/bin/launchctl", "bootout"]:
                if bootout_error:
                    code = 1
                else:
                    del live[argv[2].rsplit("/", 1)[1]]
            elif argv == [service.CLI, "system", "status", "--format", "json"]:
                output = json.dumps({"status": "running", "paths": {
                    "appRoot": env["CONTAINER_APP_ROOT"], "installRoot": "/usr/local"},
                    "server": {"version": "1.5.0", "commit": "d265d66"}}).encode()
            elif argv == [service.CLI, "image", "inspect", service.INIT]:
                output = b"[{}]"
            else:
                raise AssertionError("Unexpected command: " + str(argv))
            return subprocess.CompletedProcess(argv, code, output, b"")

        with ExitStack() as stack:
            for name, value in (("BUNDLE", bundle), ("SETUP", setup), ("PLUGIN_ROOT", plugins),
                                ("PLUGIN_CONFIGS", pins), ("CUSTOM_PLUGINS", bundle / "no-custom-plugins"),
                                ("ENV", env), ("START", start)):
                stack.enter_context(patch.object(service, name, value))
            stack.enter_context(patch.object(service.os, "getuid", return_value=501))
            run = stack.enter_context(patch.object(service.subprocess, "run", side_effect=respond))
            code = service.setup()
            calls = [call.args[0] for call in run.call_args_list]
        raw = (bundle / "evidence/setup-v2.json").read_text()
        self.assertNotIn("not-retained", raw)
        self.assertEqual((bundle / "evidence/setup-v1.json").read_bytes(), b"original receipt\n")
        self.assertFalse(any(cmd[:3] == [service.CLI, "system", "stop"] for cmd in calls))
        return code, calls, json.loads(raw), bundle

    def test_aqua_and_background_select_only_the_source_matched_domain(self):
        for manager, expected in (("Aqua", "gui/501"), ("Background", "user/501")):
            with self.subTest(manager=manager):
                code, calls, report, _ = self.attempt(manager)
                self.assertEqual(code, 0)
                self.assertEqual(report["launchd_domain"], expected)
                self.assertEqual(set(report["owned_services"]), {API, IMAGE})
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
                    self.assertFalse((bundle / "setup-v2").exists())

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
                        ["/bin/launchctl", "bootout", domain + "/" + label] for label in (API, IMAGE)])
                    self.assertEqual(report["recovery"], "NO_CONTAINER_REGISTRATIONS_OBSERVED")

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

    def test_repeated_v2_refuses_before_service_contact(self):
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


if __name__ == "__main__":
    unittest.main()
