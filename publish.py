"""
Publikacja zatwierdzonych paczek (jedyne miejsce wołające sendery zewnętrzne).

  python publish.py [--base-dir DIR]

Dla każdej paczki ze statusem "approved" i każdego zatwierdzonego kanału, który nie ma
published[kanał].status == "ok": wysyła (gdy kanał jest live) albo zapisuje DRY_RUN_SKIPPED.
Wynik per kanał: ok | DRY_RUN_SKIPPED | error:<msg>. Exit 1 tylko gdy wszystkie próby live padły.
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_DIR = Path(__file__).parent.resolve()
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from agents.runtime import channel_live, log_skip
from agents.free_ai_router import _load_key
import approve

CMS_KEYS = {"github_markdown": "CMS_GH_TOKEN", "wordpress": "WP_APP_PASSWORD", "custom_webhook": "CMS_WEBHOOK_URL", "webhook": "CMS_WEBHOOK_URL"}


def _read(folder: Path, name: str) -> str:
    p = folder / name
    return p.read_text(encoding="utf-8") if p.exists() else ""


def _project(base: Path, project_id: str) -> dict:
    try:
        for p in json.loads((base / "saas_core" / "projects.json").read_text(encoding="utf-8")):
            if p.get("id") == project_id:
                return p
    except Exception:
        pass
    return {"id": project_id}


def publish_channel(channel: str, folder: Path, data: dict, base: Path) -> dict:
    """Returns {"status": "ok"|"DRY_RUN_SKIPPED"|"error:<msg>"}; never raises."""
    from publishers import social_publisher as sp
    try:
        if channel == "linkedin":
            if not channel_live("LINKEDIN_ACCESS_TOKEN", "LINKEDIN_AUTHOR_URN"):
                log_skip("LinkedIn", f"publikacja {folder.name}")
                return {"status": "DRY_RUN_SKIPPED"}
            return sp._post_linkedin(_read(folder, "1_LINKEDIN_POST.md"), sp.load_channel_config()["linkedin"])
        if channel == "webhook":
            if not channel_live("WEBHOOK_URL"):
                log_skip("Webhook", f"wysyłka {folder.name}")
                return {"status": "DRY_RUN_SKIPPED"}
            payload = json.loads(_read(folder, "7_API_PAYLOAD_READY.json") or "{}")
            return sp._post_webhook(payload, sp.load_channel_config()["webhook"])
        if channel == "telegram":
            if not channel_live("TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID"):
                log_skip("Telegram", f"powiadomienie {folder.name}")
                return {"status": "DRY_RUN_SKIPPED"}
            files = ", ".join(sorted(p.name for p in folder.iterdir()))
            return sp._post_telegram(f"Zatwierdzona paczka: {folder.name}\nPliki: {files}", sp.load_channel_config()["telegram"])
        if channel == "newsletter":
            if not (channel_live("BREVO_API_KEY", "NEWSLETTER_FROM") or channel_live("RESEND_API_KEY", "NEWSLETTER_FROM")):
                log_skip("Newsletter", f"wysyłka {folder.name}")
                return {"status": "DRY_RUN_SKIPPED"}
            from agents.newsletter_agent import send_newsletter_batch
            md = _read(folder, "4_NEWSLETTER_EDITION.md")
            subject = next((l[2:].strip() for l in md.splitlines() if l.startswith("# ")), "Newsletter")[:90]
            res = send_newsletter_batch(subject, approve._md_to_html(md), sender_email=_load_key("NEWSLETTER_FROM"), queue_dir=folder)
            return {"status": "ok" if res.get("status") in ("sent", "no_subscribers") else f"error:{res.get('status')}", "count": res.get("count", 0)}
        if channel == "website_article":
            if approve.is_owner_tenant(data.get("tenant_id", "default"), base):
                return {"status": "DRY_RUN_SKIPPED", "note": "właściciel: publikuje approve.py"}
            cms_type = _load_key("CMS_TYPE") or "github_markdown"
            key = CMS_KEYS.get(cms_type, "CMS_GH_TOKEN")
            if not channel_live(key) or (_load_key("CMS_OWNER_AUTHORIZED") or "false").lower() != "true":
                log_skip("CMS", f"publikacja artykułu {folder.name}")
                return {"status": "DRY_RUN_SKIPPED"}
            from publishers.cms_connector import publish_article_to_website
            from publishers.indexnow import submit_to_indexnow
            md = _read(folder, "0_WEBSITE_SEO_ARTICLE.md")
            title = next((l[2:].strip() for l in md.splitlines() if l.startswith("# ")), folder.name)
            project = _project(base, data.get("project_id", ""))
            article = {"title": title, "slug": approve._article_slug(md, folder), "markdown": md}
            res = publish_article_to_website(article, project, force_owner_override=True)
            if "PUBLISHED" not in res.get("status", ""):
                return {"status": f"error:{res.get('status')}"}
            url = project.get("website_url", "").rstrip("/")
            host = url.replace("https://", "").replace("http://", "").split("/")[0]
            if host:
                submit_to_indexnow(host, [f"{url}/articles/{article['slug']}"])
            return {"status": "ok"}
        return {"status": f"error:nieznany kanał {channel}"}
    except Exception as e:
        return {"status": f"error:{e}"}


def run(base: Path) -> int:
    live_attempts = live_failures = 0
    for folder in approve.bundles(base):
        try:
            data, exists = approve.read_approval(folder)
        except approve.ApprovalError as e:
            print(str(e))
            continue
        if not exists or data.get("status") != "approved":
            continue
        published = data.setdefault("published", {})
        for ch, st in (data.get("items") or {}).items():
            if st != "approved" or published.get(ch, {}).get("status") == "ok":
                continue
            res = publish_channel(ch, folder, data, base)
            res["at"] = datetime.now().isoformat(timespec="seconds")
            published[ch] = res
            if res["status"] != "DRY_RUN_SKIPPED":
                live_attempts += 1
                if res["status"].startswith("error"):
                    live_failures += 1
                    print(f"[ERROR] publish {folder.name}/{ch}: {res['status']}")
            print(f"{folder.name} / {ch}: {res['status']}")
        approve.write_approval(folder, data)
    return 1 if live_attempts and live_failures == live_attempts else 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Publikacja zatwierdzonych paczek")
    ap.add_argument("--base-dir", default=str(BASE_DIR), help=argparse.SUPPRESS)
    args = ap.parse_args(argv)
    return run(Path(args.base_dir).resolve())


if __name__ == "__main__":
    sys.exit(main())
