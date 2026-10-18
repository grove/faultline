"""Mocked setup only: no launchctl, Container service or guest is executed."""

import importlib.util
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("service_setup", ROOT / "qualification/apple_container_service_setup.py")
service = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(service)


class ServiceSetupTests(unittest.TestCase):
    def attempt(self, responses):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        bundle = Path(temporary.name).resolve()
        (bundle / "evidence").mkdir()
        setup = bundle / "setup-v1"
        plugins = bundle / "plugins"
        (plugins / "images").mkdir(parents=True)
        (plugins / "images/config.toml").write_bytes(b"synthetic plugin metadata")
        pins = {"images": hashlib.sha256(b"synthetic plugin metadata").hexdigest()}
        for name, value in (("BUNDLE", bundle), ("SETUP", setup), ("PLUGIN_ROOT", plugins),
                            ("PLUGIN_CONFIGS", pins), ("CUSTOM_PLUGINS", bundle / "no-custom-plugins")):
            patcher = patch.object(service, name, value)
            patcher.start()
            self.addCleanup(patcher.stop)
        def respond(argv, **kwargs):
            if argv == service.START:
                copied = setup / "runtime/config"
                copied.mkdir(parents=True)
                (copied / "config.toml").write_bytes((service.HERE / "apple-container-service.toml").read_bytes())
            response = next(responses)
            if isinstance(response, Exception):
                raise response
            return subprocess.CompletedProcess(argv, 0, response, b"")
        with patch.object(service.subprocess, "run", side_effect=respond) as run:
            code = service.setup()
            calls = run.call_args_list
        report = json.loads((bundle / "evidence/setup-v1.json").read_text())
        return code, calls, report, bundle

    def test_preexisting_services_stop_before_registration(self):
        code, calls, report, bundle = self.attempt(iter([b"Aqua\n", b"123 0 com.apple.container.apiserver\n"]))
        self.assertEqual(code, 1)
        self.assertEqual(len(calls), 2)
        self.assertFalse(report["startup_attempted"])
        self.assertFalse((bundle / "setup-v1").exists())

    def test_success_observes_pinned_init_without_launching_workload(self):
        status = json.dumps({"status": "running", "paths": {
            "appRoot": service.ENV["CONTAINER_APP_ROOT"], "installRoot": "/usr/local"},
            "server": {"version": "1.5.0", "commit": "d265d669ecae041bf338cb3b39c4118316d138f0"}}).encode()
        code, calls, report, bundle = self.attempt(iter([
            b"Aqua\n", b"PID Status Label\n", b"started\n", status, b"[{}]", b"123 0 com.apple.container.apiserver\n"]))
        self.assertEqual(code, 0)
        self.assertEqual([c.args[0] for c in calls][2:5], [service.START,
            [service.CLI, "system", "status", "--format", "json"],
            [service.CLI, "image", "inspect", service.INIT]])
        self.assertEqual(report["boundary_launches_requested"], 0)
        self.assertFalse(report["qualification_granted"])
        self.assertEqual(report["result"], "SERVICES_STARTED_INIT_METADATA_PRESENT")
        with patch.object(service.subprocess, "run") as run:
            with self.assertRaises(FileExistsError):
                service.setup()
            run.assert_not_called()

    def test_startup_timeout_records_recovery_without_retry(self):
        code, calls, report, _ = self.attempt(iter([
            b"Aqua\n", b"", subprocess.TimeoutExpired(service.START, 120, output=b"partial"), b"stopped", b""]))
        self.assertEqual(code, 1)
        self.assertEqual([c.args[0] for c in calls][3], service.STOP)
        self.assertTrue(report["observations"][2]["timed_out"])
        self.assertEqual(report["recovery"], "NO_CONTAINER_LABELS")
        self.assertEqual(sum(c.args[0] == service.START for c in calls), 1)


if __name__ == "__main__":
    unittest.main()
