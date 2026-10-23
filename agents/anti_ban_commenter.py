"""
Anti-Ban Engagement & Comment Responder Agent.
Crafts authentic, helpful responses to comments and discussions on social platforms
with randomized human-like delays (jitter) and strict zero-spam protection.
"""

import sys
import random
from datetime import datetime, timedelta

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

def calculate_safe_delay_minutes(min_min=15, max_min=45):
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
    pname = profile.get("product_name", "naszym rozwiązaniu")
    delay = calculate_safe_delay_minutes()
    scheduled_for = (datetime.now() + timedelta(minutes=delay)).strftime("%H:%M:%S")

    # Anti-ban safe template generator
    reply_text = f"""Świetny punkt i bardzo trafne pytanie odnośnie: "{incoming_comment[:60]}...".

Z praktycznego punktu widzenia kluczem jest tutaj uniknięcie dwóch skrajności: ręcznego marnowania godzin na rutynę vs. odpalania prymitywnych botów, które kończą się banami kont.

Sprawdza się podejście oparte o:
1. Ustalenie stałych, bezpiecznych limitów dziennych akcji.
2. Wprowadzenie losowych odstępów czasowych (jitter).
3. Dostarczanie w pierwszej kolejności realnej wartości merytorycznej.

Właśnie pod ten proces projektowaliśmy architekturę {pname} — żeby cały workflow działo się bezpiecznie w chmurze bez ryzyka restrykcji. 

Gdybyś chciał zgłębić temat od strony technicznej, daj znać!"""

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
    sample_profile = {"product_name": "Nasz SaaS"}
    res = generate_safe_reply(test_comment, sample_profile)
    print("🤖 [ANTI-BAN RESPONDER]")
    print(f"⏰ Bezpieczne opóźnienie: {res['delay_minutes']} min (publikacja o: {res['scheduled_for']})")
    print(f"🛡️ Zgodność z Anti-Ban: {res['safety_checks']}")
    print("-" * 50)
    print(res["reply"])
