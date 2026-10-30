"""
Autonoma AI — Local Server (localhost only, port 3000).
Serves the public site (public/) and the local admin panel (/admin/ from admin/), plus:
- POST /api/lead          -> validated lead saved to SQLite (or Supabase when configured)
- GET  /api/load-keys     -> which keys are set (values masked, never returned in full)
- POST /api/save-keys     -> merges non-empty values into .env (unknown keys are kept)
- POST /api/save-projects -> saves projects to saas_core/projects.json
Binds to LOCAL_BIND (default 127.0.0.1). No CORS headers: same-origin only.
"""

import os
import sys
import json
import time
import http.server
import socketserver
from pathlib import Path

BASE_DIR = Path(__file__).parent.resolve()
PUBLIC_DIR = BASE_DIR / "public"
ADMIN_DIR = BASE_DIR / "admin"
ENV_FILE = BASE_DIR / ".env"
PROJECTS_FILE = BASE_DIR / "saas_core" / "projects.json"
MAX_BODY = 64 * 1024

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from agents.free_ai_router import _load_key

# UI field -> env key
KEY_MAP = {
    "gemini": "GEMINI_API_KEY",
    "groq": "GROQ_API_KEY",
    "webhook": "WEBHOOK_URL",
    "linkedin": "LINKEDIN_ACCESS_TOKEN",
    "brevo": "BREVO_API_KEY",
    "telegram": "TELEGRAM_BOT_TOKEN",
    "cmsUrl": "CMS_WEBHOOK_URL",
    "cmsToken": "CMS_API_KEY",
}


def mask(value: str) -> str:
    if not value:
        return ""
    if len(value) < 8:
        return "***"
    return f"{value[:4]}…{value[-4:]}"


def merge_env(updates: dict, env_file: Path = ENV_FILE) -> list:
    """Writes non-empty updates into .env, keeping every other line. Returns changed keys."""
    updates = {k: v.strip() for k, v in updates.items() if isinstance(v, str) and v.strip()}
    lines = env_file.read_text(encoding="utf-8").splitlines() if env_file.exists() else [
        "# AUTONOMA AI — lokalne klucze API (plik chroniony przez .gitignore)"]
    done = set()
    for i, line in enumerate(lines):
        if "=" in line and not line.lstrip().startswith("#"):
            k = line.split("=", 1)[0].strip()
            if k in updates:
                lines[i] = f"{k}={updates[k]}"
                done.add(k)
    for k, v in updates.items():
        if k not in done:
            lines.append(f"{k}={v}")
    env_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return sorted(updates)


class AutonomaRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(PUBLIC_DIR), **kwargs)

    def translate_path(self, path):
        if path == "/admin" or path.startswith("/admin/"):
            rel = path[len("/admin"):].split("?", 1)[0].split("#", 1)[0].lstrip("/") or "index.html"
            target = (ADMIN_DIR / rel).resolve()
            if ADMIN_DIR.resolve() in target.parents or target == ADMIN_DIR.resolve():
                return str(target)
            return str(ADMIN_DIR / "__forbidden__")
        return super().translate_path(path)

    def _send_json(self, data: dict, status: int = 200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/api/load-keys":
            keys = {}
            for field, env_key in KEY_MAP.items():
                val = _load_key(env_key)
                keys[field] = {"set": bool(val), "masked": mask(val)}
            return self._send_json({"ok": True, "keys": keys})
        if self.path == "/admin":
            self.send_response(301)
            self.send_header("Location", "/admin/")
            self.end_headers()
            return
        return super().do_GET()

    def _read_json(self):
        length = int(self.headers.get("Content-Length", 0) or 0)
        if length > MAX_BODY:
            return None, 413
        raw = self.rfile.read(length).decode("utf-8") if length > 0 else "{}"
        try:
            data = json.loads(raw)
            return (data, 200) if isinstance(data, dict) else (None, 400)
        except Exception:
            return None, 400

    def do_POST(self):
        payload, code = self._read_json()
        if payload is None:
            if code == 413:
                return self._send_json({"ok": False, "errors": {"_": "too_large"}}, 413)
            return self._send_json({"ok": False, "errors": {"_": "invalid_json"}}, 400)

        if self.path == "/api/lead":
            from crm.validation import validate_lead
            from db.supabase_client import db
            clean, errors = validate_lead(payload, int(time.time() * 1000))
            if errors.get("_spam"):
                return self._send_json({"ok": True})  # silent drop, do not teach bots
            if errors:
                return self._send_json({"ok": False, "errors": errors}, 400)
            try:
                db.insert_lead(clean)
            except Exception as e:
                print(f"[ERROR] lead_store_failed: {type(e).__name__}")
                return self._send_json({"ok": False, "fallback": "mailto"}, 503)
            return self._send_json({"ok": True})

        if self.path == "/api/save-keys":
            updates = {KEY_MAP[f]: v for f, v in payload.items() if f in KEY_MAP}
            changed = merge_env(updates)
            return self._send_json({"ok": True, "saved_to": [".env"], "updated": changed})

        if self.path == "/api/save-projects":
            projects = payload.get("projects")
            if isinstance(projects, list) and len(projects) > 0:
                PROJECTS_FILE.parent.mkdir(parents=True, exist_ok=True)
                PROJECTS_FILE.write_text(json.dumps(projects, indent=2, ensure_ascii=False), encoding="utf-8")
                return self._send_json({"ok": True, "saved_to": "saas_core/projects.json", "count": len(projects)})
            return self._send_json({"ok": False, "error": "Invalid projects list"}, status=400)

        return self._send_json({"ok": False, "error": "Unknown endpoint"}, status=404)


def make_server(port: int = 3000, bind: str = None):
    socketserver.TCPServer.allow_reuse_address = True
    return socketserver.TCPServer((bind or os.environ.get("LOCAL_BIND", "127.0.0.1"), port), AutonomaRequestHandler)


def run_server(port: int = 3000):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    with make_server(port) as httpd:
        host = httpd.server_address[0]
        print(f"[Autonoma AI Local Server] http://{host}:{port}/ (strona) i http://{host}:{port}/admin/ (panel)", flush=True)
        httpd.serve_forever()


if __name__ == "__main__":
    run_server(3000)
