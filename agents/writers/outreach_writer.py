"""
B2B Outreach & Partnership SDR Agent (Autonoma AI Workforce — Employee #9).
Generates hyper-personalized, non-spammy value-first outreach sequences (LinkedIn DM + Cold Email)
and objection-handling responses tailored to the client's target audience.
"""

from agents.geo_seo_engine import load_product_profile, derive_seo_headline

def generate_outreach_content(topic, persona):
    profile = load_product_profile()
    pname = profile.get("product_name", "Autonoma AI")
    purl = profile.get("website_url", "https://twoja-domena.pl")
    pcat = profile.get("category", "SaaS & Automatyzacja")
    paud = profile.get("target_audience", "właścicieli firm B2B")
    pproblem = profile.get("primary_problem_solved", "")
    features = profile.get("key_features", ["Pełna automatyzacja 24/7"])
    cta_text = profile.get("call_to_action", {}).get("text", "Wypróbuj za darmo")

    meta = derive_seo_headline(profile, topic)
    short_topic = meta["short_topic"]
    metric = meta["metric_highlight"]

    outreach_md = f"""# 🤝 Sekwencje Pozyskiwania Klientów B2B (SDR Outreach & DM) — {pname}

**Profil idealnego klienta (ICP):** {paud}
**Zasada bezpieczeństwa Anti-Spam:** Zero masowego spamu. Wysyłaj maksymalnie 15–20 spersonalizowanych wiadomości dziennie do osób, które skomentowały tematy branżowe lub odwiedziły profil.

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

## 📧 2. Krótki Email B2B do Decydentów (Value-First Cold Email)

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
