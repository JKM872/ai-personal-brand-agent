"""
LinkedIn Ghostwriter Agent (Project-Adaptive Polsia Engine).
Adapts tone to the active Multi-Armed Bandit Persona ('analityk_danych', 'case_study', 'kontrowersyjny_ekspert')
and connects trending industry insights directly to the owner's project DNA.
"""

from agents.geo_seo_engine import load_product_profile

def generate_linkedin_content(topic, persona):
    profile = load_product_profile()
    product_name = profile.get("product_name", "Nasz Projekt")
    problem_solved = profile.get("primary_problem_solved", "optymalizacja i automatyzacja procesów")
    target_aud = profile.get("target_audience", "przedsiębiorcy i liderzy")
    features = profile.get("key_features", ["Automatyzacja 24/7", "Skalowalność", "Bezpieczeństwo"])
    
    title = topic.get("title", "")
    url = topic.get("url", "")
    desc = topic.get("description", topic.get("summary", ""))
    source = topic.get("source", "Raport branżowy")
    active_style = persona.get("active_style", "analityk_danych")

    if active_style == "case_study":
        hook = f"Jak przełożyć trend wokół '{title}' na mierzalny wzrost w biznesie? Rozbijmy to na konkretny przypadek wdrożeniowy."
        angle = f"Zespoły, które wdrażają nowoczesne podejście (jak w analizowanym projekcie z {source}), redukują czas operacyjny o ponad 60%."
    elif active_style == "kontrowersyjny_ekspert":
        hook = f"Niepopularna opinia: 90% firm marnuje budżet na narzędzia, których nikt nie używa, podczas gdy projekty takie jak '{title}' zmieniają reguły gry."
        angle = f"Zamiast dokładać kolejne ręczne procesy, spójrz na to, co dzieje się w {source}: liczy się autonomiczne działanie i twardy zwrot z inwestycji."
    else:
        hook = f"Twarde dane nie kłamią: analiza projektu '{title}' ({source}) pokazuje dokładnie, w którą stronę zmierza rynek."
        angle = f"Z perspektywy architektury i efektywności procesowej kluczowe są tu 3 mierzalne czynniki:"

    post = f"""{hook}

Przeanalizowałem dzisiaj szczegóły dotyczące:
👉 {title} ({source})

{angle}
1. Kontekst rynkowy: {desc}
2. Eliminacja wąskich gardeł: Zamiast ręcznego powtarzania operacji, proces zostaje zautomatyzowany u źródła.
3. Bezpośrednie przełożenie na {target_aud}: {problem_solved}

💡 Wniosek dla twórców i właścicieli produktów:
Dokładnie na tych fundamentach rozwijamy {product_name}. Naszym celem jest:
• {features[0] if len(features) > 0 else 'Pełna automatyzacja'}
• {features[1] if len(features) > 1 else 'Skalowalna architektura'}

Pytanie do Waszej sieci:
Jak obecnie mierzycie zwrot z czasu poświęconego na procesy wokół tego obszaru? Stawiacie na własne automatyzacje czy gotowe platformy?

*(Link do źródła oraz pełnej analizy porównawczej zostawiam w pierwszym komentarzu poniżej 👇)*

#Biznes #SaaS #Automatyzacja #Technologia #Growth #Innowacje"""

    carousel = f"""### 📑 KONSPEKT KARUZELI PDF (5 SLAJDÓW – STYL: {active_style.upper()})

* **Slajd 1 (Okładka – Hook):**
  - Nagłówek: "{title[:55]}"
  - Podtytuł: "Co ten trend oznacza dla {target_aud}? Analiza {product_name}"

* **Slajd 2 (Diagnoza Problemu):**
  - Nagłówek: "Dlaczego tradycyjne podejście przestaje działać?"
  - Kontekst: "{desc[:140]}..."

* **Slajd 3 (Mechanizm & Wnioski z {source}):**
  - Punkt 1: Automatyzacja zamiast ręcznej pracy
  - Punkt 2: Decyzje oparte o dane (Multi-Armed Bandit)
  - Punkt 3: Bezpieczna dystrybucja bez blokad

* **Slajd 4 (Jak rozwiązuje to {product_name}):**
  - Problem: {problem_solved[:120]}
  - Kluczowa przewaga: {features[0] if features else 'Autonomiczna praca 24/7'}

* **Slajd 5 (Podsumowanie & Call To Action):**
  - Wniosek: "Zbuduj proces, który pracuje i konwertuje, gdy Ty skupiasz się na produkcie."
  - CTA: "Sprawdź link w pierwszym komentarzu i przetestuj {product_name}."
"""

    return {"post": post.strip(), "carousel": carousel.strip()}
