"""Offline installer delivery tests; no npx, network or project execution."""

import importlib.util
from pathlib import Path
import re
import shutil
import tempfile
import unittest
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
CHECK = ROOT / "scripts" / "check_install.py"
SPEC = importlib.util.spec_from_file_location("faultline_install_check", CHECK)
install_check = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(install_check)


class InstallDeliveryTests(unittest.TestCase):
    def test_first_use_and_optional_guides_have_resolving_local_links(self):
        documents = [ROOT / name for name in (
            "README.md", "docs/usage.md", "docs/maintaining.md",
            "DESIGN.md", "IMPLEMENTATION.md",
        )]
        for document in documents:
            for target in re.findall(r"\[[^\]\n]+\]\(([^)]+)\)",
                                     document.read_text(encoding="utf-8")):
                parsed = urlsplit(target)
                if parsed.scheme or parsed.netloc or not parsed.path:
                    continue
                with self.subTest(document=document.name, target=target):
                    resolved = (document.parent / unquote(parsed.path)).resolve()
                    self.assertTrue(resolved.is_relative_to(ROOT))
                    self.assertTrue(resolved.is_file(), f"Broken link: {target}")

    def test_public_install_instructions_match_one_standalone_skill(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("npx skills@latest add grove/faultline", readme)
        self.assertIn("Use faultline-audit to check my changes.", readme)
        self.assertIn("It does not change files or run tests", readme)
        self.assertIn("NO_GO / UNAVAILABLE",
                      (ROOT / "docs/maintaining.md").read_text(encoding="utf-8"))
        self.assertEqual(install_check.SKILL_NAME, "faultline-audit")
        self.assertEqual(
            install_check.payload(ROOT / "faultline-audit"),
            {name: install_check.payload(ROOT / "faultline-audit")[name]
             for name in ("SKILL.md", "agents/openai.yaml")},
        )

    def test_full_payload_survives_copy_and_drift_is_rejected(self):
        source = ROOT / "faultline-audit"
        with tempfile.TemporaryDirectory() as temporary:
            installed = Path(temporary) / ".agents" / "skills" / "faultline-audit"
            installed.parent.mkdir(parents=True)
            shutil.copytree(source, installed)
            self.assertEqual(install_check.verify_payload(source, installed), 2)
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
