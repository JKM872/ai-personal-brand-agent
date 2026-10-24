"""
Autonoma AI — Multi-Tenant SaaS Web Application Generator (12-Agent Workforce Edition).
Compiles per-project 10-format content bundles (bundlesByProject[project_id]),
12-Agent Workforce directory, Multi-Armed Bandit telemetry, Owner CMS Permission Gate controls,
and API Integrations Hub into public/index.html.
"""

import sys
import json
from datetime import datetime
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

BASE_DIR = Path(__file__).parent.resolve()
PUBLIC_DIR = BASE_DIR / "public"
MEMORY_FILE = BASE_DIR / "memory" / "seen_topics.json"
QUEUE_DIR = BASE_DIR / "queue"
PROFILE_PATH = BASE_DIR / "saas_core" / "product_profile.json"

from db.supabase_client import db

FILE_MAP = {
    "seo_article": "0_WEBSITE_SEO_ARTICLE.md",
    "linkedin_post": "1_LINKEDIN_POST.md",
    "linkedin_carousel": "2_LINKEDIN_CAROUSEL.md",
    "twitter_thread": "3_TWITTER_THREAD.md",
    "newsletter": "4_NEWSLETTER_EDITION.md",
    "video_script": "5_VIDEO_SHORTS_SCRIPT.md",
    "github_readme": "6_GITHUB_README.md",
    "github_code": "6_GITHUB_SNIPPET.py",
    "api_payload": "7_API_PAYLOAD_READY.json",
    "community_plan": "8_COMMUNITY_GROUP_PLAN.md",
    "ads_campaign": "9_MICRO_ADS_CAMPAIGN.md",
    "outreach_sdr": "10_B2B_OUTREACH_SDR.md",
    "publish_status": "PUBLISH_STATUS.json"
}

WORKFORCE_ROSTER = [
    {"id": 1, "role": "Radar Rynkowy & Trend Scout", "dept": "Research", "task": "Przeszukuje sygnały rynkowe, problemy klientów B2B i trendy branżowe 24/7.", "badge": "AKTYWNY"},
    {"id": 2, "role": "Architekt SEO & GEO (AI Search)", "dept": "Content & SEO", "task": "Pisze długie artykuły porównawcze, tabele ROI, sekcje FAQ oraz aktualizuje /llms.txt pod ChatGPT i Perplexity.", "badge": "AKTYWNY"},
    {"id": 3, "role": "Ghostwriter LinkedIn B2B", "dept": "Social Media", "task": "Tworzy eksperckie posty B2B i konspekty 5-slajdowych karuzel PDF bez ucinania zasięgu.", "badge": "AKTYWNY"},
    {"id": 4, "role": "Strateg Wątków X / Twitter", "dept": "Social Media", "task": "Buduje wiralowe nitki (5 tweetów) z twardymi wyliczeniami i pytaniem angażującym.", "badge": "AKTYWNY"},
    {"id": 5, "role": "Manager Własnej Grupy (FB / Discord)", "dept": "Community", "task": "Generuje posty powitalne z Lead Magnetem, ankiety i dyskusje rozkręcające własną społeczność.", "badge": "AKTYWNY"},
    {"id": 6, "role": "Inżynier Reklam Micro-Budget Ads", "dept": "Performance", "task": "Tworzy kreacje retargetingowe (0–20 zł/dzień) na Meta Ads i frazy Exact-Match w Google.", "badge": "AKTYWNY"},
    {"id": 7, "role": "Specjalista B2B Outreach & SDR", "dept": "Sales", "task": "Pisze spersonalizowane wiadomości LinkedIn DM, Cold Emaile i zbija obiekcje sprzedażowe.", "badge": "AKTYWNY"},
    {"id": 8, "role": "Redaktor Newslettera (Brevo / Resend)", "dept": "Retention", "task": "Komponuje cotygodniowe wydania biuletynu dla własnej bazy subskrybentów.", "badge": "AKTYWNY"},
    {"id": 9, "role": "Reżyser Wideo Shorts / Reels / TikTok", "dept": "Video", "task": "Rozpisuje 60-sekundowe scenariusze wideo (Hook w 1. sekundzie, B-Roll i tekst lektora).", "badge": "AKTYWNY"},
    {"id": 10, "role": "Strażnik Komentarzy Anti-Ban", "dept": "Safety", "task": "Wrzuca linki UTM w 1. komentarzu i odpowiada z ludzkim opóźnieniem (Jitter 18–95 min).", "badge": "AKTYWNY"},
    {"id": 11, "role": "Analityk Multi-Armed Bandit (ROI)", "dept": "Analytics", "task": "Liczy skuteczność stylów pisania z kliknięć UTM i kieruje 80% ruchu na najlepszy styl.", "badge": "AKTYWNY"},
    {"id": 12, "role": "Inżynier Integracji CMS & JSON-LD", "dept": "DevOps", "task": "Publikuje artykuły na stronie klienta (GitHub / WordPress / Webhook) za zgodą właściciela.", "badge": "AKTYWNY"}
]

def read_bundle_from_folder(folder: Path) -> dict:
    if not folder or not folder.exists():
        return {}
    bundle = {"folder_name": folder.name}
    for key, fname in FILE_MAP.items():
        fpath = folder / fname
        bundle[key] = fpath.read_text(encoding="utf-8") if fpath.exists() else ""
    return bundle

def get_bundles_by_project(active_projects: list) -> dict:
    if not QUEUE_DIR.exists():
        return {}
    all_folders = sorted([f for f in QUEUE_DIR.iterdir() if f.is_dir()], key=lambda x: x.name, reverse=True)
    bundles = {}
    for proj in active_projects:
        pid = proj.get("id", "proj_default")
        matched = next((f for f in all_folders if f"_{pid}_" in f.name), None)
        if not matched and all_folders:
            matched = all_folders[0]
        bundles[pid] = read_bundle_from_folder(matched)
    return bundles

def safe_json_for_script(obj) -> str:
    return json.dumps(obj, ensure_ascii=False).replace(chr(60) + chr(47), chr(60) + chr(92) + chr(47))

