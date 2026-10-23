"""
LinkedIn Ghostwriter Agent (Polsia Multi-Tenant SaaS).
Generates 100% Polish, executive-grade LinkedIn posts and 5-slide PDF carousel outlines
tailored to the client's project DNA and the active Multi-Armed Bandit persona.
"""

from agents.geo_seo_engine import load_product_profile, derive_seo_headline

def generate_linkedin_content(topic, persona):
    profile = load_product_profile()
    product_name = profile.get("product_name", "Nasz Projekt")
    problem_solved = profile.get("primary_problem_solved", "optymalizacja i automatyzacja procesów")
    target_aud = profile.get("target_audience", "przedsiębiorcy i liderzy")
    features = profile.get("key_features", ["Automatyzacja 24/7", "Skalowalność", "Bezpieczeństwo"])
    active_style = persona.get("active_style", "analityk_danych")

    meta = derive_seo_headline(profile, topic)
    short_topic = meta["short_topic"]
    polish_insight = meta["polish_insight"]
    metric = meta["metric_highlight"]

    if active_style == "case_study":
        hook = f"Jak w praktyce rozwiązać jeden z najdroższych problemów dla grupy {target_aud}? Rozbijmy to na konkretny przypadek wdrożeniowy."
        angle = "Zespoły, które zastępują ręczną rutynę zautomatyzowanym procesem, odzyskują średnio kilkanaście godzin tygodniowo już w pierwszym miesiącu:"
    elif active_style == "kontrowersyjny_ekspert":
        hook = f"Niepopularna opinia: większość firm z sektora {profile.get('category', 'B2B')} przepala budżet na pracę ręczną, którą nowoczesna architektura wykonuje w tle w kilka sekund."
        angle = "Zamiast dokładać kolejne etaty i powtarzalne zadania, spójrzmy na twarde liczby z rynku:"
    else:
        hook = f"Twarde dane nie kłamią: analiza obszaru „{short_topic}” pokazuje dokładnie, gdzie nowoczesne firmy budują dziś przewagę operacyjną."
        angle = "Z perspektywy architektury procesowej i zwrotu z inwestycji (ROI) kluczowe są tu 3 mierzalne czynniki:"

    feat_lines = "\n".join([f"• {f}" for f in features[:3]])

    post = f"""{hook}

Temat na dziś:
👉 {short_topic}

{angle}
1. Diagnoza rynkowa: {polish_insight}
2. Kluczowy efekt: {metric}.
3. Bezpośrednie przełożenie na {target_aud}: {problem_solved}

💡 Jak podchodzimy do tego w {product_name}?
Zbudowaliśmy nasz system wokół trzech filarów:
{feat_lines}

Pytanie do właścicieli firm i liderów zespołów:
Który proces operacyjny pożera dziś w Waszej organizacji najwięcej czasu i powinien zostać zautomatyzowany w pierwszej kolejności?

*(Link do pełnego artykułu porównawczego oraz strony {product_name} zostawiam w pierwszym komentarzu poniżej 👇)*

#Biznes #SaaS #Automatyzacja #Efektywnosc #Wzrost #B2B"""

    carousel = f"""### 📑 KONSPEKT KARUZELI PDF (5 SLAJDÓW – STYL: {active_style.upper()})

* **Slajd 1 (Okładka – Hook):**
  - Nagłówek: "{short_topic}"
  - Podtytuł: "Przewodnik i twarde dane dla: {target_aud} | {product_name}"

* **Slajd 2 (Diagnoza Problemu):**
  - Nagłówek: "Dlaczego tradycyjne podejście przestaje działać?"
  - Dane z rynku: "{polish_insight}"

* **Slajd 3 (Wymierny Efekt Automatyzacji):**
  - Punkt 1: {metric}
  - Punkt 2: Eliminacja ręcznej, powtarzalnej pracy zespołu
  - Punkt 3: Pełna kontrola właściciela i przewidywalne ROI

* **Slajd 4 (Jak rozwiązuje to {product_name}):**
  - Cel: {problem_solved}
  - Kluczowa przewaga: {features[0] if features else 'Autonomiczna praca 24/7'}

* **Slajd 5 (Podsumowanie & Call To Action):**
  - Wniosek: "Zbuduj proces, który pracuje i zarabia, gdy Ty skupiasz się na strategii."
  - CTA: "Sprawdź link w pierwszym komentarzu i przetestuj {product_name}."
"""

    return {"post": post.strip(), "carousel": carousel.strip()}
