"""
Newsletter & Blog Ghostwriter Agent.
Produces a technical deep-dive issue in Markdown format for Substack/Beehiiv/Medium.
"""

def generate_newsletter_content(topic, persona, secondaries):
    title = topic.get("title", "")
    url = topic.get("url", "")
    desc = topic.get("description", topic.get("summary", ""))
    
    other_topics_md = ""
    for idx, s in enumerate(secondaries[:3], 1):
        s_title = s.get("title", "")
        s_url = s.get("url", "")
        s_src = s.get("source", "")
        other_topics_md += f"* **[{s_src}] {s_title}** – [Czytaj więcej]({s_url})\n"
        
    issue = f"""# 🧠 Deep Dive: Przyszłość runtime dla autonomicznych agentów AI

*Wydanie cotygodniowego biuletynu inżynierii AI*

---

## 📌 Temat Tygodnia: {title}

Cześć! W tym wydaniu odrzucamy marketingowy szum i zaglądamy pod maskę tego, co aktualnie dzieje się w ekosystemie agentów AI.

Jeśli śledzisz rozwój LLM-ów, wiesz, że modele osiągnęły już wysoki poziom logicznego rozumowania. Jednak kiedy próbujemy wdrożyć je w środowisku 24/7, niemal natychmiast uderzamy w ścianę. Tą ścianą jest **bezpieczeństwo, izolacja i determinizm wykonania**.

Projekt **[{title}]({url})** pokazuje, jak inżynierowie radzą sobie z tym wyzwaniem.

### 🔍 Co dokładnie rozwiązuje ten projekt?
> "{desc}"

Z perspektywy inżyniera oprogramowania warto zwrócić uwagę na trzy elementy:
1. **Ścisłe zarządzanie uprawnieniami (Granular Access Control):** Koniec z podawaniem agentowi pełnego dostępu do powłoki systemowej.
2. **Obserwowalność (Observability):** Każde wywołanie narzędzia, czas odpowiedzi i stan pamięci są rejestrowane w ustrukturyzowanych logach.
3. **Prywatność i praca w środowisku lokalnym/hybrydowym:** Coraz więcej firm odchodzi od wysyłania wrażliwych danych do zewnętrznych chmur, stawiając na lokalne runtime'y.

---

## 🛠️ Praktyczna lekcja dla architektów systemów

Jeśli budujesz lub planujesz wdrożenie agentów w swojej organizacji, oto reguła, którą warto wdrożyć od dziś:

> **Nigdy nie pozwalaj agentowi na bezpośrednie wykonywanie poleceń w głównym systemie bez warstwy piaskownicy (sandbox) i jawnej białej listy akcji.**

Zbudowanie prostej piaskownicy w Dockerze lub skorzystanie z gotowego runtime'u zaoszczędzi Ci setek godzin debugowania nieoczekiwanych skutków ubocznych.

---

## ⚡ Szybki Radar: Inne warte uwagi projekty i badania

{other_topics_md}

---

*Podobało Ci się to wydanie? Podziel się nim z zespołem lub odpowiedz na ten e-mail ze swoimi przemyśleniami!*
"""

    return {"newsletter": issue.strip()}
