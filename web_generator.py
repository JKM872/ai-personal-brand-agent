"""
Web Dashboard Generator for Cloudflare Pages / Workers.
Turns the latest queue posts and memory history into a beautiful,
responsive HTML/JS dashboard with instant 'Copy to Clipboard' buttons.
"""

import sys
import json
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
            if fpath.exists():
                latest_data[key] = fpath.read_text(encoding="utf-8")
            else:
                latest_data[key] = ""
                
    # Load memory history
    memory = {"runs": []}
    if MEMORY_FILE.exists():
        try:
            memory = json.loads(MEMORY_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
            
    # Save public/data.json for API / client rendering
    (PUBLIC_DIR / "data.json").write_text(
        json.dumps({"latest_topic": latest_folder.name if latest_folder else "", "latest": latest_data, "history": memory.get("runs", [])}, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )
    
    latest_title = latest_data.get("publish_status", "")
    topic_title = "Brak wygenerowanego tematu"
    source = "Cloud"
    if latest_folder:
        # Extract title from folder name
        parts = latest_folder.name.split("_", 2)
        if len(parts) >= 3:
            topic_title = parts[2].replace("-", " ").title()
            
    html_content = f"""<!DOCTYPE html>
<html lang="pl" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>⚡ AI Personal Brand Agent 24/7 | Panel Cloudflare</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {{
      darkMode: 'class',
      theme: {{
        extend: {{
          colors: {{
            brand: {{ 50: '#eef2ff', 500: '#6366f1', 600: '#4f46e5', 700: '#4338ca' }}
          }}
        }}
      }}
    }}
  </script>
  <style>
    pre {{ white-space: pre-wrap; word-wrap: break-word; }}
  </style>
</head>
<body class="bg-slate-950 text-slate-100 min-h-screen font-sans antialiased">

  <!-- Header -->
  <header class="border-b border-slate-800 bg-slate-900/80 backdrop-blur sticky top-0 z-50">
    <div class="max-w-6xl mx-auto px-4 py-4 flex flex-col sm:flex-row justify-between items-center gap-3">
      <div class="flex items-center gap-3">
        <span class="flex h-3 w-3 relative">
          <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
          <span class="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
        </span>
        <h1 class="text-xl font-bold tracking-tight text-white flex items-center gap-2">
          🚀 AI Personal Brand Agent <span class="text-xs bg-indigo-500/20 text-indigo-400 px-2 py-0.5 rounded-full border border-indigo-500/30">24/7 Live</span>
        </h1>
      </div>
      <div class="flex items-center gap-4 text-sm text-slate-400">
        <span>Serwer: <strong class="text-emerald-400">GitHub Actions + Cloudflare</strong></span>
        <a href="https://github.com/JKM872/ai-personal-brand-agent" target="_blank" class="text-indigo-400 hover:text-indigo-300 underline text-xs">Repozytorium GitHub &rarr;</a>
      </div>
    </div>
  </header>

  <!-- Main Container -->
  <main class="max-w-6xl mx-auto px-4 py-8 space-y-8">

    <!-- Hero Card: Current Content Pack -->
    <div class="bg-gradient-to-br from-slate-900 via-slate-900 to-indigo-950/40 border border-slate-800 rounded-2xl p-6 shadow-xl relative overflow-hidden">
      <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 border-b border-slate-800/80 pb-5">
        <div>
          <span class="text-xs font-semibold uppercase tracking-wider text-indigo-400 bg-indigo-950/60 px-2.5 py-1 rounded-md border border-indigo-800/50">Najnowszy temat w kolejce</span>
          <h2 class="text-2xl font-bold text-white mt-2" id="hero-title">{topic_title}</h2>
          <p class="text-slate-400 text-sm mt-1">Paczka: <code class="text-xs bg-slate-800 px-2 py-0.5 rounded text-indigo-300">{latest_folder.name if latest_folder else 'Brak'}</code></p>
        </div>
        <div class="flex gap-2">
          <a href="https://github.com/JKM872/ai-personal-brand-agent/actions" target="_blank" class="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium rounded-lg transition shadow-md shadow-indigo-600/20">
            ⚡ Odpal nowy cykl w chmurze
          </a>
        </div>
      </div>

      <!-- Navigation Tabs -->
      <div class="mt-6 flex flex-wrap gap-2 border-b border-slate-800 pb-3" id="tab-nav">
        <button onclick="switchTab('linkedin')" id="tab-btn-linkedin" class="px-3.5 py-1.5 rounded-lg text-sm font-medium bg-indigo-600 text-white transition">💼 LinkedIn Post</button>
        <button onclick="switchTab('carousel')" id="tab-btn-carousel" class="px-3.5 py-1.5 rounded-lg text-sm font-medium bg-slate-800 text-slate-300 hover:bg-slate-700 transition">📑 Karuzela PDF</button>
        <button onclick="switchTab('twitter')" id="tab-btn-twitter" class="px-3.5 py-1.5 rounded-lg text-sm font-medium bg-slate-800 text-slate-300 hover:bg-slate-700 transition">🐦 X / Twitter Thread</button>
        <button onclick="switchTab('newsletter')" id="tab-btn-newsletter" class="px-3.5 py-1.5 rounded-lg text-sm font-medium bg-slate-800 text-slate-300 hover:bg-slate-700 transition">📰 Newsletter</button>
        <button onclick="switchTab('video')" id="tab-btn-video" class="px-3.5 py-1.5 rounded-lg text-sm font-medium bg-slate-800 text-slate-300 hover:bg-slate-700 transition">🎬 Wideo Shorts (60s)</button>
        <button onclick="switchTab('github')" id="tab-btn-github" class="px-3.5 py-1.5 rounded-lg text-sm font-medium bg-slate-800 text-slate-300 hover:bg-slate-700 transition">💻 Kod Python / README</button>
        <button onclick="switchTab('api')" id="tab-btn-api" class="px-3.5 py-1.5 rounded-lg text-sm font-medium bg-slate-800 text-slate-300 hover:bg-slate-700 transition">🔌 API Payload (JSON)</button>
      </div>

      <!-- Content Viewer Area -->
      <div class="mt-4 relative">
        <div class="flex justify-between items-center mb-2">
          <span class="text-xs text-slate-400 font-mono" id="format-indicator">Format: LinkedIn Post (Markdown)</span>
          <button onclick="copyCurrentContent()" id="copy-btn" class="px-3 py-1 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded-md border border-slate-700 flex items-center gap-1.5 transition">
            <span>📋 Kopiuj do schowka</span>
          </button>
        </div>

        <div class="bg-slate-950 border border-slate-800 rounded-xl p-5 text-sm text-slate-300 font-mono overflow-x-auto max-h-[500px]">
          <pre id="content-display"></pre>
        </div>
      </div>
    </div>

    <!-- History / Memory Table -->
    <div class="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-lg">
      <h3 class="text-lg font-bold text-white mb-4 flex items-center gap-2">
        🕒 Ostatnie Cykle Wykonane w Chmurze (Pamięć Anty-Duplikacyjna)
      </h3>
      <div class="overflow-x-auto">
        <table class="w-full text-left text-sm text-slate-400">
          <thead class="text-xs uppercase bg-slate-800/60 text-slate-300 border-b border-slate-700">
            <tr>
              <th class="py-3 px-4">Czas</th>
              <th class="py-3 px-4">Źródło</th>
              <th class="py-3 px-4">Temat</th>
              <th class="py-3 px-4">Wynik</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-800 font-mono text-xs" id="history-tbody">
            <!-- Rendered by JS -->
          </tbody>
        </table>
      </div>
    </div>

  </main>

  <footer class="border-t border-slate-800 py-6 text-center text-xs text-slate-500">
    AI Brand Agent 24/7 &bull; Działa bezobsługowo na serwerach GitHub Actions i Cloudflare Pages
  </footer>

  <script>
    const dataStore = {json.dumps(latest_data, ensure_ascii=False)};
    const historyStore = {json.dumps(memory.get("runs", []), ensure_ascii=False)};

    let currentTab = 'linkedin';

    const tabMap = {{
      'linkedin': {{ key: 'linkedin_post', label: 'LinkedIn Post' }},
      'carousel': {{ key: 'linkedin_carousel', label: 'Konspekt Karuzeli PDF' }},
      'twitter': {{ key: 'twitter_thread', label: 'X / Twitter Thread' }},
      'newsletter': {{ key: 'newsletter', label: 'Newsletter Deep Dive' }},
      'video': {{ key: 'video_script', label: 'Scenariusz Wideo Shorts' }},
      'github': {{ key: 'github_code', label: 'Kod Python + README' }},
      'api': {{ key: 'api_payload', label: 'Gotowy Payload API / Webhook' }}
    }};

    function switchTab(tabId) {{
      currentTab = tabId;
      document.querySelectorAll('#tab-nav button').forEach(btn => {{
        btn.classList.remove('bg-indigo-600', 'text-white');
        btn.classList.add('bg-slate-800', 'text-slate-300');
      }});
      const activeBtn = document.getElementById('tab-btn-' + tabId);
      if (activeBtn) {{
        activeBtn.classList.add('bg-indigo-600', 'text-white');
        activeBtn.classList.remove('bg-slate-800', 'text-slate-300');
      }}
      const conf = tabMap[tabId];
      document.getElementById('format-indicator').textContent = 'Format: ' + conf.label;
      let text = dataStore[conf.key] || 'Brak treści';
      if (tabId === 'github' && dataStore['github_readme']) {{
        text = dataStore['github_readme'] + '\\n\\n' + '='.repeat(40) + '\\n# agent_guard.py\\n' + '='.repeat(40) + '\\n\\n' + (dataStore['github_code'] || '');
      }}
      document.getElementById('content-display').textContent = text;
    }}

    function copyCurrentContent() {{
      const text = document.getElementById('content-display').textContent;
      navigator.clipboard.writeText(text).then(() => {{
        const btn = document.getElementById('copy-btn');
        btn.innerHTML = '<span>✅ Skopiowano!</span>';
        btn.classList.add('bg-emerald-600', 'text-white');
        setTimeout(() => {{
          btn.innerHTML = '<span>📋 Kopiuj do schowka</span>';
          btn.classList.remove('bg-emerald-600', 'text-white');
        }}, 2000);
      }});
    }}

    // Render history
    const tbody = document.getElementById('history-tbody');
    const recent = historyStore.slice(-10).reverse();
    if (recent.length === 0) {{
      tbody.innerHTML = '<tr><td colspan="4" class="py-4 text-center">Brak historii</td></tr>';
    }} else {{
      tbody.innerHTML = recent.map(r => `
        <tr class="hover:bg-slate-800/40 transition">
          <td class="py-3 px-4">${{r.timestamp}}</td>
          <td class="py-3 px-4 text-indigo-400 font-semibold">${{r.source}}</td>
          <td class="py-3 px-4 text-slate-200"><a href="${{r.url}}" target="_blank" class="hover:underline">${{r.title}}</a></td>
          <td class="py-3 px-4 text-emerald-400">${{r.score}} pkt</td>
        </tr>
      `).join('');
    }}

    // Initial load
    switchTab('linkedin');
  </script>
</body>
</html>
"""
    (PUBLIC_DIR / "index.html").write_text(html_content, encoding="utf-8")
    print(f"✅ Panel Web Cloudflare wygenerowany w: {PUBLIC_DIR / 'index.html'}")

if __name__ == "__main__":
    build_web_dashboard()
