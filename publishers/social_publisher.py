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

BASE_DIR = Path(__file__).parent.parent.resolve()
CONFIG_FILE = BASE_DIR / "config" / "accounts.json"
LOCAL_CONFIG_FILE = BASE_DIR / "config" / "accounts.local.json"

def load_accounts_config():
    cfg = {"mode": "dry_run", "channels": {}}
    for p in (CONFIG_FILE, LOCAL_CONFIG_FILE):
        if p.exists():
            try:
                loaded = json.loads(p.read_text(encoding="utf-8"))
                cfg.update(loaded)
            except Exception:
                pass

    channels = cfg.setdefault("channels", {})

    # 1. Webhook (Make.com / n8n / Zapier)
    wh_url = _load_key("WEBHOOK_URL") or channels.get("webhook_automation", {}).get("webhook_url", "").strip()
    if not _is_placeholder(wh_url):
        cfg["mode"] = "live"
        channels["webhook_automation"] = {"enabled": True, "webhook_url": wh_url}

    # 2. Telegram Notifier
    tg_token = _load_key("TELEGRAM_BOT_TOKEN") or channels.get("telegram_notifier", {}).get("bot_token", "").strip()
    tg_chat = _load_key("TELEGRAM_CHAT_ID") or channels.get("telegram_notifier", {}).get("chat_id", "").strip()
    if not _is_placeholder(tg_token) and not _is_placeholder(tg_chat):
        cfg["mode"] = "live"
        channels["telegram_notifier"] = {"enabled": True, "bot_token": tg_token, "chat_id": tg_chat}

    # 3. LinkedIn Direct API
    li_token = _load_key("LINKEDIN_ACCESS_TOKEN") or channels.get("linkedin", {}).get("access_token", "").strip()
    li_urn = _load_key("LINKEDIN_AUTHOR_URN") or channels.get("linkedin", {}).get("author_urn", "").strip()
    if not _is_placeholder(li_token) and not _is_placeholder(li_urn):
        cfg["mode"] = "live"
        channels["linkedin"] = {"enabled": True, "access_token": li_token, "author_urn": li_urn}

    # 4. Newsletter (Brevo / Resend)
    brevo_key = _load_key("BREVO_API_KEY")
    resend_key = _load_key("RESEND_API_KEY")
    if brevo_key or resend_key:
        cfg["mode"] = "live"
        channels["newsletter"] = {"enabled": True, "provider": "brevo" if brevo_key else "resend"}

    return cfg

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

def dispatch_content_bundle(topic, bundle, queue_dir):
    """
    Dispatches or queues the generated content bundle across all configured channels.
    """
    cfg = load_accounts_config()
    mode = cfg.get("mode", "dry_run")
    channels = cfg.get("channels", {})

    results = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "mode": mode,
        "topic": topic.get("title"),
        "dispatches": {}
    }

    universal_payload = {
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

    if mode == "dry_run":
        results["status_summary"] = "GOTOWE W KOLEJCE (Tryb Dry-Run — konta jeszcze niepodpięte)"
        for ch_name in ["linkedin", "twitter_x", "github", "webhook_automation", "telegram_notifier", "newsletter"]:
            results["dispatches"][ch_name] = "QUEUED_FOR_AUTO_PUBLISH"
    else:
        results["status_summary"] = "AUTOMATYCZNA PUBLIKACJA AKTYWNA (Tryb LIVE)"

        # 1. Webhook (Make / n8n / Zapier)
        wh_cfg = channels.get("webhook_automation", {})
        if wh_cfg.get("enabled") and wh_cfg.get("webhook_url"):
            try:
                code = send_webhook(wh_cfg["webhook_url"], universal_payload)
                results["dispatches"]["webhook_automation"] = f"SENT (HTTP {code})"
            except Exception as e:
                results["dispatches"]["webhook_automation"] = f"ERROR: {e}"

        # 2. LinkedIn Direct API
        li_cfg = channels.get("linkedin", {})
        if li_cfg.get("enabled") and li_cfg.get("access_token"):
            try:
                code = post_to_linkedin(li_cfg["access_token"], li_cfg["author_urn"], bundle["linkedin"]["post"])
                results["dispatches"]["linkedin"] = f"PUBLISHED (HTTP {code})"
            except Exception as e:
                results["dispatches"]["linkedin"] = f"ERROR: {e}"

        # 3. Telegram Notification
        tg_cfg = channels.get("telegram_notifier", {})
        if tg_cfg.get("enabled") and tg_cfg.get("bot_token"):
            try:
                msg = f"🚀 *Autonoma AI — Nowa paczka 10 kanałów!*\n\n*Temat:* {topic.get('title')}\n*Źródło:* {topic.get('url')}\n\n---\n{bundle['linkedin']['post'][:1000]}"
                code = send_telegram_notification(tg_cfg["bot_token"], tg_cfg["chat_id"], msg)
                results["dispatches"]["telegram_notifier"] = f"SENT (HTTP {code})"
            except Exception as e:
                results["dispatches"]["telegram_notifier"] = f"ERROR: {e}"

        # 4. Newsletter (Brevo / Resend)
        nl_cfg = channels.get("newsletter", {})
        if nl_cfg.get("enabled"):
            try:
                from agents.newsletter_agent import send_newsletter_batch
                nl_res = send_newsletter_batch(
                    subject=f"📩 Biuletyn Strategiczny: {topic.get('title', 'Nowości')[:65]}",
                    html_content=f"<pre style='font-family:sans-serif;white-space:pre-wrap'>{bundle['newsletter']['newsletter']}</pre>"
                )
                results["dispatches"]["newsletter"] = f"{nl_res.get('status')} ({nl_res.get('count', 0)} odbiorców)"
            except Exception as e:
                results["dispatches"]["newsletter"] = f"ERROR: {e}"

    (queue_dir / "7_API_PAYLOAD_READY.json").write_text(
        json.dumps(universal_payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (queue_dir / "PUBLISH_STATUS.json").write_text(
        json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return results
