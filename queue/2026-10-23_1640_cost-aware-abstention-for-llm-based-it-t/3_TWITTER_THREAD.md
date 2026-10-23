🧵 1/5 
Przestańmy traktować agentów AI jak zwykłe czaty. Prawdziwa rewolucja dzieje się w warstwie runtime.

Oto dlaczego projekt "Cost-Aware Abstention for LLM-Based IT Ticket Classification" przyciąga uwagę inżynierów i co to oznacza dla architektury systemów agentowych: 👇

---

2/5 
Problem z obecnymi frameworkami agentowymi:
Większość z nich zakłada, że model "wie co robi" i daje mu bezpośredni dostęp do shella lub wrappery API.

Efekt?
- Wycieki pamięci i pętle promptów
- Ryzyko nieodwracalnych zmian w systemie
- Brak deterministycznego audytu

---

3/5 
Co robi Cost-Aware Abstention for LLM-Based IT Ticket Classification?
👉 Wrong automatic routing of an IT support ticket can cost more than human triage. We evaluate cost-aware abstention as an offline, cost-conditional readiness assessment: select a routing policy on calibration data under explicit costs, then evaluate that frozen policy once on held...

Kluczowa zmiana myślenia:
Agent nie jest "użytkownikiem systemu". Agent jest niepewnym procesem, który wymaga ścisłych uprawnień i piaskownicy.

---

4/5 
3 zasady architektury agentów 24/7 na 2026/2027 rok:
1. Least Privilege Access (żadnych wildcardów w komendach)
2. Deterministyczne testy regresyjne przed puszczeniem w produkcję
3. Transparentne logi w formacie JSONL do natychmiastowego audytu

---

5/5 
Repozytorium / link do źródła:
🔗 http://arxiv.org/abs/2610.31657v1

Budujesz agentów u siebie w firmie czy na razie testujesz lokalnie? Daj znać w komentarzu, jak rozwiązujesz kwestię bezpieczeństwa.

### Standalone Hooks:
Większość agentów AI psuje się nie przez 'słaby model', ale przez brak izolowanego runtime. Zobaczcie architekturę Cost-Aware Abstention for LLM-Based IT Ticket Classification: http://arxiv.org/abs/2610.31657v1

Przyszłość software engineeringu to nie 'pisanie promptów', tylko projektowanie środowisk, w których agenci mogą bezpiecznie odpalać kod i testy. Cost-Aware Abstention for LLM-Based IT Ticket Classification to krok w tę stronę: http://arxiv.org/abs/2610.31657v1