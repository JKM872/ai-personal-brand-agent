"""
Free AI Router & Universal Secret Loader (0,00 PLN Budget — Autonoma AI Workforce).
Intelligently cascades across 100% free AI model providers and reads keys from:
1. Environment variables (GEMINI_API_KEY, GROQ_API_KEY, etc.)
2. Local .env file (git-ignored, safe from accidental commits)
3. Local config/accounts.local.json (git-ignored)
4. Local config/accounts.json

Tiers:
- Tier 1: Google Gemini 2.5 / 2.0 / 1.5 Flash API (Google AI Studio — 1,500 free reqs/day)
- Tier 2: Groq LLaMA 3.3 70B Versatile API (Groq Cloud Free Tier)
- Tier 3: Cloudflare Workers AI (@cf/meta/llama-3.3-70b-instruct)
- Tier 4: Deterministic Project-Adaptive Synthesis Fallback
"""

import os
import json
import urllib.request
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.resolve()
CONFIG_FILE = BASE_DIR / "config" / "accounts.json"
LOCAL_CONFIG_FILE = BASE_DIR / "config" / "accounts.local.json"
ENV_FILE = BASE_DIR / ".env"

def _is_placeholder(val: str) -> bool:
    if not val:
        return True
    v = val.strip()
    return (
        not v
        or v.startswith("TWÓJ_")
        or v.startswith("TWOJ_")
        or v.startswith("ghp_TWÓJ")
        or v == "urn:li:person:TWOJE_ID"
    )

def _load_key(key_name: str) -> str:
    # 1. Check OS Environment
    val = os.environ.get(key_name, "").strip()
    if not _is_placeholder(val):
        return val

    # 2. Check .env file
    if ENV_FILE.exists():
        try:
            for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    if k.strip() == key_name:
                        v_clean = v.strip().strip('"').strip("'")
                        if not _is_placeholder(v_clean):
                            return v_clean
        except Exception:
            pass

    # 3. Check config/accounts.local.json and config/accounts.json
    for cfg_path in (LOCAL_CONFIG_FILE, CONFIG_FILE):
        if cfg_path.exists():
            try:
                cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
                # Check top-level or ai_keys
                for section in (cfg.get("ai_keys", {}), cfg):
                    if isinstance(section, dict) and key_name in section:
                        v_clean = str(section.get(key_name, "")).strip()
                        if not _is_placeholder(v_clean):
                            return v_clean
            except Exception:
                pass

    return ""

def has_live_ai_key() -> bool:
    return bool(_load_key("GEMINI_API_KEY") or _load_key("GROQ_API_KEY") or (_load_key("CF_ACCOUNT_ID") and _load_key("CF_API_TOKEN")))

_mock_logged = False

def log_mock_ai_once() -> None:
    """Logs once per process that no AI key is configured (writers fall back to templates)."""
    global _mock_logged
    if not _mock_logged:
        _mock_logged = True
        print("[MOCK] AI: brak klucza, writery używają szablonów")

def ask_free_ai(system_prompt: str, user_prompt: str, temperature: float = 0.7) -> str:
    if not has_live_ai_key():
        log_mock_ai_once()
        return ""
    # --- TIER 1: Google Gemini API (Darmowy limit w Google AI Studio) ---
    gemini_key = _load_key("GEMINI_API_KEY")
    if gemini_key:
        for model in ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={gemini_key}"
                payload = {
                    "system_instruction": {"parts": [{"text": system_prompt}]},
                    "contents": [{"parts": [{"text": user_prompt}]}],
                    "generationConfig": {"temperature": temperature, "maxOutputTokens": 2048}
                }
                req = urllib.request.Request(
                    url,
                    data=json.dumps(payload).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                    method="POST"
                )
                with urllib.request.urlopen(req, timeout=25) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    text = data["candidates"][0]["content"]["parts"][0]["text"]
                    if text.strip():
                        return text.strip()
            except Exception as e:
                print(f"[Fallback] Gemini ({model}) info: {e}. Przełączam...")

    # --- TIER 2: Groq API (Darmowy tier - LLaMA 3.3 70B Versatile) ---
    groq_key = _load_key("GROQ_API_KEY")
    if groq_key:
        try:
            url = "https://api.groq.com/openai/v1/chat/completions"
            payload = {
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": temperature,
                "max_tokens": 2048
            }
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Authorization": f"Bearer {groq_key}",
                    "Content-Type": "application/json",
                    "User-Agent": "AutonomaAI/2.0"
                },
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=25) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            print(f"[Fallback] Groq LLaMA info: {e}. Przełączam na Cloudflare...")

    # --- TIER 3: Cloudflare Workers AI ---
    try:
        from agents.cloudflare_ai import call_cloudflare_ai
        cf_res = call_cloudflare_ai(user_prompt, system_prompt=system_prompt)
        if cf_res and cf_res.strip():
            return cf_res.strip()
    except Exception:
        pass

    return ""

if __name__ == "__main__":
    print("Aktywny klucz Live AI:", has_live_ai_key())
