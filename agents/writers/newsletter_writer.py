"""
Newsletter & Substack Ghostwriter Agent (Polsia Multi-Tenant SaaS).
Generates a high-converting weekly newsletter tailored to the specific client project,
target audience, and chosen Multi-Armed Bandit persona.
"""

from agents.geo_seo_engine import load_product_profile, derive_seo_headline

def generate_newsletter_content(topic, persona, secondaries):
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
    trend_title = topic.get("title", "")
    trend_url = topic.get("url", purl)
    trend_desc = topic.get("description", topic.get("summary", ""))

    other_topics_md = ""
    for s in secondaries[:3]:
        other_topics_md += f"- **[{s.get('source', 'Rynek')}]** [{s.get('title', '')}]({s.get('url', '#')})\n"

    feat_list = "\n".join([f"1. **{f}**" for f in features])

    issue = f"""# 📩 Biuletyn Strategiczny {pname}: {short_topic}

*Wydanie specjalne dla: {paud} | Styl: {persona.get('active_style', 'analityk_danych')}*

---

## 📌 Główny Sygnał Rynkowy Tygodnia

Cześć! W dzisiejszym wydaniu przyglądamy się temu, jak najnowsze zmiany technologiczne (w tym głośny temat **[{trend_title}]({trend_url})**) wpływają na codzienną efektywność i wyniki finansowe nowoczesnych firm.

> **Kluczowy kontekst:** {trend_desc}

Dla zespołów i właścicieli z grupy **{paud}** wniosek jest jeden: ręczne wykonywanie powtarzalnych procesów staje się największym kosztem alternatywnym w firmie.

---

## 🛠️ Jak przekuć ten trend w przewagę z {pname}?

Budując **{pname}** ({purl}), skupiliśmy się na wyeliminowaniu głównej blokady wzrostu:
*{pproblem}*

W praktyce opiera się to na 3 filarach wdrożeniowych:
{feat_list}

---

## ⚡ Radar Tygodnia: 3 Dodatkowe Sygnały z Rynku

{other_topics_md}

---

## 🚀 Zrób kolejny krok

Chcesz wdrożyć to podejście w swoim biznesie bez budowania wszystkiego od zera?
👉 **[{cta_text} ({pname})]({cta_url})**
"""
    return {"newsletter": issue.strip()}
