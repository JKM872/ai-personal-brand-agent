"""
Polsia-Grade Web Application Generator (Autonomous AI Company OS).
Builds a studio-quality, dark-mode glassmorphic SaaS interface in public/index.html
with rendered Markdown preview, Owner CMS Permission Gate controls, Project DNA Scanner,
Multi-Armed Bandit visual telemetry, and Anti-Ban queue inspector.
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

def get_latest_queue_folder():
    if not QUEUE_DIR.exists():
        return None
    folders = [f for f in QUEUE_DIR.iterdir() if f.is_dir()]
    if not folders:
        return None
    folders.sort(key=lambda x: x.name, reverse=True)
    return folders[0]

def build_web_dashboard():
    PUBLIC_DIR.mkdir(parents=True, exist_ok=True)
    
    latest_folder = get_latest_queue_folder()
    latest_data = {}
    
    if latest_folder:
        files = {
            "seo_article": "0_WEBSITE_SEO_ARTICLE.md",
            "linkedin_post": "1_LINKEDIN_POST.md",
            "linkedin_carousel": "2_LINKEDIN_CAROUSEL.md",
            "twitter_thread": "3_TWITTER_THREAD.md",
            "newsletter": "4_NEWSLETTER_EDITION.md",
            "video_script": "5_VIDEO_SHORTS_SCRIPT.md",
            "github_readme": "6_GITHUB_README.md",
            "github_code": "6_GITHUB_SNIPPET.py",
            "api_payload": "7_API_PAYLOAD_READY.json",
            "publish_status": "PUBLISH_STATUS.json"
        }
        for key, fname in files.items():
            fpath = latest_folder / fname
            latest_data[key] = fpath.read_text(encoding="utf-8") if fpath.exists() else ""

    memory = {"runs": []}
    if MEMORY_FILE.exists():
        try:
            memory = json.loads(MEMORY_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass

    profile = {}
    if PROFILE_PATH.exists():
        try:
            profile = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass

    personas = db.get_personas()
    scheduled_pipeline = db.get_scheduled_pipeline(limit=8)
    active_projects = db.get_active_projects()

    # Save structured JSON API file
    (PUBLIC_DIR / "data.json").write_text(
        json.dumps({
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "project_profile": profile,
            "projects": active_projects,
            "personas": personas,
            "latest_folder": latest_folder.name if latest_folder else "",
            "latest": latest_data,
            "history": memory.get("runs", []),
            "pipeline": scheduled_pipeline
        }, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    runs_list = memory.get("runs", [])
    latest_run = runs_list[-1] if runs_list else {"title": "Brak wygenerowanego tematu", "source": "System", "score": 95, "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")}

    html_content = f"""<!DOCTYPE html>
