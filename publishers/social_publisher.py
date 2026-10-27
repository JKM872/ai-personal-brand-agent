"""
Autonomous Social Publisher Hub (Autonoma AI Workforce).
Connects generated content to Make/n8n Webhooks, LinkedIn, Telegram, and Brevo/Resend Newsletter.
Automatically detects credentials from .env, OS environment, config/accounts.local.json, or config/accounts.json.
Safely defaults to 'dry_run' mode per channel until credentials are provided.
"""

import json
import urllib.request
from datetime import datetime
from pathlib import Path
from agents.free_ai_router import _load_key, _is_placeholder
from agents.runtime import is_dry_run, log_skip

BASE_DIR = Path(__file__).parent.parent.resolve()
CONFIG_FILE = BASE_DIR / "config" / "accounts.json"
LOCAL_CONFIG_FILE = BASE_DIR / "config" / "accounts.local.json"

def _load_file_channels() -> dict:
    """Legacy channel settings from config/accounts*.json (keys in env/.env take precedence)."""
    channels = {}
    for p in (CONFIG_FILE, LOCAL_CONFIG_FILE):
        if p.exists():
            try:
                loaded = json.loads(p.read_text(encoding="utf-8"))
                channels.update(loaded.get("channels", {}) or {})
            except Exception:
                pass
    return channels

def _val(key: str, section: dict, field: str) -> str:
    v = _load_key(key) or str((section or {}).get(field, "") or "").strip()
    return "" if _is_placeholder(v) else v

def load_channel_config() -> dict:
    """Resolved credentials per channel (may be empty strings)."""
    ch = _load_file_channels()
    return {
        "webhook": {"webhook_url": _val("WEBHOOK_URL", ch.get("webhook_automation"), "webhook_url")},
        "telegram": {"bot_token": _val("TELEGRAM_BOT_TOKEN", ch.get("telegram_notifier"), "bot_token"),
                     "chat_id": _val("TELEGRAM_CHAT_ID", ch.get("telegram_notifier"), "chat_id")},
        "linkedin": {"access_token": _val("LINKEDIN_ACCESS_TOKEN", ch.get("linkedin"), "access_token"),
                     "author_urn": _val("LINKEDIN_AUTHOR_URN", ch.get("linkedin"), "author_urn")},
        "newsletter": {"brevo": _load_key("BREVO_API_KEY"), "resend": _load_key("RESEND_API_KEY"),
                       "sender": _load_key("NEWSLETTER_FROM")},
    }

def resolve_channel_modes(cfg: dict = None) -> dict:
    """Returns {"webhook": "live|dry_run", ...}. A channel is live only outside dry-run with all its keys set."""
    cfg = cfg or load_channel_config()
    dry = is_dry_run()
    nl = cfg["newsletter"]
    ready = {
        "webhook": bool(cfg["webhook"]["webhook_url"]),
        "telegram": bool(cfg["telegram"]["bot_token"] and cfg["telegram"]["chat_id"]),
        "linkedin": bool(cfg["linkedin"]["access_token"] and cfg["linkedin"]["author_urn"]),
        "newsletter": bool((nl["brevo"] or nl["resend"]) and nl["sender"]),
    }
    return {k: ("live" if (ok and not dry) else "dry_run") for k, ok in ready.items()}

def load_accounts_config():
    """Backward-compatible summary: global mode is live only when >=1 channel is live."""
    modes = resolve_channel_modes()
    return {"mode": "live" if "live" in modes.values() else "dry_run", "channels": modes}

def send_webhook(webhook_url, payload):
    if "discord.com/api/webhooks" in webhook_url or "discordapp.com/api/webhooks" in webhook_url:
        discord_body = {
            "content": (
                f"🚀 **Autonoma AI — Nowa Paczka 10 Kanałów Gotowa!**\n"
                f"**Temat:** {payload.get('topic_title', '')}\n\n"
                f"**Post LinkedIn:**\n{payload.get('linkedin_post', '')[:1200]}\n\n"
                f"**Wątek X/Twitter:**\n{payload.get('twitter_thread', '')[:500]}"
            )[:1990]
        }
        data = json.dumps(discord_body).encode("utf-8")
    else:
        data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        webhook_url,
        data=data,
        headers={"Content-Type": "application/json", "User-Agent": "AutonomaAIAgent/2.0"},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return resp.status

def send_telegram_notification(bot_token, chat_id, message):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message[:4000],
        "parse_mode": "Markdown"
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return resp.status

def post_to_linkedin(access_token, author_urn, text):
    url = "https://api.linkedin.com/v2/ugcPosts"
    payload = {
        "author": author_urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": text},
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0"
        },
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return resp.status

def _post_webhook(payload: dict, cfg: dict) -> dict:
    url = (cfg or {}).get("webhook_url", "")
    if not url:
        return {"status": "error:brak WEBHOOK_URL"}
    try:
        code = send_webhook(url, payload)
        return {"status": "ok", "http": code}
    except Exception as e:
        return {"status": f"error:{e}"}

