"""
Tenant loader (multi-tenant foundation, no billing).
A tenant = brand persona + offer + site settings. Files live in tenants/<id>/tenant.json.
The "default" tenant is the owner's own brand (is_owner: true) — only it is published to public/.
"""

import json
import re
from pathlib import Path

from agents.free_ai_router import _load_key

BASE_DIR = Path(__file__).parent.parent.resolve()
TENANT_ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,39}$")
_cache = {}


def _read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate_tenant_id(tenant_id) -> str:
    if not tenant_id:
        return "default"
    if not isinstance(tenant_id, str) or not TENANT_ID_RE.match(tenant_id):
        raise ValueError(f"Nieprawidłowy tenant_id: {tenant_id!r}")
    return tenant_id


def load_tenant(tenant_id: str = "default", base_dir: Path = None) -> dict:
    """Returns {"id","display_name","persona","offer","site_url","contact_email","is_owner"}."""
    base = Path(base_dir) if base_dir else BASE_DIR
    tid = validate_tenant_id(tenant_id)
    key = (str(base), tid)
    if key in _cache:
        return _cache[key]

    tfile = base / "tenants" / tid / "tenant.json"
    if not tfile.exists() and tid != "default":
        print(f"[WARN] Brak tenants/{tid}/tenant.json — używam tenanta default")
        return load_tenant("default", base)

    raw = {}
    try:
        raw = _read_json(tfile)
    except Exception as e:
        print(f"[WARN] Nie można wczytać {tfile}: {e}")
        raw = {"id": tid, "display_name": "Marka właściciela", "is_owner": tid == "default"}

    display_name = raw.get("display_name", tid)
    persona = {"name": display_name}
    pfile = raw.get("persona_file")
    if pfile:
        try:
            loaded = _read_json(base / pfile)
            if isinstance(loaded, dict):
                persona = loaded
        except Exception as e:
            print(f"[WARN] Persona tenanta {tid} niedostępna ({pfile}): {e} — persona minimalna")
    else:
        print(f"[WARN] Tenant {tid} bez persona_file — persona minimalna")

    offer = {}
    ofile = raw.get("offer_file")
    if ofile:
        try:
            offer = _read_json(base / ofile)
        except Exception as e:
            print(f"[WARN] Oferta tenanta {tid} niedostępna ({ofile}): {e}")

    site_url = raw.get("site_url", "https://twoja-domena.pl")
    contact_email = raw.get("contact_email", offer.get("contact_email", ""))
    if tid == "default":
        site_url = _load_key("SITE_URL") or site_url
        contact_email = _load_key("CONTACT_EMAIL") or contact_email

    tenant = {
        "id": tid,
        "display_name": display_name,
        "persona": persona,
        "offer": offer,
        "site_url": site_url.rstrip("/"),
        "contact_email": contact_email,
        "is_owner": raw.get("is_owner") is True,
    }
    _cache[key] = tenant
    return tenant


def list_tenants(base_dir: Path = None) -> list:
    base = Path(base_dir) if base_dir else BASE_DIR
    root = base / "tenants"
    if not root.exists():
        return []
    return sorted(d.name for d in root.iterdir() if (d / "tenant.json").exists() and TENANT_ID_RE.match(d.name))


def clear_cache() -> None:
    _cache.clear()
