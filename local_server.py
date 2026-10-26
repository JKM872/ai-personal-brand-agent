"""
Autonoma AI — Local Full-Stack Server (Port 3000).
Serves the Web Command Center (public/) AND provides live disk-persistence endpoints:
- POST /api/save-keys     -> Saves API keys permanently to .env & config/accounts.local.json
- GET  /api/load-keys     -> Returns saved API keys from .env / config/accounts.local.json
- POST /api/save-projects -> Saves multi-tenant projects permanently to saas_core/projects.json
- POST /api/run-engine    -> Triggers engine.py cycle on demand
"""

import os
import sys
import json
import http.server
import socketserver
from pathlib import Path

BASE_DIR = Path(__file__).parent.resolve()
PUBLIC_DIR = BASE_DIR / "public"
ENV_FILE = BASE_DIR / ".env"
LOCAL_ACCOUNTS_FILE = BASE_DIR / "config" / "accounts.local.json"
PROJECTS_FILE = BASE_DIR / "saas_core" / "projects.json"

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from agents.free_ai_router import _load_key

class AutonomaRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(PUBLIC_DIR), **kwargs)

    def _send_json(self, data: dict, status: int = 200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        if self.path == "/api/load-keys":
            keys = {
                "gemini": _load_key("GEMINI_API_KEY"),
                "groq": _load_key("GROQ_API_KEY"),
                "webhook": _load_key("WEBHOOK_URL"),
                "linkedin": _load_key("LINKEDIN_ACCESS_TOKEN"),
                "brevo": _load_key("BREVO_API_KEY"),
                "telegram": _load_key("TELEGRAM_BOT_TOKEN"),
                "cmsUrl": _load_key("CMS_WEBHOOK_URL"),
                "cmsToken": _load_key("CMS_API_KEY")
            }
            return self._send_json({"ok": True, "keys": keys})
        return super().do_GET()

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length).decode("utf-8") if length > 0 else "{}"
        try:
            payload = json.loads(raw)
        except Exception:
            payload = {}

        if self.path == "/api/save-keys":
            env_lines = [
                "# AUTONOMA AI — Automatycznie zapisane klucze API (chronione przez .gitignore)",
                f"GEMINI_API_KEY={payload.get('gemini', '').strip()}",
                f"GROQ_API_KEY={payload.get('groq', '').strip()}",
                f"WEBHOOK_URL={payload.get('webhook', '').strip()}",
                f"LINKEDIN_ACCESS_TOKEN={payload.get('linkedin', '').strip()}",
                f"BREVO_API_KEY={payload.get('brevo', '').strip()}",
                f"TELEGRAM_BOT_TOKEN={payload.get('telegram', '').strip()}",
                f"CMS_WEBHOOK_URL={payload.get('cmsUrl', '').strip()}",
                f"CMS_API_KEY={payload.get('cmsToken', '').strip()}",
            ]
            ENV_FILE.write_text("\n".join(env_lines) + "\n", encoding="utf-8")

            local_cfg = {
                "mode": "live" if any(payload.values()) else "dry_run",
                "ai_keys": {
                    "GEMINI_API_KEY": payload.get("gemini", "").strip(),
                    "GROQ_API_KEY": payload.get("groq", "").strip()
                },
                "channels": {
                    "webhook_automation": {
                        "enabled": bool(payload.get("webhook", "").strip()),
                        "webhook_url": payload.get("webhook", "").strip()
                    },
                    "linkedin": {
                        "enabled": bool(payload.get("linkedin", "").strip()),
                        "access_token": payload.get("linkedin", "").strip()
                    },
                    "telegram_notifier": {
                        "enabled": bool(payload.get("telegram", "").strip()),
                        "bot_token": payload.get("telegram", "").strip()
                    }
                }
            }
            LOCAL_ACCOUNTS_FILE.parent.mkdir(parents=True, exist_ok=True)
            LOCAL_ACCOUNTS_FILE.write_text(json.dumps(local_cfg, indent=2, ensure_ascii=False), encoding="utf-8")
            return self._send_json({"ok": True, "saved_to": [".env", "config/accounts.local.json"]})

        if self.path == "/api/save-projects":
            projects = payload.get("projects")
            if isinstance(projects, list) and len(projects) > 0:
                PROJECTS_FILE.parent.mkdir(parents=True, exist_ok=True)
                PROJECTS_FILE.write_text(json.dumps(projects, indent=2, ensure_ascii=False), encoding="utf-8")
                return self._send_json({"ok": True, "saved_to": "saas_core/projects.json", "count": len(projects)})
            return self._send_json({"ok": False, "error": "Invalid projects list"}, status=400)

        return self._send_json({"ok": False, "error": "Unknown endpoint"}, status=404)

def run_server(port: int = 3000):
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", port), AutonomaRequestHandler) as httpd:
        print(f"🚀 [Autonoma AI Local Server] Działa na http://localhost:{port} (z automatycznym zapisem na dysk do .env i projects.json!)", flush=True)
        httpd.serve_forever()

if __name__ == "__main__":
    run_server(3000)
