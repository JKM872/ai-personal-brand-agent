"""
Free AI Router (0,00 PLN Budget — Autonoma AI Workforce).
Intelligently cascades across 100% free AI model providers and reads keys from:
1. Environment variables (GEMINI_API_KEY, GROQ_API_KEY, CF_API_TOKEN)
2. Local configuration file (config/accounts.json)
3. Local .env file if present

Tiers:
- Tier 1: Google Gemini 2.5 / 1.5 Flash API (Google AI Studio — 1,500 free reqs/day)
- Tier 2: Groq LLaMA 3.3 70B Versatile API (Groq Cloud Free Tier)
- Tier 3: Cloudflare Workers AI (@cf/meta/llama-3.3-70b-instruct)
- Tier 4: Deterministic Project-Adaptive Synthesis Fallback
"""

import os
import json
import urllib.request
import urllib.parse
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.resolve()
CONFIG_FILE = BASE_DIR / "config" / "accounts.json"
ENV_FILE = BASE_DIR / ".env"

def _load_key(key_name: str) -> str:
    # 1. Check OS Environment
    val = os.environ.get(key_name, "").strip()
    if val and not val.startswith("TWÓJ_"):
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
                        if v_clean and not v_clean.startswith("TWÓJ_"):
                            return v_clean
        except Exception:
            pass

    # 3. Check config/accounts.json
    if CONFIG_FILE.exists():
        try:
            cfg = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
            ai_cfg = cfg.get("ai_keys", {})
            val = ai_cfg.get(key_name, "").strip()
            if val and not val.startswith("TWÓJ_"):
                return val
        except Exception:
            pass

    return ""

def has_live_ai_key() -> bool:
    return bool(_load_key("GEMINI_API_KEY") or _load_key("GROQ_API_KEY"))

def ask_free_ai(system_prompt: str, user_prompt: str, temperature: float = 0.7) -> str:
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
