"""
Polsia-Style Autonomous Project DNA Scanner.
Connects to ANY website URL, extracts title, meta description, headings, value proposition,
and adapts the entire AI agent workforce to the target project and industry.
"""

import re
import json
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.resolve()
PROFILE_PATH = BASE_DIR / "saas_core" / "product_profile.json"

class WebsiteMetaParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_title = False
        self.in_h1 = False
        self.in_h2 = False
        self.title = ""
        self.description = ""
        self.h1s = []
        self.h2s = []

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict((k.lower(), v) for k, v in attrs if k)
        if tag == "title":
            self.in_title = True
        elif tag == "h1":
            self.in_h1 = True
        elif tag == "h2":
            self.in_h2 = True
        elif tag == "meta":
            name = (attrs_dict.get("name") or attrs_dict.get("property") or "").lower()
            content = attrs_dict.get("content", "")
            if name in ("description", "og:description") and content and not self.description:
                self.description = content.strip()

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False
        elif tag == "h1":
            self.in_h1 = False
        elif tag == "h2":
            self.in_h2 = False

    def handle_data(self, data):
        text = " ".join(data.split())
        if not text:
            return
        if self.in_title and not self.title:
            self.title = text
        elif self.in_h1 and len(self.h1s) < 5:
            self.h1s.append(text)
        elif self.in_h2 and len(self.h2s) < 8:
            self.h2s.append(text)

def scan_website_dna(url: str) -> dict:
    """
    Scrapes a target website URL and builds an adaptive Project DNA profile.
    """
    if not url.startswith("http"):
        url = "https://" + url

    parsed_meta = {"title": "", "description": "", "h1s": [], "h2s": []}
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (compatible; PolsiaAutonomousAgent/2.0)"}
        )
        with urllib.request.urlopen(req, timeout=12) as resp:
            raw_html = resp.read().decode("utf-8", errors="ignore")
        parser = WebsiteMetaParser()
        parser.feed(raw_html)
        parsed_meta = {
            "title": parser.title,
            "description": parser.description,
            "h1s": parser.h1s,
            "h2s": parser.h2s
        }
    except Exception as e:
        print(f"[WARN] Nie udało się pobrać HTML z {url}: {e}")

    from agents.free_ai_router import ask_free_ai

    domain = url.replace("https://", "").replace("http://", "").split("/")[0]
    brand_name = parsed_meta["title"].split("|")[0].split("-")[0].strip() if parsed_meta["title"] else domain

    # Try AI synthesis if keys are available
    prompt = f"""Przeanalizuj dane pobrane ze strony internetowej projektu:
URL: {url}
Title: {parsed_meta['title']}
Meta Description: {parsed_meta['description']}
Nagłówki H1: {parsed_meta['h1s']}
Nagłówki H2: {parsed_meta['h2s']}

Zwróć poprawny obiekt JSON z polami:
- product_name (krótka nazwa marki/produktu)
- tagline (1 zdanie propozycji wartości)
- category (branża/kategoria)
- target_audience (grupa docelowa)
- primary_problem_solved (jaki główny problem klienta rozwiązuje)
- industry_keywords (lista 5 słów kluczowych do wyszukiwania trendów i artykułów SEO)
- key_features (lista 3 głównych korzyści/funkcji)
Tylko czysty JSON bez bloków markdown."""

    ai_resp = ask_free_ai(
        "Jesteś analitykiem produktowym SaaS. Zwracasz wyłącznie poprawny JSON.",
        prompt
    )

    profile = None
    try:
        json_match = re.search(r"\{.*\}", ai_resp, re.DOTALL)
        if json_match:
            profile = json.loads(json_match.group(0))
    except Exception:
        profile = None

    if not profile or not isinstance(profile, dict) or "product_name" not in profile:
        profile = {
            "product_name": brand_name or "Twój Projekt",
            "tagline": parsed_meta["description"] or (parsed_meta["h1s"][0] if parsed_meta["h1s"] else f"Nowoczesna platforma cyfrowa ({domain})"),
            "website_url": url,
            "pricing_model": "Darmowy start / Elastyczne plany",
            "category": "SaaS & Rozwiązania Cyfrowe",
            "target_audience": "Klienci biznesowi (B2B), twórcy i zespoły szukające automatyzacji",
            "primary_problem_solved": parsed_meta["description"] or "Automatyzacja procesów, oszczędność czasu i skalowanie wyników biznesowych bez ręcznej pracy",
            "industry_keywords": ["automation", "saas", "ai", "productivity", "growth"],
            "key_features": (parsed_meta["h2s"][:3] if len(parsed_meta["h2s"]) >= 3 else [
                "Szybkie wdrożenie i intuicyjna obsługa w chmurze",
                "Automatyzacja powtarzalnych zadań i procesów",
                "Mierzalny zwrot z inwestycji i pełna analityka"
            ]),
            "competitors_for_comparison": [
                "Tradycyjne, czasochłonne procesy ręczne",
                "Kosztowne agencje zewnętrzne",
                "Rozproszone narzędzia bez integracji"
            ],
            "call_to_action": {
                "text": "Sprawdź na żywo i zacznij za darmo",
                "url": url
            },
            "cms_permissions": {
                "owner_authorized": False,
                "publish_mode": "require_approval",
                "cms_type": "github_markdown",
                "target_branch": "main",
                "content_Folder": "public/articles"
            }
        }
    else:
        profile["website_url"] = url
        profile.setdefault("call_to_action", {"text": "Wypróbuj teraz", "url": url})
        profile.setdefault("cms_permissions", {
            "owner_authorized": False,
            "publish_mode": "require_approval",
            "cms_type": "github_markdown"
        })

    PROFILE_PATH.parent.mkdir(parents=True, exist_ok=True)
    PROFILE_PATH.write_text(json.dumps(profile, indent=2, ensure_ascii=False), encoding="utf-8")
    return profile
