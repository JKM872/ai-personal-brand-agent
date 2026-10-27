"""
Scout module for ArXiv Research Papers.
Fetches recent cutting-edge papers in CS.AI (Artificial Intelligence) & CS.CL (Computation and Language).
"""

import urllib.request
import xml.etree.ElementTree as ET

from agents.runtime import is_offline, load_fixture

def fetch_recent_ai_papers(limit=4):
    """
    Fetches the latest research papers from ArXiv API in AI & LLMs.
    """
    if is_offline():
        return load_fixture("arxiv", "ArXiv scout", limit)
    query_url = (
        "http://export.arxiv.org/api/query?"
        "search_query=cat:cs.AI+OR+cat:cs.CL"
        "&sortBy=submittedDate&sortOrder=descending"
        f"&max_results={limit}"
    )
    headers = {"User-Agent": "PersonalBrandAgent/1.0"}
    
    try:
        req = urllib.request.Request(query_url, headers=headers)
        with urllib.request.urlopen(req, timeout=12) as resp:
            xml_data = resp.read()
            
        root = ET.fromstring(xml_data)
        # Atom XML namespace
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        
        papers = []
        for entry in root.findall("atom:entry", ns):
            title = entry.find("atom:title", ns)
            summary = entry.find("atom:summary", ns)
            link = entry.find("atom:id", ns)
            published = entry.find("atom:published", ns)
            
            clean_title = " ".join(title.text.split()) if title is not None and title.text else ""
            clean_summary = " ".join(summary.text.split()) if summary is not None and summary.text else ""
            paper_url = link.text.strip() if link is not None and link.text else ""
            
            papers.append({
                "source": "ArXiv",
                "title": clean_title,
                "summary": clean_summary[:280] + ("..." if len(clean_summary) > 280 else ""),
                "url": paper_url,
                "published": published.text[:10] if published is not None and published.text else ""
            })
        return papers
    except Exception as e:
        print(f"[WARN] ArXiv scout error: {e}")
        return []

if __name__ == "__main__":
    papers = fetch_recent_ai_papers(2)
    import json
    print(json.dumps(papers, indent=2, ensure_ascii=False))
