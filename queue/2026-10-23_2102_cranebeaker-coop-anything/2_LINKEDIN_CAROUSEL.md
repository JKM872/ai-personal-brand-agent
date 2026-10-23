### 📑 KONSPEKT KARUZELI (5 SLAJDÓW PDF)

* **Slajd 1 (Okładka - Hook):**
  - Tytuł: "Jak bezpiecznie odpalić flotę agentów AI?"
  - Podtytuł: "Architektura runtime, izolacja i realne wnioski z cranebeaker/coop-anything"
  - Wizualia: Ciemny motyw, schemat agent -> piaskownica -> system.

* **Slajd 2 (Problem):**
  - Nagłówek: "Dlaczego `eval()` i surowe shell command to koszmar?"
  - Punkty: Brak limitów zasobów, nieprzewidywalne pętle, wycieki kluczy API.

* **Slajd 3 (Rozwiązanie i Architektura):**
  - Nagłówek: "Jak działa cranebeaker/coop-anything"
  - Schemat warstwowy: Agent Logic -> Permission Layer -> Isolated Sandbox -> Host.

* **Slajd 4 (3 kluczowe metryki do wdrożenia):**
  - 1. Czas życia piaskownicy (Ephemeral vs Persistent)
  - 2. Koszt i latencja per tool-call
  - 3. Fail-safe fallback przy halucynacji narzędzia

* **Slajd 5 (Podsumowanie & CTA):**
  - Nagłówek: "Podsumowanie w 1 zdaniu"
  - Treść: "Autonomia bez izolacji to dług technologiczny."
  - CTA: "Obserwuj profil po więcej konkretnych analiz inżynierii AI."