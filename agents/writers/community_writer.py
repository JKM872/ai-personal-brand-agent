"""
Community & Own Group Builder Agent (Autonoma AI Workforce — Employee #5).
Generates weekly growth plans and engagement posts for the owner's proprietary community
(Facebook Group, Discord, Skool, or LinkedIn Group) to turn passive readers into warm leads.
"""

from agents.writers._common import resolve_profile, headline, brand_prompt
from agents.free_ai_router import has_live_ai_key, ask_free_ai

def generate_community_content(topic, persona, project=None, brand=None):
    profile = resolve_profile(project)
    pname = profile.get("product_name", "Autonoma AI")
    purl = profile.get("website_url", "https://twoja-domena.pl")
    paud = profile.get("target_audience", "właścicieli firm i twórców")
    pproblem = profile.get("primary_problem_solved", "")
    features = profile.get("key_features", ["Automatyzacja procesów 24/7"])

    meta = headline(profile, topic)
    short_topic = meta["short_topic"]
    polish_insight = meta["polish_insight"]
    metric = meta["metric_highlight"]

    if has_live_ai_key():
        ai_comm = ask_free_ai(
            "Jesteś managerem społeczności B2B (FB Group / Discord / Skool) w Autonoma AI. Piszesz w 100% po polsku w formacie Markdown." + brand_prompt(brand),
            f"Przygotuj strategię własnej grupy na ten tydzień dla produktu {pname} ({purl}), grupa docelowa: {paud}, problem: {pproblem}, temat: {short_topic}. Uwzględnij: 1) Post przypięty z zaproszeniem do grupy i pytaniem otwartym, 2) Ankietę dyskusyjną (1, 2 lub 3), 3) Szablony odpowiedzi do ręcznego użycia przez autora (bez automatycznych wiadomości prywatnych)."
        )
        if ai_comm and len(ai_comm) > 200:
            return {"community_playbook": ai_comm.strip()}

    community_plan = f"""# 👥 Strategia Własnej Grupy i Społeczności (FB Group / Discord / Skool) — {pname}

**Grupa docelowa społeczności:** {paud}
**Cel tygodnia:** Przekształcenie biernych członków grupy w aktywne leady testujące **{pname}** ({purl})

---

## 📌 1. Post Przypięty (Powitalny Lead Magnet na Górze Grupy)

**Nagłówek:** 👋 Witaj w społeczności praktyków! Odbierz bezpłatny pakiet startowy od {pname}

Cześć! Jeśli jesteś w grupie **{paud}**, prawdopodobnie szukasz sposobu, aby przestać tracić czas na powtarzalne operacje i skupić się na skalowaniu wyniku.

W tej grupie dzielimy się wyłącznie sprawdzonymi procesami, twardymi wyliczeniami i gotowymi szablonami.

🎁 **Na start przygotowaliśmy dla członków grupy:**
1. Pełne porównanie narzędzi i strategii: *{short_topic}*.
2. Dostęp do naszego systemu **{pname}**, który bezpośrednio rozwiązuje główny problem: *{pproblem}*

👉 **Przedstaw się w komentarzu i napisz, z jakim wyzwaniem przychodzisz** — materiały i checklistę znajdziesz tu: {purl}

---

## 🔥 2. Post Dyskusyjny / Ankieta Angażująca (Środek Tygodnia)

**Temat:** {short_topic} — jak wygląda to obecnie u Was?

Przeanalizowaliśmy ostatnio świeże dane z naszego sektora:
> {polish_insight}

W praktyce wdrożenie odpowiedniej automatyzacji daje jeden mierzalny efekt: **{metric}**.

📊 **Szybka ankieta dla członków grupy — zagłosuj w komentarzu (1, 2 lub 3):**
- **[1]** Nadal robimy ten proces ręcznie wewnątrz zespołu (szukamy automatyzacji)
- **[2]** Korzystamy z zewnętrznych podwykonawców / agencji (chcemy obniżyć koszty)
- **[3]** Mamy już wdrożony własny system automatyczny

Najciekawsze komentarze rozłożymy na czynniki pierwsze w piątkowym podsumowaniu!

---

## 💬 3. Szablony odpowiedzi do ręcznego użycia (piszesz i publikujesz sam)

* **Gdy nowa osoba się przedstawi:**
  > „Cześć! Świetnie, że jesteś z nami. Jakie jest teraz Twoje największe wyzwanie w tym obszarze? Materiały zebraliśmy tu: {purl}”

* **Gdy członek grupy wybierze [1] (praca ręczna):**
  > „Dzięki za szczerość! Większość firm z grupy {paud} zaczyna dokładnie w tym punkcie. Największy przełom daje zautomatyzowanie pierwszego kroku: *{features[0] if features else 'automatyzacja bazowa'}*. Sprawdź nasze ostatnie zestawienie na blogu!”
"""
    return {"community_playbook": community_plan.strip()}
