"""
Scout module for GitHub Trending & Top AI Repositories.
Fetches high-signal AI/developer tools and repos from GitHub API.
"""

import json
import urllib.request
import urllib.parse
from datetime import datetime, timedelta, timezone

from agents.runtime import is_offline, load_fixture

def fetch_trending_ai_repos(limit=5):
    """
    Fetches trending or popular recently created AI repositories.
    """
    if is_offline():
        return load_fixture("github", "GitHub scout", limit)
    seven_days_ago = (datetime.now(timezone.utc) - timedelta(days=14)).strftime("%Y-%m-%d")
    query = f"ai agent created:>{seven_days_ago}"
    url = f"https://api.github.com/search/repositories?q={urllib.parse.quote(query)}&sort=stars&order=desc&per_page={limit}"
    
    headers = {
        "User-Agent": "PersonalBrandAgent/1.0 (Mozilla/5.0 compatible)",
        "Accept": "application/vnd.github.v3+json"
    }
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            
        items = []
        for repo in data.get("items", [])[:limit]:
            items.append({
                "source": "GitHub",
                "title": repo.get("full_name", ""),
                "description": repo.get("description", "") or "Brak opisu",
                "url": repo.get("html_url", ""),
                "stars": repo.get("stargazers_count", 0),
                "language": repo.get("language", "Unknown"),
                "topics": repo.get("topics", [])
            })
        return items
    except Exception as e:
        print(f"[WARN] GitHub scout error: {e}")
        return []

if __name__ == "__main__":
    repos = fetch_trending_ai_repos(3)
    print(json.dumps(repos, indent=2, ensure_ascii=False))
