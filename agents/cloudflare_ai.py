"""
Cloudflare Workers AI Client (Autonoma AI — 0,00 PLN Edge LLM).
Allows the Python engine to use Cloudflare's serverless AI models
(@cf/meta/llama-3.3-70b-instruct, @cf/deepseek-ai/deepseek-r1-distill-qwen-32b)
via Cloudflare REST API with zero local GPU overhead.
"""

import json
import urllib.request
from agents.free_ai_router import _load_key

DEFAULT_MODEL = "@cf/meta/llama-3.3-70b-instruct"

def call_cloudflare_ai(prompt, system_prompt="Jesteś inżynierem AI tworzącym merytoryczne treści.", model=DEFAULT_MODEL):
    account_id = _load_key("CF_ACCOUNT_ID")
    api_token = _load_key("CF_API_TOKEN")

    if not account_id or not api_token:
        return ""

    url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run/{model}"
    payload = {
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 1500,
        "temperature": 0.7
    }

    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }

    try:
        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if data.get("success"):
                return data.get("result", {}).get("response", "")
    except Exception as e:
        print(f"[WARN] Cloudflare Workers AI error: {e}")
        return None
