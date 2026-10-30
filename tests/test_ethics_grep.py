"""Code and docs must not contain platform-evasion / spam mechanics or invented statistics."""
import re
import unittest
from pathlib import Path

REPO = Path(__file__).parent.parent.resolve()
SKIP = ("queue", "public/articles", ".agents", ".git", "__pycache__", "tests", "admin")
PATTERNS = [re.compile(p, re.I) for p in (r"anti.?ban", r"jitter", r"human.?delay", r"zweryfikowana platforma", r"64%")]
START = re.compile(r"„START”|'START'|\"START\"|słowo „START")


def files():
    for ext in ("*.py", "*.js", "*.sql", "*.md", "*.html"):
        for f in REPO.rglob(ext):
            rel = f.relative_to(REPO).as_posix()
            if any(rel == s or rel.startswith(s + "/") for s in SKIP):
                continue
            yield rel, f


class EthicsTests(unittest.TestCase):
    def test_no_evasion_or_fake_data(self):
        hits = []
        for rel, f in files():
            text = f.read_text(encoding="utf-8", errors="replace")
            for p in PATTERNS:
                if p.search(text):
                    hits.append(f"{rel}: {p.pattern}")
            if START.search(text):
                hits.append(f"{rel}: START")
        self.assertEqual(hits, [])

    def test_anti_ban_module_removed(self):
        self.assertFalse((REPO / "agents" / "anti_ban_commenter.py").exists())


if __name__ == "__main__":
    unittest.main()
