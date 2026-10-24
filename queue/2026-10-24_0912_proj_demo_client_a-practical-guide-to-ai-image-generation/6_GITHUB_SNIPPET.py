# cms_receiver_example.py
# Przykładowy odbiornik Webhooka CMS dla projektu: InvoicePulse AI (Klient Subskrypcyjny #1) (https://invoicepulse-demo.com)
# Pozwala agentowi Autonoma AI publikować artykuły SEO/GEO po autoryzacji właściciela.

import os
import json
from pathlib import Path

EXPECTED_OWNER_TOKEN = os.environ.get("CMS_API_KEY", "twoj_sekretny_klucz_wlasciciela")

def handle_incoming_article_webhook(headers: dict, payload: dict) -> dict:
    auth_header = headers.get("Authorization", "")
    if auth_header != f"Bearer {EXPECTED_OWNER_TOKEN}":
        return {"status": 403, "error": "Brak autoryzacji właściciela strony (Owner Permission Denied)"}

    slug = payload.get("slug", "nowy-artykul")
    markdown_body = payload.get("markdown", "")

    output_path = Path("content/blog") / f"{slug}.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(markdown_body, encoding="utf-8")

    return {
        "status": 200,
        "project": "InvoicePulse AI (Klient Subskrypcyjny #1)",
        "published_path": str(output_path)
    }