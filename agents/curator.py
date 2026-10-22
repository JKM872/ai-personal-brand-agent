"""
Curator Agent.
Analyzes scouted raw items from GitHub, HN, and ArXiv, scores them based on the
persona criteria, and selects the strongest topic for today's Content Multiplier Pack.
"""

def score_item(item):
    """
    Heuristic scoring based on community traction, novelty, and engineer relevance.
    """
    score = 0
    source = item.get("source", "")
    
    if source == "GitHub":
        stars = item.get("stars", 0)
        score += min(stars / 100, 50)
        desc = item.get("description", "").lower()
        if "agent" in desc: score += 15
        if "autonomous" in desc or "runtime" in desc: score += 10
        if "mcp" in desc or "llm" in desc: score += 10
        
    elif source == "Hacker News":
        points = item.get("points", 0)
        comments = item.get("comments", 0)
        score += min(points / 5, 40)
        score += min(comments / 3, 20)
        title = item.get("title", "").lower()
        if "agent" in title: score += 15
        if "nvidia" in title or "runtime" in title: score += 15
        
    elif source == "ArXiv":
        score += 30  # Baseline for scientific rigor
        summary = item.get("summary", "").lower()
        if "reasoning" in summary or "zero data" in summary: score += 15
        if "long-context" in summary: score += 10

    return round(score, 1)

def curate_topics(all_items):
    """
    Sorts and prioritizes topics. Returns (primary_topic, secondary_topics).
    """
    scored = []
    for item in all_items:
        s = score_item(item)
        scored.append((s, item))
        
    scored.sort(key=lambda x: x[0], reverse=True)
    
    if not scored:
        return None, []
        
    primary = scored[0][1]
    primary["curator_score"] = scored[0][0]
    
    secondaries = [x[1] for x in scored[1:5]]
    return primary, secondaries
