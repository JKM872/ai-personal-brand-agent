"""
Agent: Automated Newsletter Engine (Własna baza leadów za 0,00 PLN).
Integrates with Brevo API (up to 300 free emails/day) & Resend API (up to 100/day).
Pulls active leads from Supabase and delivers curated weekly digests with anti-spam pacing.
"""

import os
import sys
import time
import json
import random
import urllib.request
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.resolve()
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from db.supabase_client import db

def send_newsletter_batch(subject: str, html_content: str, sender_name: str = "AI Growth Digest", sender_email: str = "newsletter@twojadomena.pl"):
    """
    Sends a newsletter batch to up to 280 subscribers (staying safely below Brevo's 300/day free limit).
    """
    subs = db.get_active_subscribers(limit=280)
    if not subs:
        print("[INFO] Brak aktywnych subskrybentów w bazie newslettera.")
        return {"status": "no_subscribers", "count": 0}

    brevo_key = os.environ.get("BREVO_API_KEY", "").strip()
    resend_key = os.environ.get("RESEND_API_KEY", "").strip()
    
    # 1. Brevo API (300 maili/dzień za darmo)
    if brevo_key:
        print(f"📧 [BREVO API] Rozpoczynanie wysyłki do {len(subs)} subskrybentów...")
        headers = {
            "api-key": brevo_key,
            "Content-Type": "application/json"
        }
        sent_count = 0
        for sub in subs:
            payload = {
                "sender": {"name": sender_name, "email": sender_email},
                "to": [{"email": sub["email"]}],
                "subject": subject,
                "htmlContent": html_content
            }
            try:
                req = urllib.request.Request(
                    "https://api.brevo.com/v3/smtp/email",
                    data=json.dumps(payload).encode("utf-8"),
                    headers=headers,
                    method="POST"
                )
                with urllib.request.urlopen(req, timeout=15) as resp:
                    if resp.status in (200, 201):
                        sent_count += 1
            except Exception as e:
                print(f"[WARN] Błąd wysyłki do {sub['email']}: {e}")
            time.sleep(random.uniform(1.2, 3.0)) # Anti-spam pacing
        return {"status": "sent", "provider": "brevo", "count": sent_count}

    # 2. Resend API Fallback (100 maili/dzień)
    elif resend_key:
        print(f"📧 [RESEND API] Rozpoczynanie wysyłki do {len(subs)} subskrybentów...")
        headers = {
            "Authorization": f"Bearer {resend_key}",
            "Content-Type": "application/json"
        }
        sent_count = 0
        for sub in subs:
            payload = {
                "from": f"{sender_name} <{sender_email}>",
                "to": [sub["email"]],
                "subject": subject,
                "html": html_content
            }
            try:
                req = urllib.request.Request(
                    "https://api.resend.com/emails",
                    data=json.dumps(payload).encode("utf-8"),
                    headers=headers,
                    method="POST"
                )
                with urllib.request.urlopen(req, timeout=15) as resp:
                    sent_count += 1
            except Exception as e:
                print(f"[WARN] Błąd wysyłki Resend do {sub['email']}: {e}")
            time.sleep(random.uniform(1.0, 2.5))
        return {"status": "sent", "provider": "resend", "count": sent_count}

    # 3. Dry-Run / Queue Mode
    else:
        print(f"ℹ️ [DRY-RUN] Przygotowano biuletyn dla {len(subs)} subskrybentów (Klucz BREVO_API_KEY niepodpięty).")
        queue_file = BASE_DIR / "queue" / "last_newsletter_batch.html"
        queue_file.parent.mkdir(parents=True, exist_ok=True)
        queue_file.write_text(html_content, encoding="utf-8")
        return {"status": "dry_run", "count": len(subs), "file": str(queue_file)}

if __name__ == "__main__":
    test_html = "<h1>Cześć!</h1><p>Oto najnowsze zestawienie narzędzi AI i automatyzacji.</p>"
    res = send_newsletter_batch("🧠 Tygodniowy Przegląd Techniczny AI", test_html)
    print("Wynik wysyłki:", res)
