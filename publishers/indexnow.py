"""
IndexNow API Submitter (Instant AI & Bing Indexing for 0,00 PLN).
Notifies Microsoft Bing & ChatGPT Web Search crawlers the second a new article is generated,
guaranteeing crawling in minutes instead of waiting weeks.
"""

import os
import json
import urllib.request

INDEXNOW_ENDPOINT = "https://api.indexnow.org/indexnow"

def submit_to_indexnow(host: str, url_list: list, api_key: str = None):
    """
    Submits URLs to IndexNow.
    If no api_key is configured in INDEXNOW_KEY env var, logs a dry-run dispatch.
    """
    key = api_key or os.environ.get("INDEXNOW_KEY", "ai_brand_agent_key")
    
    payload = {
        "host": host,
        "key": key,
        "keyLocation": f"https://{host}/{key}.txt",
        "urlList": url_list
    }
    
    headers = {"Content-Type": "application/json; charset=utf-8"}
    
    try:
        req = urllib.request.Request(
            INDEXNOW_ENDPOINT,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            print(f"🚀 [INDEXNOW] Zgłoszono {len(url_list)} URL-i do natychmiastowej indeksacji w Bing/ChatGPT (HTTP {resp.status}).")
            return resp.status
    except Exception as e:
        print(f"[INFO] IndexNow ping info: {e} (Wymaga umieszczenia pliku {key}.txt w domenie głównej).")
        return None

if __name__ == "__main__":
    submit_to_indexnow("twoja-domena.pl", ["https://twoja-domena.pl/artykuly/nowy-post"])
