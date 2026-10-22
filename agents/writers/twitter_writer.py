"""
X / Twitter Ghostwriter Agent.
Produces a punchy 5-tweet technical thread + 2 standalone viral hooks.
High density of insights, concise formatting, technical authority.
"""

def generate_twitter_content(topic, persona):
    title = topic.get("title", "")
    url = topic.get("url", "")
    desc = topic.get("description", topic.get("summary", ""))
    
    thread = f"""🧵 1/5 
Przestańmy traktować agentów AI jak zwykłe czaty. Prawdziwa rewolucja dzieje się w warstwie runtime.

Oto dlaczego projekt "{title}" przyciąga uwagę inżynierów i co to oznacza dla architektury systemów agentowych: 👇

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
Co robi {title}?
👉 {desc}

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
🔗 {url}

Budujesz agentów u siebie w firmie czy na razie testujesz lokalnie? Daj znać w komentarzu, jak rozwiązujesz kwestię bezpieczeństwa.
"""

    standalone_hooks = [
        f"Większość agentów AI psuje się nie przez 'słaby model', ale przez brak izolowanego runtime. Zobaczcie architekturę {title}: {url}",
        f"Przyszłość software engineeringu to nie 'pisanie promptów', tylko projektowanie środowisk, w których agenci mogą bezpiecznie odpalać kod i testy. {title} to krok w tę stronę: {url}"
    ]

    return {
        "thread": thread.strip(),
        "standalone_hooks": standalone_hooks
    }
