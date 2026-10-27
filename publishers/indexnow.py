"""
IndexNow API Submitter (Instant AI & Bing Indexing for 0,00 PLN).
Notifies Bing / IndexNow-compatible crawlers after an approved article is published.
Requires INDEXNOW_KEY (and the key file public/<key>.txt on the domain).
Without the key or in dry-run mode nothing is sent.
"""

import json
import urllib.request

from agents.free_ai_router import _load_key
from agents.runtime import is_dry_run, log_skip

INDEXNOW_ENDPOINT = "https://api.indexnow.org/indexnow"

def submit_to_indexnow(host: str, url_list: list, api_key: str = None):
    """
    Submits URLs to IndexNow.
    Returns {"status": "SKIPPED"} without a key or in dry-run, otherwise the HTTP status (or None on error).
    """
    key = api_key or _load_key("INDEXNOW_KEY")
    if not key or is_dry_run():
        log_skip("IndexNow", f"zgłoszenie {len(url_list)} URL")
        return {"status": "SKIPPED"}

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
            print(f"🚀 [INDEXNOW] Zgłoszono {len(url_list)} URL-i do indeksacji (HTTP {resp.status}).")
            return resp.status
    except Exception as e:
        print(f"[INFO] IndexNow ping info: {e} (Wymaga umieszczenia pliku {key}.txt w domenie głównej).")
        return None

if __name__ == "__main__":
    print(submit_to_indexnow("twoja-domena.pl", ["https://twoja-domena.pl/articles/nowy-post"]))
