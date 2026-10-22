"""
24/7 Background Daemon for Personal Brand Engine.
Runs continuously in the background, waking up at configured intervals (e.g. every 12 hours)
to scour for new trends, curate, and update the review queue.
"""

import time
import sys
import subprocess
from datetime import datetime

INTERVAL_HOURS = 12
INTERVAL_SECONDS = INTERVAL_HOURS * 3600

def main():
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except Exception:
            pass
            
    print(f"⏰ Demon 24/7 uruchomiony. Interwał skanowania: co {INTERVAL_HOURS} godzin.")
    print("Naciśnij Ctrl+C, aby zatrzymać.\n")
    
    while True:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{now}] 🚀 Rozpoczynanie cyklu skanowania i generowania treści...")
        try:
            subprocess.run([sys.executable, "engine.py"], check=True)
            print(f"[{now}] ✅ Cykl zakończony sukcesem. Kolejne uruchomienie za {INTERVAL_HOURS}h.")
        except Exception as e:
            print(f"[{now}] ❌ Błąd podczas wykonywania cyklu: {e}")
            
        print(f"💤 Usypianie na {INTERVAL_HOURS} godzin...")
        time.sleep(INTERVAL_SECONDS)

if __name__ == "__main__":
    main()
