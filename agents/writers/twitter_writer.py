"""
X / Twitter Ghostwriter Agent (Autonoma AI Multi-Tenant SaaS — Employee #4).
Generates a 100% Polish 5-part thread without outbound links in Tweet #1 (preventing algorithmic reach penalties),
placing the tracked UTM link in the delayed follow-up comment.
"""

from agents.geo_seo_engine import load_product_profile, derive_seo_headline
from agents.free_ai_router import has_live_ai_key, ask_free_ai

def generate_twitter_content(topic, persona):
    profile = load_product_profile()
    product_name = profile.get("product_name", "Autonoma AI")
    problem_solved = profile.get("primary_problem_solved", "automatyzacja wzrostu")
    target_aud = profile.get("target_audience", "właściciele firm B2B")
    features = profile.get("key_features", ["Pełna automatyzacja 24/7"])
    active_style = persona.get("active_style", "analityk_danych")

    meta = derive_seo_headline(profile, topic)
    short_topic = meta["short_topic"]
    polish_insight = meta["polish_insight"]
    metric = meta["metric_highlight"]

    thread = None
    if has_live_ai_key():
        ai_thread = ask_free_ai(
            f"Jesteś strategiem X / Twitter B2B w stylu: {active_style}. Tworzysz 5-częściowe wątki (1/5 do 5/5) w 100% po polsku, bez linków w pierwszym tweecie (Anti-Ban).",
            f"Napisz 5-tweetowy wątek dla projektu {product_name} ({profile.get('website_url')}). Grupa docelowa: {target_aud}. Rozwiązywany problem: {problem_solved}. Temat: {short_topic}. Dane rynkowe: {polish_insight}. Efekt: {metric}. Oddziel tweety linią '---'."
        )
        if ai_thread and len(ai_thread) > 150:
            thread = ai_thread.strip()

    if not thread:
        thread = f"""🧵 1/5 [Styl: {active_style}]
Większość firm z grupy {target_aud} traci kilkanaście godzin tygodniowo na procesy, które dziś powinny działać w 100% automatycznie.

Temat: {short_topic}.

Oto konkretna analiza i twarde dane w 4 punktach (bez lania wody): 👇

---

2/5 🔍 Co mówią liczby z rynku?
{polish_insight}

---

3/5 📊 Wymierny rezultat po wdrożeniu automatyzacji:
👉 {metric}.

Zespoły, które nadal wykonują te operacje ręcznie, płacą za to najwyższy koszt alternatywny na rynku.

---

4/5 🛠️ Jak rozwiązaliśmy to w {product_name}?
Zbudowaliśmy nasz system wokół jednej zasady:
👉 {problem_solved}

Kluczowy filar: {features[0] if features else 'Automatyzacja 24/7 pod kontrolą właściciela'}.

---

5/5 💬 Pytanie do Was:
Który proces w Waszej firmie pożera dziś najwięcej czasu i powinien zostać zautomatyzowany jako pierwszy?

*(Link do pełnego artykułu porównawczego oraz strony {product_name} wrzucam w pierwszym komentarzu poniżej 👇)*"""

    standalone_hooks = [
        f"Patrząc na aktualne dane wokół obszaru „{short_topic}”, widać jedną rzecz: wygrywają firmy, które budują systemy pracujące 24/7 zamiast polegać na ręcznej rutynie.",
        f"Szybki wniosek dla {target_aud}: {metric}. Właśnie po to rozwijamy {product_name}."
    ]

    return {
        "thread": thread.strip(),
        "standalone_hooks": standalone_hooks
    }
