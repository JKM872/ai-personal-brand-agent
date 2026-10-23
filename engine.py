"""
Main Orchestrator Engine for 24/7 Personal Brand & SaaS Growth Swarm.
Integrates:
- Real-time Trend Scouts (GitHub, Hacker News, ArXiv)
- Multi-Armed Bandit Persona Picker (Dział Statystyczny)
- Free AI Router (Gemini -> Groq -> Cloudflare AI -> Fallback)
- Multi-Platform Ghostwriters + Long-Form SEO & GEO Engine
- IndexNow Instant Search Engine Indexer
- Supabase / PostgreSQL Pipeline Queue & UTM Campaign Attribution
- Cloudflare Web Dashboard & Memory Deduplication
"""

import os
import sys
import re
import json
import random
from datetime import datetime, timedelta
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

from sources.github_scout import fetch_trending_ai_repos
from sources.hacker_news_scout import fetch_top_hn_ai_stories
from sources.arxiv_scout import fetch_recent_ai_papers
from agents.curator import curate_topics
from agents.memory import filter_unseen_items, save_to_memory, load_memory
from agents.writers.linkedin_writer import generate_linkedin_content
from agents.writers.twitter_writer import generate_twitter_content
from agents.writers.newsletter_writer import generate_newsletter_content
from agents.writers.video_writer import generate_video_content
from agents.writers.github_writer import generate_github_content
from agents.geo_seo_engine import generate_geo_article, load_product_profile
from agents.analyst_agent import pick_best_persona
from tracking.utm_builder import build_tracked_url
from db.supabase_client import db
from publishers.social_publisher import dispatch_content_bundle
from publishers.indexnow import submit_to_indexnow
from web_generator import build_web_dashboard

def slugify(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text).strip('-')
    return text[:40]

def enrich_item_descriptions(items):
    for item in items:
        desc = item.get("description") or item.get("summary") or ""
        if not desc.strip():
            if item.get("source") == "Hacker News":
                pts = item.get("points", 0)
                cms = item.get("comments", 0)
                desc = f"Projekt wywołał gorącą dyskusję wśród inżynierów na Hacker News ({pts} punktów, {cms} komentarzy), adresując kluczowe wyzwania w architekturze nowoczesnych systemów AI."
            else:
                desc = f"Nowoczesne narzędzie technologiczne z obszaru AI i automatyzacji: {item.get('title')}."
        item["description"] = desc
    return items

