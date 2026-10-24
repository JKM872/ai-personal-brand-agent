"""
Technical Integration & GEO Schema Generator (Polsia Multi-Tenant SaaS).
Generates project-specific JSON-LD Schema.org markup, /llms.txt specification,
and a Python CMS Webhook receiver for the client's website.
"""

import json
from agents.geo_seo_engine import load_product_profile

def generate_github_content(topic, persona):
    profile = load_product_profile()
    pname = profile.get("product_name", "Autonoma AI")
    purl = profile.get("website_url", "https://twoja-domena.pl")
    pcat = profile.get("category", "SaaS")
    ptagline = profile.get("tagline", "")
    cms_type = profile.get("cms_permissions", {}).get("cms_type", "github_markdown")

    schema_obj = {
        "@context": "https://schema.org",
        "@type": "SoftwareApplication",
        "name": pname,
        "url": purl,
        "applicationCategory": pcat,
        "operatingSystem": "Web, Cloud",
        "description": ptagline,
        "offers": {"@type": "Offer", "price": "0", "priceCurrency": "PLN"}
    }

    readme = f"""# 🔌 Pakiet Integracyjny Strony (GEO Schema + Tracker + CMS) — {pname}

Gotowy pakiet wdrożeniowy dla domeny **{purl}** (Tryb CMS: `{cms_type}`).
Wklej poniższy znacznik `JSON-LD` w sekcji `<head>` swojej strony, aby roboty **ChatGPT Search (GPTBot)**, **Perplexity** oraz **Google** natychmiast indeksowały Twój produkt.

## 1. Kod Schema.org JSON-LD (Wklej do `<head>`)

```html
<script type="application/ld+json">
{json.dumps(schema_obj, indent=2, ensure_ascii=False)}
</script>
<script src="/tracker.js" defer></script>
```
"""

    demo_code = f"""# cms_receiver_example.py
# Przykładowy odbiornik Webhooka CMS dla projektu: {pname} ({purl})
# Pozwala agentowi Autonoma AI publikować artykuły SEO/GEO po autoryzacji właściciela.

import os
import json
from pathlib import Path

EXPECTED_OWNER_TOKEN = os.environ.get("CMS_API_KEY", "twoj_sekretny_klucz_wlasciciela")

def handle_incoming_article_webhook(headers: dict, payload: dict) -> dict:
    auth_header = headers.get("Authorization", "")
    if auth_header != f"Bearer {{EXPECTED_OWNER_TOKEN}}":
        return {{"status": 403, "error": "Brak autoryzacji właściciela strony (Owner Permission Denied)"}}

    slug = payload.get("slug", "nowy-artykul")
    markdown_body = payload.get("markdown", "")

    output_path = Path("content/blog") / f"{{slug}}.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(markdown_body, encoding="utf-8")

    return {{
        "status": 200,
        "project": "{pname}",
        "published_path": str(output_path)
    }}
"""

    return {
        "readme": readme.strip(),
        "demo_code": demo_code.strip()
    }
