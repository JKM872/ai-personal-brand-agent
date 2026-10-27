"""
Lead validation (same rules as functions/api/_lead_validate.js).
validate_lead(data, now_ms) -> (clean, errors)
  clean  = dict ready for db.insert_lead (or None when errors)
  errors = {field: code}; {"_spam": reason} means: answer 200 but do not store.
"""
import re
from datetime import datetime, timezone

EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]{2,}$")
SERVICES = ("audyt", "wdrozenie", "abonament", "inne")
LEAD_STATUSES = ("new", "contacted", "qualified", "proposal", "won", "lost")
CONSENT_TEXT_VERSION = "v1"
_CTRL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


def _clean(value, max_len=None):
    if value is None:
        return ""
    s = _CTRL_RE.sub("", str(value)).strip()
    return s


def validate_email(email: str) -> bool:
    return bool(email) and len(email) <= 254 and bool(EMAIL_RE.match(email))


def validate_lead(data: dict, now_ms: int = None, check_spam: bool = True):
    if not isinstance(data, dict):
        return None, {"_": "invalid_json"}
    if now_ms is None:
        now_ms = int(datetime.now(timezone.utc).timestamp() * 1000)

    if check_spam:
        if _clean(data.get("website")):
            return None, {"_spam": "honeypot"}
        ts = data.get("ts")
        if isinstance(ts, bool) or not isinstance(ts, (int, float)):
            try:
                ts = float(ts)
            except (TypeError, ValueError):
                return None, {"_spam": "no_ts"}
        if now_ms - ts < 3000:
            return None, {"_spam": "too_fast"}

    errors = {}
    name = _clean(data.get("name"))
    email = _clean(data.get("email")).lower()
    company = _clean(data.get("company"))
    message = _clean(data.get("message"))
    service = _clean(data.get("service"))

    if not name:
        errors["name"] = "required"
    elif len(name) > 100:
        errors["name"] = "too_long"
    if not email:
        errors["email"] = "required"
    elif not validate_email(email):
        errors["email"] = "invalid"
    if len(company) > 150:
        errors["company"] = "too_long"
    if len(message) > 2000:
        errors["message"] = "too_long"
    if service and service not in SERVICES:
        errors["service"] = "invalid"
    if data.get("consent") is not True:
        errors["consent"] = "required"

    utm = {}
    for k in ("utm_source", "utm_medium", "utm_campaign"):
        v = _clean(data.get(k))
        if len(v) > 100:
            errors[k] = "too_long"
        elif v:
            utm[k] = v

    if errors:
        return None, errors

    clean = {
        "tenant_id": "default",
        "name": name,
        "email": email,
        "company": company,
        "service_interest": service,
        "message": message,
        "source_utm": "&".join(f"{k}={v}" for k, v in utm.items()),
        "consent_at": datetime.now(timezone.utc).isoformat(),
        "consent_text_version": CONSENT_TEXT_VERSION,
        "status": "new",
    }
    return clean, {}
