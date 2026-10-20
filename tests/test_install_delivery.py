"""Offline installer delivery tests; no npx, network or project execution."""

import importlib.util
from pathlib import Path
import shutil
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
CHECK = ROOT / "scripts" / "check_install.py"
SPEC = importlib.util.spec_from_file_location("faultline_install_check", CHECK)
install_check = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(install_check)


class InstallDeliveryTests(unittest.TestCase):
    def test_public_install_instructions_match_one_standalone_skill(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("npx skills@latest add grove/faultline", readme)
        self.assertIn("Use faultline-audit to find weak tests", readme)
        self.assertIn("NO_GO / UNAVAILABLE", readme)
        self.assertEqual(install_check.SKILL_NAME, "faultline-audit")
        self.assertEqual(
            install_check.payload(ROOT / "faultline-audit"),
            {"SKILL.md": install_check.payload(ROOT / "faultline-audit")["SKILL.md"]},
        )

    def test_full_payload_survives_copy_and_drift_is_rejected(self):
        source = ROOT / "faultline-audit"
        with tempfile.TemporaryDirectory() as temporary:
            installed = Path(temporary) / ".agents" / "skills" / "faultline-audit"
            installed.parent.mkdir(parents=True)
            shutil.copytree(source, installed)
            self.assertEqual(install_check.verify_payload(source, installed), 1)
            (installed / "SKILL.md").write_bytes(b"changed")
            with self.assertRaises(install_check.InstallCheckError):
                install_check.verify_payload(source, installed)

    def test_local_links_must_resolve_within_installed_package(self):
        source = ROOT / "faultline-audit"
        install_check.check_relative_links(source)
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary) / "example"
            directory.mkdir()
            (directory / "SKILL.md").write_text(
                "---\nname: example\ndescription: example\n---\n"
                "[bad](../missing.md)\n", encoding="utf-8",
            )
            with self.assertRaises(install_check.InstallCheckError):
                install_check.check_relative_links(directory)


if __name__ == "__main__":
    unittest.main()
