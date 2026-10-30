"""
Micro-Budget Ads & Retargeting Agent (Autonoma AI Workforce — Employee #6).
Generates high-ROI ad campaigns for minimum-budget performance marketing (0-20 PLN / day)
across Meta Ads (Facebook/Instagram), LinkedIn Boost, and Google High-Intent Search.
"""

from agents.writers._common import resolve_profile, headline, brand_prompt
from agents.free_ai_router import has_live_ai_key, ask_free_ai

def generate_ads_content(topic, persona, project=None, brand=None):
    profile = resolve_profile(project)
    pname = profile.get("product_name", "Autonoma AI")
    purl = profile.get("website_url", "https://twoja-domena.pl")
    pcat = profile.get("category", "SaaS & Automatyzacja")
    paud = profile.get("target_audience", "właścicieli firm B2B")
    pproblem = profile.get("primary_problem_solved", "")
    features = profile.get("key_features", ["Pełna automatyzacja 24/7"])
    cta_text = profile.get("call_to_action", {}).get("text", "Wypróbuj za darmo")

    meta = headline(profile, topic)
    metric = meta["metric_highlight"]

    if has_live_ai_key():
        ai_ads = ask_free_ai(
            "Jesteś inżynierem kampanii Performance Marketing (Micro-Budget 0-20 zł/dzień) w Autonoma AI. Piszesz w 100% po polsku w formacie Markdown." + brand_prompt(brand),
            f"Przygotuj kampanię reklamową niskiego budżetu (0-20 zł/dzień) dla projektu {pname} ({purl}), kategoria: {pcat}, grupa docelowa: {paud}, problem: {pproblem}, kluczowy wynik: {metric}. Uwzględnij: 1) Meta Ads Retargeting (10 zł/dzień), 2) Google Search Ads Exact-Match (10 zł/dzień), 3) Alternatywę 0,00 zł (GEO + Newsletter)."
        )
        if ai_ads and len(ai_ads) > 200:
            return {"ads_campaign": ai_ads.strip()}

    ads_markdown = f"""# 🎯 Kampania Reklamowa Minimalnego Budżetu (Micro-Budget Ads: 0 – 20 zł / dzień) — {pname}

**Grupa docelowa (Targeting):** {paud}
**Cel kampanii:** Maksymalny zwrot z inwestycji (ROAS) przy minimalnym budżecie (Retargeting osób odwiedzających artykuły SEO/GEO + Wyszukiwarka Google na frazy wysokiego zamiaru zakupu).

---

## 1. Meta Ads (Facebook & Instagram Retargeting — Budżet: 10 zł / dzień)

> **Zasada oszczędzania budżetu:** Nie przepalaj budżetu na zimny ruch. Kieruj tę reklamę wyłącznie do osób, które przeczytały Twój artykuł porównawczy na stronie `{purl}` w ciągu ostatnich 30 dni.

* **Tekst główny reklamy (Primary Text):**
  Nadal tracisz czas na procesy, które w 2026 roku powinny działać w 100% automatycznie?
  Firmy z grupy **{paud}** przechodzą na **{pname}**, bo liczy się konkretny wynik:
  ✅ {metric}
  ✅ {features[0] if len(features) > 0 else 'Działa 24/7 w chmurze'}
  ✅ {features[1] if len(features) > 1 else 'Pełna kontrola właściciela'}
  Sprawdź, jak **{pname}** eliminuje główny ból operacyjny: *{pproblem}*

* **Nagłówek (Headline):** {pname} — {cta_text}
* **Opis linku (Description):** Wdrożenie w 5 minut • Bezpieczna architektura
* **Przycisk CTA:** `Więcej informacji` / `Zarejestruj się`
* **Docelowy URL z UTM:** `{purl}?utm_source=meta_ads&utm_medium=retargeting_micro&utm_campaign=roi_boost`

---

## 2. Google Search Ads (Tylko Frazy Exact-Match — Budżet: 10 zł / dzień)

* **Słowa kluczowe (Exact Match — najwyższa intencja zakupowa):**
  - `[najlepsze narzędzie do {pcat.lower()}]`
  - `[{pname.lower()} opinie]`
  - `[automatyzacja dla {paud.lower()[:35]}]`
* **Nagłówek 1 ( do 30 znaków ):** {pname[:28]} — Oficjalna
* **Nagłówek 2 ( do 30 znaków ):** Automatyzacja 24/7 dla Firm
* **Nagłówek 3 ( do 30 znaków ):** {cta_text[:28]}
* **Tekst reklamy 1 ( do 90 znaków ):** {pproblem[:88]}
* **Tekst reklamy 2 ( do 90 znaków ):** {metric[:88]}

---

## 3. Darmowa Alternatywa 0,00 zł (Organic Boost + AI Search Ads)

Jeśli chcesz utrzymać budżet reklamowy na poziomie **dokładnie 0,00 zł**:
1. **Pozycjonowanie w ChatGPT i Perplexity (GEO):** Twój plik `/llms.txt` oraz artykuł porównawczy z tabelą sprawiają, że asystenci AI rekomendują **{pname}** za darmo, gdy użytkownik pyta o rozwiązania w kategorii *{pcat}*.
2. **Retargeting przez Newsletter:** Zamiast płacić za kliknięcia w Meta Ads, zbieraj maile pod artykułem blogowym i pozwól Agentowi Newsletterowemu domykać sprzedaż za 0 zł (Brevo Free Tier).
"""
    return {"ads_campaign": ads_markdown.strip()}
