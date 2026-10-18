"""Preparation/observer checks only: never run guest code, services or canaries."""

import ast
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("apple_preparation", ROOT / "qualification/apple_container.py")
probe = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(probe)


class ApplePreparationTests(unittest.TestCase):
    def test_fresh_bundle_and_unchanged_observation_never_grant_go(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = probe.prepare(Path(temporary) / "attempt")
            receipt = root / "evidence/prepared.json"
            prepared = json.loads(receipt.read_text())
            self.assertTrue(all(c["status"] == "NOT_RUN" for c in prepared["controls"]))
            self.assertEqual(probe.manifest(root / "original"), prepared["before"]["original"])
            self.assertEqual(os.stat(root / "original/candidate.txt").st_ino,
                             os.stat(root / "inputs/source-hardlink").st_ino)
            self.assertTrue(probe.verify(root, "positive", probe.digest(receipt)))
            result = json.loads((root / "evidence/positive.json").read_text())
            self.assertEqual(result["decision"], "UNAVAILABLE")
            self.assertFalse(result["qualification_granted"])
            with self.assertRaises(FileExistsError):
                probe.prepare(root)
            with self.assertRaises(FileExistsError):
                probe.verify(root, "positive", probe.digest(receipt))

    def test_bytes_mode_and_link_drift_fail_closed(self):
        for change in ("bytes", "mode", "link"):
            with self.subTest(change=change), tempfile.TemporaryDirectory() as temporary:
                root = probe.prepare(Path(temporary) / "attempt")
                expected = probe.digest(root / "evidence/prepared.json")
                target = root / "original/candidate.txt"
                if change == "bytes":
                    target.write_text("changed\n")
                elif change == "mode":
                    target.chmod(0o600 if target.stat().st_mode & 0o777 != 0o600 else 0o400)
                else:
                    target.unlink()
                    target.symlink_to(root / "private/token.txt")
                self.assertFalse(probe.verify(root, "source-write", expected))
                result = json.loads((root / "evidence/source-write.json").read_text())
                self.assertEqual(result["decision"], "NO_GO")

    def test_substituted_receipt_cannot_rebaseline(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = probe.prepare(Path(temporary) / "attempt")
            receipt = root / "evidence/prepared.json"
            expected = probe.digest(receipt)
            receipt.write_text("{}\n")
            with self.assertRaisesRegex(ValueError, "identity changed"):
                probe.verify(root, "positive", expected)

    def test_manifest_records_links_without_reading_their_targets(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "missing-link").symlink_to("/does-not-exist/synthetic")
            result = probe.manifest(root)
            self.assertEqual(result["./missing-link"]["kind"], "symlink")
            self.assertNotIn("sha256", result["./missing-link"])
            (root / "large").write_bytes(b"x" * 1048577)
            with self.assertRaisesRegex(ValueError, "one MiB"):
                probe.manifest(root)

    def test_missing_cli_is_unavailable_without_starting_anything(self):
        with patch.object(probe.shutil, "which", return_value=None), \
                patch.object(probe.Path, "is_file", return_value=False), \
                patch.object(probe.platform, "system", return_value="Test"), \
                patch.object(probe.subprocess, "run") as run:
            result = probe.inspect_host()
        run.assert_not_called()
        self.assertIsNone(result["cli"])
        self.assertEqual(result["decision"], "UNAVAILABLE")

    def test_guest_is_syntax_checked_only(self):
        ast.parse((ROOT / "qualification/apple_container_guest.py").read_text())


if __name__ == "__main__":
    unittest.main()
