"""Check frozen design data without importing or executing any fixture code."""

import ast
import hashlib
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]


class SpikeDesignTests(unittest.TestCase):
    def test_frozen_sources_have_valid_syntax_and_matching_hashes(self):
        text = (ROOT / "experiments/lost-acknowledgement.md").read_text(encoding="utf-8")
        sources = re.findall(r"<!-- file: ([a-z_]+\.py) -->\n```python\n(.*?)```",
                             text, re.S)
        manifest = dict(re.findall(r"\| `([a-z_]+\.py)` \| `([0-9a-f]{64})` \|", text))
        self.assertEqual(len(sources), 3)
        self.assertEqual(set(manifest), {"deduplicating.py", "reapplying.py", "scenario.py"})
        self.assertEqual({name for name, _ in sources}, set(manifest))
        for name, source in sources:
            with self.subTest(file=name):
                ast.parse(source, filename=name)
                self.assertTrue(source.endswith("\n"))
                self.assertEqual(hashlib.sha256(source.encode("utf-8")).hexdigest(),
                                 manifest[name])


if __name__ == "__main__":
    unittest.main()