def _post_linkedin(text: str, cfg: dict) -> dict:
    cfg = cfg or {}
    if not (cfg.get("access_token") and cfg.get("author_urn")):
        return {"status": "error:brak LINKEDIN_ACCESS_TOKEN/LINKEDIN_AUTHOR_URN"}
    try:
        code = post_to_linkedin(cfg["access_token"], cfg["author_urn"], text)
        return {"status": "ok", "http": code}
    except Exception as e:
        return {"status": f"error:{e}"}

def _post_telegram(text: str, cfg: dict) -> dict:
    cfg = cfg or {}
    if not (cfg.get("bot_token") and cfg.get("chat_id")):
        return {"status": "error:brak TELEGRAM_BOT_TOKEN/TELEGRAM_CHAT_ID"}
    try:
        code = send_telegram_notification(cfg["bot_token"], cfg["chat_id"], text)
        return {"status": "ok", "http": code}
    except Exception as e:
        return {"status": f"error:{e}"}

def build_universal_payload(topic: dict, bundle: dict) -> dict:
    return {
        "topic_title": topic.get("title"),
        "topic_url": topic.get("url"),
        "topic_source": topic.get("source"),
        "linkedin_post": bundle["linkedin"]["post"],
        "linkedin_carousel": bundle["linkedin"]["carousel"],
        "twitter_thread": bundle["twitter"]["thread"],
        "twitter_hooks": bundle["twitter"]["standalone_hooks"],
        "community_playbook": bundle.get("community", {}).get("community_playbook", ""),
        "ads_campaign": bundle.get("ads", {}).get("ads_campaign", ""),
        "outreach_playbook": bundle.get("outreach", {}).get("outreach_playbook", ""),
        "newsletter_markdown": bundle["newsletter"]["newsletter"],
        "video_script": bundle["video"]["video_script"],
        "github_code": bundle["github"]["demo_code"]
    }

def dispatch_content_bundle(topic, bundle, queue_dir, dry_run_only: bool = False):
    """
    Writes 7_API_PAYLOAD_READY.json + PUBLISH_STATUS.json for the bundle.
    dry_run_only=True (used by engine.py): nothing is sent; channels are AWAITING_APPROVAL
    until a human approves the bundle (approve.py) and publish.py sends it.
    """
    universal_payload = build_universal_payload(topic, bundle)
    cfg = load_channel_config()
    modes = resolve_channel_modes(cfg)
    any_live = "live" in modes.values()
    results = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "mode": "dry_run" if (dry_run_only or not any_live) else "live",
        "topic": topic.get("title"),
        "dispatches": {}
    }

    if dry_run_only or not any_live:
        results["status_summary"] = "GOTOWE W KOLEJCE — czeka na akceptację człowieka (python approve.py list)"
        for ch_name in ["website_article", "linkedin", "webhook", "telegram", "newsletter"]:
            results["dispatches"][ch_name] = "AWAITING_APPROVAL"
    else:
        results["status_summary"] = "PUBLIKACJA (tylko kanały z kluczami)"
        if modes["webhook"] == "live":
            results["dispatches"]["webhook"] = _post_webhook(universal_payload, cfg["webhook"])["status"]
        else:
            log_skip("Webhook", "wysyłka")
        if modes["linkedin"] == "live":
            results["dispatches"]["linkedin"] = _post_linkedin(bundle["linkedin"]["post"], cfg["linkedin"])["status"]
        else:
            log_skip("LinkedIn", "publikacja")
        if modes["telegram"] == "live":
            msg = f"🚀 *Autonoma AI — nowa paczka*\n\n*Temat:* {topic.get('title')}\n*Źródło:* {topic.get('url')}\n\n---\n{bundle['linkedin']['post'][:1000]}"
            results["dispatches"]["telegram"] = _post_telegram(msg, cfg["telegram"])["status"]
        else:
            log_skip("Telegram", "powiadomienie")
        if modes["newsletter"] == "live":
            try:
                from agents.newsletter_agent import send_newsletter_batch
                nl_res = send_newsletter_batch(
                    subject=f"📩 Biuletyn: {topic.get('title', 'Nowości')[:65]}",
                    html_content=f"<pre style='font-family:sans-serif;white-space:pre-wrap'>{bundle['newsletter']['newsletter']}</pre>",
                    sender_email=cfg["newsletter"]["sender"],
                    queue_dir=queue_dir,
                )
                results["dispatches"]["newsletter"] = f"{nl_res.get('status')} ({nl_res.get('count', 0)} odbiorców)"
            except Exception as e:
                results["dispatches"]["newsletter"] = f"error:{e}"
        else:
            log_skip("Newsletter", "wysyłka")

    (queue_dir / "7_API_PAYLOAD_READY.json").write_text(
        json.dumps(universal_payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (queue_dir / "PUBLISH_STATUS.json").write_text(
        json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return results
