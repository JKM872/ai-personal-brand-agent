"""
Runtime mode (DRY_RUN / OFFLINE) shared by all publishers and scouts.

- DRY_RUN=1/true/yes  -> nothing is sent to external platforms
- DRY_RUN=0/false/no  -> live where the channel's keys are configured
- empty/other         -> auto: dry-run unless at least one write key is configured
- OFFLINE=1           -> scouts read sources/fixtures/*.json instead of the network

Keys are resolved by agents.free_ai_router._load_key (env -> .env -> config/accounts*.json).
"""

import os

from agents.free_ai_router import _load_key

WRITE_KEYS = ["WEBHOOK_URL", "TELEGRAM_BOT_TOKEN", "LINKEDIN_ACCESS_TOKEN", "BREVO_API_KEY",
              "RESEND_API_KEY", "INDEXNOW_KEY", "CMS_GH_TOKEN", "WP_APP_PASSWORD", "CMS_WEBHOOK_URL"]

_TRUE = ("1", "true", "yes")
_FALSE = ("0", "false", "no")
_warned = set()


def is_dry_run() -> bool:
    raw = os.environ.get("DRY_RUN", "").strip().lower()
    if raw in _TRUE:
        return True
    if raw in _FALSE:
        return False
    if raw and raw not in _warned:
        _warned.add(raw)
        print(f"[WARN] DRY_RUN={raw} nierozpoznane, tryb auto")
    return not any(_load_key(k) for k in WRITE_KEYS)


def is_offline() -> bool:
    return os.environ.get("OFFLINE", "").strip().lower() in _TRUE


def load_fixture(name: str, scout: str, limit: int) -> list:
    """Reads sources/fixtures/<name>.json (used when OFFLINE=1)."""
    import json
    from pathlib import Path
    path = Path(__file__).parent.parent.resolve() / "sources" / "fixtures" / f"{name}.json"
    print(f"[OFFLINE] {scout}: fixture")
    try:
        return json.loads(path.read_text(encoding="utf-8"))[:limit]
    except Exception as e:
        print(f"[WARN] {scout}: brak fixture {path.name}: {e}")
        return []


def log_skip(service: str, action: str) -> None:
    print(f"[DRY_RUN] {service}: {action} pominięta")


def channel_live(*keys) -> bool:
    """True only when not in dry-run and every given key is configured."""
    if is_dry_run():
        return False
    return all(_load_key(k) for k in keys)
