"""
Agent 6: Data Analyst & Growth Optimizer (Dział Statystyczny).
Implements the Multi-Armed Bandit algorithm (80% exploitation / 20% exploration)
over content personas. Uses only real recorded clicks/conversions — never invented numbers.
"""

import sys
import random
import sqlite3
import argparse
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.resolve()
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from db.supabase_client import db

def pick_best_persona():
    """
    Selects a content persona using weighted Multi-Armed Bandit sampling:
    80% probability goes to historically proven top-converting styles,
    20% probability is reserved for exploring other styles.
    """
    personas = db.get_personas()
    if not personas:
        return {
            "persona_name": "analityk_danych",
            "system_prompt": "Jesteś inżynierem i analitykiem. Operujesz liczbami, architekturą i wyliczeniami. Zero lania wody.",
            "effectiveness_score": 1.0
        }

    # 20% Exploration (random choice)
    if random.random() < 0.20:
        return random.choice(personas)

    # 80% Exploitation (weighted by effectiveness_score)
    weights = [max(float(p.get("effectiveness_score") or 1.0), 0.1) for p in personas]
    chosen = random.choices(personas, weights=weights, k=1)[0]
    return chosen

def run_nightly_optimization():
    """
    Recalculates effectiveness_score = (clicks + conversions * 5) / max(posts, 1).
    No real data (0 clicks and 0 conversions) -> score 1.0 and the report says so.
    """
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except Exception:
            pass

    personas = db.get_personas()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report_lines = [
        f"# 📊 Nocny Raport Działu Statystycznego ({now_str})",
        "",
        "| Styl (Persona) | Opublikowane Posty | Kliknięcia (CTR) | Konwersje / Leady | Wynik Efektywności | Status Alokacji |",
        "|---|---|---|---|---|---|"
    ]

    sorted_personas = []
    any_data = False
    for p in personas:
        pname = p["persona_name"]
        posts = max(int(p.get("posts_count") or 0), 1)
        clicks = int(p.get("total_clicks") or 0)
        conversions = int(p.get("conversions") or 0)
        if clicks or conversions:
            any_data = True
            score = round((clicks + (conversions * 5)) / posts, 2)
        else:
            score = 1.0
        db.update_persona_score(pname, score, clicks, conversions)
        sorted_personas.append((pname, posts, clicks, conversions, score))

    if not sorted_personas:
        sorted_personas.append(("analityk_danych", 1, 0, 0, 1.0))
    sorted_personas.sort(key=lambda x: x[4], reverse=True)
    best_persona = sorted_personas[0]

    for pname, posts, clicks, convs, score in sorted_personas:
        status = "🟢 Priorytet (Większość ruchu)" if pname == best_persona[0] else "🟡 Testowanie (20% eksploracji)"
        report_lines.append(f"| **{pname}** | {posts} | {clicks} | {convs} | **{score} pkt** | {status} |")

    report_lines.extend(["", "---", "### 💡 Werdykt Analityka AI:"])
    if any_data:
        report_lines.append(f"Najwyższy wynik ma styl **'{best_persona[0]}'** ({best_persona[4]} pkt).")
    else:
        report_lines.append("Brak realnych danych o kliknięciach — wszystkie style mają równy wynik 1.0, wybór jest losowy.")
    report_lines.append("")

    report_text = "\n".join(report_lines)
    report_file = BASE_DIR / "public" / "raport_statystyczny.md"
    report_file.parent.mkdir(parents=True, exist_ok=True)
    report_file.write_text(report_text, encoding="utf-8")

    print("=" * 60)
    print("📈 [DZIAŁ STATYSTYCZNY] Optymalizacja zakończona.")
    print(f"🏆 Lider: {best_persona[0]} ({best_persona[4]} pkt){'' if any_data else ' — brak realnych danych o kliknięciach'}")
    print(f"📄 Raport zapisano w: {report_file}")
    print("=" * 60)
    return report_text

def reset_stats():
    from db import supabase_client
    with sqlite3.connect(supabase_client.LOCAL_DB_PATH) as conn:
        conn.execute("UPDATE agent_strategy SET posts_count = 0, total_clicks = 0, conversions = 0, effectiveness_score = 1.0")
        conn.commit()
    print("Statystyki bandyty wyzerowane (posts/clicks/conversions = 0, score = 1.0).")

def main(argv=None):
    ap = argparse.ArgumentParser(description="Dział statystyczny (Multi-Armed Bandit)")
    ap.add_argument("--reset-stats", action="store_true", help="wyzeruj statystyki person w lokalnej bazie")
    ap.add_argument("--yes", action="store_true", help="potwierdzenie dla --reset-stats")
    args = ap.parse_args(argv)
    if args.reset_stats:
        if not args.yes:
            print("Dodaj --yes, aby potwierdzić zerowanie statystyk.", file=sys.stderr)
            return 2
        reset_stats()
        return 0
    run_nightly_optimization()
    return 0

if __name__ == "__main__":
    sys.exit(main())