def run_brand_engine():
    base_dir = Path(__file__).parent.resolve()
    now_dt = datetime.now()
    print("=" * 65)
    print(f"🚀 [AUTO-GROWTH ENGINE 24/7] START CYKLU: {now_dt.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 65)
    
    # 1. Load Persona & Consult Statistical Department
    persona_path = base_dir / "brand_core" / "persona.json"
    with open(persona_path, "r", encoding="utf-8") as f:
        persona = json.load(f)
        
    chosen_persona = pick_best_persona()
    print(f"🎯 [DZIAŁ STATYSTYCZNY] Wybrany styl (Persona): {chosen_persona.get('persona_name')} (Skuteczność: {chosen_persona.get('effectiveness_score', 1.0)} pkt)")
    persona["active_style"] = chosen_persona.get("persona_name")
    
    # 2. Run Scouts
    print("🔍 [1/5] Skauci skanują GitHub Trending, Hacker News i ArXiv...")
    gh_items = fetch_trending_ai_repos(limit=6)
    hn_items = fetch_top_hn_ai_stories(limit=6)
    arxiv_items = fetch_recent_ai_papers(limit=5)
    
    all_items = enrich_item_descriptions(gh_items + hn_items + arxiv_items)
    unseen_items = filter_unseen_items(all_items)
    print(f"   Pobrano: {len(all_items)} tematów (nowych/niepublikowanych: {len(unseen_items)}).")
    
    if not unseen_items:
        print("[!] Wszystkie tematy w tym oknie czasowym zostały już przetworzone.")
        return
        
    # 3. Curate & Select Top Story
    print("🧠 [2/5] Agent Kurator wybiera najmocniejszy temat...")
    primary_topic, secondaries = curate_topics(unseen_items)
    print(f"   🏆 WYBRANO: {primary_topic['title']} ({primary_topic['source']} | Score: {primary_topic.get('curator_score', 0)})")
    
    # 4. Generate Content via Multi-Agent Swarm
    print("✍️  [3/5] Ghostwriterzy tworzą paczkę na 5 platform + Artykuł SEO/GEO...")
    li_data = generate_linkedin_content(primary_topic, persona)
    tw_data = generate_twitter_content(primary_topic, persona)
    nl_data = generate_newsletter_content(primary_topic, persona, secondaries)
    vid_data = generate_video_content(primary_topic, persona)
    gh_data = generate_github_content(primary_topic, persona)
    
    # Generate SEO & GEO article for the SaaS
    saas_profile = load_product_profile()
    try:
        geo_res = generate_geo_article(primary_topic['title'], saas_profile)
        print(f"   🌐 Wygenerowano artykuł SEO/GEO: {geo_res['title']}")
        # Instant Ping to IndexNow for Bing & ChatGPT Web Search
        host = saas_profile.get("website_url", "twoja-domena.pl").replace("https://", "").replace("http://", "").split("/")[0]
        submit_to_indexnow(host, [f"{saas_profile.get('website_url')}/articles/{geo_res['slug']}"])
    except Exception as e:
        print(f"[WARN] Błąd generatora GEO/SEO: {e}")
        geo_res = None
    
    bundle = {
        "linkedin": li_data,
        "twitter": tw_data,
        "newsletter": nl_data,
        "video": vid_data,
        "github": gh_data
    }
    
    # 5. Save to Queue, UTM Campaign Attribution & Supabase Database
    stamp_str = now_dt.strftime("%Y-%m-%d_%H%M")
    topic_slug = slugify(primary_topic['title'])
    queue_dir = base_dir / "queue" / f"{stamp_str}_{topic_slug}"
    queue_dir.mkdir(parents=True, exist_ok=True)
    
    # Build UTM tracking links
    utm_info = build_tracked_url(saas_profile.get("website_url", "https://twoja-domena.pl"), "social", chosen_persona.get("persona_name", "default"), topic_slug)
    followup_comment = f"Pełne zestawienie, architekturę i dane znajdziesz tutaj 👉 {utm_info['tracked_url']}"
    
    if geo_res and geo_res.get("markdown"):
        (queue_dir / "0_WEBSITE_SEO_ARTICLE.md").write_text(geo_res["markdown"], encoding="utf-8")

    (queue_dir / "1_LINKEDIN_POST.md").write_text(li_data["post"], encoding="utf-8")
    (queue_dir / "2_LINKEDIN_CAROUSEL.md").write_text(li_data["carousel"], encoding="utf-8")
    (queue_dir / "3_TWITTER_THREAD.md").write_text(tw_data["thread"] + "\n\n### Standalone Hooks:\n" + "\n\n".join(tw_data["standalone_hooks"]) + f"\n\n### 💬 Anti-Ban 1st Comment:\n{followup_comment}", encoding="utf-8")
    (queue_dir / "4_NEWSLETTER_EDITION.md").write_text(nl_data["newsletter"], encoding="utf-8")
    (queue_dir / "5_VIDEO_SHORTS_SCRIPT.md").write_text(vid_data["video_script"], encoding="utf-8")
    (queue_dir / "6_GITHUB_SNIPPET.py").write_text(gh_data["demo_code"], encoding="utf-8")
    (queue_dir / "6_GITHUB_README.md").write_text(gh_data["readme"], encoding="utf-8")
    
    # Save scheduled post to database (Supabase / local DB)
    db.insert_content({
        "id": f"{stamp_str}_{topic_slug}",
        "channel": "x",
        "persona_used": chosen_persona.get("persona_name"),
        "title": primary_topic['title'],
        "body": tw_data['thread'][:1500],
        "followup_comment": followup_comment,
        "utm_tag": utm_info['utm_tag'],
        "status": "scheduled",
        "scheduled_for": (now_dt + timedelta(minutes=random.randint(18, 95))).isoformat(),
        "created_at": now_dt.isoformat()
    })
    
    save_to_memory(primary_topic, queue_dir.name)
    
    # 6. Dispatch to Publishers (or Queue in Dry-Run)
    print("📡 [4/5] Moduł Publikacji przygotowuje wysyłkę na konta społecznościowe...")
    pub_status = dispatch_content_bundle(primary_topic, bundle, queue_dir)
    print(f"   Status publikacji: {pub_status['status_summary']}")
    
    # 7. Update DASHBOARD.md & Web Dashboard & Log
    print("📊 [5/5] Aktualizacja DASHBOARD.md i public/index.html (Cloudflare)...")
    try:
        build_web_dashboard()
    except Exception as e:
        print(f"[WARN] Błąd generatora web: {e}")
        
    mem_data = load_memory()
    recent_runs = list(reversed(mem_data.get("runs", [])))[:10]
    
    history_rows = ""
    for r in recent_runs:
        r_folder = base_dir / "queue" / r['folder']
        history_rows += f"| `{r['timestamp']}` | **{r['source']}** | [{r['title'][:50]}]({r['url']}) | {r['score']} pkt | [Otwórz paczkę](file:///{r_folder.as_posix()}) |\n"

    dashboard_path = base_dir / "DASHBOARD.md"
    dashboard_content = f"""# ⚡ Centrum Dowodzenia Marką Osobistą & SaaS 24/7

> **Ostatni cykl:** `{now_dt.strftime('%Y-%m-%d %H:%M:%S')}`  
> **Wybrany styl (Dział Statystyczny):** `{chosen_persona.get('persona_name')}` (Waga ROI: `{chosen_persona.get('effectiveness_score', 1.0)}` pkt)  
> **Status bazy danych:** `{'🟢 Połączono z Supabase' if db.is_connected else '🟡 Pamięć lokalna SQLite (Wklej klucze w Supabase)'}`  
> **Tryb publikacji:** `{pub_status['status_summary']}`  

---

## 🏆 Najnowszy Temat w Kolejce: `{primary_topic['title']}`
* **Źródło:** {primary_topic['source']} | [Oryginalny link]({primary_topic.get('url', '#')})
* **Kampania UTM:** `{utm_info['utm_tag']}`
* **Folder paczki:** [`queue/{queue_dir.name}/`](file:///{queue_dir.as_posix()})

---

## 📦 Gotowe Materiały z Ostatniego Cyklu

| Kanał | Zawartość | Plik Gotowy | Status Konta |
|---|---|---|---|
| **Artykuł SEO / GEO** | Długi artykuł na blog + optymalizacja pod ChatGPT/Perplexity | [0_WEBSITE_SEO_ARTICLE.md](file:///{queue_dir.as_posix()}/0_WEBSITE_SEO_ARTICLE.md) | `GOTOWY DO CMS` |
| **LinkedIn Post** | Post ekspercki + pytanie do dyskusji | [1_LINKEDIN_POST.md](file:///{queue_dir.as_posix()}/1_LINKEDIN_POST.md) | `{pub_status['dispatches'].get('linkedin', 'QUEUED')}` |
| **LinkedIn Karuzela** | Konspekt 5 slajdów PDF | [2_LINKEDIN_CAROUSEL.md](file:///{queue_dir.as_posix()}/2_LINKEDIN_CAROUSEL.md) | `GOTOWE` |
| **X / Twitter** | Wątek 5 tweetów + link w 1. komentarzu (Anti-Ban!) | [3_TWITTER_THREAD.md](file:///{queue_dir.as_posix()}/3_TWITTER_THREAD.md) | `{pub_status['dispatches'].get('twitter_x', 'QUEUED')}` |
| **Newsletter / Blog** | Pełny artykuł Deep-Dive | [4_NEWSLETTER_EDITION.md](file:///{queue_dir.as_posix()}/4_NEWSLETTER_EDITION.md) | `GOTOWE (Brevo/Resend)` |
| **YouTube / TikTok** | Scenariusz 60s Shorts (Audio+Wideo) | [5_VIDEO_SHORTS_SCRIPT.md](file:///{queue_dir.as_posix()}/5_VIDEO_SHORTS_SCRIPT.md) | `GOTOWE` |
| **GitHub Code** | Kod Python + README z diagramem | [6_GITHUB_SNIPPET.py](file:///{queue_dir.as_posix()}/6_GITHUB_SNIPPET.py) | `{pub_status['dispatches'].get('github', 'QUEUED')}` |
| **Payload API / Webhook** | Gotowy JSON pod Make/n8n/Zapier | [7_API_PAYLOAD_READY.json](file:///{queue_dir.as_posix()}/7_API_PAYLOAD_READY.json) | `{pub_status['dispatches'].get('webhook_automation', 'QUEUED')}` |

---

## 🕒 Historia Cykli (Pamięć Anty-Duplikacyjna)

| Data i Godzina | Źródło | Przetworzony Temat | Ocena | Paczka Plików |
|---|---|---|---|---|
{history_rows}
"""
    dashboard_path.write_text(dashboard_content, encoding="utf-8")
    
    # Append to logs/agent.log
    log_dir = base_dir / "logs"
    log_dir.mkdir(exist_ok=True)
    with open(log_dir / "agent.log", "a", encoding="utf-8") as lf:
        lf.write(f"[{now_dt.strftime('%Y-%m-%d %H:%M:%S')}] OK | Persona: {chosen_persona.get('persona_name')} | Topic: {primary_topic['title']} | Folder: {queue_dir.name}\n")

    print(f"✅ CYKL ZAKOŃCZONY! Paczka zapisana w: queue/{queue_dir.name}")
    print("=" * 65)

if __name__ == "__main__":
    run_brand_engine()
