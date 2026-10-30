"""End-to-end: engine.py in a temp copy, no keys, OFFLINE=1. Skip with SKIP_E2E=1."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).parent.parent.resolve()
IGNORE = shutil.ignore_patterns(".git", ".agents", "__pycache__", ".env", "accounts.local.json", "exports")


@unittest.skipIf(os.environ.get("SKIP_E2E") == "1", "SKIP_E2E=1")
class EngineDryRunTests(unittest.TestCase):
    def test_engine_dry_run(self):
        tmp = Path(tempfile.mkdtemp()) / "repo"
        try:
            shutil.copytree(REPO, tmp, ignore=IGNORE)
            before_articles = set(p.name for p in (tmp / "public" / "articles").glob("*"))
            before_queue = set(p.name for p in (tmp / "queue").iterdir())
            profile = tmp / "saas_core" / "product_profile.json"
            before_profile = profile.read_bytes() if profile.exists() else None
            env = {k: v for k, v in os.environ.items()
                   if not any(s in k for s in ("KEY", "TOKEN", "WEBHOOK", "SUPABASE", "CMS_", "LINKEDIN", "TELEGRAM"))}
            env.update({"OFFLINE": "1", "DRY_RUN": "", "PYTHONIOENCODING": "utf-8", "LOCAL_DB_PATH": str(tmp / "db" / "test.db")})
            r = subprocess.run([sys.executable, "engine.py"], cwd=tmp, env=env, capture_output=True, text=True,
                               encoding="utf-8", errors="replace", timeout=300)
            self.assertEqual(r.returncode, 0, r.stdout[-2000:] + r.stderr[-2000:])
            self.assertNotIn("Traceback", r.stdout + r.stderr)
            new = [tmp / "queue" / n for n in set(p.name for p in (tmp / "queue").iterdir()) - before_queue]
            new = [p for p in new if p.is_dir()]
            self.assertTrue(new)
            for b in new:
                data = json.loads((b / "APPROVAL.json").read_text(encoding="utf-8"))
                self.assertEqual(data["status"], "pending_approval")
                self.assertTrue((b / "PUBLISH_STATUS.json").exists())
            self.assertEqual(set(p.name for p in (tmp / "public" / "articles").glob("*")), before_articles)
            self.assertEqual(profile.read_bytes() if profile.exists() else None, before_profile)
        finally:
            shutil.rmtree(tmp.parent, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
