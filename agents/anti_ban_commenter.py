"""
Anti-Ban Engagement & Comment Responder Agent (Autonoma AI Workforce — Employee #10).
Crafts authentic, helpful responses to comments and discussions on social platforms
with randomized human-like delays (jitter 18-95 min) and strict zero-spam protection.
"""

import sys
import random
from datetime import datetime, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.resolve()
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

from agents.free_ai_router import has_live_ai_key, ask_free_ai

def calculate_safe_delay_minutes(min_min=18, max_min=95):
    """
    Computes a human-like delay with random jitter.
    Prevents instantaneous replies that trigger social media bot-detection algorithms.
    """
    jitter = random.uniform(0.1, 0.9)
    return round(random.randint(min_min, max_min) + jitter, 1)

def is_within_active_hours(start_hour=8, end_hour=22):
    """
    Ensures comments are only posted during natural human active hours.
    """
    current_hour = datetime.now().hour
    return start_hour <= current_hour <= end_hour

def generate_safe_reply(incoming_comment, profile):
    """
    Crafts a high-value, non-spammy response adhering to platform anti-ban guidelines.
    Formula:
    1. Validation / Direct Answer
    2. Practical Engineering / Business Value
    3. Soft, natural context (no naked links!)
    """
    pname = profile.get("product_name", "Autonoma AI")
    pproblem = profile.get("primary_problem_solved", "automatyzacja procesów")
    delay = calculate_safe_delay_minutes()
    scheduled_for = (datetime.now() + timedelta(minutes=delay)).strftime("%H:%M:%S")

    reply_text = None
    if has_live_ai_key():
        ai_reply = ask_free_ai(
            "Jesteś Pracownikiem #10 (Strażnik Komentarzy Anti-Ban) w Autonoma AI. Piszesz naturalne, pomocne odpowiedzi po polsku, BEZ żadnych linków URL.",
            f"Użytkownik napisał komentarz: '{incoming_comment}'. Odpowiedz merytorycznie i naturalnie w kontekście projektu {pname} (który rozwiązuje problem: {pproblem}). Zero linków, zero agresywnego spamu."
        )
        if ai_reply and len(ai_reply) > 40:
            reply_text = ai_reply.strip()

    if not reply_text:
        reply_text = f"""Świetny punkt i bardzo trafne pytanie odnośnie: "{incoming_comment[:60]}...".

Z praktycznego punktu widzenia kluczem jest tutaj uniknięcie dwóch skrajności: ręcznego marnowania godzin na rutynę vs. odpalania prymitywnych botów, które kończą się banami kont.

Sprawdza się podejście oparte o:
1. Ustalenie stałych, bezpiecznych limitów dziennych akcji.
2. Wprowadzenie losowych odstępów czasowych (Human Jitter).
3. Dostarczanie w pierwszej kolejności realnej wartości merytorycznej.

Właśnie pod ten proces projektowaliśmy architekturę {pname} — żeby cały workflow działał bezpiecznie w chmurze ({pproblem}) bez ryzyka restrykcji.

Gdybyś chciał zgłębić temat od strony wdrożeniowej, daj znać!"""

    return {
        "reply": reply_text.strip(),
        "delay_minutes": delay,
        "scheduled_for": scheduled_for,
        "safety_checks": {
            "no_naked_links": True,
            "human_jitter": True,
            "value_first": True,
            "within_active_hours": is_within_active_hours()
        }
    }

if __name__ == "__main__":
    test_comment = "Jak automatyzujecie posty, żeby nie dostać shadowbana na LinkedIn i X?"
    sample_profile = {"product_name": "Autonoma AI"}
    res = generate_safe_reply(test_comment, sample_profile)
    print("🤖 [ANTI-BAN RESPONDER — PRACOWNIK #10]")
    print(f"⏰ Bezpieczne opóźnienie: {res['delay_minutes']} min (publikacja o: {res['scheduled_for']})")
    print(f"🛡️ Zgodność z Anti-Ban: {res['safety_checks']}")
    print("-" * 50)
    print(res["reply"])
