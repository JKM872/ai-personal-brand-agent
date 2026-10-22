# 🚀 24/7 Personal Brand Multi-Agent Engine (AI & Tech)

W pełni autonomiczny, wieloagentowy system działający 24/7, który buduje Twoją markę osobistą w branży AI i inżynierii oprogramowania.

## 🏗️ Architektura Systemu

```mermaid
graph TD
    subgraph 1. Źródła 24/7
        GH[GitHub Trending AI]
        HN[Hacker News Top Stories]
        AX[ArXiv Research Papers]
    end

    subgraph 2. Selekcja & Strategia
        GH --> Curator[Agent Kurator]
        HN --> Curator
        AX --> Curator
        Curator --> Topic[Temat Dnia + 3 Radary]
    end

    subgraph 3. Fabryka Formatów (Ghostwriterzy)
        Topic --> LI[LinkedIn: Post & Karuzela PDF]
        Topic --> TW[X / Twitter: Thread 5 tweetów + Hooki]
        Topic --> NL[Newsletter: Deep-Dive Issue]
        Topic --> YT[Wideo: 60s Shorts / Reel Script]
        Topic --> GH_W[GitHub: Kod Demo + README]
    end

    subgraph 4. Centrum Dowodzenia
        LI --> Dash[DASHBOARD.md & Folder Queue]
        TW --> Dash
        NL --> Dash
        YT --> Dash
        GH_W --> Dash
    end
```

---

## ⚡ Jak z tego korzystać?

### 1. Sprawdź dzisiejszy wygenerowany materiał
Otwórz plik [DASHBOARD.md](file:///c:/Users/hp/Documents/antigravity/mysterious-darwin/DASHBOARD.md). Znajdziesz tam gotowe teksty na wszystkie platformy przygotowane przez agentów z ostatniej rundy.

### 2. Dostosuj swoją tożsamość i styl (Persona)
W pliku [brand_core/persona.json](file:///c:/Users/hp/Documents/antigravity/mysterious-darwin/brand_core/persona.json) możesz zmienić:
* Swoje imię, nazwisko i biogram.
* Swój unikalny *Tone of Voice* (np. bardziej techniczny, startupowy, krytyczny wobec hype'u).
* Filary tematyczne (tematy, na których chcesz budować pozycję lidera opinii).

### 3. Uruchomienie na żądanie
Aby natychmiast odpalić nową rundę skanowania i wygenerować świeżą paczkę:
```bash
python engine.py
```

### 4. Działanie ciągłe 24/7
Aby system działał nieprzerwanie w tle na Twoim komputerze i sprawdzał trendy np. co 12 godzin:
```bash
python run_daemon.py
```
Możesz także skonfigurować go jako harmonogram w Antigravity za pomocą komendy `/automation`.
