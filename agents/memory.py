"""
Persistent Memory Module for 24/7 Agent.
Ensures the agent never repeats the same topic across autonomous cycles.
"""

import json
from pathlib import Path
from datetime import datetime

MEMORY_FILE = Path(__file__).parent.parent / "memory" / "seen_topics.json"

def load_memory():
    if not MEMORY_FILE.exists():
        MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)
        return {"processed_urls": [], "runs": []}
    try:
        return json.loads(MEMORY_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {"processed_urls": [], "runs": []}

def save_to_memory(topic, queue_folder):
    mem = load_memory()
    url = topic.get("url") or topic.get("title")
    if url and url not in mem["processed_urls"]:
        mem["processed_urls"].append(url)
    
    mem["runs"].append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "title": topic.get("title"),
        "source": topic.get("source"),
        "url": url,
        "score": topic.get("curator_score", 0),
        "folder": str(queue_folder)
    })
    # Keep last 500 entries
    mem["processed_urls"] = mem["processed_urls"][-500:]
    mem["runs"] = mem["runs"][-100:]
    
    MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    MEMORY_FILE.write_text(json.dumps(mem, indent=2, ensure_ascii=False), encoding="utf-8")

def filter_unseen_items(items):
    mem = load_memory()
    seen = set(mem.get("processed_urls", []))
    unseen = [item for item in items if (item.get("url") or item.get("title")) not in seen]
    # Fallback if everything was seen in a very short window
    return unseen if unseen else items