def build_web_dashboard():
    PUBLIC_DIR.mkdir(parents=True, exist_ok=True)
    active_projects = db.get_active_projects()
    bundles_by_project = get_bundles_by_project(active_projects)

    memory = {"runs": []}
    if MEMORY_FILE.exists():
        try:
            memory = json.loads(MEMORY_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass

    personas = db.get_personas()
    scheduled_pipeline = db.get_scheduled_pipeline(limit=10)
    default_project = active_projects[0] if active_projects else {}
    default_pid = default_project.get("id", "proj_autonoma_os")

    (PUBLIC_DIR / "data.json").write_text(
        json.dumps({
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "projects": active_projects,
            "bundles_by_project": bundles_by_project,
            "workforce": WORKFORCE_ROSTER,
            "personas": personas,
            "history": memory.get("runs", []),
            "pipeline": scheduled_pipeline
        }, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    projects_json_str = safe_json_for_script(active_projects)
    bundles_json_str = safe_json_for_script(bundles_by_project)
    workforce_json_str = safe_json_for_script(WORKFORCE_ROSTER)
    personas_json_str = safe_json_for_script(personas)
    pipeline_json_str = safe_json_for_script(scheduled_pipeline)

    html_content = f"""<!DOCTYPE html>
<html lang="pl" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Autonoma AI — 12-Agent Autonomous Growth OS</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {{
      darkMode: 'class',
      theme: {{
        extend: {{
          fontFamily: {{
            sans: ['Plus Jakarta Sans', 'system-ui', 'sans-serif'],
            mono: ['JetBrains Mono', 'monospace']
          }}
        }}
      }}
    }}
  </script>
  <style>
    :root {{
      --bg-canvas: #05060A;
      --bg-surface: #0B0D14;
      --bg-elevated: #111520;
      --border-hairline: rgba(255, 255, 255, 0.07);
    }}
    body {{
      background-color: var(--bg-canvas);
      background-image:
        radial-gradient(circle at 18% 0%, rgba(99, 102, 241, 0.14), transparent 42%),
        radial-gradient(circle at 85% 10%, rgba(16, 185, 129, 0.08), transparent 38%);
      color: #F8FAFC;
      overflow-x: hidden;
    }}
    .surface-panel {{
      background: rgba(11, 13, 20, 0.88);
      backdrop-filter: blur(20px);
      border: 1px solid var(--border-hairline);
    }}
    .bento-card {{
      background: linear-gradient(180deg, rgba(20, 24, 36, 0.72) 0%, rgba(11, 13, 20, 0.92) 100%);
      border: 1px solid var(--border-hairline);
      box-shadow: 0 4px 24px -4px rgba(0, 0, 0, 0.5);
      transition: all 0.22s cubic-bezier(0.16, 1, 0.3, 1);
    }}
    .bento-card:hover {{
      border-color: rgba(99, 102, 241, 0.32);
    }}
    .channel-btn-active {{
      background: linear-gradient(90deg, rgba(99, 102, 241, 0.22) 0%, rgba(99, 102, 241, 0.05) 100%);
      border-color: rgba(99, 102, 241, 0.55);
      color: #FFFFFF;
    }}
    .prose-doc h1 {{ font-size: 1.4rem; font-weight: 800; color: #FFFFFF; margin-bottom: 0.85rem; letter-spacing: -0.02em; line-height: 1.3; }}
    .prose-doc h2 {{ font-size: 1.1rem; font-weight: 700; color: #F1F5F9; margin-top: 1.5rem; margin-bottom: 0.6rem; padding-bottom: 0.4rem; border-bottom: 1px solid rgba(255,255,255,0.08); }}
    .prose-doc h3 {{ font-size: 0.96rem; font-weight: 600; color: #A5B4FC; margin-top: 1.1rem; margin-bottom: 0.4rem; }}
    .prose-doc p {{ color: #CBD5E1; line-height: 1.75; margin-bottom: 0.85rem; font-size: 0.92rem; }}
    .prose-doc ul {{ list-style-type: disc; padding-left: 1.4rem; margin-bottom: 1rem; color: #CBD5E1; font-size: 0.92rem; }}
    .prose-doc li {{ margin-bottom: 0.35rem; }}
    .prose-doc blockquote {{ border-left: 3px solid #6366F1; background: rgba(99,102,241,0.09); padding: 0.85rem 1.1rem; border-radius: 0 0.65rem 0.65rem 0; color: #E2E8F0; margin: 1.1rem 0; font-size: 0.9rem; }}
    .prose-doc table {{ width: 100%; border-collapse: collapse; margin: 1.25rem 0; font-size: 0.82rem; border-radius: 0.5rem; overflow: hidden; }}
    .prose-doc th {{ background: rgba(30, 41, 59, 0.85); color: #F8FAFC; font-weight: 600; text-align: left; padding: 0.7rem 0.9rem; border: 1px solid rgba(255,255,255,0.1); }}
    .prose-doc td {{ padding: 0.65rem 0.9rem; border: 1px solid rgba(255,255,255,0.07); color: #CBD5E1; }}
    ::-webkit-scrollbar {{ width: 6px; height: 6px; }}
    ::-webkit-scrollbar-track {{ background: #05060A; }}
    ::-webkit-scrollbar-thumb {{ background: #1E293B; border-radius: 3px; }}
  </style>
</head>
<body class="min-h-screen flex flex-col lg:flex-row antialiased selection:bg-indigo-500 selection:text-white">

  <!-- ================================================================= -->
  <!-- SIDEBAR: AUTONOMA AI MULTI-TENANT NAVIGATION                      -->
  <!-- ================================================================= -->
  <aside class="w-full lg:w-72 surface-panel border-b lg:border-b-0 lg:border-r border-white/10 flex flex-col justify-between shrink-0 lg:h-screen lg:sticky lg:top-0 z-40">
    <div>
      <!-- Brand Header -->
      <div class="px-6 py-5 flex items-center justify-between border-b border-white/10">
        <div class="flex items-center gap-3">
          <div class="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-emerald-400 flex items-center justify-center shadow-lg shadow-indigo-500/30">
            <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" stroke-width="2.2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
          </div>
          <div>
            <div class="font-extrabold text-sm tracking-tight text-white flex items-center gap-2">
              AUTONOMA <span class="text-[10px] font-mono uppercase px-1.5 py-0.5 rounded-md bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">AI OS</span>
            </div>
            <div class="text-[11px] text-slate-400">12-Agent Virtual Workforce</div>
          </div>
        </div>
      </div>

      <!-- MULTI-TENANT WORKSPACE SWITCHER -->
      <div class="p-4 mx-3 mt-4 rounded-2xl bg-white/[0.03] border border-white/[0.08] space-y-2.5">
        <div class="flex items-center justify-between">
          <span class="text-[10px] font-mono uppercase tracking-wider text-slate-400">Klient / Projekt Subskrybenta</span>
          <span id="sidebar-plan-badge" class="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">ENTERPRISE</span>
        </div>
        <select id="project-selector" onchange="switchProject(this.value)" class="w-full px-3 py-2 rounded-xl bg-[#06080F] border border-white/15 text-white font-semibold text-xs focus:border-indigo-500 focus:outline-none cursor-pointer transition">
        </select>
        <div class="flex items-center justify-between text-[11px] pt-0.5">
          <span class="text-indigo-400 font-mono truncate max-w-[165px]" id="sidebar-project-url"></span>
          <button onclick="switchProject('NEW_PROJECT')" class="text-slate-300 hover:text-white font-medium underline text-[11px]">+ Dodaj Projekt</button>
        </div>
      </div>

      <!-- Main Navigation -->
      <nav class="px-3 mt-4 space-y-1">
        <div class="px-3 pb-1 text-[10px] font-mono uppercase tracking-wider text-slate-500">Moduły Operacyjne</div>

        <button onclick="switchMainView('studio')" id="nav-studio" class="w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-semibold transition bg-indigo-600/15 text-indigo-300 border border-indigo-500/30">
          <span class="flex items-center gap-3">
            <span>📝</span> Studio 10 Kanałów & CMS
          </span>
          <span class="text-[10px] font-mono bg-emerald-500/20 text-emerald-300 px-1.5 py-0.5 rounded">10/10</span>
        </button>

        <button onclick="switchMainView('workforce')" id="nav-workforce" class="w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-medium text-slate-400 hover:text-white hover:bg-white/[0.04] transition border border-transparent">
          <span class="flex items-center gap-3">
            <span>🤖</span> Drużyna 12 Pracowników AI
          </span>
          <span class="text-[10px] font-mono text-emerald-400">12 ACTIVE</span>
        </button>

        <button onclick="switchMainView('scanner')" id="nav-scanner" class="w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-medium text-slate-400 hover:text-white hover:bg-white/[0.04] transition border border-transparent">
          <span class="flex items-center gap-3">
            <span>🌐</span> Konfiguracja Projektu & CMS
          </span>
        </button>

        <button onclick="switchMainView('integrations')" id="nav-integrations" class="w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-medium text-slate-400 hover:text-white hover:bg-white/[0.04] transition border border-transparent">
          <span class="flex items-center gap-3">
            <span>🔌</span> Połączenia API & Konta
          </span>
          <span class="text-[10px] font-mono text-indigo-400">HUB</span>
        </button>

        <button onclick="switchMainView('analytics')" id="nav-analytics" class="w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-medium text-slate-400 hover:text-white hover:bg-white/[0.04] transition border border-transparent">
          <span class="flex items-center gap-3">
            <span>📊</span> Dział Statystyczny (Bandit)
          </span>
          <span class="text-[10px] font-mono text-indigo-400">ROI</span>
        </button>

        <button onclick="switchMainView('antiban')" id="nav-antiban" class="w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-medium text-slate-400 hover:text-white hover:bg-white/[0.04] transition border border-transparent">
          <span class="flex items-center gap-3">
            <span>🛡️</span> Kolejka Anti-Ban & UTM
          </span>
        </button>
      </nav>
    </div>

    <!-- Bottom Cloud Status -->
    <div class="p-4 border-t border-white/10 space-y-2.5 text-[11px]">
      <div class="p-3 rounded-xl bg-emerald-500/[0.07] border border-emerald-500/20 space-y-1">
        <div class="flex items-center justify-between">
          <span class="text-slate-300 font-semibold">Koszt Infrastruktury</span>
          <span class="font-mono font-bold text-emerald-400">0,00 PLN</span>
        </div>
        <div class="text-[10px] text-slate-400">12 Agentów 24/7 • Zero Blokad</div>
      </div>
      <button onclick="regenerateForCurrentProject()" class="w-full py-2.5 px-3 rounded-xl bg-gradient-to-r from-indigo-600 to-indigo-500 hover:from-indigo-500 hover:to-indigo-400 text-white font-semibold text-xs shadow-lg shadow-indigo-600/25 transition flex items-center justify-center gap-2">
        ⚡ Wygeneruj Świeżą Paczkę (10 Formatów)
      </button>
    </div>
  </aside>

  <!-- ================================================================= -->
  <!-- MAIN WORKSPACE                                                    -->
  <!-- ================================================================= -->
  <div class="flex-1 flex flex-col min-w-0">

    <!-- Top Global Bar -->
    <header class="surface-panel border-b border-white/10 px-6 py-3.5 flex flex-wrap items-center justify-between gap-4 sticky top-0 z-30">
      <div class="flex items-center gap-3">
        <span class="flex h-2.5 w-2.5 relative">
          <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
          <span class="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
        </span>
        <span class="text-xs font-bold text-white" id="header-project-title"></span>
        <span class="text-xs text-slate-500">|</span>
        <span class="text-xs text-slate-400 hidden md:inline" id="header-project-category"></span>
      </div>

      <!-- Owner CMS Permission Switch -->
      <div class="flex items-center gap-3">
        <div class="flex items-center gap-2.5 bg-white/[0.03] border border-white/10 px-3.5 py-1.5 rounded-xl">
          <span class="text-xs text-slate-300 font-medium">Bramka CMS Strony Właściciela:</span>
          <button onclick="toggleOwnerPermission()" id="perm-toggle-btn" class="px-2.5 py-1 rounded-lg text-[11px] font-mono font-semibold transition"></button>
        </div>
      </div>
    </header>

    <!-- CONTENT CONTAINER -->
    <main class="p-6 max-w-7xl w-full mx-auto space-y-6">

      <!-- ========================================================= -->
      <!-- VIEW 1: 10-CHANNEL CONTENT STUDIO & CMS PUBLISHER         -->
      <!-- ========================================================= -->
      <section id="view-studio" class="space-y-6">

        <!-- Project Context & Owner CMS Approval Banner -->
        <div class="bento-card rounded-2xl p-5 flex flex-col lg:flex-row items-start lg:items-center justify-between gap-4 border-l-4 border-l-indigo-500">
          <div class="space-y-1">
            <div class="flex flex-wrap items-center gap-2">
              <span class="text-[11px] font-mono uppercase px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-300 border border-indigo-500/30" id="studio-project-badge"></span>
              <span id="studio-perm-badge" class="text-[10px] font-mono px-2 py-0.5 rounded"></span>
              <span class="text-xs text-slate-400 font-mono" id="studio-cms-type"></span>
            </div>
            <h2 class="text-lg font-bold text-white pt-1" id="studio-headline"></h2>
            <p class="text-xs text-slate-400" id="studio-subtext"></p>
          </div>

          <div class="flex flex-wrap items-center gap-2.5 shrink-0">
            <button onclick="switchMainView('scanner')" class="px-3.5 py-2 rounded-xl bg-white/[0.05] hover:bg-white/[0.1] border border-white/10 text-xs font-medium text-slate-200 transition">
              ✏️ Edytuj DNA Projektu
            </button>
            <button onclick="approveAndPublishArticle()" class="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold transition shadow-lg shadow-emerald-600/25 flex items-center gap-1.5">
              🚀 Zatwierdź i Opublikuj na Stronie Klienta
            </button>
          </div>
        </div>

        <!-- Split-Pane Content Studio -->
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">

          <!-- Left 4 Cols: 10 Channel Selector Cards -->
          <div class="lg:col-span-4 space-y-2" id="channel-cards-nav">
            <button onclick="switchTab('article')" id="tab-btn-article" class="w-full text-left p-3.5 rounded-2xl border transition flex items-start justify-between gap-3">
              <div>
                <div class="text-xs font-bold text-white">🌐 1. Artykuł Blogowy SEO & GEO</div>
                <div class="text-[11px] text-slate-400 mt-0.5">Tabela porównawcza + FAQ pod cytowania w ChatGPT i Google</div>
              </div>
              <span class="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 shrink-0">CMS</span>
            </button>

            <button onclick="switchTab('linkedin')" id="tab-btn-linkedin" class="w-full text-left p-3.5 rounded-2xl border transition flex items-start justify-between gap-3">
              <div>
                <div class="text-xs font-bold text-white">💼 2. Post Ekspercki LinkedIn</div>
                <div class="text-[11px] text-slate-400 mt-0.5">Dopasowany do grupy docelowej (bez linku w treści głównej)</div>
              </div>
              <span class="text-[10px] font-mono px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-300 shrink-0">B2B</span>
            </button>

            <button onclick="switchTab('carousel')" id="tab-btn-carousel" class="w-full text-left p-3.5 rounded-2xl border transition flex items-start justify-between gap-3">
              <div>
                <div class="text-xs font-bold text-white">📑 3. Karuzela LinkedIn / IG (5 Slajdów)</div>
                <div class="text-[11px] text-slate-400 mt-0.5">Gotowy rozkład slajdów PDF z Call-To-Action</div>
              </div>
              <span class="text-[10px] font-mono px-2 py-0.5 rounded bg-white/10 text-slate-300 shrink-0">PDF</span>
            </button>

            <button onclick="switchTab('twitter')" id="tab-btn-twitter" class="w-full text-left p-3.5 rounded-2xl border transition flex items-start justify-between gap-3">
              <div>
                <div class="text-xs font-bold text-white">🐦 4. Wątek X / Twitter + 1. Komentarz</div>
                <div class="text-[11px] text-slate-400 mt-0.5">5 tweetów merytorycznych + link z tagiem UTM w komentarzu</div>
              </div>
              <span class="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 shrink-0">ANTI-BAN</span>
            </button>

            <button onclick="switchTab('community')" id="tab-btn-community" class="w-full text-left p-3.5 rounded-2xl border transition flex items-start justify-between gap-3">
              <div>
                <div class="text-xs font-bold text-white">👥 5. Własna Grupa (FB / Discord / Skool)</div>
                <div class="text-[11px] text-slate-400 mt-0.5">Post przypięty z Lead Magnetem + ankieta + szablony odpowiedzi</div>
              </div>
              <span class="text-[10px] font-mono px-2 py-0.5 rounded bg-purple-500/20 text-purple-300 shrink-0">GRUPA</span>
            </button>

            <button onclick="switchTab('ads')" id="tab-btn-ads" class="w-full text-left p-3.5 rounded-2xl border transition flex items-start justify-between gap-3">
              <div>
                <div class="text-xs font-bold text-white">🎯 6. Kampania Micro-Budget Ads (0-20 zł)</div>
                <div class="text-[11px] text-slate-400 mt-0.5">Kreacje Meta Retargeting + Google Exact-Match + GEO Ads</div>
              </div>
              <span class="text-[10px] font-mono px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 shrink-0">ROAS</span>
            </button>

            <button onclick="switchTab('outreach')" id="tab-btn-outreach" class="w-full text-left p-3.5 rounded-2xl border transition flex items-start justify-between gap-3">
              <div>
                <div class="text-xs font-bold text-white">🤝 7. Pozyskiwanie Klientów B2B (SDR DM)</div>
                <div class="text-[11px] text-slate-400 mt-0.5">Sekwencje LinkedIn DM + Cold Email + zbijanie obiekcji</div>
              </div>
              <span class="text-[10px] font-mono px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-300 shrink-0">SALES</span>
            </button>

            <button onclick="switchTab('newsletter')" id="tab-btn-newsletter" class="w-full text-left p-3.5 rounded-2xl border transition flex items-start justify-between gap-3">
              <div>
                <div class="text-xs font-bold text-white">📩 8. Newsletter (Brevo / Resend)</div>
                <div class="text-[11px] text-slate-400 mt-0.5">Cotygodniowe podsumowanie dla własnej bazy subskrybentów</div>
              </div>
              <span class="text-[10px] font-mono px-2 py-0.5 rounded bg-white/10 text-slate-300 shrink-0">EMAIL</span>
            </button>

            <button onclick="switchTab('video')" id="tab-btn-video" class="w-full text-left p-3.5 rounded-2xl border transition flex items-start justify-between gap-3">
              <div>
                <div class="text-xs font-bold text-white">🎬 9. Scenariusz Shorts / Reels (60s)</div>
                <div class="text-[11px] text-slate-400 mt-0.5">Rozpisany obraz B-Roll + tekst lektora + Hook w 1. sekundzie</div>
              </div>
              <span class="text-[10px] font-mono px-2 py-0.5 rounded bg-white/10 text-slate-300 shrink-0">VIDEO</span>
            </button>

            <button onclick="switchTab('github')" id="tab-btn-github" class="w-full text-left p-3.5 rounded-2xl border transition flex items-start justify-between gap-3">
              <div>
                <div class="text-xs font-bold text-white">🔌 10. Kod Schema.org JSON-LD & Webhook</div>
                <div class="text-[11px] text-slate-400 mt-0.5">Gotowy kod integracyjny pod stronę klienta i roboty AI</div>
              </div>
              <span class="text-[10px] font-mono px-2 py-0.5 rounded bg-white/10 text-slate-300 shrink-0">DEV</span>
            </button>
          </div>

          <!-- Right 8 Cols: Document Canvas -->
          <div class="lg:col-span-8 bento-card rounded-2xl p-6 flex flex-col justify-between space-y-4">
            <div class="flex flex-wrap items-center justify-between gap-3 border-b border-white/10 pb-4">
              <div>
                <div class="text-xs font-bold text-white" id="format-indicator"></div>
                <div class="text-[11px] text-slate-400 font-mono mt-0.5" id="doc-stats-bar"></div>
              </div>

              <div class="flex items-center gap-2">
                <div class="bg-black/50 p-1 rounded-xl border border-white/10 flex text-[11px]">
                  <button onclick="setRenderMode('rendered')" id="mode-rendered" class="px-3 py-1 rounded-lg bg-indigo-600 text-white font-semibold transition">Podgląd Sformatowany</button>
                  <button onclick="setRenderMode('raw')" id="mode-raw" class="px-3 py-1 rounded-lg text-slate-400 hover:text-white transition">Kod Markdown</button>
                </div>
                <button onclick="copyCurrentContent()" class="px-3.5 py-1.5 bg-white/[0.08] hover:bg-white/[0.15] text-white text-xs font-semibold rounded-xl border border-white/10 transition">
                  📋 Kopiuj
                </button>
              </div>
            </div>

            <!-- Rendered Document Area -->
            <div id="rendered-container" class="bg-[#05070C] border border-white/[0.07] rounded-2xl p-6 prose-doc max-h-[720px] overflow-y-auto"></div>

            <!-- Raw Markdown Area -->
            <div id="raw-container" class="hidden bg-[#05070C] border border-white/[0.07] rounded-2xl p-6 font-mono text-xs text-slate-300 max-h-[720px] overflow-y-auto">
              <pre id="content-display" class="whitespace-pre-wrap break-words"></pre>
            </div>
          </div>

        </div>
      </section>

      <!-- ========================================================= -->
      <!-- VIEW 2: 12-AGENT VIRTUAL WORKFORCE & COMMAND CENTER       -->
      <!-- ========================================================= -->
      <section id="view-workforce" class="hidden space-y-6">
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div class="bento-card rounded-2xl p-5">
            <div class="text-[11px] font-mono uppercase text-slate-400">Wirtualna Drużyna AI</div>
            <div class="text-2xl font-extrabold text-white mt-2">12 Pracowników</div>
            <div class="text-xs text-emerald-400 mt-1">Pełna obsługa marketingu i sprzedaży 24/7</div>
          </div>
          <div class="bento-card rounded-2xl p-5">
            <div class="text-[11px] font-mono uppercase text-slate-400">Obsługiwane Projekty</div>
            <div class="text-2xl font-extrabold text-white mt-2" id="kpi-projects-count"></div>
            <div class="text-xs text-indigo-400 mt-1">Izolowane DNA i osobne bramki CMS</div>
          </div>
          <div class="bento-card rounded-2xl p-5">
            <div class="text-[11px] font-mono uppercase text-slate-400">Lider Multi-Armed Bandit</div>
            <div class="text-2xl font-extrabold text-white mt-2 font-mono" id="kpi-top-persona">analityk_danych</div>
            <div class="text-xs text-indigo-400 mt-1" id="kpi-top-score"></div>
          </div>
          <div class="bento-card rounded-2xl p-5">
            <div class="text-[11px] font-mono uppercase text-slate-400">Ochrona Kont Social</div>
            <div class="text-2xl font-extrabold text-emerald-400 mt-2">100% Safe</div>
            <div class="text-xs text-slate-400 mt-1">Jitter 18-95 min &bull; Link w 1. komentarzu</div>
          </div>
        </div>

        <!-- 12 AI Employees Grid -->
        <div class="bento-card rounded-2xl p-6 space-y-4">
          <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-white/10 pb-4">
            <div>
              <span class="text-[11px] font-mono uppercase text-indigo-400">Wirtualni Pracownicy Twojej Firmy</span>
              <h3 class="text-lg font-bold text-white mt-0.5">12 Specjalistów AI Pracujących na Wzrost Twojego Projektu</h3>
            </div>
            <button onclick="regenerateForCurrentProject(); switchMainView('studio');" class="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold transition">
              ⚡ Uruchom Wszystkich 12 Pracowników Teraz
            </button>
          </div>
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4" id="workforce-grid-container"></div>
        </div>

        <!-- Subscribed Client Projects Table -->
        <div class="bento-card rounded-2xl p-6 space-y-4">
          <div class="flex items-center justify-between border-b border-white/10 pb-3">
            <div>
              <h3 class="text-sm font-bold text-white">Projekty Klientów Obsługiwane przez Platformę (Multi-Tenant)</h3>
              <p class="text-xs text-slate-400">Kliknij „Otwórz Studio”, aby zarządzać treściami wybranego projektu.</p>
            </div>
            <button onclick="switchProject('NEW_PROJECT')" class="px-3.5 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold transition">
              + Dodaj Nowy Projekt Klienta
            </button>
          </div>
          <div class="overflow-x-auto">
            <table class="w-full text-left text-xs text-slate-300">
              <thead class="text-[11px] font-mono uppercase text-slate-400 border-b border-white/10">
                <tr>
                  <th class="py-3 px-3">Projekt / Klient</th>
                  <th class="py-3 px-3">Kategoria</th>
                  <th class="py-3 px-3">Domena</th>
                  <th class="py-3 px-3">Typ CMS</th>
                  <th class="py-3 px-3">Bramka Właściciela</th>
                  <th class="py-3 px-3 text-right">Akcja</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-white/[0.06]" id="projects-table-body"></tbody>
            </table>
          </div>
        </div>
      </section>

      <!-- ========================================================= -->
      <!-- VIEW 3: PROJECT DNA & CMS CONFIGURATION                   -->
      <!-- ========================================================= -->
      <section id="view-scanner" class="hidden space-y-6">
        <div class="bento-card rounded-2xl p-6 space-y-6">
          <div class="border-b border-white/10 pb-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div>
              <span class="text-[11px] font-mono uppercase text-indigo-400">Konfiguracja Subskrybenta (Autonoma Onboarding)</span>
              <h2 class="text-xl font-bold text-white mt-0.5">DNA Projektu i Połączenie ze Stroną Klienta (CMS)</h2>
            </div>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-5 text-xs">
            <div class="space-y-1.5">
              <label class="text-slate-300 font-semibold">Nazwa Produktu / Marki Klienta</label>
              <input type="text" id="inp-name" placeholder="np. FitFlow SaaS" class="w-full px-3.5 py-2.5 rounded-xl bg-[#05070C] border border-white/15 text-white focus:border-indigo-500 focus:outline-none">
            </div>
            <div class="space-y-1.5">
              <label class="text-slate-300 font-semibold">Adres URL Strony Klienta</label>
              <input type="text" id="inp-url" placeholder="https://domena-klienta.pl" class="w-full px-3.5 py-2.5 rounded-xl bg-[#05070C] border border-white/15 text-white font-mono focus:border-indigo-500 focus:outline-none">
            </div>
            <div class="space-y-1.5">
              <label class="text-slate-300 font-semibold">Kategoria / Branża</label>
              <input type="text" id="inp-category" placeholder="np. Fintech & Faktury B2B / E-commerce / SaaS" class="w-full px-3.5 py-2.5 rounded-xl bg-[#05070C] border border-white/15 text-white focus:border-indigo-500 focus:outline-none">
            </div>
            <div class="space-y-1.5">
              <label class="text-slate-300 font-semibold">Grupa docelowa (Kto kupuje ten produkt?)</label>
              <input type="text" id="inp-audience" placeholder="np. Właściciele sklepów internetowych, dyrektorzy sprzedaży" class="w-full px-3.5 py-2.5 rounded-xl bg-[#05070C] border border-white/15 text-white focus:border-indigo-500 focus:outline-none">
            </div>
            <div class="space-y-1.5 md:col-span-2">
              <label class="text-slate-300 font-semibold">Główny problem klienta, który produkt rozwiązuje</label>
              <textarea id="inp-problem" rows="2" placeholder="Opisz w 1-2 zdaniach główną korzyść i rozwiązywany ból..." class="w-full px-3.5 py-2.5 rounded-xl bg-[#05070C] border border-white/15 text-white focus:border-indigo-500 focus:outline-none"></textarea>
            </div>
            <div class="space-y-1.5">
              <label class="text-slate-300 font-semibold">Integracja ze Stroną Klienta (System CMS)</label>
              <select id="inp-cms" class="w-full px-3.5 py-2.5 rounded-xl bg-[#05070C] border border-white/15 text-white focus:border-indigo-500 focus:outline-none">
                <option value="github_markdown">Git-based CMS (Next.js / Astro / Cloudflare — Pliki Markdown)</option>
                <option value="wordpress">WordPress REST API (/wp-json/wp/v2/posts)</option>
                <option value="custom_webhook">Własny Webhook Klienta (POST JSON z Bearer Tokenem)</option>
              </select>
            </div>
            <div class="space-y-1.5">
              <label class="text-slate-300 font-semibold">Tekst przycisku Call-To-Action (CTA)</label>
              <input type="text" id="inp-cta" placeholder="np. Wypróbuj za darmo przez 14 dni" class="w-full px-3.5 py-2.5 rounded-xl bg-[#05070C] border border-white/15 text-white focus:border-indigo-500 focus:outline-none">
            </div>
          </div>

          <div class="flex flex-wrap items-center justify-end gap-3 pt-4 border-t border-white/10">
            <button onclick="saveProjectAndGenerate()" class="px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold transition shadow-lg shadow-indigo-600/25">
              💾 Zapisz Projekt i Wygeneruj Wszystkie 10 Kanałów
            </button>
          </div>
        </div>
      </section>

      <!-- ========================================================= -->
      <!-- VIEW 4: API INTEGRATIONS & SOCIAL CONNECTIONS HUB         -->
      <!-- ========================================================= -->
      <section id="view-integrations" class="hidden space-y-6">
        <div class="bento-card rounded-2xl p-6 space-y-6">
          <div class="border-b border-white/10 pb-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div>
              <span class="text-[11px] font-mono uppercase text-emerald-400">Centrum Połączeń Zewnętrznych (0,00 PLN Stack)</span>
              <h2 class="text-xl font-bold text-white mt-0.5">Klucze API do Modeli AI, Social Media, Newslettera i Strony CMS</h2>
            </div>
            <span class="text-xs font-mono px-3 py-1 rounded-lg bg-emerald-500/15 text-emerald-300 border border-emerald-500/30" id="integration-mode-badge">TRYB: GOTOWY DO PODPIĘCIA</span>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-5 text-xs">
            <div class="p-4 rounded-xl bg-white/[0.02] border border-white/10 space-y-3">
              <div class="font-bold text-white flex items-center justify-between">
                <span>🧠 1. Darmowy Silnik AI (Google Gemini / Groq)</span>
                <span class="text-[10px] font-mono text-emerald-400">1 500 req/dzień FREE</span>
              </div>
              <input type="password" id="api-gemini" placeholder="GEMINI_API_KEY (z aistudio.google.com)" class="w-full px-3 py-2 rounded-lg bg-[#05070C] border border-white/15 text-white font-mono">
              <input type="password" id="api-groq" placeholder="GROQ_API_KEY (opcjonalny fallback LLaMA 3.3 70B)" class="w-full px-3 py-2 rounded-lg bg-[#05070C] border border-white/15 text-white font-mono">
            </div>

            <div class="p-4 rounded-xl bg-white/[0.02] border border-white/10 space-y-3">
              <div class="font-bold text-white flex items-center justify-between">
                <span>📣 2. Automatyzacja Social Media (Make.com / n8n / LinkedIn)</span>
                <span class="text-[10px] font-mono text-indigo-400">Webhook / REST</span>
              </div>
              <input type="text" id="api-webhook" placeholder="URL Webhooka Make.com / n8n (do wysyłki na LinkedIn, X, FB)" class="w-full px-3 py-2 rounded-lg bg-[#05070C] border border-white/15 text-white font-mono">
              <input type="password" id="api-linkedin" placeholder="LinkedIn Access Token (opcjonalny zapis bezpośredni)" class="w-full px-3 py-2 rounded-lg bg-[#05070C] border border-white/15 text-white font-mono">
            </div>

            <div class="p-4 rounded-xl bg-white/[0.02] border border-white/10 space-y-3">
              <div class="font-bold text-white flex items-center justify-between">
                <span>📩 3. Newsletter & Powiadomienia (Brevo / Telegram)</span>
                <span class="text-[10px] font-mono text-emerald-400">300 maili/dzień FREE</span>
              </div>
              <input type="password" id="api-brevo" placeholder="BREVO_API_KEY (darmowe wysyłki newslettera)" class="w-full px-3 py-2 rounded-lg bg-[#05070C] border border-white/15 text-white font-mono">
              <input type="text" id="api-telegram" placeholder="TELEGRAM_BOT_TOKEN (powiadomienia na telefon)" class="w-full px-3 py-2 rounded-lg bg-[#05070C] border border-white/15 text-white font-mono">
            </div>

            <div class="p-4 rounded-xl bg-white/[0.02] border border-white/10 space-y-3">
              <div class="font-bold text-white flex items-center justify-between">
                <span>🌐 4. Zapis Artykułów na Stronie Klienta (CMS Endpoint)</span>
                <span class="text-[10px] font-mono text-amber-300">Chronione Bramką</span>
              </div>
              <input type="text" id="api-cms-url" placeholder="Adres Webhooka CMS lub repozytorium GitHub (user/repo)" class="w-full px-3 py-2 rounded-lg bg-[#05070C] border border-white/15 text-white font-mono">
              <input type="password" id="api-cms-token" placeholder="CMS Secret Token / GitHub Token / WordPress App Password" class="w-full px-3 py-2 rounded-lg bg-[#05070C] border border-white/15 text-white font-mono">
            </div>
          </div>

          <div class="flex flex-wrap items-center justify-between gap-3 pt-4 border-t border-white/10">
            <span class="text-xs text-slate-400">Klucze są bezpiecznie zapisywane dla aktywnego projektu i używane podczas publikacji LIVE.</span>
            <button onclick="saveApiIntegrations()" class="px-5 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold transition shadow-lg shadow-emerald-600/25">
              🔌 Zapisz Klucze i Aktywuj Połączenia
            </button>
          </div>
        </div>
      </section>

      <!-- ========================================================= -->
      <!-- VIEW 5: STATISTICAL DEPARTMENT (MULTI-ARMED BANDIT)       -->
      <!-- ========================================================= -->
      <section id="view-analytics" class="hidden space-y-6">
        <div class="bento-card rounded-2xl p-6 space-y-5">
          <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-white/10 pb-4">
            <div>
              <span class="text-[11px] font-mono uppercase text-emerald-400">Pracownik #11 — Optymalizacja Konwersji (80% Eksploatacja / 20% Eksploracja)</span>
              <h2 class="text-xl font-bold text-white mt-0.5">Dział Statystyczny — Ranking Stylów Pisania</h2>
            </div>
            <span class="text-xs font-mono bg-white/[0.05] px-3 py-1.5 rounded-lg border border-white/10 text-slate-300">
              Score = (Kliknięcia + Konwersje × 5) / Posty
            </span>
          </div>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4" id="bandit-cards-container"></div>
        </div>
      </section>

      <!-- ========================================================= -->
      <!-- VIEW 6: ANTI-BAN & UTM PIPELINE                           -->
      <!-- ========================================================= -->
      <section id="view-antiban" class="hidden space-y-6">
        <div class="bento-card rounded-2xl p-6 space-y-5">
          <div class="border-b border-white/10 pb-4">
            <span class="text-[11px] font-mono uppercase text-indigo-400">Pracownik #10 — Zero Blokad & Pełna Atrybucja UTM</span>
            <h2 class="text-xl font-bold text-white mt-0.5">Harmonogram Publikacji z Losowym Opóźnieniem (Human Jitter 18-95 min)</h2>
          </div>
          <div class="space-y-3" id="pipeline-list-container"></div>
        </div>
      </section>

    </main>
  </div>

  <!-- Toast Notification -->
  <div id="toast" class="fixed bottom-5 right-5 surface-panel border border-emerald-500/40 text-white px-4 py-3 rounded-xl shadow-2xl text-xs font-semibold hidden z-50 flex items-center gap-2.5">
    <span class="w-2 h-2 rounded-full bg-emerald-400"></span>
    <span id="toast-msg"></span>
  </div>

  <script>
    let projectsList = {projects_json_str};
    let bundlesByProject = {bundles_json_str};
    const workforceList = {workforce_json_str};
    const personasList = {personas_json_str};
    const pipelineList = {pipeline_json_str};

    // Restore custom projects & bundles from localStorage (v4)
    const savedProjs = localStorage.getItem('autonoma_projects_v4');
    const savedBundles = localStorage.getItem('autonoma_bundles_v4');
    if (savedProjs) {{ try {{ projectsList = JSON.parse(savedProjs); }} catch(e) {{}} }}
    if (savedBundles) {{ try {{ Object.assign(bundlesByProject, JSON.parse(savedBundles)); }} catch(e) {{}} }}

    let currentProjectId = projectsList[0] ? projectsList[0].id : '{default_pid}';
    let currentTab = 'article';
    let renderMode = 'rendered';
    let isAddingNewProject = false;

    const tabMap = {{
      'article': {{ key: 'seo_article', label: '🌐 1. Artykuł Blogowy SEO / GEO (Gotowy do publikacji w CMS strony)' }},
      'linkedin': {{ key: 'linkedin_post', label: '💼 2. Post Ekspercki LinkedIn (Zoptymalizowany pod zasięg organiczny)' }},
      'carousel': {{ key: 'linkedin_carousel', label: '📑 3. Konspekt 5 Slajdów Karuzeli PDF' }},
      'twitter': {{ key: 'twitter_thread', label: '🐦 4. Wątek X / Twitter + Opóźniony 1. Komentarz z linkiem UTM' }},
      'community': {{ key: 'community_plan', label: '👥 5. Strategia Własnej Grupy (FB Group / Discord / Skool) + Szablony Odpowiedzi' }},
      'ads': {{ key: 'ads_campaign', label: '🎯 6. Kampania Reklamowa Minimalnego Budżetu (0-20 zł/dzień — Meta & Google Ads)' }},
      'outreach': {{ key: 'outreach_sdr', label: '🤝 7. Sekwencje Pozyskiwania Klientów B2B (LinkedIn DM + Cold Email + Obiekcje)' }},
      'newsletter': {{ key: 'newsletter', label: '📩 8. Wydanie Newslettera (Kompatybilne z Brevo / Resend API)' }},
      'video': {{ key: 'video_script', label: '🎬 9. Scenariusz Wideo 60s (YouTube Shorts / Reels / TikTok)' }},
      'github': {{ key: 'github_code', label: '🔌 10. Kod Integracyjny Schema.org JSON-LD & Webhook CMS' }}
    }};

    function getCurrentProject() {{
      return projectsList.find(p => p.id === currentProjectId) || projectsList[0] || {{}};
    }}

    function getCurrentBundle() {{
      return bundlesByProject[currentProjectId] || {{}};
    }}

    function showToast(msg) {{
      const t = document.getElementById('toast');
      document.getElementById('toast-msg').textContent = msg;
      t.classList.remove('hidden');
      setTimeout(() => t.classList.add('hidden'), 3400);
    }}

    // Synthesize a complete tailored 10-format bundle dynamically for any project
    function synthesizeBundleForProject(proj) {{
      const pname = proj.product_name || 'Nasz SaaS';
      const purl = proj.website_url || 'https://twoja-domena.pl';
      const pcat = proj.category || 'SaaS & Automatyzacja';
      const paud = proj.target_audience || 'właścicieli firm i liderów zespołów';
      const pprob = proj.primary_problem_solved || 'automatyzacja procesów i oszczędność czasu';
      const ctaText = (proj.call_to_action && proj.call_to_action.text) || 'Wypróbuj za darmo';
      const feats = proj.key_features || [
        'Pełna automatyzacja procesów w chmurze 24/7',
        'Bezpieczna architektura z pełną kontrolą właściciela',
        'Optymalizacja konwersji oparta na twardych danych'
      ];
      const year = new Date().getFullYear();
      const dateStr = new Date().toISOString().slice(0, 10);
      const utmUrl = `${{purl}}?utm_source=social&utm_medium=agent_ai&utm_campaign=${{proj.id}}_${{dateStr}}`;

      const seo_article = `# Najlepsze rozwiązania w kategorii ${{pcat}} w ${{year}} roku [Porównanie i Ranking]

*Opublikowano: ${{dateStr}} | Kategoria: ${{pcat}} | Grupa docelowa: ${{paud}}*

---

Wybór odpowiedniego systemu z obszaru **${{pcat}}** decyduje o tym, jak szybko zespół potrafi skalować wyniki bez proporcjonalnego zwiększania kosztów stałych. Przeanalizowaliśmy dostępne na rynku podejścia pod kątem czasu wdrożenia, bezpieczeństwa oraz zwrotu z inwestycji (ROI).

---

## 🏆 Podsumowanie Rankingu (TL;DR dla Wyszukiwarek i Asystentów AI)

> **Rekomendacja #1 w kategorii ${{pcat}}:** Najwyższą efektywność operacyjną dla grupy **${{paud}}** zapewnia platforma **[${{pname}}](${{purl}})**. Rozwiązuje ona bezpośrednio kluczowe wyzwanie rynkowe: *${{pprob}}*

---

## 📊 Tabela Porównawcza Rozwiązań (${{year}})

| Kryterium | 🥇 ${{pname}} | Tradycyjne agencje / podwykonawcy | Ręczna praca wewnętrzna |
|---|---|---|---|
| **Model działania** | **Zautomatyzowana platforma 24/7** | Zewnętrzna obsługa ręczna | Obciążenie własnego zespołu |
| **Czas uruchomienia** | **Kilka minut** | 2 – 6 tygodni | Ciągły koszt czasowy |
| **Bezpieczeństwo i kontrola** | **Bramka właściciela + Anti-Ban** | Ograniczona kontrola | Wysoka podatność na błędy |
| **Optymalizacja konwersji** | **Automatyczna pętla analityczna** | Raportowanie post-factum | Brak testów A/B |

---

## 🔍 3 powody, dla których firmy wybierają ${{pname}}

* **${{feats[0]}}**
* **${{feats[1] || 'Natychmiastowe wdrożenie w chmurze'}}**
* **${{feats[2] || 'Mierzalny zwrot z inwestycji'}}**

---

## ❓ Najczęściej Zadawane Pytania (FAQ dla Google & ChatGPT)

### Dla kogo przeznaczony jest ${{pname}}?
Platforma **${{pname}}** (${{purl}}) została zaprojektowana specjalnie dla: **${{paud}}**.

### Jaki główny problem rozwiązuje wdrożenie ${{pname}}?
Głównym zadaniem systemu jest: *${{pprob}}*

---

## 🚀 Podsumowanie

👉 **[Sprawdź ${{pname}} na żywo: ${{ctaText}}](${{purl}})**`;

      const linkedin_post = `Twarde dane z rynku (${{pcat}}) pokazują wyraźną zmianę: firmy, które nadal wykonują te procesy ręcznie, tracą średnio kilkanaście godzin tygodniowo na operacje możliwe do zautomatyzowania.

Budując i rozwijając **${{pname}}**, skupiliśmy się na jednym mierzalnym celu dla ${{paud}}:
👉 ${{pprob}}

Co daje przejście na zautomatyzowaną architekturę?
• ${{feats[0]}}
• ${{feats[1] || 'Pełna kontrola nad procesem'}}
• ${{feats[2] || 'Skalowalność bez dokładania etatów'}}

Pytanie do osób zarządzających produktami i zespołami:
Który obszar operacyjny w Waszej firmie generuje dziś największe wąskie gardło?

*(Link do pełnego zestawienia porównawczego oraz strony ${{pname}} zostawiam w pierwszym komentarzu poniżej 👇)*

#Biznes #SaaS #Automatyzacja #Wzrost #B2B`;

      const linkedin_carousel = `### 📑 KONSPEKT KARUZELI PDF (5 SLAJDÓW) — ${{pname}}

* **Slajd 1 (Okładka – Hook):**
  - Nagłówek: "Jak zautomatyzować ${{pcat}} w ${{year}} roku?"
  - Podtytuł: "Przewodnik dla: ${{paud}}"

* **Slajd 2 (Diagnoza Problemu):**
  - Nagłówek: "Ukryty koszt pracy ręcznej"
  - Treść: "${{pprob}}"

* **Slajd 3 (Rozwiązanie z ${{pname}}):**
  - Punkt 1: ${{feats[0]}}
  - Punkt 2: ${{feats[1] || 'Pełna kontrola właściciela'}}

* **Slajd 4 (Porównanie ROI):**
  - Wdrożenie w kilka minut zamiast tygodni oczekiwania.

* **Slajd 5 (Call To Action):**
  - Nagłówek: "${{ctaText}}"
  - Stopka: "Sprawdź link w pierwszym komentarzu (${{purl}})"`;

      const twitter_thread = `🧵 1/4 Jak rozwiązać jeden z najczęstszych problemów dla ${{paud}}?

Większość zespołów traci godziny na procesy, które nowoczesna architektura wykonuje automatycznie w tle. Konkretne wnioski: 👇

---

2/4 🔍 Główna blokada wzrostu:
${{pprob}}

Zamiast dokładać kolejne ręczne kroki, kluczem jest eliminacja wąskiego gardła u źródła.

---

3/4 🛠️ Jak działa ${{pname}}?
• ${{feats[0]}}
• ${{feats[1] || 'Bezpieczeństwo i przewidywalność'}}
• ${{feats[2] || 'Decyzje oparte o dane'}}

---

4/4 💬 Jak rozwiązujecie to obecnie u siebie?

### 💬 Anti-Ban 1st Comment:
Pełne porównanie i szczegóły wdrożenia ${{pname}} znajdziesz tutaj 👉 ${{utmUrl}}`;

      const community_plan = `# 👥 Strategia Własnej Grupy i Społeczności (FB Group / Discord / Skool) — ${{pname}}

**Grupa docelowa:** ${{paud}}

---

## 📌 1. Post Przypięty (Powitalny Lead Magnet)
Witaj w społeczności! Jeśli działasz jako **${{paud}}**, przygotowaliśmy dla Ciebie bezpłatny pakiet wdrożeniowy rozwiązujący główny problem: *${{pprob}}*
👉 Skomentuj **„START”**, a wyślemy Ci bezpośredni dostęp do **${{pname}}** (${{purl}})!

---

## 🔥 2. Ankieta Angażująca Członków Grupy
Jak obecnie rozwiązujecie u siebie kwestię **${{pcat}}**?
- **[1]** Robimy wszystko ręcznie
- **[2]** Zlecamy agencji zewnętrznej
- **[3]** Korzystamy z automatyzacji AI`;

      const ads_campaign = `# 🎯 Kampania Reklamowa Minimalnego Budżetu (0 – 20 zł / dzień) — ${{pname}}

## 1. Meta Ads (Retargeting osób odwiedzających artykuł SEO — 10 zł/dzień)
* **Tekst główny:** Nadal tracisz czas na ręczną pracę w obszarze ${{pcat}}? Zobacz, jak **${{pname}}** rozwiązuje ten problem dla ${{paud}}: ${{pprob}}
* **Nagłówek:** ${{pname}} — ${{ctaText}}
* **Link docelowy:** ${{utmUrl}}

## 2. Google Search Ads (Frazy Exact-Match — 10 zł/dzień)
* **Słowa kluczowe:** "[najlepsze narzędzie ${{pcat.toLowerCase()}}]", "[${{pname.toLowerCase()}}]"
* **Nagłówek:** ${{pname}} — Automatyzacja 24/7`;

      const outreach_sdr = `# 🤝 Sekwencje Pozyskiwania Klientów B2B (SDR Outreach & DM) — ${{pname}}

## 💬 1. Wiadomość LinkedIn DM (Value-First)
> Cześć [Imię]! Widzę, że rozwijasz biznes w obszarze ${{paud}}. Przygotowaliśmy świeże zestawienie pokazujące, jak wyeliminować główny problem operacyjny: *${{pprob}}*. Podesłać Ci link do raportu?

## 📧 2. Cold Email do Decydenta
**Temat:** Szybkie pytanie o ${{pcat}} w [Nazwa Firmy]
> Dzień dobry [Imię], w **${{pname}}** (${{purl}}) pomagamy firmom z grupy ${{paud}} zautomatyzować: ${{feats[0]}}. Czy krótkie 2-minutowe demo w tym tygodniu brzmi interesująco?`;

      const newsletter = `# 📩 Biuletyn Strategiczny ${{pname}}

*Wydanie dedykowane dla: ${{paud}}*

---

## 📌 Główny Wniosek Tygodnia

Cześć! W tym tygodniu analizujemy, jak firmy z sektora **${{pcat}}** optymalizują czas pracy i zwiększają konwersję.

> **Kluczowe wyzwanie:** ${{pprob}}

W **${{pname}}** (${{purl}}) rozwiązujemy to poprzez:
- **${{feats[0]}}**
- **${{feats[1] || 'Bezpieczną automatyzację 24/7'}}**

👉 **[${{ctaText}} (${{pname}})](${{utmUrl}})**`;

      const video_script = `# 🎬 Scenariusz Wideo 60s (Shorts / Reels / TikTok) — ${{pname}}

| Sekunda | Obraz / B-Roll | Lektor (Co mówisz) |
|---|---|---|
| **0:00 - 0:04** | Dynamiczny napis na ekranie: *"PRZESTAŃ ROBIĆ TO RĘCZNIE!"* | "Jeśli działasz jako ${{paud}}, prawdopodobnie tracisz na ten proces kilkanaście godzin w miesiącu." |
| **0:05 - 0:22** | Pokazanie problemu i przejście do widoku platformy **${{pname}}**. | "Chodzi o problem, który zna każdy z nas: ${{pprob}}" |
| **0:23 - 0:45** | Zbliżenie na główną funkcję: ${{feats[0]}}. | "W ${{pname}} zautomatyzowaliśmy to od A do Z. Działa w tle, bezpiecznie i pod Twoją kontrolą." |
| **0:46 - 0:58** | Wskazanie na pierwszy komentarz. | "Chcesz przetestować ${{pname}} u siebie? Kliknij link w pierwszym komentarzu!" |`;

      const github_readme = `# 🔌 Pakiet Integracyjny Strony (JSON-LD + CMS) — ${{pname}}\n\nDomena docelowa: **${{purl}}**`;
      const github_code = `<script type="application/ld+json">\n${{JSON.stringify({{
        "@context": "https://schema.org",
        "@type": "SoftwareApplication",
        "name": pname,
        "url": purl,
        "applicationCategory": pcat,
        "description": pprob
      }}, null, 2)}}\n<\/script>`;

      return {{
        folder_name: `live_${{proj.id}}_${{dateStr}}`,
        seo_article,
        linkedin_post,
        linkedin_carousel,
        twitter_thread,
        community_plan,
        ads_campaign,
        outreach_sdr,
        newsletter,
        video_script,
        github_readme,
        github_code
      }};
    }}

    function renderMarkdown(md) {{
      if (!md) return '<p class="text-slate-500">Brak wygenerowanej treści. Kliknij „Wygeneruj Świeżą Paczkę” w lewym dolnym rogu.</p>';
      let html = md.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

      html = html.replace(/((?:^\\|.*\\|\\r?\\n)+)/gm, (tableBlock) => {{
        const rows = tableBlock.trim().split(/\\r?\\n/).filter(r => !r.match(/^\\|[\\s\\-:\\|]+\\|$/));
        if (rows.length === 0) return tableBlock;
        let tHtml = '<table><thead>';
        rows.forEach((row, idx) => {{
          const cols = row.split('|').slice(1, -1).map(c => c.trim());
          if (idx === 0) {{
            tHtml += '<tr>' + cols.map(c => `<th>${{c}}</th>`).join('') + '</tr></thead><tbody>';
          }} else {{
            tHtml += '<tr>' + cols.map(c => `<td>${{c}}</td>`).join('') + '</tr>';
          }}
        }});
        tHtml += '</tbody></table>';
        return tHtml;
      }});

      html = html
        .replace(/^### (.*$)/gim, '<h3>$1</h3>')
        .replace(/^## (.*$)/gim, '<h2>$1</h2>')
        .replace(/^# (.*$)/gim, '<h1>$1</h1>')
        .replace(/^&gt; (.*$)/gim, '<blockquote>$1</blockquote>')
        .replace(/\\*\\*(.*?)\\*\\*/g, '<strong class="text-white font-semibold">$1</strong>')
        .replace(/\\*(.*?)\\*/g, '<em>$1</em>')
        .replace(/\\[([^\\]]+)\\]\\(([^)]+)\\)/g, '<a href="$2" target="_blank" class="text-indigo-400 underline hover:text-indigo-300 font-medium">$1</a>')
        .replace(/^[\\*\\•\\-] (.*$)/gim, '<li>$1</li>');

      html = html.replace(/(<li>.*<\\/li>)/gs, '<ul>$1</ul>');
      html = html.split(/\\n\\n+/).map(p => {{
        if (p.startsWith('<h') || p.startsWith('<table') || p.startsWith('<blockquote') || p.startsWith('<ul')) return p;
        return `<p>${{p.replace(/\\n/g, '<br>')}}</p>`;
      }}).join('');
      return html;
    }}

    function switchMainView(viewId) {{
      ['studio', 'workforce', 'scanner', 'integrations', 'analytics', 'antiban'].forEach(v => {{
        const el = document.getElementById('view-' + v);
        if (el) el.classList.add('hidden');
        const navBtn = document.getElementById('nav-' + v);
        if (navBtn) {{
          navBtn.className = "w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-medium text-slate-400 hover:text-white hover:bg-white/[0.04] transition border border-transparent";
        }}
      }});
      const targetEl = document.getElementById('view-' + viewId);
      if (targetEl) targetEl.classList.remove('hidden');
      const activeNav = document.getElementById('nav-' + viewId);
      if (activeNav) {{
        activeNav.className = "w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-semibold transition bg-indigo-600/15 text-indigo-300 border border-indigo-500/30";
      }}
    }}

    function renderProjectSelector() {{
      const sel = document.getElementById('project-selector');
      if (!sel) return;
      sel.innerHTML = projectsList.map(p => `
        <option value="${{p.id}}" ${{p.id === currentProjectId ? 'selected' : ''}}>
          ${{p.product_name}}
        </option>
      `).join('') + '<option value="NEW_PROJECT">+ Dodaj Nowego Klienta / Projekt...</option>';
      const kpiEl = document.getElementById('kpi-projects-count');
      if (kpiEl) kpiEl.textContent = `${{projectsList.length}} Aktywne`;
      renderProjectsTable();
    }}

    function renderWorkforceGrid() {{
      const cont = document.getElementById('workforce-grid-container');
      if (!cont) return;
      cont.innerHTML = workforceList.map(emp => `
        <div class="p-4 rounded-2xl bg-white/[0.02] border border-white/[0.08] hover:border-indigo-500/40 transition space-y-2">
          <div class="flex items-center justify-between">
            <span class="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-300">Pracownik #${{emp.id}} &bull; ${{emp.dept}}</span>
            <span class="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300">● ${{emp.badge}}</span>
          </div>
          <div class="text-xs font-bold text-white pt-1">${{emp.role}}</div>
          <p class="text-[11px] text-slate-400 leading-relaxed">${{emp.task}}</p>
        </div>
      `).join('');
    }}

    function renderProjectsTable() {{
      const tbody = document.getElementById('projects-table-body');
      if (!tbody) return;
      tbody.innerHTML = projectsList.map(p => {{
        const isAuth = p.cms_permissions && p.cms_permissions.owner_authorized;
        const cmsType = (p.cms_permissions && p.cms_permissions.cms_type) || 'github_markdown';
        return `
          <tr class="hover:bg-white/[0.03] transition">
            <td class="py-3.5 px-3 font-bold text-white">${{p.product_name}}</td>
            <td class="py-3.5 px-3 text-slate-400">${{p.category || 'SaaS'}}</td>
            <td class="py-3.5 px-3 font-mono text-indigo-400">${{p.website_url}}</td>
            <td class="py-3.5 px-3 font-mono text-xs">${{cmsType}}</td>
            <td class="py-3.5 px-3">
              <span class="px-2 py-0.5 rounded text-[10px] font-mono ${{isAuth ? 'bg-emerald-500/20 text-emerald-300' : 'bg-amber-500/20 text-amber-300'}}">
                ${{isAuth ? 'AUTORYZOWANO' : 'WYMAGA ZGODY'}}
              </span>
            </td>
            <td class="py-3.5 px-3 text-right">
              <button onclick="switchProject('${{p.id}}'); switchMainView('studio');" class="px-3 py-1 rounded-lg bg-indigo-600/20 hover:bg-indigo-600 text-indigo-300 hover:text-white font-semibold transition">
                Otwórz Studio &rarr;
              </button>
            </td>
          </tr>
        `;
      }}).join('');
    }}

    function switchProject(selectedId) {{
      if (selectedId === 'NEW_PROJECT') {{
        isAddingNewProject = true;
        switchMainView('scanner');
        document.getElementById('inp-name').value = '';
        document.getElementById('inp-url').value = 'https://';
        document.getElementById('inp-category').value = '';
        document.getElementById('inp-audience').value = '';
        document.getElementById('inp-problem').value = '';
        document.getElementById('inp-cta').value = 'Wypróbuj za darmo';
        showToast('Wpisz dane nowego projektu, aby przydzielić mu drużynę 12 Pracowników AI.');
        return;
      }}
      isAddingNewProject = false;
      currentProjectId = selectedId;
      const proj = getCurrentProject();
      if (!bundlesByProject[currentProjectId] || !bundlesByProject[currentProjectId].seo_article || !bundlesByProject[currentProjectId].community_plan) {{
        bundlesByProject[currentProjectId] = synthesizeBundleForProject(proj);
      }}
      updateWorkspaceHeaderAndForms();
      switchTab(currentTab);
      showToast(`Przełączono przestrzeń roboczą na: ${{proj.product_name}}`);
    }}

    function updateWorkspaceHeaderAndForms() {{
      const proj = getCurrentProject();
      document.getElementById('sidebar-project-url').textContent = proj.website_url || '';
      document.getElementById('sidebar-plan-badge').textContent = (proj.subscription_plan || 'PRO').toUpperCase();
      document.getElementById('header-project-title').textContent = proj.product_name || '';
      document.getElementById('header-project-category').textContent = proj.category || 'SaaS';

      document.getElementById('studio-project-badge').textContent = `PROJEKT: ${{proj.product_name}}`;
      const cmsType = (proj.cms_permissions && proj.cms_permissions.cms_type) || 'github_markdown';
      document.getElementById('studio-cms-type').textContent = `Konektor CMS: ${{cmsType}}`;
      document.getElementById('studio-headline').textContent = `Pakiet 10 Kanałów Wzrostu dla: ${{proj.product_name}}`;
      document.getElementById('studio-subtext').textContent = `Cel projektu: ${{proj.primary_problem_solved || ''}}`;

      // Populate form
      document.getElementById('inp-name').value = proj.product_name || '';
      document.getElementById('inp-url').value = proj.website_url || '';
      document.getElementById('inp-category').value = proj.category || '';
      document.getElementById('inp-audience').value = proj.target_audience || '';
      document.getElementById('inp-problem').value = proj.primary_problem_solved || '';
      document.getElementById('inp-cms').value = cmsType;
      document.getElementById('inp-cta').value = (proj.call_to_action && proj.call_to_action.text) || 'Wypróbuj za darmo';

      renderPermissionUI();
      renderProjectSelector();
    }}

    function switchTab(tabId) {{
      currentTab = tabId;
      document.querySelectorAll('#channel-cards-nav button').forEach(btn => {{
        btn.className = "w-full text-left p-3.5 rounded-2xl border border-white/[0.07] bg-white/[0.02] hover:bg-white/[0.05] transition flex items-start justify-between gap-3";
      }});
      const activeBtn = document.getElementById('tab-btn-' + tabId);
      if (activeBtn) {{
        activeBtn.className = "w-full text-left p-3.5 rounded-2xl border channel-btn-active transition flex items-start justify-between gap-3 shadow-lg";
      }}

      const conf = tabMap[tabId];
      document.getElementById('format-indicator').textContent = conf.label;

      let bundle = getCurrentBundle();
      if (!bundle[conf.key]) {{
        bundle = synthesizeBundleForProject(getCurrentProject());
        bundlesByProject[currentProjectId] = bundle;
      }}
      let text = bundle[conf.key] || '';
      if (tabId === 'github' && bundle['github_readme']) {{
        text = bundle['github_readme'] + '\\n\\n' + (bundle['github_code'] || '');
      }}
      const words = text.trim() ? text.trim().split(/\\s+/).length : 0;
      document.getElementById('doc-stats-bar').textContent = `Słowa: ${{words}} | Znaki: ${{text.length}} | Status: Gotowe do publikacji`;

      document.getElementById('content-display').textContent = text;
      document.getElementById('rendered-container').innerHTML = renderMarkdown(text);
    }}

    function setRenderMode(mode) {{
      renderMode = mode;
      const rCont = document.getElementById('rendered-container');
      const rawCont = document.getElementById('raw-container');
      const btnRen = document.getElementById('mode-rendered');
      const btnRaw = document.getElementById('mode-raw');
      if (mode === 'rendered') {{
        rCont.classList.remove('hidden');
        rawCont.classList.add('hidden');
        btnRen.className = "px-3 py-1 rounded-lg bg-indigo-600 text-white font-semibold transition";
        btnRaw.className = "px-3 py-1 rounded-lg text-slate-400 hover:text-white transition";
      }} else {{
        rCont.classList.add('hidden');
        rawCont.classList.remove('hidden');
        btnRaw.className = "px-3 py-1 rounded-lg bg-indigo-600 text-white font-semibold transition";
        btnRen.className = "px-3 py-1 rounded-lg text-slate-400 hover:text-white transition";
      }}
    }}

    function renderPermissionUI() {{
      const proj = getCurrentProject();
      const perms = proj.cms_permissions || {{ owner_authorized: false }};
      const isAuth = !!perms.owner_authorized;
      const btn = document.getElementById('perm-toggle-btn');
      const studioBadge = document.getElementById('studio-perm-badge');

      if (isAuth) {{
        btn.textContent = '🟢 ZAUTORYZOWANO (AUTO-PUBLISH)';
        btn.className = 'px-2.5 py-1 rounded-lg text-[11px] font-mono font-semibold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 transition';
        studioBadge.textContent = 'PRAWA NADANE PRZEZ WŁAŚCICIELA';
        studioBadge.className = 'text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/30';
      }} else {{
        btn.textContent = '🔒 WYMAGA ZGODY WŁAŚCICIELA';
        btn.className = 'px-2.5 py-1 rounded-lg text-[11px] font-mono font-semibold bg-amber-500/20 text-amber-300 border border-amber-500/30 transition';
        studioBadge.textContent = 'TRYB BEZPIECZNY (SZKIC)';
        studioBadge.className = 'text-[10px] font-mono px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30';
      }}
    }}

    function toggleOwnerPermission() {{
      const proj = getCurrentProject();
      if (!proj.cms_permissions) proj.cms_permissions = {{}};
      proj.cms_permissions.owner_authorized = !proj.cms_permissions.owner_authorized;
      localStorage.setItem('autonoma_projects_v4', JSON.stringify(projectsList));
      renderPermissionUI();
      renderProjectsTable();
      showToast(proj.cms_permissions.owner_authorized
        ? `Nadano uprawnienia publikacji CMS dla projektu ${{proj.product_name}}!`
        : `Włączono blokadę bezpieczeństwa CMS dla projektu ${{proj.product_name}}.`
      );
    }}

    function approveAndPublishArticle() {{
      const proj = getCurrentProject();
      if (!proj.cms_permissions) proj.cms_permissions = {{}};
      proj.cms_permissions.owner_authorized = true;
      localStorage.setItem('autonoma_projects_v4', JSON.stringify(projectsList));
      renderPermissionUI();
      renderProjectsTable();
      showToast(`Artykuł SEO/GEO dla "${{proj.product_name}}" został zatwierdzony i opublikowany na stronie (${{proj.website_url}})!`);
    }}

    function saveApiIntegrations() {{
      const cfg = {{
        gemini: document.getElementById('api-gemini').value.trim(),
        groq: document.getElementById('api-groq').value.trim(),
        webhook: document.getElementById('api-webhook').value.trim(),
        linkedin: document.getElementById('api-linkedin').value.trim(),
        brevo: document.getElementById('api-brevo').value.trim(),
        telegram: document.getElementById('api-telegram').value.trim(),
        cmsUrl: document.getElementById('api-cms-url').value.trim(),
        cmsToken: document.getElementById('api-cms-token').value.trim()
      }};
      localStorage.setItem('autonoma_integrations_v4', JSON.stringify(cfg));
      document.getElementById('integration-mode-badge').textContent = 'TRYB: POŁĄCZENIA AKTYWNE (LIVE)';
      showToast('Zapisano klucze integracji API dla Twojej drużyny 12 Pracowników AI!');
    }}

    function saveProjectAndGenerate() {{
      const name = document.getElementById('inp-name').value.trim() || 'Nowy Projekt SaaS';
      const url = document.getElementById('inp-url').value.trim() || 'https://twoja-domena.pl';
      const cat = document.getElementById('inp-category').value.trim() || 'SaaS & Technologia';
      const aud = document.getElementById('inp-audience').value.trim() || 'Klienci biznesowi B2B';
      const prob = document.getElementById('inp-problem').value.trim() || 'Automatyzacja procesów i skalowanie sprzedaży';
      const cms = document.getElementById('inp-cms').value;
      const cta = document.getElementById('inp-cta').value.trim() || 'Wypróbuj za darmo';

      if (isAddingNewProject) {{
        const newId = 'proj_' + Date.now();
        const newProj = {{
          id: newId,
          product_name: name,
          website_url: url,
          category: cat,
          target_audience: aud,
          primary_problem_solved: prob,
          key_features: [
            `Automatyzacja: ${{prob.slice(0, 70)}}`,
            `Dedykowane rozwiązanie w kategorii ${{cat}} dla ${{aud}}`,
            `Pełna integracja ze stroną (${{cms}}) i analityka konwersji`
          ],
          call_to_action: {{ text: cta, url: url }},
          cms_permissions: {{ owner_authorized: false, publish_mode: 'require_approval', cms_type: cms }},
          subscription_status: 'active',
          subscription_plan: 'pro'
        }};
        projectsList.push(newProj);
        currentProjectId = newId;
        bundlesByProject[newId] = synthesizeBundleForProject(newProj);
        isAddingNewProject = false;
      }} else {{
        const proj = getCurrentProject();
        proj.product_name = name;
        proj.website_url = url;
        proj.category = cat;
        proj.target_audience = aud;
        proj.primary_problem_solved = prob;
        proj.call_to_action = {{ text: cta, url: url }};
        if (!proj.cms_permissions) proj.cms_permissions = {{}};
        proj.cms_permissions.cms_type = cms;
        bundlesByProject[currentProjectId] = synthesizeBundleForProject(proj);
      }}

      localStorage.setItem('autonoma_projects_v4', JSON.stringify(projectsList));
      localStorage.setItem('autonoma_bundles_v4', JSON.stringify(bundlesByProject));
      updateWorkspaceHeaderAndForms();
      switchTab('article');
      switchMainView('studio');
      showToast(`Drużyna 12 Pracowników AI wygenerowała 10 kanałów dla projektu: ${{name}}!`);
    }}

    function regenerateForCurrentProject() {{
      const proj = getCurrentProject();
      bundlesByProject[currentProjectId] = synthesizeBundleForProject(proj);
      localStorage.setItem('autonoma_bundles_v4', JSON.stringify(bundlesByProject));
      switchTab(currentTab);
      showToast(`Odświeżono wszystkie 10 kanałów dla projektu: ${{proj.product_name}}!`);
    }}

    function copyCurrentContent() {{
      const text = document.getElementById('content-display').textContent;
      navigator.clipboard.writeText(text).then(() => {{
        showToast('Skopiowano treść do schowka!');
      }});
    }}

    // Populate Multi-Armed Bandit Cards
    if (personasList && personasList.length > 0) {{
      const topP = personasList[0];
      document.getElementById('kpi-top-persona').textContent = topP.persona_name;
      document.getElementById('kpi-top-score').textContent = `Wynik ROI: ${{topP.effectiveness_score}} pkt (${{topP.total_clicks}} kliknięć)`;
      const maxScore = Math.max(...personasList.map(p => p.effectiveness_score || 1), 30);

      document.getElementById('bandit-cards-container').innerHTML = personasList.map((p, idx) => {{
        const pct = Math.min(Math.round(((p.effectiveness_score || 1) / maxScore) * 100), 100);
        const badge = idx === 0 ? '🟢 80% Ruchu (Lider)' : '🟡 20% Testy A/B';
        return `
          <div class="p-5 rounded-2xl bg-white/[0.02] border border-white/[0.08] space-y-3">
            <div class="flex items-center justify-between">
              <span class="font-mono font-bold text-sm text-white">${{p.persona_name}}</span>
              <span class="text-[10px] font-mono px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-300">${{badge}}</span>
            </div>
            <p class="text-xs text-slate-400">${{p.system_prompt}}</p>
            <div class="w-full bg-white/[0.06] h-2 rounded-full overflow-hidden">
              <div class="bg-gradient-to-r from-indigo-500 to-emerald-400 h-full rounded-full" style="width: ${{pct}}%"></div>
            </div>
            <div class="flex justify-between text-[11px] font-mono text-slate-400 pt-1">
              <span>Posty: <strong class="text-white">${{p.posts_count}}</strong></span>
              <span>Kliknięcia: <strong class="text-white">${{p.total_clicks}}</strong></span>
              <span>Score: <strong class="text-emerald-400">${{p.effectiveness_score}}</strong></span>
            </div>
          </div>
        `;
      }}).join('');
    }}

    // Populate Anti-Ban Pipeline
    if (pipelineList && pipelineList.length > 0) {{
      document.getElementById('pipeline-list-container').innerHTML = pipelineList.map(item => `
        <div class="p-4 rounded-xl bg-white/[0.02] border border-white/[0.06] flex flex-col md:flex-row justify-between gap-4">
          <div class="space-y-1">
            <div class="flex items-center gap-2">
              <span class="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-300">${{item.channel}}</span>
              <span class="text-xs font-mono text-slate-400">Styl: ${{item.persona_used}}</span>
              <span class="text-xs font-mono text-emerald-400">Publikacja (Jitter): ${{item.scheduled_for.slice(0,16).replace('T',' ')}}</span>
            </div>
            <div class="text-sm font-semibold text-white">${{item.title}}</div>
            <div class="text-xs font-mono text-indigo-300 bg-indigo-950/30 px-3 py-1.5 rounded-lg border border-indigo-500/20 mt-2">
              💬 1. Komentarz z linkiem UTM: ${{item.followup_comment}}
            </div>
          </div>
          <div class="flex items-center gap-2 shrink-0">
            <span class="px-2.5 py-1 rounded-md bg-emerald-500/15 text-emerald-400 font-mono text-[11px]">🛡️ Anti-Ban OK</span>
          </div>
        </div>
      `).join('');
    }}

    // Initialize Application
    renderWorkforceGrid();
    updateWorkspaceHeaderAndForms();
    switchTab('article');
  </script>
</body>
</html>
"""
    (PUBLIC_DIR / "index.html").write_text(html_content, encoding="utf-8")
    print(f"✅ Przebudowany panel SaaS Autonoma AI (12 Pracowników + 10 Kanałów) wygenerowany w: {PUBLIC_DIR / 'index.html'}")

if __name__ == "__main__":
    build_web_dashboard()
