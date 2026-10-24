"""
Community & Own Group Builder Agent (Autonoma AI Workforce — Employee #7).
Generates weekly growth plans and engagement posts for the owner's proprietary community
(Facebook Group, Discord, Skool, or LinkedIn Group) to turn passive readers into warm leads.
"""

from agents.geo_seo_engine import load_product_profile, derive_seo_headline

def generate_community_content(topic, persona):
    profile = load_product_profile()
    pname = profile.get("product_name", "Autonoma AI")
    purl = profile.get("website_url", "https://twoja-domena.pl")
    paud = profile.get("target_audience", "właścicieli firm i twórców")
    pproblem = profile.get("primary_problem_solved", "")
    features = profile.get("key_features", ["Automatyzacja procesów 24/7"])
    cta_text = profile.get("call_to_action", {}).get("text", "Dołącz i przetestuj za darmo")

    meta = derive_seo_headline(profile, topic)
    short_topic = meta["short_topic"]
    polish_insight = meta["polish_insight"]
    metric = meta["metric_highlight"]

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

👉 **Napisz w komentarzu pod tym postem słowo „START”**, a nasz zespół (lub automatyczny asystent) wyśle Ci bezpośredni dostęp oraz checklistę wdrożeniową!

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

## 💬 3. Gotowe Szablony Odpowiedzi Agenta na Komentarze Członków (Human-Delay 18-45 min)

* **Gdy członek grupy napisze „START”:**
  > „Cześć! Świetnie, że jesteś z nami. Wysłałem Ci szczegóły w wiadomości prywatnej, a tutaj zostawiam bezpośredni link do uruchomienia {pname}: {purl} — daj znać, jak pierwsze wrażenia!”

* **Gdy członek grupy wybierze [1] (praca ręczna):**
  > „Dzięki za szczerość! Większość firm z grupy {paud} zaczyna dokładnie w tym punkcie. Największy przełom daje zautomatyzowanie pierwszego kroku: *{features[0] if features else 'automatyzacja bazowa'}*. Sprawdź nasze ostatnie zestawienie na blogu!”
"""
    return {"community_playbook": community_plan.strip()}
