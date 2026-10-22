"""
Main Orchestrator Engine for 24/7 Personal Brand Multi-Agent Swarm.
Runs scouts, curates top AI topics, triggers specialized writers,
and populates the daily review queue and executive DASHBOARD.md.
"""

import os
import sys
import re
import json

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass
from datetime import datetime, timezone
from pathlib import Path

from sources.github_scout import fetch_trending_ai_repos
from sources.hacker_news_scout import fetch_top_hn_ai_stories
from sources.arxiv_scout import fetch_recent_ai_papers
from agents.curator import curate_topics
from agents.writers.linkedin_writer import generate_linkedin_content
from agents.writers.twitter_writer import generate_twitter_content
from agents.writers.newsletter_writer import generate_newsletter_content
from agents.writers.video_writer import generate_video_content
from agents.writers.github_writer import generate_github_content

def slugify(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text).strip('-')
    return text[:40]

def run_brand_engine():
    base_dir = Path(__file__).parent.resolve()
    print("=" * 60)
    print("🚀 URUCHAMIANIE SYSTEMU AGENTÓW 24/7: MARKA OSOBISTA AI")
    print("=" * 60)
    
    # 1. Load Persona
    persona_path = base_dir / "brand_core" / "persona.json"
    with open(persona_path, "r", encoding="utf-8") as f:
        persona = json.load(f)
    print(f"👤 Persona załadowana: {persona.get('name')} ({persona.get('title')})")
    
    # 2. Run Scouts
    print("\n🔍 Krok 1/4: Skauci przeczesują źródła (GitHub, Hacker News, ArXiv)...")
    gh_items = fetch_trending_ai_repos(limit=4)
    hn_items = fetch_top_hn_ai_stories(limit=4)
    arxiv_items = fetch_recent_ai_papers(limit=3)
    
    all_items = gh_items + hn_items + arxiv_items
    print(f"   Znaleziono łącznie: {len(all_items)} potencjalnych tematów.")
    
    if not all_items:
        print("[!] Brak nowych tematów ze źródeł.")
        return
        
    # 3. Curate & Select Top Story
    print("\n🧠 Krok 2/4: Agent Kurator ocenia potencjał i wybiera temat dnia...")
    primary_topic, secondaries = curate_topics(all_items)
    print(f"   🏆 TEMAT DNIA: {primary_topic['title']} (Źródło: {primary_topic['source']}, Wynik: {primary_topic.get('curator_score', 0)})")
    
    # 4. Generate Content via Multi-Agent Swarm
    print("\n✍️  Krok 3/4: Agenci ghostwriterzy tworzą pełną paczkę treści...")
    li_data = generate_linkedin_content(primary_topic, persona)
    tw_data = generate_twitter_content(primary_topic, persona)
    nl_data = generate_newsletter_content(primary_topic, persona, secondaries)
    vid_data = generate_video_content(primary_topic, persona)
    gh_data = generate_github_content(primary_topic, persona)
    
    # 5. Save to Queue
    today_str = datetime.now().strftime("%Y-%m-%d")
    topic_slug = slugify(primary_topic['title'])
    queue_dir = base_dir / "queue" / f"{today_str}_{topic_slug}"
    queue_dir.mkdir(parents=True, exist_ok=True)
    
    # Save individual files
    (queue_dir / "1_LINKEDIN_POST.md").write_text(li_data["post"], encoding="utf-8")
    (queue_dir / "2_LINKEDIN_CAROUSEL.md").write_text(li_data["carousel"], encoding="utf-8")
    (queue_dir / "3_TWITTER_THREAD.md").write_text(tw_data["thread"] + "\n\n### Standalone Hooks:\n" + "\n\n".join(tw_data["standalone_hooks"]), encoding="utf-8")
    (queue_dir / "4_NEWSLETTER_EDITION.md").write_text(nl_data["newsletter"], encoding="utf-8")
    (queue_dir / "5_VIDEO_SHORTS_SCRIPT.md").write_text(vid_data["video_script"], encoding="utf-8")
    (queue_dir / "6_GITHUB_SNIPPET.py").write_text(gh_data["demo_code"], encoding="utf-8")
    (queue_dir / "6_GITHUB_README.md").write_text(gh_data["readme"], encoding="utf-8")
    
    # 6. Update DASHBOARD.md
    print("\n📊 Krok 4/4: Aktualizacja panelu dowodzenia DASHBOARD.md...")
    dashboard_path = base_dir / "DASHBOARD.md"
    
    dashboard_content = f"""# ⚡ Centrum Dowodzenia Marką Osobistą 24/7 (AI & Software Engineering)

> Ostatnia automatyczna runda agentów: **{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}**  
> Status kolejki: 🟢 **Gotowa do 10-minutowego przeglądu i publikacji**

---

## 🏆 Temat Dnia: `{primary_topic['title']}`
* **Źródło:** {primary_topic['source']} | [Oryginalny link]({primary_topic.get('url', '#')})
* **Ocena Kuratora:** {primary_topic.get('curator_score', 0)} / 100 pkt
* **Folder paczki:** [`queue/{today_str}_{topic_slug}/`](file:///{queue_dir.as_posix()})

---

## 📦 Wygenerowana Paczka Mediów (Do skopiowania jednym kliknięciem)

| Format | Opis | Plik |
|---|---|---|
| **LinkedIn Post** | Post merytoryczny z perspektywą inżynierską i pytaniem dyskusyjnym | [1_LINKEDIN_POST.md](file:///{queue_dir.as_posix()}/1_LINKEDIN_POST.md) |
| **LinkedIn Karuzela** | 5-slajdowy konspekt PDF (Hook -> Problem -> Architektura -> Metryki -> CTA) | [2_LINKEDIN_CAROUSEL.md](file:///{queue_dir.as_posix()}/2_LINKEDIN_CAROUSEL.md) |
| **X / Twitter Thread** | Wątek (5 tweetów o dużej gęstości wiedzy) + 2 one-linery | [3_TWITTER_THREAD.md](file:///{queue_dir.as_posix()}/3_TWITTER_THREAD.md) |
| **Newsletter / Blog** | Pełne wydanie Substack/Medium (Deep dive + radar 3 innych tematów) | [4_NEWSLETTER_EDITION.md](file:///{queue_dir.as_posix()}/4_NEWSLETTER_EDITION.md) |
| **YouTube Shorts / Reel** | 60-sekundowy skrypt (Audio + B-Roll cues + Hook w 1. sekundzie) | [5_VIDEO_SHORTS_SCRIPT.md](file:///{queue_dir.as_posix()}/5_VIDEO_SHORTS_SCRIPT.md) |
| **GitHub Proof-of-Work** | Działający snippet Python + README z diagramem architektury | [6_GITHUB_SNIPPET.py](file:///{queue_dir.as_posix()}/6_GITHUB_SNIPPET.py) |

---

## 🔭 Tematy Rezerwowe / Radar Dnia
"""
    for sec in secondaries:
        dashboard_content += f"- **[{sec.get('source')}]** [{sec.get('title')}]({sec.get('url', '#')})\n"
        
    dashboard_content += f"""
---

## 🔄 Jak uruchomić kolejny cykl?
Uruchom w terminalu:
```bash
python engine.py
```
Lub pozwól zaplanowanemu zadaniu Antigravity wykonywać ten cykl automatycznie co ustalony czas!
"""
    dashboard_path.write_text(dashboard_content, encoding="utf-8")
    
    print("\n✅ GOTOWE! Wygenerowano pełną paczkę treści w:")
    print(f"   📁 {queue_dir}")
    print(f"   📄 Zobacz panel: {dashboard_path}")
    print("=" * 60)

if __name__ == "__main__":
    run_brand_engine()
