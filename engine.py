"""
Main Multi-Tenant Orchestrator Engine for Autonoma AI (Autonomous AI Workforce OS).
Coordinates the 12-Agent Virtual Workforce across ALL active subscribed client projects:
- Employee #1: Radar Rynkowy & Trend Scout
- Employee #2: Architekt SEO & GEO (ChatGPT / Perplexity / Google /llms.txt)
- Employee #3: LinkedIn B2B Ghostwriter & Carousel Designer
- Employee #4: X / Twitter Viral Thread Strategist
- Employee #5: Manager Własnej Grupy i Społeczności (FB Group / Discord / Skool)
- Employee #6: Inżynier Kampanii Reklamowych (Micro-Budget Ads 0-20 PLN & Retargeting)
- Employee #7: Specjalista B2B Outreach & SDR (LinkedIn DM + Cold Email)
- Employee #8: Redaktor Newslettera i Lead Nurturingu (Brevo / Resend)
- Employee #9: Reżyser Wideo Shorts / Reels / TikTok (60s)
- Employee #10: Strażnik Komentarzy Anti-Ban (Human Jitter 18-95 min)
- Employee #11: Dział Statystyczny Multi-Armed Bandit (Optymalizacja ROI 80/20)
- Employee #12: Inżynier Integracji CMS & Schema.org JSON-LD (Owner Permission Gate)
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
from agents.writers.community_writer import generate_community_content
from agents.writers.ads_writer import generate_ads_content
from agents.writers.outreach_writer import generate_outreach_content
from agents.geo_seo_engine import generate_geo_article
from agents.analyst_agent import pick_best_persona
from tracking.utm_builder import build_tracked_url
from db.supabase_client import db
from publishers.social_publisher import dispatch_content_bundle
from publishers.cms_connector import publish_article_to_website
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
            desc = f"Nowoczesny sygnał technologiczny z obszaru automatyzacji i skalowania biznesu: {item.get('title')}."
        item["description"] = desc
    return items

def run_single_project_cycle(project: dict, all_scouted_items: list, base_dir: Path, now_dt: datetime):
    proj_id = project.get("id", "proj_default")
    proj_name = project.get("product_name", "Nasz Projekt")
    print(f"\n" + "-" * 65)
    print(f"🏢 [PROJEKT: {proj_name}] (ID: {proj_id}) | Plan: {project.get('subscription_plan', 'pro').upper()}")
    print("-" * 65)

    # 1. Multi-Armed Bandit Persona Selection (Employee #11)
    chosen_persona = pick_best_persona()
    persona_dict = {
        "active_style": chosen_persona.get("persona_name", "analityk_danych"),
        "name": proj_name,
        "title": project.get("tagline", "Autonomous Growth Engine")
    }
    print(f"🎯 [Pracownik #11 — Analityk Bandit] Wybrany styl: {chosen_persona.get('persona_name')} (ROI: {chosen_persona.get('effectiveness_score', 1.0)} pkt)")

    # 2. Filter Unseen Items for this specific project (Employee #1)
    unseen_items = filter_unseen_items(all_scouted_items)
    if not unseen_items:
        unseen_items = all_scouted_items

    primary_topic, secondaries = curate_topics(unseen_items)
    print(f"🔍 [Pracownik #1 — Radar Rynkowy] Sygnał bazowy: {primary_topic['title']} ({primary_topic['source']})")

    # 3. Save this project as active profile in saas_core/product_profile.json
    profile_path = base_dir / "saas_core" / "product_profile.json"
    profile_path.write_text(json.dumps(project, indent=2, ensure_ascii=False), encoding="utf-8")

    # 4. Generate 10-Channel Content Suite across all AI Employees
    li_data = generate_linkedin_content(primary_topic, persona_dict)
    tw_data = generate_twitter_content(primary_topic, persona_dict)
    nl_data = generate_newsletter_content(primary_topic, persona_dict, secondaries)
    vid_data = generate_video_content(primary_topic, persona_dict)
    gh_data = generate_github_content(primary_topic, persona_dict)
    comm_data = generate_community_content(primary_topic, persona_dict)
    ads_data = generate_ads_content(primary_topic, persona_dict)
    out_data = generate_outreach_content(primary_topic, persona_dict)
    print(f"✍️  [Pracownicy #3-#9] Wygenerowano: LinkedIn, Karuzelę, X Thread, Własną Grupę, Kampanię Ads, Outreach B2B, Newsletter i Wideo 60s.")

    # 5. Generate SEO & GEO Article + Owner Permission CMS Gate (Employee #2 & #12)
    cms_result = {"status": "AWAITING_OWNER_PERMISSION"}
    geo_res = None
    try:
        geo_res = generate_geo_article(primary_topic, project)
        print(f"🌐 [Pracownik #2 — SEO & GEO] Artykuł: {geo_res['title']}")
        cms_result = publish_article_to_website(geo_res, project)
        print(f"🔐 [Pracownik #12 — Bramka CMS] Status dla {proj_name}: {cms_result['status']}")
        if "PUBLISHED" in cms_result.get("status", ""):
            host = project.get("website_url", "twoja-domena.pl").replace("https://", "").replace("http://", "").split("/")[0]
            submit_to_indexnow(host, [f"{project.get('website_url')}/articles/{geo_res['slug']}"])
    except Exception as e:
        print(f"[WARN] Błąd generatora GEO/SEO dla {proj_name}: {e}")

    bundle = {
        "linkedin": li_data,
        "twitter": tw_data,
        "newsletter": nl_data,
        "video": vid_data,
        "github": gh_data,
        "community": comm_data,
        "ads": ads_data,
        "outreach": out_data
    }

    # 6. Save to Queue & Memory (Employee #10 — Anti-Ban Guard)
    stamp_str = now_dt.strftime("%Y-%m-%d_%H%M")
    topic_slug = slugify(primary_topic['title'])
    queue_dir = base_dir / "queue" / f"{stamp_str}_{proj_id}_{topic_slug}"
    queue_dir.mkdir(parents=True, exist_ok=True)

    utm_info = build_tracked_url(project.get("website_url", "https://twoja-domena.pl"), "social", chosen_persona.get("persona_name", "default"), topic_slug)
    followup_comment = f"Pełne zestawienie, architekturę i dane znajdziesz tutaj 👉 {utm_info['tracked_url']}"

    if geo_res and geo_res.get("markdown"):
        (queue_dir / "0_WEBSITE_SEO_ARTICLE.md").write_text(geo_res["markdown"], encoding="utf-8")

    (queue_dir / "1_LINKEDIN_POST.md").write_text(li_data["post"], encoding="utf-8")
    (queue_dir / "2_LINKEDIN_CAROUSEL.md").write_text(li_data["carousel"], encoding="utf-8")
    (queue_dir / "3_TWITTER_THREAD.md").write_text(tw_data["thread"] + f"\n\n### 💬 Anti-Ban 1st Comment:\n{followup_comment}", encoding="utf-8")
    (queue_dir / "4_NEWSLETTER_EDITION.md").write_text(nl_data["newsletter"], encoding="utf-8")
    (queue_dir / "5_VIDEO_SHORTS_SCRIPT.md").write_text(vid_data["video_script"], encoding="utf-8")
    (queue_dir / "6_GITHUB_SNIPPET.py").write_text(gh_data["demo_code"], encoding="utf-8")
    (queue_dir / "6_GITHUB_README.md").write_text(gh_data["readme"], encoding="utf-8")
    (queue_dir / "8_COMMUNITY_GROUP_PLAN.md").write_text(comm_data["community_playbook"], encoding="utf-8")
    (queue_dir / "9_MICRO_ADS_CAMPAIGN.md").write_text(ads_data["ads_campaign"], encoding="utf-8")
    (queue_dir / "10_B2B_OUTREACH_SDR.md").write_text(out_data["outreach_playbook"], encoding="utf-8")

    db.insert_content({
        "id": f"{stamp_str}_{proj_id}_{topic_slug}",
        "channel": "x",
        "persona_used": chosen_persona.get("persona_name"),
        "title": f"[{proj_name}] {geo_res['short_topic'] if geo_res else primary_topic['title']}",
        "body": tw_data['thread'][:1500],
        "followup_comment": followup_comment,
        "utm_tag": utm_info['utm_tag'],
        "status": "scheduled",
        "scheduled_for": (now_dt + timedelta(minutes=random.randint(18, 95))).isoformat(),
        "created_at": now_dt.isoformat()
    })

    save_to_memory(primary_topic, queue_dir.name)
    dispatch_content_bundle(primary_topic, bundle, queue_dir)
    print(f"✅ Kompletna paczka 10 formatów dla {proj_name} zapisana w: queue/{queue_dir.name}")
    return queue_dir

def run_brand_engine():
    base_dir = Path(__file__).parent.resolve()
    now_dt = datetime.now()
    print("=" * 70)
    print(f"🚀 [AUTONOMA AI — 12-AGENT WORKFORCE OS] START CYKLU: {now_dt.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    active_projects = db.get_active_projects()
    print(f"👥 Liczba aktywnych projektów / subskrybentów: {len(active_projects)}")

    if not active_projects:
        print("[!] Brak aktywnych projektów w bazie. Dodaj projekt w saas_core/projects.json")
        return

    print("\n🔍 [Pracownik #1] Przeczesywanie źródeł trendów dla wszystkich projektów...")
    gh_items = fetch_trending_ai_repos(limit=6)
    hn_items = fetch_top_hn_ai_stories(limit=6)
    arxiv_items = fetch_recent_ai_papers(limit=5)
    all_items = enrich_item_descriptions(gh_items + hn_items + arxiv_items)

    for project in active_projects:
        run_single_project_cycle(project, all_items, base_dir, now_dt)

    print("\n📊 Aktualizacja Autonoma AI Web Studio & Telemetry...")
    try:
        build_web_dashboard()
    except Exception as e:
        print(f"[WARN] Błąd generatora web: {e}")

    print("\n" + "=" * 70)
    print(f"🎉 Wszystkie projekty ({len(active_projects)}) zostały obsłużone przez drużynę 12 Pracowników AI!")
    print("=" * 70)

if __name__ == "__main__":
    run_brand_engine()
