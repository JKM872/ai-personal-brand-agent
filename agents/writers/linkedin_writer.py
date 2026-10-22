"""
LinkedIn Ghostwriter Agent.
Produces high-engagement technical posts and 5-slide carousel outlines.
Follows the: Hook -> Tension -> Solution/Architecture -> Actionable Takeaway -> Discussion CTA.
"""

def generate_linkedin_content(topic, persona):
    title = topic.get("title", "")
    url = topic.get("url", "")
    desc = topic.get("description", topic.get("summary", ""))
    source = topic.get("source", "")
    
    post = f"""Większość ludzi myśli, że wdrożenie autonomicznych agentów AI to kwestia promptów. W rzeczywistości największym problemem jest środowisko wykonawcze i bezpieczeństwo.

Właśnie natrafiłem na ciekawy projekt zyskujący ogromną trakcję:
👉 {title} ({source})

Czym się wyróżnia z perspektywy inżynierskiej?
1. Zamiast 'magicznych' wrapperów na API, skupia się na izolacji i deterministycznym działaniu.
2. {desc}
3. Rozwiązuje realne wąskie gardło: jak dać agentowi dostęp do narzędzi bez ryzyka, że uszkodzi system hosta.

💡 Mój pragmatyczny wniosek:
Wchodzimy w fazę, gdzie 'demo-hype' przestaje działać. Wygrają rozwiązania z solidną architekturą runtime, zarządzaniem uprawnieniami i lokalną telemetrią.

Link do projektu i szczegółów: {url}

Pytanie do osób budujących systemy agentowe:
W jaki sposób dzisiaj izolujecie i monitorujecie narzędzia oddane w ręce modeli w Waszych projektach? (Docker, microVM, czy dedykowane piaskownice?)

#AI #SoftwareEngineering #LLM #AutonomousAgents #Python #Architecture
"""

    carousel = f"""### 📑 KONSPEKT KARUZELI (5 SLAJDÓW PDF)

* **Slajd 1 (Okładka - Hook):**
  - Tytuł: "Jak bezpiecznie odpalić flotę agentów AI?"
  - Podtytuł: "Architektura runtime, izolacja i realne wnioski z {title}"
  - Wizualia: Ciemny motyw, schemat agent -> piaskownica -> system.

* **Slajd 2 (Problem):**
  - Nagłówek: "Dlaczego `eval()` i surowe shell command to koszmar?"
  - Punkty: Brak limitów zasobów, nieprzewidywalne pętle, wycieki kluczy API.

* **Slajd 3 (Rozwiązanie i Architektura):**
  - Nagłówek: "Jak działa {title}"
  - Schemat warstwowy: Agent Logic -> Permission Layer -> Isolated Sandbox -> Host.

* **Slajd 4 (3 kluczowe metryki do wdrożenia):**
  - 1. Czas życia piaskownicy (Ephemeral vs Persistent)
  - 2. Koszt i latencja per tool-call
  - 3. Fail-safe fallback przy halucynacji narzędzia

* **Slajd 5 (Podsumowanie & CTA):**
  - Nagłówek: "Podsumowanie w 1 zdaniu"
  - Treść: "Autonomia bez izolacji to dług technologiczny."
  - CTA: "Obserwuj profil po więcej konkretnych analiz inżynierii AI."
"""

    return {"post": post.strip(), "carousel": carousel.strip()}
