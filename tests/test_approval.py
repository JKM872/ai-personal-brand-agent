import io
import json
import shutil
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path
from unittest import mock

import approve
import publish
from agents import runtime
from saas_core import tenants

REPO = Path(__file__).parent.parent.resolve()


def make_bundle(base: Path, name: str, tenant="default", with_approval=True, title="Testowy artykuł"):
    b = base / "queue" / name
    b.mkdir(parents=True)
    (b / "0_WEBSITE_SEO_ARTICLE.md").write_text(f"# {title}\n\ntreść", encoding="utf-8")
    (b / "1_LINKEDIN_POST.md").write_text("post", encoding="utf-8")
    (b / "4_NEWSLETTER_EDITION.md").write_text("# NL\n\ntekst", encoding="utf-8")
    (b / "7_API_PAYLOAD_READY.json").write_text("{}", encoding="utf-8")
    if with_approval:
        (b / "APPROVAL.json").write_text(json.dumps({
            "status": "pending_approval", "tenant_id": tenant, "project_id": "proj_x",
            "items": {k: "pending" for k in approve.ITEMS}, "published": {}}), encoding="utf-8")
    return b


class ApprovalTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        shutil.copytree(REPO / "tenants", self.tmp / "tenants")
        shutil.copytree(REPO / "brand_core", self.tmp / "brand_core")
        (self.tmp / "saas_core").mkdir()
        shutil.copy(REPO / "saas_core" / "projects.json", self.tmp / "saas_core" / "projects.json")
        (self.tmp / "public" / "articles").mkdir(parents=True)
        (self.tmp / "public" / "blog.html").write_text("<html><body><!-- LEADFORM:START --><!-- LEADFORM:END --></body></html>", encoding="utf-8")
        tenants.clear_cache()
        self.env = mock.patch.dict("os.environ", {"DRY_RUN": "1"})
        self.env.start()

    def tearDown(self):
        self.env.stop()
        tenants.clear_cache()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def run_cli(self, mod, *args):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = mod.main(["--base-dir", str(self.tmp), *args])
        return code, out.getvalue(), err.getvalue()

    def test_list_shows_pending_and_legacy(self):
        make_bundle(self.tmp, "2026-01-01_0000_proj_x_a")
        make_bundle(self.tmp, "2026-01-01_0000_proj_x_b", with_approval=False)
        code, out, _ = self.run_cli(approve, "list")
        self.assertEqual(code, 0)
        self.assertIn("pending_approval", out)
        self.assertIn("legacy", out)

    def test_approve_owner_copies_without_overwrite(self):
        (self.tmp / "public" / "articles" / "testowy-artykul.md").write_text("stary", encoding="utf-8")
        make_bundle(self.tmp, "2026-01-01_0000_proj_x_a")
        code, _, _ = self.run_cli(approve, "approve", "2026-01-01_0000_proj_x_a")
        self.assertEqual(code, 0)
        arts = self.tmp / "public" / "articles"
        self.assertEqual((arts / "testowy-artykul.md").read_text(encoding="utf-8"), "stary")
        self.assertTrue((arts / "testowy-artykul-2.md").exists())
        self.assertTrue((self.tmp / "public" / "llms.txt").exists())
        self.assertTrue((self.tmp / "public" / "sitemap.xml").exists())
        self.assertIn("ARTICLES:START", (self.tmp / "public" / "blog.html").read_text(encoding="utf-8"))
        data = json.loads((self.tmp / "queue" / "2026-01-01_0000_proj_x_a" / "APPROVAL.json").read_text(encoding="utf-8"))
        self.assertEqual(data["status"], "approved")
        self.assertEqual(data["published"]["website_article"]["via"], "approve")

    def test_non_owner_does_not_touch_public(self):
        make_bundle(self.tmp, "2026-01-01_0000_proj_x_demo", tenant="demo")
        self.run_cli(approve, "approve", "2026-01-01_0000_proj_x_demo")
        self.assertEqual(list((self.tmp / "public" / "articles").iterdir()), [])

    def test_reject_and_errors(self):
        make_bundle(self.tmp, "2026-01-01_0000_proj_x_a")
        make_bundle(self.tmp, "2026-01-01_0000_proj_x_b")
        self.assertEqual(self.run_cli(approve, "approve", "nie-ma")[0], 2)
        self.assertEqual(self.run_cli(approve, "approve", "2026-01-01_0000_proj_x_")[0], 2)
        self.assertEqual(self.run_cli(approve, "reject", "2026-01-01_0000_proj_x_a")[0], 0)
        bad = self.tmp / "queue" / "2026-01-01_0000_proj_x_b" / "APPROVAL.json"
        bad.write_text("{zły", encoding="utf-8")
        self.assertEqual(self.run_cli(approve, "show", "2026-01-01_0000_proj_x_b")[0], 3)
        self.assertEqual(bad.read_text(encoding="utf-8"), "{zły")

    def test_publish_skips_pending_and_dry_runs_approved(self):
        make_bundle(self.tmp, "2026-01-01_0000_proj_x_a")
        make_bundle(self.tmp, "2026-01-01_0000_proj_x_b")
        self.run_cli(approve, "approve", "2026-01-01_0000_proj_x_a")
        with mock.patch("urllib.request.urlopen") as up:
            code, out, _ = self.run_cli(publish)
            up.assert_not_called()
        self.assertEqual(code, 0)
        a = json.loads((self.tmp / "queue" / "2026-01-01_0000_proj_x_a" / "APPROVAL.json").read_text(encoding="utf-8"))
        b = json.loads((self.tmp / "queue" / "2026-01-01_0000_proj_x_b" / "APPROVAL.json").read_text(encoding="utf-8"))
        self.assertEqual(a["published"]["linkedin"]["status"], "DRY_RUN_SKIPPED")
        self.assertEqual(a["published"]["website_article"]["status"], "ok")
        self.assertEqual(b["published"], {})


if __name__ == "__main__":
    unittest.main()
