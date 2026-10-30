"""
24/7 Background Daemon for Personal Brand Engine.
Runs engine.py every N hours (config/accounts.json: schedule_interval_hours).
Generated bundles land in the approval queue; nothing is published without approve.py.
Stops cleanly on Ctrl+C / SIGTERM.
"""

import time
import sys
import json
import signal
import subprocess
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent.resolve()
CONFIG_FILE = BASE_DIR / "config" / "accounts.json"
_stop = False

def get_interval_hours():
    try:
        if CONFIG_FILE.exists():
            cfg = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
            return float(cfg.get("schedule_interval_hours", 6))
    except Exception:
        pass
    return 6.0

def _handle_stop(signum, frame):
    global _stop
    _stop = True

def main():
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding='utf-8')
            sys.stderr.reconfigure(encoding='utf-8')
        except Exception:
            pass
    try:
        signal.signal(signal.SIGTERM, _handle_stop)
    except (ValueError, AttributeError):
        pass

    print(f"⏰ [DAEMON 24/7] Uruchomiony. Interwał cyklu: co {get_interval_hours()} godz.", flush=True)
    cycle_num = 1
    try:
        while not _stop:
            interval_h = get_interval_hours()
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"\n[{now}] 🔄 Cykl #{cycle_num}: uruchamianie engine.py...", flush=True)
            try:
                subprocess.run([sys.executable, str(BASE_DIR / "engine.py")], cwd=str(BASE_DIR), check=True)
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"[{now}] ✅ Cykl #{cycle_num} zakończony. Następny za {interval_h}h.", flush=True)
            except Exception as e:
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"[{now}] ❌ Błąd w cyklu #{cycle_num}: {e}", flush=True)
            cycle_num += 1
            deadline = time.time() + int(interval_h * 3600)
            while not _stop and time.time() < deadline:
                time.sleep(min(5, max(0, deadline - time.time())))
    except KeyboardInterrupt:
        pass
    print("[DAEMON 24/7] Zatrzymano.", flush=True)

if __name__ == "__main__":
    main()
