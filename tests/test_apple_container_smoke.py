"""Host preparation and mocked inventory only; never execute a guest or CLI."""

import ast
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("smoke", ROOT / "qualification/apple_container_smoke.py")
smoke = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(smoke)


class SmokePreparationTests(unittest.TestCase):
    def test_v2_is_fresh_frozen_and_does_not_execute(self):
        with tempfile.TemporaryDirectory() as temporary, patch.object(smoke.subprocess, "run") as run:
            directory = smoke.prepare(Path(temporary) / "v2")
            report = json.loads((directory / "evidence/prepared-v2.json").read_text())
            self.assertEqual(report["boundary_launches"], 0)
            self.assertFalse(report["qualification_granted"])
            self.assertEqual(report["positive"], "NOT_RUN")
            self.assertEqual((directory / "inputs/positive-v2.py").read_bytes(),
                             (ROOT / "qualification/apple_container_positive_v2.py").read_bytes())
            for name, before in report["before"].items():
                self.assertEqual(smoke.preparation.manifest(directory / name), before)
            for name, expected in report["source_sha256"].items():
                self.assertEqual(smoke.preparation.digest(ROOT / name), expected)
            with self.assertRaises(FileExistsError):
                smoke.prepare(directory)
            run.assert_not_called()
        ast.parse((ROOT / "qualification/apple_container_positive_v2.py").read_text())

    def test_inventory_is_only_status_list_and_scoped_kernel_hash(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = smoke.prepare(Path(temporary) / "v2")
            app_root = Path(temporary).resolve() / "runtime"
            kernels = app_root / "kernels"
            kernels.mkdir(parents=True)
            (kernels / "kernel").write_bytes(b"synthetic kernel, never executed")
            (kernels / "default.kernel-arm64").symlink_to("kernel")
            status = {"status": "running", "paths": {"appRoot": str(app_root)}}
            responses = [subprocess.CompletedProcess([], 0, json.dumps(status).encode(), b""),
                         subprocess.CompletedProcess([], 0, b"[]", b"")]
            with patch.object(smoke, "APP_ROOT", app_root), \
                    patch.object(smoke.subprocess, "run", side_effect=responses) as run:
                self.assertTrue(smoke.inventory(directory))
                with self.assertRaises(FileExistsError):
                    smoke.inventory(directory)
            self.assertEqual([c.args[0] for c in run.call_args_list], [
                [smoke.CLI, "system", "status", "--format", "json"],
                [smoke.CLI, "image", "list", "--format", "json"]])
            for call in run.call_args_list:
                self.assertEqual(call.kwargs, {
                    "cwd": "/", "env": smoke.ENV, "stdin": subprocess.DEVNULL,
                    "capture_output": True, "timeout": 15})
            report = json.loads((directory / "evidence/inventory.json").read_text())
            self.assertEqual(report["kernel"]["sha256"], smoke.preparation.digest(kernels / "kernel"))
            self.assertEqual(report["boundary_launches"], 0)
            self.assertFalse(report["qualification_granted"])

    def test_inventory_stops_and_preserves_failures(self):
        for response in (
            subprocess.CompletedProcess([], 1, b'{"status":"unregistered"}', b"not running"),
            subprocess.CompletedProcess([], 0, b"x" * 65537, b""),
            subprocess.CompletedProcess([], 0, b"{}", b""),
            subprocess.TimeoutExpired([smoke.CLI], 15, output=b"partial", stderr=b"timeout"),
        ):
            with self.subTest(response=response), tempfile.TemporaryDirectory() as temporary:
                directory = smoke.prepare(Path(temporary) / "v2")
                with patch.object(smoke.subprocess, "run", side_effect=[response]) as run:
                    self.assertFalse(smoke.inventory(directory))
                self.assertEqual(run.call_count, 1)
                report = json.loads((directory / "evidence/inventory.json").read_text())
                self.assertIn("error", report)
                self.assertEqual(report["kernel"], "NOT_INSPECTED")
                if isinstance(response, subprocess.TimeoutExpired):
                    self.assertEqual(report["timeout_stdout"], "partial")

    def test_kernel_alias_outside_store_is_not_read(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = smoke.prepare(Path(temporary) / "v2")
            app_root = Path(temporary).resolve() / "runtime"
            kernels = app_root / "kernels"
            kernels.mkdir(parents=True)
            external = Path(temporary) / "unapproved"
            external.write_bytes(b"not a kernel")
            (kernels / "default.kernel-arm64").symlink_to(external)
            status = {"status": "running", "paths": {"appRoot": str(app_root)}}
            responses = [subprocess.CompletedProcess([], 0, json.dumps(status).encode(), b""),
                         subprocess.CompletedProcess([], 0, b"[]", b"")]
            with patch.object(smoke, "APP_ROOT", app_root), \
                    patch.object(smoke.subprocess, "run", side_effect=responses):
                self.assertFalse(smoke.inventory(directory))
            report = json.loads((directory / "evidence/inventory.json").read_text())
            self.assertIn("outside approved kernel store", report["error"])


if __name__ == "__main__":
    unittest.main()
