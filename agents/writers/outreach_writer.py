"""
B2B Outreach & Partnership SDR Agent (Autonoma AI Workforce — Employee #7).
Generates hyper-personalized, non-spammy value-first outreach sequences (LinkedIn DM + Cold Email)
and objection-handling responses tailored to the client's target audience.
"""

from agents.writers._common import resolve_profile, headline, brand_prompt
from agents.free_ai_router import has_live_ai_key, ask_free_ai

def generate_outreach_content(topic, persona, project=None, brand=None):
    profile = resolve_profile(project)
    pname = profile.get("product_name", "Autonoma AI")
    purl = profile.get("website_url", "https://twoja-domena.pl")
    paud = profile.get("target_audience", "właścicieli firm B2B")
    pproblem = profile.get("primary_problem_solved", "")
    features = profile.get("key_features", ["Pełna automatyzacja 24/7"])

    meta = headline(profile, topic)
    short_topic = meta["short_topic"]
    metric = meta["metric_highlight"]

    if has_live_ai_key():
        ai_out = ask_free_ai(
            "Jesteś specjalistą B2B SDR & Cold Outreach w Autonoma AI. Piszesz w 100% po polsku w formacie Markdown, bez spamu (Value-First)." + brand_prompt(brand),
            f"Przygotuj sekwencję pozyskiwania klientów B2B dla produktu {pname} ({purl}), grupa docelowa (ICP): {paud}, problem: {pproblem}, temat: {short_topic}, efekt: {metric}. Uwzględnij: 1) Sekwencję 2 wiadomości LinkedIn DM, 2) E-mail 1:1 do znanej osoby z możliwością rezygnacji, 3) Zbijanie 2 obiekcji sprzedażowych."
        )
        if ai_out and len(ai_out) > 200:
            return {"outreach_playbook": ai_out.strip()}

    outreach_md = f"""# 🤝 Sekwencje Pozyskiwania Klientów B2B (SDR Outreach & DM) — {pname}

**Profil idealnego klienta (ICP):** {paud}
**Szablony do ręcznego, spersonalizowanego kontaktu (1:1). Pisz tylko do osób, z którymi masz relację lub uzasadniony interes; zawsze dodaj zdanie o możliwości rezygnacji.**

---

## 💬 1. Sekwencja LinkedIn DM (Po przyjęciu zaproszenia do sieci)

**Wiadomość #1 (Dzień 1 — Czysta wartość, zero sprzedawania):**
> Cześć [Imię]! Dzięki za dołączenie do sieci. Widzę, że działasz w obszarze {paud}.
> Przygotowaliśmy właśnie świeże zestawienie i benchmarki dotyczące tematu: *{short_topic}* (pokazujemy m.in. jak uzyskać efekt: {metric.lower()}).
> Pomyślałem, że może Ci się przydać w codziennej pracy — wysłać Ci link do podsumowania?

**Wiadomość #2 (Po odpowiedzi „Tak, poproszę” — Miękkie przejście do produktu):**
> Jasne, proszę bardzo: {purl}
> Swoją drogą, dokładnie na bazie tych wniosków zbudowaliśmy **{pname}** — pomaga zespołom takim jak Twój wyeliminować główny problem: *{pproblem}*
> Jeśli będziesz chciał przetestować to u siebie w 5 minut, daj znać, chętnie pomogę w konfiguracji!

---

## 📧 2. Krótki e-mail 1:1 (tylko do osób, z którymi masz relację lub które wyraziły zgodę)

**Temat maila:** Szybkie pytanie o proces w [Nazwa Firmy] / {short_topic}

> Dzień dobry [Imię],
>
> obserwuję rozwój [Nazwa Firmy] i zwracam się z krótkim, konkretnym pytaniem.
>
> Większość firm z grupy **{paud}** traci obecnie kilkanaście godzin tygodniowo przez jeden wąski punkt:
> *{pproblem}*
>
> W **{pname}** ({purl}) zautomatyzowaliśmy ten proces od A do Z, co pozwala osiągnąć mierzalny rezultat:
> 👉 **{metric}**.
>
> Kluczowe przewagi naszego podejścia:
> - {features[0] if len(features) > 0 else 'Wdrożenie w 5 minut w chmurze'}
> - {features[1] if len(features) > 1 else 'Pełna kontrola właściciela nad procesem'}
>
> Czy ma sens, abym podesłał krótkie, 2-minutowe nagranie pokazujące, jak zadziała to w [Nazwa Firmy]?
>
> Jeśli to nie jest dla Ciebie temat, po prostu daj znać — nie będę więcej pisać.
>
> Pozdrawiam serdecznie,
> Zespół {pname} ({purl})

---

## 🛡️ 3. Ściągawka Zbijania Obiekcji Sprzedażowych (Dla Agenta i Właściciela)

* **Obiekcja klienta:** *„Nie mamy teraz czasu na wdrażanie kolejnego narzędzia.”*
  **Odpowiedź:** „Rozumiem — właśnie dlatego {pname} konfiguruje się w mniej niż 5 minut na podstawie samego linku do strony, a cała praca dzieje się w tle bez obciążania Waszego zespołu.”

* **Obiekcja klienta:** *„Boimy się utraty kontroli nad tym, co publikuje AI.”*
  **Odpowiedź:** „W {pname} działa wbudowana Bramka Uprawnień Właściciela (Owner Permission Gate). Żaden artykuł nie trafi na stronę bez Twojej autoryzacji jednym kliknięciem.”
"""
    return {"outreach_playbook": outreach_md.strip()}
