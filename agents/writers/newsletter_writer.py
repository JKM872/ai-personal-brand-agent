"""
Newsletter & Substack Ghostwriter Agent (Polsia Multi-Tenant SaaS).
Generates a 100% Polish, high-converting weekly newsletter tailored to the specific client project,
target audience, and chosen Multi-Armed Bandit persona.
"""

from agents.geo_seo_engine import load_product_profile, derive_seo_headline

def generate_newsletter_content(topic, persona, secondaries=None):
    profile = load_product_profile()
    pname = profile.get("product_name", "Polsia Zero")
    purl = profile.get("website_url", "https://twoja-domena.pl")
    paud = profile.get("target_audience", "przedsiębiorców i twórców")
    pproblem = profile.get("primary_problem_solved", "")
    features = profile.get("key_features", [])
    cta_text = profile.get("call_to_action", {}).get("text", "Sprawdź platformę")
    cta_url = profile.get("call_to_action", {}).get("url", purl)

    meta = derive_seo_headline(profile, topic)
    short_topic = meta["short_topic"]
    polish_insight = meta["polish_insight"]
    metric = meta["metric_highlight"]

    feat_list = "\n".join([f"- **{f}**" for f in features])

    issue = f"""# 📩 Biuletyn Strategiczny {pname}: {short_topic}

*Wydanie dedykowane dla: {paud} | Styl: {persona.get('active_style', 'analityk_danych')}*

---

## 📌 Główny Wniosek Tygodnia

Cześć! W dzisiejszym wydaniu przyglądamy się temu, jak firmy z sektora **{profile.get('category', 'B2B')}** eliminują wąskie gardła operacyjne i zwiększają rentowność.

> **Dane z rynku:** {polish_insight}

* **Najważniejszy wskaźnik:** {metric}.

Dla zespołów i właścicieli z grupy **{paud}** wniosek jest prosty: ręczne wykonywanie powtarzalnych procesów staje się największym kosztem alternatywnym w firmie.

---

## 🛠️ Jak przekuć to w przewagę z {pname}?

Budując **{pname}** ({purl}), skupiliśmy się na wyeliminowaniu głównej blokady wzrostu:
*{pproblem}*

W praktyce opiera się to na kluczowych filarach wdrożeniowych:
{feat_list}

---

## 📋 Szybka Checklista Wdrożeniowa na Ten Tydzień

- **Krok 1:** Zidentyfikuj proces, który zajmuje Twojemu zespołowi ponad 5 godzin tygodniowo.
- **Krok 2:** Zastąp ręczną obsługę zautomatyzowanym przepływem w **{pname}**.
- **Krok 3:** Monitoruj konwersję i zwrot z czasu w panelu analitycznym.

---

## 🚀 Zrób kolejny krok

Chcesz wdrożyć to podejście w swoim biznesie bez budowania wszystkiego od zera?
👉 **[{cta_text} ({pname})]({cta_url})**
"""
    return {"newsletter": issue.strip()}