<html lang="pl" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Polsia Zero — Autonomous AI Growth OS</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {{
      darkMode: 'class',
      theme: {{
        extend: {{
          fontFamily: {{
            sans: ['Inter', 'system-ui', 'sans-serif'],
            mono: ['JetBrains Mono', 'monospace']
          }},
          colors: {{
            obsidian: '#06070B',
            panel: '#0D1017',
            panelHover: '#131722',
            borderSubtle: 'rgba(255,255,255,0.08)'
          }}
        }}
      }}
    }}
  </script>
  <style>
    body {{
      background-color: #06070B;
      background-image: 
        radial-gradient(ellipse 80% 50% at 50% -15%, rgba(99, 102, 241, 0.16), transparent),
        radial-gradient(ellipse 50% 40% at 85% 20%, rgba(16, 185, 129, 0.07), transparent);
      color: #F1F5F9;
    }}
    .glass-panel {{
      background: rgba(13, 16, 23, 0.82);
      backdrop-filter: blur(16px);
      border: 1px solid rgba(255, 255, 255, 0.08);
    }}
    .glass-card {{
      background: linear-gradient(180deg, rgba(22, 27, 38, 0.65) 0%, rgba(13, 16, 23, 0.85) 100%);
      border: 1px solid rgba(255, 255, 255, 0.07);
      transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
    }}
    .glass-card:hover {{
      border-color: rgba(99, 102, 241, 0.35);
      box-shadow: 0 8px 30px -10px rgba(99, 102, 241, 0.18);
    }}
    .prose-preview h1 {{ font-size: 1.5rem; font-weight: 700; color: #fff; margin-bottom: 0.75rem; line-height: 1.3; }}
    .prose-preview h2 {{ font-size: 1.15rem; font-weight: 600; color: #E2E8F0; margin-top: 1.5rem; margin-bottom: 0.5rem; border-bottom: 1px solid rgba(255,255,255,0.07); padding-bottom: 0.35rem; }}
    .prose-preview h3 {{ font-size: 1rem; font-weight: 600; color: #A5B4FC; margin-top: 1.1rem; margin-bottom: 0.35rem; }}
    .prose-preview p {{ color: #94A3B8; line-height: 1.7; margin-bottom: 0.85rem; font-size: 0.925rem; }}
    .prose-preview ul {{ list-style-type: disc; padding-left: 1.4rem; margin-bottom: 1rem; color: #CBD5E1; font-size: 0.925rem; }}
    .prose-preview li {{ margin-bottom: 0.35rem; }}
    .prose-preview blockquote {{ border-left: 3px solid #6366F1; background: rgba(99,102,241,0.08); padding: 0.75rem 1rem; border-radius: 0 0.5rem 0.5rem 0; color: #E2E8F0; margin: 1rem 0; font-style: italic; }}
    .prose-preview table {{ width: 100%; border-collapse: collapse; margin: 1.25rem 0; font-size: 0.82rem; }}
    .prose-preview th {{ background: rgba(30,41,59,0.7); color: #F8FAFC; font-weight: 600; text-align: left; padding: 0.65rem 0.85rem; border: 1px solid rgba(255,255,255,0.1); }}
    .prose-preview td {{ padding: 0.6rem 0.85rem; border: 1px solid rgba(255,255,255,0.07); color: #CBD5E1; }}
    ::-webkit-scrollbar {{ width: 6px; height: 6px; }}
    ::-webkit-scrollbar-track {{ background: #06070B; }}
    ::-webkit-scrollbar-thumb {{ background: #1E293B; border-radius: 3px; }}
    ::-webkit-scrollbar-thumb:hover {{ background: #334155; }}
  </style>
</head>
<body class="min-h-screen flex flex-col lg:flex-row selection:bg-indigo-500 selection:text-white">

  <!-- LEFT SIDEBAR NAVIGATION -->
  <aside class="w-full lg:w-64 glass-panel border-b lg:border-b-0 lg:border-r border-white/10 flex flex-col justify-between shrink-0 lg:h-screen lg:sticky lg:top-0 z-40">
    <div>
      <!-- Brand Logo -->
      <div class="px-6 py-5 flex items-center justify-between border-b border-white/10">
        <div class="flex items-center gap-3">
          <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 via-indigo-600 to-emerald-500 flex items-center justify-center shadow-lg shadow-indigo-500/25">
            <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" stroke-width="2.2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
          </div>
          <div>
            <div class="font-bold text-sm tracking-tight text-white flex items-center gap-1.5">
              POLSIA <span class="text-[10px] font-mono uppercase px-1.5 py-0.5 rounded bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">Zero</span>
            </div>
            <div class="text-[11px] text-slate-400">Autonomous Growth OS</div>
          </div>
        </div>
      </div>

      <!-- Multi-Tenant Project Switcher -->
      <div class="px-4 py-3.5 mx-3 mt-4 rounded-xl bg-white/[0.03] border border-white/[0.06] space-y-2">
        <div class="flex items-center justify-between text-[10px] text-slate-400">
          <span>WYBIERZ PROJEKT / KLIENTA</span>
          <span class="flex items-center gap-1 text-emerald-400 font-medium">
            <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span> Multi-Tenant
          </span>
        </div>
        <select id="project-selector" onchange="switchProject(this.value)" class="w-full px-2.5 py-1.5 rounded-lg bg-black/60 border border-white/10 text-white font-medium text-xs focus:border-indigo-500 focus:outline-none cursor-pointer">
          <!-- Populated by JS -->
        </select>
        <div class="text-[11px] text-indigo-400 font-mono truncate" id="sidebar-project-url"></div>
      </div>

      <!-- Navigation Links -->
      <nav class="px-3 mt-5 space-y-1">
        <button onclick="switchMainView('overview')" id="nav-overview" class="w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-xs font-medium transition bg-indigo-600/15 text-indigo-300 border border-indigo-500/30">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z"/></svg>
          Centrum Dowodzenia
        </button>

        <button onclick="switchMainView('studio')" id="nav-studio" class="w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-medium text-slate-400 hover:text-white hover:bg-white/[0.04] transition border border-transparent">
          <span class="flex items-center gap-3">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z"/></svg>
            Studio Treści & CMS
          </span>
          <span class="text-[10px] font-mono bg-emerald-500/20 text-emerald-300 px-1.5 py-0.5 rounded">7 plików</span>
        </button>

        <button onclick="switchMainView('scanner')" id="nav-scanner" class="w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-xs font-medium text-slate-400 hover:text-white hover:bg-white/[0.04] transition border border-transparent">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9"/></svg>
          Adaptacja Projektu (DNA)
        </button>

        <button onclick="switchMainView('analytics')" id="nav-analytics" class="w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-xs font-medium text-slate-400 hover:text-white hover:bg-white/[0.04] transition border border-transparent">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/></svg>
          Dział Statystyczny (Bandit)
        </button>

        <button onclick="switchMainView('antiban')" id="nav-antiban" class="w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-xs font-medium text-slate-400 hover:text-white hover:bg-white/[0.04] transition border border-transparent">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/></svg>
          Ochrona Anti-Ban & UTM
        </button>
      </nav>
    </div>

    <!-- Bottom Infrastructure Status -->
    <div class="p-4 border-t border-white/10 space-y-2.5 text-[11px]">
      <div class="flex items-center justify-between text-slate-400">
        <span>Budżet Operacyjny</span>
        <span class="font-mono font-semibold text-emerald-400">0,00 PLN / mies.</span>
      </div>
      <div class="flex items-center justify-between text-slate-400">
        <span>Router AI</span>
        <span class="font-mono text-slate-200">Gemini ➔ Groq ➔ CF</span>
      </div>
      <a href="https://github.com/JKM872/ai-personal-brand-agent/actions" target="_blank" class="mt-2 w-full py-2 px-3 rounded-lg bg-white/[0.05] hover:bg-white/[0.1] border border-white/10 text-center block text-slate-200 font-medium transition">
        ⚡ Wywołaj Cykl w Chmurze &rarr;
      </a>
    </div>
  </aside>

  <!-- MAIN CONTENT WORKSPACE -->
  <div class="flex-1 flex flex-col min-w-0">

    <!-- Top Status Header -->
    <header class="glass-panel border-b border-white/10 px-6 py-3.5 flex flex-wrap items-center justify-between gap-4 sticky top-0 z-30">
      <div class="flex items-center gap-3">
        <span class="text-xs font-medium text-slate-400">Ostatnia synchronizacja:</span>
        <span class="text-xs font-mono bg-white/[0.05] px-2.5 py-1 rounded-md border border-white/10 text-slate-200">{latest_run.get('timestamp', '')}</span>
        <span class="hidden sm:inline-flex items-center gap-1.5 text-xs font-medium px-2.5 py-1 rounded-md bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
          🛡️ Anti-Ban Guard: Aktywny (Jitter 18-95 min)
        </span>
      </div>

      <!-- Owner Permission Quick Switch -->
      <div class="flex items-center gap-3">
        <div class="flex items-center gap-2 bg-white/[0.03] border border-white/10 px-3 py-1.5 rounded-lg">
          <span class="text-xs text-slate-300">Prawa publikacji na stronie (CMS):</span>
          <button onclick="toggleOwnerPermission()" id="perm-toggle-btn" class="px-2.5 py-0.5 rounded text-[11px] font-mono font-semibold transition">
            <!-- JS populated -->
          </button>
        </div>
      </div>
    </header>

    <!-- WORKSPACE VIEWS CONTAINER -->
    <main class="p-6 max-w-7xl w-full mx-auto space-y-6">

      <!-- ========================================================= -->
      <!-- VIEW 1: OVERVIEW & COMMAND CENTER                         -->
      <!-- ========================================================= -->
      <section id="view-overview" class="space-y-6">
        
        <!-- Top KPI Grid -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div class="glass-card rounded-2xl p-5">
            <div class="flex items-center justify-between text-xs text-slate-400 mb-2">
              <span>WIRTUALNA DRUŻYNA</span>
              <span class="w-2 h-2 rounded-full bg-emerald-400"></span>
            </div>
            <div class="text-2xl font-bold text-white tracking-tight">6 Agentów AI</div>
            <div class="text-xs text-emerald-400 mt-1 font-medium">Pracują w chmurze co 6h</div>
          </div>

          <div class="glass-card rounded-2xl p-5">
            <div class="flex items-center justify-between text-xs text-slate-400 mb-2">
              <span>LIDER MULTI-ARMED BANDIT</span>
              <span class="font-mono text-[11px] text-indigo-400">80% Ruchu</span>
            </div>
            <div class="text-2xl font-bold text-white tracking-tight font-mono" id="kpi-top-persona">analityk_danych</div>
            <div class="text-xs text-slate-400 mt-1" id="kpi-top-score">Najwyższe ROI konwersji</div>
          </div>

          <div class="glass-card rounded-2xl p-5">
            <div class="flex items-center justify-between text-xs text-slate-400 mb-2">
              <span>POZYCJONOWANIE AI (GEO)</span>
              <span class="font-mono text-[11px] text-emerald-400">/llms.txt</span>
            </div>
            <div class="text-2xl font-bold text-white tracking-tight">Gotowe</div>
            <div class="text-xs text-slate-400 mt-1">ChatGPT + Perplexity + IndexNow</div>
          </div>

          <div class="glass-card rounded-2xl p-5">
            <div class="flex items-center justify-between text-xs text-slate-400 mb-2">
              <span>PRZETWORZONE TEMATY</span>
              <span class="font-mono text-[11px] text-slate-400">Bez duplikatów</span>
            </div>
            <div class="text-2xl font-bold text-white tracking-tight" id="kpi-runs-count">{len(runs_list)} cykli</div>
            <div class="text-xs text-indigo-400 mt-1 cursor-pointer hover:underline" onclick="switchMainView('studio')">Otwórz najnowszą paczkę &rarr;</div>
          </div>
        </div>

        <!-- Latest Cycle Banner + Quick Action -->
        <div class="glass-card rounded-2xl p-6 border-l-4 border-l-indigo-500 flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6">
          <div class="space-y-1.5">
            <div class="flex items-center gap-2">
              <span class="text-[11px] font-mono uppercase tracking-wider px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">Ostatni Wygenerowany Pakiet</span>
              <span class="text-xs text-slate-400 font-mono">Źródło: {latest_run.get('source', 'Cloud')}</span>
            </div>
            <h2 class="text-xl font-bold text-white">{latest_run.get('title', '')}</h2>
            <p class="text-xs text-slate-400 max-w-3xl">
              Dla tego tematu drużyna agentów wygenerowała: pełny artykuł blogowy SEO/GEO z tabelą porównawczą, post na LinkedIn, konspekt karuzeli PDF, wątek na X z opóźnionym pierwszym komentarzem UTM, wydanie newslettera oraz skrypt wideo Shorts.
            </p>
          </div>
          <div class="flex flex-wrap gap-3 shrink-0">
            <button onclick="switchMainView('studio')" class="px-4 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold transition shadow-lg shadow-indigo-600/25">
              📖 Przejrzyj i Opublikuj Artykuł
            </button>
            <button onclick="switchMainView('scanner')" class="px-4 py-2.5 rounded-xl bg-white/[0.06] hover:bg-white/[0.12] text-slate-200 text-xs font-medium border border-white/10 transition">
              🎯 Dopasuj do innego projektu
            </button>
          </div>
        </div>

        <!-- Two-Column Grid: Active Workforce Status & Recent Runs -->
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
          
          <!-- Left 5 Cols: Active AI Workforce -->
          <div class="lg:col-span-5 glass-card rounded-2xl p-6 space-y-4">
            <div class="flex items-center justify-between border-b border-white/10 pb-3">
              <h3 class="text-sm font-semibold text-white">Status Wirtualnych Pracowników</h3>
              <span class="text-[11px] font-mono text-emerald-400">Autonomia 24/7</span>
            </div>

            <div class="space-y-3 text-xs">
              <div class="p-3 rounded-xl bg-white/[0.02] border border-white/[0.05] flex items-start justify-between gap-3">
                <div>
                  <div class="font-semibold text-slate-200">1. Agent SEO & GEO (Redaktor Strony)</div>
                  <div class="text-slate-400 text-[11px] mt-0.5">Pisze artykuły porównawcze, aktualizuje <code class="text-indigo-300">/llms.txt</code> i pinguje IndexNow.</div>
                </div>
                <span class="px-2 py-0.5 rounded bg-emerald-500/15 text-emerald-400 font-mono text-[10px] shrink-0">AKTYWNY</span>
              </div>

              <div class="p-3 rounded-xl bg-white/[0.02] border border-white/[0.05] flex items-start justify-between gap-3">
                <div>
                  <div class="font-semibold text-slate-200">2. Agent CMS (Strażnik Uprawnień Właściciela)</div>
                  <div class="text-slate-400 text-[11px] mt-0.5">Publikuje artykuły na stronie (GitHub MDX / WordPress / Webhook) tylko po nadaniu praw.</div>
                </div>
                <span id="agent-cms-badge" class="px-2 py-0.5 rounded bg-amber-500/15 text-amber-300 font-mono text-[10px] shrink-0">CZEKA NA ZGODĘ</span>
              </div>

              <div class="p-3 rounded-xl bg-white/[0.02] border border-white/[0.05] flex items-start justify-between gap-3">
                <div>
                  <div class="font-semibold text-slate-200">3. Fabryka Social Media (LinkedIn, X, Shorts)</div>
                  <div class="text-slate-400 text-[11px] mt-0.5">Tworzy posty bez gołych linków w treści głównej; link z UTM idzie w 1. komentarzu.</div>
                </div>
                <span class="px-2 py-0.5 rounded bg-emerald-500/15 text-emerald-400 font-mono text-[10px] shrink-0">AKTYWNY</span>
              </div>

              <div class="p-3 rounded-xl bg-white/[0.02] border border-white/[0.05] flex items-start justify-between gap-3">
                <div>
                  <div class="font-semibold text-slate-200">4. Asystent Relacji Anti-Ban</div>
                  <div class="text-slate-400 text-[11px] mt-0.5">Odpowiada na komentarze w godzinach 08:00-22:00 z losowym opóźnieniem 15-45 min.</div>
                </div>
                <span class="px-2 py-0.5 rounded bg-emerald-500/15 text-emerald-400 font-mono text-[10px] shrink-0">AKTYWNY</span>
              </div>

              <div class="p-3 rounded-xl bg-white/[0.02] border border-white/[0.05] flex items-start justify-between gap-3">
                <div>
                  <div class="font-semibold text-slate-200">5. Dział Statystyczny (Multi-Armed Bandit)</div>
                  <div class="text-slate-400 text-[11px] mt-0.5">Mierzy CTR i konwersje z tagów UTM, kierując 80% ruchu na najskuteczniejszy styl.</div>
                </div>
                <span class="px-2 py-0.5 rounded bg-emerald-500/15 text-emerald-400 font-mono text-[10px] shrink-0">AKTYWNY</span>
              </div>
            </div>
          </div>

          <!-- Right 7 Cols: Cloud Execution History -->
          <div class="lg:col-span-7 glass-card rounded-2xl p-6 flex flex-col justify-between">
            <div>
              <div class="flex items-center justify-between border-b border-white/10 pb-3 mb-4">
                <h3 class="text-sm font-semibold text-white">Historia Cykli Wykonanych w Chmurze</h3>
                <span class="text-[11px] font-mono text-slate-400">Pamięć Anty-Duplikacyjna</span>
              </div>
              <div class="overflow-x-auto">
                <table class="w-full text-left text-xs text-slate-300">
                  <thead class="text-[11px] uppercase font-mono text-slate-400 border-b border-white/10">
                    <tr>
                      <th class="py-2.5 px-3">Czas</th>
                      <th class="py-2.5 px-3">Źródło</th>
                      <th class="py-2.5 px-3">Przetworzony Temat</th>
                      <th class="py-2.5 px-3 text-right">Potencjał</th>
                    </tr>
                  </thead>
                  <tbody class="divide-y divide-white/[0.05] font-mono text-[11px]" id="history-tbody"></tbody>
                </table>
              </div>
            </div>
          </div>

        </div>
      </section>

      <!-- ========================================================= -->
      <!-- VIEW 2: CONTENT STUDIO & WEBSITE CMS PUBLISHER            -->
      <!-- ========================================================= -->
      <section id="view-studio" class="hidden space-y-6">
        
        <!-- Owner Permission & Direct Website Publish Bar -->
        <div class="glass-card rounded-2xl p-5 flex flex-col md:flex-row items-start md:items-center justify-between gap-4 border border-indigo-500/30 bg-indigo-950/15">
          <div class="space-y-1">
            <div class="flex items-center gap-2">
              <span class="text-xs font-semibold text-white">🔐 Publikacja Artykułu na Twojej Stronie (CMS Gate)</span>
              <span id="studio-perm-badge" class="text-[10px] font-mono px-2 py-0.5 rounded"></span>
            </div>
            <p class="text-xs text-slate-400">
              Agent nigdy nie opublikuje artykułu na Twojej domenie bez Twojej autoryzacji. Możesz nadać stałe uprawnienia lub zatwierdzić ten artykuł jednym kliknięciem.
            </p>
          </div>
          <div class="flex items-center gap-3 shrink-0">
            <button onclick="toggleOwnerPermission()" class="px-3.5 py-2 rounded-xl bg-white/[0.06] hover:bg-white/[0.12] border border-white/10 text-xs font-medium text-slate-200 transition">
              ⚙️ Zmień prawa właściciela
            </button>
            <button onclick="approveAndPublishArticle()" id="btn-publish-cms" class="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold transition shadow-lg shadow-emerald-600/25">
              🚀 Zatwierdź i Opublikuj na Stronie
            </button>
          </div>
        </div>

        <!-- Studio Main Viewer -->
        <div class="glass-card rounded-2xl p-6 space-y-5">
          <!-- Format Tabs -->
          <div class="flex flex-wrap items-center justify-between gap-4 border-b border-white/10 pb-4">
            <div class="flex flex-wrap gap-1.5" id="tab-nav">
              <button onclick="switchTab('article')" id="tab-btn-article" class="px-3.5 py-2 rounded-xl text-xs font-semibold transition">🌐 Artykuł na Stronę (SEO/GEO)</button>
              <button onclick="switchTab('linkedin')" id="tab-btn-linkedin" class="px-3.5 py-2 rounded-xl text-xs font-semibold transition">LinkedIn Post</button>
              <button onclick="switchTab('carousel')" id="tab-btn-carousel" class="px-3.5 py-2 rounded-xl text-xs font-semibold transition">Karuzela PDF</button>
              <button onclick="switchTab('twitter')" id="tab-btn-twitter" class="px-3.5 py-2 rounded-xl text-xs font-semibold transition">X / Twitter + 1. Komentarz</button>
              <button onclick="switchTab('newsletter')" id="tab-btn-newsletter" class="px-3.5 py-2 rounded-xl text-xs font-semibold transition">Newsletter (Brevo)</button>
              <button onclick="switchTab('video')" id="tab-btn-video" class="px-3.5 py-2 rounded-xl text-xs font-semibold transition">Wideo Shorts (60s)</button>
              <button onclick="switchTab('github')" id="tab-btn-github" class="px-3.5 py-2 rounded-xl text-xs font-semibold transition">Kod / Snippet</button>
            </div>

            <!-- View Mode Toggle (Rendered vs Raw) + Copy -->
            <div class="flex items-center gap-2">
              <div class="bg-black/40 p-1 rounded-lg border border-white/10 flex text-[11px]">
                <button onclick="setRenderMode('rendered')" id="mode-rendered" class="px-2.5 py-1 rounded-md bg-indigo-600 text-white font-medium transition">Podgląd Wizualny</button>
                <button onclick="setRenderMode('raw')" id="mode-raw" class="px-2.5 py-1 rounded-md text-slate-400 hover:text-white transition">Kod Markdown</button>
              </div>
              <button onclick="copyCurrentContent()" id="copy-btn" class="px-3.5 py-1.5 bg-white/[0.08] hover:bg-white/[0.14] text-white text-xs font-medium rounded-lg border border-white/10 transition">
                📋 Kopiuj
              </button>
            </div>
          </div>

          <div class="text-xs font-mono text-indigo-400" id="format-indicator"></div>

          <!-- Rendered Markdown View -->
          <div id="rendered-container" class="bg-black/30 border border-white/[0.07] rounded-2xl p-6 prose-preview max-h-[620px] overflow-y-auto"></div>

          <!-- Raw Code View -->
          <div id="raw-container" class="hidden bg-black/50 border border-white/[0.07] rounded-2xl p-6 font-mono text-xs text-slate-300 max-h-[620px] overflow-y-auto">
            <pre id="content-display"></pre>
          </div>
        </div>
      </section>

      <!-- ========================================================= -->
      <!-- VIEW 3: PROJECT DNA SCANNER (POLSIA ADAPTATION)           -->
      <!-- ========================================================= -->
      <section id="view-scanner" class="hidden space-y-6">
        <div class="glass-card rounded-2xl p-6 space-y-6">
          <div class="border-b border-white/10 pb-4">
            <span class="text-[11px] font-mono uppercase text-indigo-400">Uniwersalna Adaptacja (Polsia Engine)</span>
            <h2 class="text-xl font-bold text-white mt-1">Dopasuj Drużynę Agentów do Dowolnego Projektu</h2>
            <p class="text-xs text-slate-400 mt-1">
              Podaj adres URL swojej strony i parametry projektu. Wszyscy agenci (SEO/GEO, Social Media, Komentarze, Newsletter) natychmiast przestawią swoją narrację, słowa kluczowe i call-to-action pod Twój biznes.
            </p>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-5 text-xs">
            <div class="space-y-1.5">
              <label class="text-slate-300 font-medium">Nazwa Twojego Produktu / Projektu</label>
              <input type="text" id="inp-name" class="w-full px-3.5 py-2.5 rounded-xl bg-black/40 border border-white/10 text-white focus:border-indigo-500 focus:outline-none">
            </div>
            <div class="space-y-1.5">
              <label class="text-slate-300 font-medium">Adres URL Strony (Domena do linków UTM i /llms.txt)</label>
              <input type="text" id="inp-url" class="w-full px-3.5 py-2.5 rounded-xl bg-black/40 border border-white/10 text-white font-mono focus:border-indigo-500 focus:outline-none">
            </div>
            <div class="space-y-1.5 md:col-span-2">
              <label class="text-slate-300 font-medium">Główny problem klienta, który rozwiązujesz (Value Proposition)</label>
              <textarea id="inp-problem" rows="2" class="w-full px-3.5 py-2.5 rounded-xl bg-black/40 border border-white/10 text-white focus:border-indigo-500 focus:outline-none"></textarea>
            </div>
            <div class="space-y-1.5">
              <label class="text-slate-300 font-medium">Grupa docelowa (Kto kupuje Twój produkt?)</label>
              <input type="text" id="inp-audience" class="w-full px-3.5 py-2.5 rounded-xl bg-black/40 border border-white/10 text-white focus:border-indigo-500 focus:outline-none">
            </div>
            <div class="space-y-1.5">
              <label class="text-slate-300 font-medium">System CMS Twojej Strony (Do automatycznej publikacji artykułów)</label>
              <select id="inp-cms" class="w-full px-3.5 py-2.5 rounded-xl bg-black/40 border border-white/10 text-white focus:border-indigo-500 focus:outline-none">
                <option value="github_markdown">Git-based CMS (Next.js / Astro / Cloudflare Pages — Pliki .md)</option>
                <option value="wordpress">WordPress REST API (/wp-json/wp/v2/posts)</option>
                <option value="custom_webhook">Własny Endpoint Webhook (POST JSON z Bearer Tokenem)</option>
              </select>
            </div>
          </div>

          <div class="flex flex-wrap items-center justify-between gap-4 pt-3 border-t border-white/10">
            <div id="scanner-status" class="text-xs text-emerald-400 font-mono"></div>
            <div class="flex gap-3">
              <button onclick="saveProjectDNA()" class="px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold transition shadow-lg shadow-indigo-600/25">
                💾 Zapisz DNA Projektu i Przestaw Agentów
              </button>
            </div>
          </div>
        </div>
      </section>

      <!-- ========================================================= -->
      <!-- VIEW 4: STATISTICAL DEPARTMENT (MULTI-ARMED BANDIT)       -->
      <!-- ========================================================= -->
      <section id="view-analytics" class="hidden space-y-6">
        <div class="glass-card rounded-2xl p-6 space-y-5">
          <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-white/10 pb-4">
            <div>
              <span class="text-[11px] font-mono uppercase text-emerald-400">Zamknięta Pętla Sprzężenia Zwrotnego</span>
              <h2 class="text-xl font-bold text-white mt-0.5">Dział Statystyczny — Algorytm Multi-Armed Bandit</h2>
            </div>
            <span class="text-xs font-mono bg-white/[0.05] px-3 py-1.5 rounded-lg border border-white/10 text-slate-300">
              Wzór: Score = (Kliknięcia + Konwersje × 5) / Posty
            </span>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-3 gap-4" id="bandit-cards-container">
            <!-- Populated by JS -->
          </div>
        </div>
      </section>

      <!-- ========================================================= -->
      <!-- VIEW 5: ANTI-BAN & UTM PIPELINE                           -->
      <!-- ========================================================= -->
      <section id="view-antiban" class="hidden space-y-6">
        <div class="glass-card rounded-2xl p-6 space-y-5">
          <div class="border-b border-white/10 pb-4">
            <span class="text-[11px] font-mono uppercase text-indigo-400">Bezpieczeństwo Kont & Atrybucja</span>
            <h2 class="text-xl font-bold text-white mt-0.5">Kolejka Publikacji z Losowym Opóźnieniem (Human Jitter)</h2>
            <p class="text-xs text-slate-400 mt-1">
              Każdy post ma wycięte linki z głównej treści (ochrona przed ucięciem zasięgów). Link ze śledzeniem UTM trafia automatycznie do 1. komentarza po losowym czasie.
            </p>
          </div>

          <div class="space-y-3" id="pipeline-list-container">
            <!-- Populated by JS -->
          </div>
        </div>
      </section>

    </main>
  </div>

  <!-- Toast Notification -->
  <div id="toast" class="fixed bottom-5 right-5 glass-panel border border-emerald-500/40 bg-slate-900/95 text-white px-4 py-3 rounded-xl shadow-2xl text-xs font-medium hidden z-50 flex items-center gap-2.5">
    <span class="w-2 h-2 rounded-full bg-emerald-400"></span>
    <span id="toast-msg">Zapisano!</span>
  </div>

  <script>
    const dataStore = {json.dumps(latest_data, ensure_ascii=False)};
    const historyStore = {json.dumps(runs_list, ensure_ascii=False)};
    const projectsList = {json.dumps(active_projects, ensure_ascii=False)};
    let projectProfile = {json.dumps(profile, ensure_ascii=False)};
    const personasList = {json.dumps(personas, ensure_ascii=False)};
    const pipelineList = {json.dumps(scheduled_pipeline, ensure_ascii=False)};

    // Render Multi-Tenant Project Selector
    function renderProjectSelector() {{
      const sel = document.getElementById('project-selector');
      if (!sel) return;
      sel.innerHTML = projectsList.map(p => `
        <option value="${{p.id}}" ${{p.id === (projectProfile.id || 'proj_polsia_zero') ? 'selected' : ''}}>
          📁 ${{p.product_name}}
        </option>
      `).join('') + '<option value="NEW_PROJECT">+ Dodaj Nowego Klienta / Projekt</option>';
    }}

    function switchProject(selectedId) {{
      if (selectedId === 'NEW_PROJECT') {{
        switchMainView('scanner');
        document.getElementById('inp-name').value = '';
        document.getElementById('inp-url').value = '';
        document.getElementById('inp-problem').value = '';
        document.getElementById('inp-audience').value = '';
        showToast('Wypełnij formularz poniżej, aby dodać nowego klienta/projekt.');
        return;
      }}
      const found = projectsList.find(p => p.id === selectedId);
      if (found) {{
        projectProfile = found;
        localStorage.setItem('polsia_project_profile', JSON.stringify(projectProfile));
        initProjectScannerForm();
        renderPermissionUI();
        showToast(`Przełączono na projekt: ${{found.product_name}}`);
      }}
    }}

    // Load saved overrides from localStorage if owner edited in browser
    const savedProfile = localStorage.getItem('polsia_project_profile');
    if (savedProfile) {{
      try {{ projectProfile = JSON.parse(savedProfile); }} catch(e) {{}}
    }}

    let currentTab = 'article';
    let renderMode = 'rendered';

    const tabMap = {{
      'article': {{ key: 'seo_article', label: 'Artykuł Blogowy SEO / GEO (Gotowy do publikacji na stronie)' }},
      'linkedin': {{ key: 'linkedin_post', label: 'Post Ekspercki LinkedIn (Bez linku w treści głównej)' }},
      'carousel': {{ key: 'linkedin_carousel', label: 'Konspekt 5 Slajdów Karuzeli PDF' }},
      'twitter': {{ key: 'twitter_thread', label: 'Wątek X / Twitter + Opóźniony 1. Komentarz UTM' }},
      'newsletter': {{ key: 'newsletter', label: 'Wydanie Newslettera (Brevo / Resend)' }},
      'video': {{ key: 'video_script', label: 'Scenariusz Wideo 60s (YouTube Shorts / Reels / TikTok)' }},
      'github': {{ key: 'github_code', label: 'Kod Techniczny / Proof-of-Work' }}
    }};

    function showToast(msg) {{
      const t = document.getElementById('toast');
      document.getElementById('toast-msg').textContent = msg;
      t.classList.remove('hidden');
      setTimeout(() => t.classList.add('hidden'), 3200);
    }}

    function switchMainView(viewId) {{
      ['overview', 'studio', 'scanner', 'analytics', 'antiban'].forEach(v => {{
        document.getElementById('view-' + v).classList.add('hidden');
        const navBtn = document.getElementById('nav-' + v);
        if (navBtn) {{
          navBtn.className = "w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-medium text-slate-400 hover:text-white hover:bg-white/[0.04] transition border border-transparent";
        }}
      }});
      document.getElementById('view-' + viewId).classList.remove('hidden');
      const activeNav = document.getElementById('nav-' + viewId);
      if (activeNav) {{
        activeNav.className = "w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-medium transition bg-indigo-600/15 text-indigo-300 border border-indigo-500/30";
      }}
    }}

    // Clean Markdown-to-HTML Renderer
    function renderMarkdown(md) {{
      if (!md) return '<p class="text-slate-500">Brak wygenerowanej treści w tym formacie.</p>';
      let html = md
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;');

      // Render Markdown Tables
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
        .replace(/\\[([^\\]]+)\\]\\(([^)]+)\\)/g, '<a href="$2" target="_blank" class="text-indigo-400 underline hover:text-indigo-300">$1</a>')
        .replace(/^[\\*\\•\\-] (.*$)/gim, '<li>$1</li>');

      html = html.replace(/(<li>.*<\\/li>)/gs, '<ul>$1</ul>');
      html = html.split(/\\n\\n+/).map(p => {{
        if (p.startsWith('<h') || p.startsWith('<table') || p.startsWith('<blockquote') || p.startsWith('<ul')) return p;
        return `<p>${{p.replace(/\\n/g, '<br>')}}</p>`;
      }}).join('');
      return html;
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
        btnRen.className = "px-2.5 py-1 rounded-md bg-indigo-600 text-white font-medium transition";
        btnRaw.className = "px-2.5 py-1 rounded-md text-slate-400 hover:text-white transition";
      }} else {{
        rCont.classList.add('hidden');
        rawCont.classList.remove('hidden');
        btnRaw.className = "px-2.5 py-1 rounded-md bg-indigo-600 text-white font-medium transition";
        btnRen.className = "px-2.5 py-1 rounded-md text-slate-400 hover:text-white transition";
      }}
    }}

    function switchTab(tabId) {{
      currentTab = tabId;
      document.querySelectorAll('#tab-nav button').forEach(btn => {{
        btn.className = "px-3.5 py-2 rounded-xl text-xs font-medium bg-white/[0.04] text-slate-300 hover:bg-white/[0.08] transition";
      }});
      const activeBtn = document.getElementById('tab-btn-' + tabId);
      if (activeBtn) {{
        activeBtn.className = "px-3.5 py-2 rounded-xl text-xs font-semibold bg-indigo-600 text-white shadow-md shadow-indigo-600/20 transition";
      }}
      const conf = tabMap[tabId];
      document.getElementById('format-indicator').textContent = conf.label;
      let text = dataStore[conf.key] || 'Brak treści';
      if (tabId === 'github' && dataStore['github_readme']) {{
        text = dataStore['github_readme'] + '\\n\\n' + (dataStore['github_code'] || '');
      }}
      document.getElementById('content-display').textContent = text;
      document.getElementById('rendered-container').innerHTML = renderMarkdown(text);
    }}

    function copyCurrentContent() {{
      const text = document.getElementById('content-display').textContent;
      navigator.clipboard.writeText(text).then(() => {{
        showToast('Skopiowano treść do schowka!');
      }});
    }}

    function renderPermissionUI() {{
      const perms = (projectProfile && projectProfile.cms_permissions) || {{ owner_authorized: false }};
      const isAuth = !!perms.owner_authorized;
      const btn = document.getElementById('perm-toggle-btn');
      const studioBadge = document.getElementById('studio-perm-badge');
      const agentBadge = document.getElementById('agent-cms-badge');

      if (isAuth) {{
        btn.textContent = 'ZAUTORYZOWANO (AUTO-PUBLISH)';
        btn.className = 'px-2.5 py-0.5 rounded text-[11px] font-mono font-semibold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 transition';
        studioBadge.textContent = 'PRAWA NADANE PRZEZ WŁAŚCICIELA';
        studioBadge.className = 'text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/30';
        agentBadge.textContent = 'AUTONOMICZNY';
        agentBadge.className = 'px-2 py-0.5 rounded bg-emerald-500/15 text-emerald-400 font-mono text-[10px] shrink-0';
      }} else {{
        btn.textContent = 'ZABLOKOWANE (WYMAGA ZGODY)';
        btn.className = 'px-2.5 py-0.5 rounded text-[11px] font-mono font-semibold bg-amber-500/20 text-amber-300 border border-amber-500/30 transition';
        studioBadge.textContent = 'WYMAGA AKCEPTACJI WŁAŚCICIELA';
        studioBadge.className = 'text-[10px] font-mono px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30';
        agentBadge.textContent = 'CZEKA NA ZGODĘ';
        agentBadge.className = 'px-2 py-0.5 rounded bg-amber-500/15 text-amber-300 font-mono text-[10px] shrink-0';
      }}
    }}

    function toggleOwnerPermission() {{
      if (!projectProfile.cms_permissions) projectProfile.cms_permissions = {{}};
      projectProfile.cms_permissions.owner_authorized = !projectProfile.cms_permissions.owner_authorized;
      localStorage.setItem('polsia_project_profile', JSON.stringify(projectProfile));
      renderPermissionUI();
      if (projectProfile.cms_permissions.owner_authorized) {{
        showToast('Nadano agentowi prawo do publikowania artykułów na stronie!');
      }} else {{
        showToast('Cofnięto automatyczne prawa publikacji — artykuły trafią tylko do szkiców.');
      }}
    }}

    function approveAndPublishArticle() {{
      if (!projectProfile.cms_permissions) projectProfile.cms_permissions = {{}};
      projectProfile.cms_permissions.owner_authorized = true;
      localStorage.setItem('polsia_project_profile', JSON.stringify(projectProfile));
      renderPermissionUI();
      showToast('Artykuł zatwierdzony przez właściciela i przekazany do publikacji CMS!');
    }}

    function initProjectScannerForm() {{
      document.getElementById('sidebar-project-name').textContent = projectProfile.product_name || 'Polsia Zero';
      document.getElementById('sidebar-project-url').textContent = projectProfile.website_url || 'https://twoja-domena.pl';
      document.getElementById('inp-name').value = projectProfile.product_name || '';
      document.getElementById('inp-url').value = projectProfile.website_url || '';
      document.getElementById('inp-problem').value = projectProfile.primary_problem_solved || '';
      document.getElementById('inp-audience').value = projectProfile.target_audience || '';
      if (projectProfile.cms_permissions && projectProfile.cms_permissions.cms_type) {{
        document.getElementById('inp-cms').value = projectProfile.cms_permissions.cms_type;
      }}
    }}

    function saveProjectDNA() {{
      projectProfile.product_name = document.getElementById('inp-name').value.trim() || 'Twój Projekt';
      projectProfile.website_url = document.getElementById('inp-url').value.trim() || 'https://twoja-domena.pl';
      projectProfile.primary_problem_solved = document.getElementById('inp-problem').value.trim();
      projectProfile.target_audience = document.getElementById('inp-audience').value.trim();
      if (!projectProfile.cms_permissions) projectProfile.cms_permissions = {{}};
      projectProfile.cms_permissions.cms_type = document.getElementById('inp-cms').value;

      localStorage.setItem('polsia_project_profile', JSON.stringify(projectProfile));
      initProjectScannerForm();
      showToast('Zapisano nowe DNA projektu! Wszyscy agenci zostali przestawieni.');
    }}

    // Populate History Table
    const tbody = document.getElementById('history-tbody');
    const recent = historyStore.slice(-8).reverse();
    tbody.innerHTML = recent.map(r => `
      <tr class="hover:bg-white/[0.03] transition">
        <td class="py-3 px-3 text-slate-400 whitespace-nowrap">${{r.timestamp}}</td>
        <td class="py-3 px-3"><span class="px-2 py-0.5 rounded bg-indigo-500/15 text-indigo-300">${{r.source}}</span></td>
        <td class="py-3 px-3 text-slate-200 font-sans font-medium"><a href="${{r.url}}" target="_blank" class="hover:text-indigo-400 transition">${{r.title}}</a></td>
        <td class="py-3 px-3 text-right text-emerald-400 font-semibold">${{r.score}} pkt</td>
      </tr>
    `).join('');

    // Populate Multi-Armed Bandit Cards
    if (personasList && personasList.length > 0) {{
      const topP = personasList[0];
      document.getElementById('kpi-top-persona').textContent = topP.persona_name;
      document.getElementById('kpi-top-score').textContent = `Wynik ROI: ${{topP.effectiveness_score}} pkt (${{topP.total_clicks}} kliknięć)`;
      const maxScore = Math.max(...personasList.map(p => p.effectiveness_score || 1), 30);

      document.getElementById('bandit-cards-container').innerHTML = personasList.map((p, idx) => {{
        const pct = Math.min(Math.round(((p.effectiveness_score || 1) / maxScore) * 100), 100);
        const badge = idx === 0 ? '🟢 80% Eksploatacja (Lider)' : '🟡 20% Eksploracja';
        return `
          <div class="p-5 rounded-2xl bg-white/[0.02] border border-white/[0.07] space-y-3">
            <div class="flex items-center justify-between">
              <span class="font-mono font-bold text-sm text-white">${{p.persona_name}}</span>
              <span class="text-[10px] font-mono px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-300">${{badge}}</span>
            </div>
            <p class="text-xs text-slate-400 line-clamp-2">${{p.system_prompt}}</p>
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
              <span class="text-xs font-mono text-slate-400">Persona: ${{item.persona_used}}</span>
              <span class="text-xs font-mono text-emerald-400">Zaplanowano (Jitter): ${{item.scheduled_for.slice(0,16).replace('T',' ')}}</span>
            </div>
            <div class="text-sm font-semibold text-white">${{item.title}}</div>
            <div class="text-xs font-mono text-indigo-300 bg-indigo-950/30 px-3 py-1.5 rounded-lg border border-indigo-500/20 mt-2">
              💬 1. Komentarz (z opóźnieniem): ${{item.followup_comment}}
            </div>
          </div>
          <div class="flex items-center gap-2 shrink-0">
            <span class="px-2.5 py-1 rounded-md bg-emerald-500/15 text-emerald-400 font-mono text-[11px]">🛡️ Anti-Ban OK</span>
          </div>
        </div>
      `).join('');
    }}

    // Initialize
    renderProjectSelector();
    initProjectScannerForm();
    renderPermissionUI();
    switchTab('article');
  </script>
</body>
</html>
"""
    (PUBLIC_DIR / "index.html").write_text(html_content, encoding="utf-8")
    print(f"✅ Nowy panel Polsia Zero OS wygenerowany w: {PUBLIC_DIR / 'index.html'}")

if __name__ == "__main__":
    build_web_dashboard()
