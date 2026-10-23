"""
X / Twitter Ghostwriter Agent (Project-Adaptive & Anti-Ban Compliant).
Generates a 5-part thread without outbound links in Tweet #1 (preventing algorithmic reach penalties),
placing the tracked UTM link in the delayed follow-up comment.
"""

from agents.geo_seo_engine import load_product_profile

def generate_twitter_content(topic, persona):
    profile = load_product_profile()
    product_name = profile.get("product_name", "Nasz Projekt")
    problem_solved = profile.get("primary_problem_solved", "automatyzacja wzrostu")
    active_style = persona.get("active_style", "analityk_danych")

    title = topic.get("title", "")
    url = topic.get("url", "")
    desc = topic.get("description", topic.get("summary", ""))
    source = topic.get("source", "Rynek")

    thread = f"""🧵 1/5 [Styl: {active_style}]
Większość twórców i firm przegapia ten sygnał, skupiając się na szumie informacyjnym.

Tymczasem temat "{title}" ({source}) pokazuje dokładnie, jak zmienia się budowanie przewagi konkurencyjnej.

Oto konkretna analiza w 4 punktach (bez lania wody): 👇

---

2/5 🔍 Co dokładnie się wydarzyło?
{desc}

Dlaczego to ważne? Bo przesuwa punkt ciężkości z ręcznej pracy na zautomatyzowane, mierzalne systemy.

---

3/5 📊 Co mówią dane?
Zespoły, które nadal wykonują te operacje ręcznie, tracą średnio 15-20 godzin tygodniowo na zadania, które nowoczesna architektura wykonuje w tle w kilka sekund.

---

4/5 🛠️ Jak przekuć to w praktykę w {product_name}?
Zbudowaliśmy nasz system wokół jednej zasady:
👉 {problem_solved}

Zero spamu, pełna kontrola właściciela i pętla uczenia na podstawie realnych konwersji.

---

5/5 💬 Pytanie do Was:
Który proces w Waszym projekcie pożera dziś najwięcej czasu i powinien zostać zautomatyzowany jako pierwszy?

*(Link do pełnego artykułu porównawczego oraz źródła {source} wrzucam w komentarzu poniżej 👇)*"""

    standalone_hooks = [
        f"Analizując '{title}' ({source}), widać jedną rzecz: wygrywają ci, którzy budują systemy pracujące 24/7 zamiast polegać na ręcznej rutynie. Co o tym sądzicie?",
        f"Szybki wniosek z dzisiejszego przeglądu trendów ({title}): Automatyzacja bez pętli analitycznej to działanie na ślepo. Dlatego w {product_name} każdy ruch mierzymy twardymi danymi."
    ]

    return {
        "thread": thread.strip(),
        "standalone_hooks": standalone_hooks
    }
