"""Portable packaging checks; these do not qualify experiment isolation."""

import re
import shutil
import tempfile
import unittest
from pathlib import Path
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "faultline-audit" / "SKILL.md"


class SkillTests(unittest.TestCase):
    def test_single_canonical_skill_and_metadata(self):
        self.assertEqual(list(ROOT.rglob("SKILL.md")), [SKILL])
        text = SKILL.read_text(encoding="utf-8")
        match = re.match(r"\A---\n(.*?)\n---\n", text, re.S)
        self.assertIsNotNone(match, "Missing YAML frontmatter")
        # The package intentionally uses only two single-line plain YAML scalars.
        metadata = dict(line.split(": ", 1) for line in match[1].splitlines())
        self.assertEqual(set(metadata), {"name", "description"})
        self.assertEqual(metadata["name"], SKILL.parent.name)
        self.assertRegex(metadata["name"], r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
        self.assertLessEqual(len(metadata["name"]), 64)
        self.assertTrue(metadata["description"])
        self.assertLessEqual(len(metadata["description"]), 1024)
        for value in metadata.values():
            self.assertNotIn(": ", value)
            self.assertNotIn(" #", value)

    def test_standalone_copy_and_links(self):
        with tempfile.TemporaryDirectory() as temporary:
            installed = Path(temporary) / ".agents" / "skills" / "faultline-audit"
            installed.parent.mkdir(parents=True)
            shutil.copytree(SKILL.parent, installed)
            self.assertEqual((installed / "SKILL.md").read_bytes(), SKILL.read_bytes())
            self.assertEqual(list(installed.iterdir()), [installed / "SKILL.md"])
            links = re.findall(r"\[[^\]]+\]\(([^)]+)\)",
                               (installed / "SKILL.md").read_text(encoding="utf-8"))
            self.assertTrue(links)
            for link in links:
                parsed = urlsplit(link)
                self.assertEqual(parsed.scheme, "https")
                self.assertEqual(parsed.netloc, "github.com")
                self.assertTrue(parsed.path.startswith("/grove/faultline/"))
                if "/blob/main/" in parsed.path:
                    self.assertTrue((ROOT / parsed.path.split("/blob/main/", 1)[1]).is_file())
                else:
                    self.assertRegex(parsed.path, r"^/grove/faultline/issues/[1-9][0-9]*$")

    def test_release_execution_fence_and_outcome_contract(self):
        text = SKILL.read_text(encoding="utf-8")
        # These safety-critical instructions are the behavior this package ships.
        for instruction in (
            "**Release boundary: advice-only.** Do not run project code",
            "**NO_GO / UNAVAILABLE**",
            "**SKIP**",
            "**DIRECT TEST REVIEW**",
            "**three** concrete missing negative/boundary assertions",
            "**one targeted production-code mutation first**",
            "**ten-minute ceiling**",
            "**production code only**",
            "**unchanged candidate baseline**",
            "Zero executed means no mutation rate",
            "SKIP/direct-review decisions stay outside all mutation denominators",
        ):
            self.assertIn(instruction, " ".join(text.split()))
        statuses = set(re.findall(r"^\| `([A-Z_]+)` \|", text, re.M))
        self.assertEqual(statuses, {"KILLED", "SURVIVED", "INVALID", "INCONCLUSIVE",
                                    "UNAVAILABLE", "NOT_RUN"})
        self.assertNotRegex(text, r"(?m)^\s*(?:pip|npx|uvx|curl) ")


if __name__ == "__main__":
    unittest.main()
