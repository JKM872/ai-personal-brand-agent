"""
Autonomous Social Publisher Hub.
Connects generated content to LinkedIn, X/Twitter, GitHub, Telegram, and Make/n8n Webhooks.
Safely defaults to 'dry_run' mode until accounts are enabled in config/accounts.json.
"""

import os
import json
import urllib.request
from datetime import datetime
from pathlib import Path

CONFIG_FILE = Path(__file__).parent.parent / "config" / "accounts.json"

def load_accounts_config():
    cfg = {"mode": "dry_run", "channels": {}}
    if CONFIG_FILE.exists():
        cfg = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        
    # Cloud / GitHub Actions Secrets override
    env_webhook = os.environ.get("WEBHOOK_URL", "").strip()
    env_tg_token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    env_tg_chat = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
    
    if env_webhook:
        cfg["mode"] = "live"
        cfg.setdefault("channels", {})["webhook_automation"] = {
            "enabled": True,
            "webhook_url": env_webhook
        }
    if env_tg_token and env_tg_chat:
        cfg["mode"] = "live"
        cfg.setdefault("channels", {})["telegram_notifier"] = {
            "enabled": True,
            "bot_token": env_tg_token,
            "chat_id": env_tg_chat
        }
    return cfg

def send_webhook(webhook_url, payload):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        webhook_url,
        data=data,
        headers={"Content-Type": "application/json", "User-Agent": "PersonalBrandAgent/2.0"},
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

    # Universal payload for Make.com / n8n / Zapier / Buffer
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
        for ch_name in ["linkedin", "twitter_x", "github", "webhook_automation", "telegram_notifier"]:
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
                msg = f"🚀 *Nowa paczka treści AI wygenerowana!*\n\n*Temat:* {topic.get('title')}\n*Źródło:* {topic.get('url')}\n\n---\n{bundle['linkedin']['post'][:1000]}"
                code = send_telegram_notification(tg_cfg["bot_token"], tg_cfg["chat_id"], msg)
                results["dispatches"]["telegram_notifier"] = f"SENT (HTTP {code})"
            except Exception as e:
                results["dispatches"]["telegram_notifier"] = f"ERROR: {e}"

    # Save ready-to-send API payload & status inside queue folder
    (queue_dir / "7_API_PAYLOAD_READY.json").write_text(
        json.dumps(universal_payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (queue_dir / "PUBLISH_STATUS.json").write_text(
        json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return results
