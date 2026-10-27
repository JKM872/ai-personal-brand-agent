"""
Agent: Newsletter Engine (Autonoma AI — Employee #8, 0,00 PLN).
Integrates with Brevo API (up to 300 free emails/day) & Resend API (up to 100/day).
Sends ONLY to subscribers with recorded consent (consent_at set, not unsubscribed).
Called by publish.py for approved bundles; in dry-run it writes a preview file instead of sending.
"""

import sys
import json
import urllib.request
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.resolve()
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from db.supabase_client import db
from agents.free_ai_router import _load_key
from agents.runtime import is_dry_run, log_skip


def unsubscribe_footer() -> str:
    contact = _load_key("CONTACT_EMAIL") or "kontakt@twoja-domena.pl"
    return (
        "<hr><p style='font-size:12px;color:#666'>Otrzymujesz tę wiadomość, bo zapisałeś(-aś) się do newslettera. "
        f"<a href=\"mailto:{contact}?subject=Wypisz\">Wypisz się</a> — odpowiemy i usuniemy Twój adres.</p>"
    )


def send_newsletter_batch(subject: str, html_content: str, sender_name: str = "Autonoma AI Digest",
                          sender_email: str = None, queue_dir: Path = None):
    """
    Sends a newsletter batch to up to 280 consenting subscribers (below Brevo's 300/day free limit).
    Dry-run (or no sender / no provider key): writes queue_dir/NEWSLETTER_PREVIEW.html (if queue_dir given).
    """
    sender_email = sender_email or _load_key("NEWSLETTER_FROM")
    html_full = html_content + unsubscribe_footer()
    subs = db.get_active_subscribers(limit=280)

    brevo_key = _load_key("BREVO_API_KEY")
    resend_key = _load_key("RESEND_API_KEY")

    if is_dry_run() or not sender_email or not (brevo_key or resend_key):
        log_skip("Newsletter", f"wysyłka do {len(subs)} subskrybentów ze zgodą")
        result = {"status": "dry_run", "count": len(subs)}
        if queue_dir is not None:
            preview = Path(queue_dir) / "NEWSLETTER_PREVIEW.html"
            preview.write_text(html_full, encoding="utf-8")
            result["file"] = str(preview)
        return result

    if not subs:
        print("[INFO] Brak subskrybentów z udokumentowaną zgodą (consent_at).")
        return {"status": "no_subscribers", "count": 0}

    # 1. Brevo API (300 maili/dzień za darmo)
    if brevo_key:
        print(f"📧 [BREVO API] Wysyłka do {len(subs)} subskrybentów...")
        headers = {"api-key": brevo_key, "Content-Type": "application/json"}
        sent_count = 0
        for sub in subs:
            payload = {
                "sender": {"name": sender_name, "email": sender_email},
                "to": [{"email": sub["email"]}],
                "subject": subject,
                "htmlContent": html_full
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
                print(f"[WARN] Błąd wysyłki Brevo: {e}")
        return {"status": "sent", "provider": "brevo", "count": sent_count}

    # 2. Resend API (100 maili/dzień)
    print(f"📧 [RESEND API] Wysyłka do {len(subs)} subskrybentów...")
    headers = {"Authorization": f"Bearer {resend_key}", "Content-Type": "application/json"}
    sent_count = 0
    for sub in subs:
        payload = {
            "from": f"{sender_name} <{sender_email}>",
            "to": [sub["email"]],
            "subject": subject,
            "html": html_full
        }
        try:
            req = urllib.request.Request(
                "https://api.resend.com/emails",
                data=json.dumps(payload).encode("utf-8"),
                headers=headers,
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=15):
                sent_count += 1
        except Exception as e:
            print(f"[WARN] Błąd wysyłki Resend: {e}")
    return {"status": "sent", "provider": "resend", "count": sent_count}


if __name__ == "__main__":
    test_html = "<h1>Cześć!</h1><p>Test podglądu newslettera.</p>"
    print("Wynik:", send_newsletter_batch("Test", test_html))
