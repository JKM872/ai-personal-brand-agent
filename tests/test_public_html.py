"""Validates public/*.html: balanced tags, lead form fields + endpoint, local links point to existing files."""
import unittest
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

PUBLIC = Path(__file__).parent.parent / "public"
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
FIELDS = {"name", "email", "company", "service", "message", "consent", "website", "ts"}


class Checker(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack, self.errors, self.links, self.forms, self.fields, self.required = [], [], [], [], set(), set()
        self._raw = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "form":
            self.forms.append(a)
        if tag in ("input", "select", "textarea") and a.get("name"):
            self.fields.add(a["name"])
            if "required" in a:
                self.required.add(a["name"])
        for k in ("href", "src"):
            if a.get(k):
                self.links.append(a[k])
        if tag not in VOID:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if not self.stack or self.stack[-1] != tag:
            self.errors.append(f"unexpected </{tag}> (open: {self.stack[-3:]})")
            if tag in self.stack:
                while self.stack and self.stack.pop() != tag:
                    pass
        else:
            self.stack.pop()


def check(path: Path) -> Checker:
    c = Checker()
    c.feed(path.read_text(encoding="utf-8"))
    c.close()
    return c


def local_target(href: str):
    if href.startswith(("http:", "https:", "mailto:", "tel:", "#", "//", "data:", "javascript:")) or "$" in href:
        return None
    path = urlparse(href).path
    if not path or path == "/":
        return PUBLIC / "index.html"
    return PUBLIC / path.lstrip("/")


class TestPublicHtml(unittest.TestCase):
    def test_all_pages_well_formed_and_links_exist(self):
        pages = sorted(PUBLIC.glob("*.html"))
        self.assertTrue(pages)
        for p in pages:
            c = check(p)
            self.assertEqual(c.errors, [], p.name)
            self.assertEqual(c.stack, [], f"{p.name}: unclosed {c.stack}")
            for href in c.links:
                t = local_target(href)
                if t is not None:
                    self.assertTrue(t.exists(), f"{p.name}: broken link {href}")

    def test_lead_forms(self):
        for name in ("index.html", "blog.html"):
            c = check(PUBLIC / name)
            self.assertTrue(any(f.get("action") == "/api/lead" for f in c.forms), name)
            self.assertTrue(FIELDS <= c.fields, f"{name}: missing {FIELDS - c.fields}")
            self.assertTrue({"name", "email", "consent"} <= c.required, name)

    def test_offer_has_cta_to_form(self):
        html = (PUBLIC / "index.html").read_text(encoding="utf-8")
        self.assertIn('href="#kontakt"', html)
        self.assertIn('id="kontakt"', html)
        self.assertIn('lang="pl"', html)


if __name__ == "__main__":
    unittest.main()
