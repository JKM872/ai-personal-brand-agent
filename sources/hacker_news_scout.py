"""
Scout module for Hacker News.
Fetches top tech stories and filters for AI, agentic workflows, and developer tools.
"""

import json
import urllib.request
import re

from agents.runtime import is_offline, load_fixture

AI_KEYWORDS = [
    "ai", "llm", "agent", "gpt", "gemini", "claude", "transformer", 
    "model", "deepseek", "open source", "weights", "inference", "rag",
    "python", "benchmark", "gpu", "neural", "vision", "speech"
]

def fetch_top_hn_ai_stories(limit=5, scan_depth=30):
    """
    Fetches the top stories from Hacker News and filters for AI relevance.
    """
    if is_offline():
        return load_fixture("hn", "Hacker News scout", limit)
    top_ids_url = "https://hacker-news.firebaseio.com/v0/topstories.json"
    headers = {"User-Agent": "PersonalBrandAgent/1.0"}
    
    try:
        req = urllib.request.Request(top_ids_url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            story_ids = json.loads(resp.read().decode("utf-8"))[:scan_depth]
            
        matched_stories = []
        for story_id in story_ids:
            item_url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
            item_req = urllib.request.Request(item_url, headers=headers)
            with urllib.request.urlopen(item_req, timeout=5) as item_resp:
                item = json.loads(item_resp.read().decode("utf-8"))
                
            title = item.get("title", "")
            title_lower = title.lower()
            
            # Match keywords
            is_ai = any(re.search(rf"\b{kw}\b", title_lower) for kw in AI_KEYWORDS)
            if is_ai and item.get("url"):
                matched_stories.append({
                    "source": "Hacker News",
                    "title": title,
                    "url": item.get("url"),
                    "points": item.get("score", 0),
                    "comments": item.get("descendants", 0),
                    "hn_discussion": f"https://news.ycombinator.com/item?id={story_id}"
                })
                if len(matched_stories) >= limit:
                    break
        return matched_stories
    except Exception as e:
        print(f"[WARN] Hacker News scout error: {e}")
        return []

if __name__ == "__main__":
    stories = fetch_top_hn_ai_stories(3)
    print(json.dumps(stories, indent=2, ensure_ascii=False))
