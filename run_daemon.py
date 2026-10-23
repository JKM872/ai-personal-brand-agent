"""
24/7 Background Daemon for Personal Brand Engine.
Runs continuously in the background, waking up every N hours (configured in config/accounts.json)
to scan for new trends, curate, generate multi-platform posts, and dispatch/queue them.
"""

import time
import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent.resolve()
CONFIG_FILE = BASE_DIR / "config" / "accounts.json"

def get_interval_hours():
    try:
        if CONFIG_FILE.exists():
            cfg = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
            return float(cfg.get("schedule_interval_hours", 6))
    except Exception:
        pass
    return 6.0

def main():
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding='utf-8')
            sys.stderr.reconfigure(encoding='utf-8')
        except Exception:
            pass
            
    interval_h = get_interval_hours()
    print(f"⏰ [DAEMON 24/7] Uruchomiony w tle! Interwał cyklu: co {interval_h} godz.", flush=True)
    
    cycle_num = 1
    while True:
        interval_h = get_interval_hours()
        interval_sec = int(interval_h * 3600)
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n[{now}] 🔄 Cykl #{cycle_num}: Uruchamianie silnika engine.py...", flush=True)
        try:
            subprocess.run([sys.executable, str(BASE_DIR / "engine.py")], cwd=str(BASE_DIR), check=True)
            print(f"[{now}] ✅ Cykl #{cycle_num} zakończony. Następne automatyczne uruchomienie za {interval_h}h.", flush=True)
        except Exception as e:
            print(f"[{now}] ❌ Błąd w cyklu #{cycle_num}: {e}", flush=True)
            
        cycle_num += 1
        time.sleep(interval_sec)

if __name__ == "__main__":
    main()
