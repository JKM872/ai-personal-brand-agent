# 🧭 Master Plan: Wirtualna Drużyna Agentów AI dla Twojego Produktu

Ten dokument podsumowuje architekturę Twojej wirtualnej agencji AI, która promuje, pozycjonuje i rozwija Twój produkt w trybie 24/7 bez ryzyka blokad kont.

---

## 👥 Twoja Drużyna Pracowników AI (Kto za co odpowiada)

| Agent / Rola | Zadanie Główne | Gdzie działa w kodzie | Efekt dla Biznesu |
|---|---|---|---|
| **1. Redaktor SEO & Artykułów** | Pisanie merytorycznych poradników i studiów przypadków na bloga | `agents/geo_seo_engine.py` | Ruch organiczny z Google |
| **2. Strateg GEO (AI Ads / ChatGPT)** | Pozycjonowanie w modelach AI, wdrażanie `/llms.txt` i tabel porównawczych | `public/llms.txt` & JSON-LD | ChatGPT i Perplexity polecają Twój produkt |
| **3. Fabryka Social Media** | Generowanie postów na LinkedIn, wątków na X, newslettera i wideo | `agents/writers/` | Stała widoczność i budowa własnej grupy |
| **4. Asystent Relacji Anti-Ban** | Odpowiedzi na komentarze z ludzkim opóźnieniem (15–45 min) | `agents/anti_ban_commenter.py` | Zaangażowanie bez ryzyka bana |
| **5. Koordynator Chmurowy 24/7** | Budzenie agentów co 6 godzin na serwerach GitHuba i Cloudflare | `.github/workflows/` | Ty odpoczywasz, machina pracuje |

---

## ⏰ Dobowy Cykl Pracy Twojej Drużyny (Harmonogram 24h)

* **06:00 Rano (Prasówka & Pierwszy Post):**  
  Agent zwiadowczy przeszukuje trendy, wybiera temat dnia i przygotowuje post na LinkedIn oraz wątek na X.
* **12:00 W Południe (Nowy Artykuł Blogowy & GEO):**  
  Agent SEO generuje gotowy artykuł z tabelą porównawczą promujący Twój produkt i aktualizuje wizytówkę `/llms.txt` dla robotów ChatGPT.
* **18:00 Wieczorem (Druga Fala Social & Wideo):**  
  Przygotowanie scenariusza wideo Shorts/Reel oraz wydania newslettera na dany tydzień.
* **W ciągu dnia (Ciągły Anti-Ban Engagement):**  
  Odpowiedzi na pojawiające się komentarze z losowym opóźnieniem (minimum 15 minut), wyłącznie w godzinach ludzkiej aktywności (8:00–22:00).
* **Noc (Bezpieczeństwo & Porządki w pamięci):**  
  Dedykowana pamięć anty-duplikacyjna zapisuje przetworzone tematy, aby nigdy nie powtórzyć tego samego wpisu.

---

## 🛡️ Tarcza Bezpieczeństwa (Dlaczego nie dostaniesz bana?)

1. **Zero gołych linków (No Naked Links):** W komentarzach i postach społecznościowych agenci nie spamują bezpośrednimi linkami. Najpierw dają 95% merytorycznego rozwiązania problemu, a o produkcie wspominają kontekstowo.
2. **Losowy Jitter (Human Delay):** Odpowiedzi nie pojawiają się w 3 sekundy jak u bota, lecz po losowym czasie (np. 18.4 min, 32.1 min).
3. **Czysta reputacja domeny:** Całość hostowana jest na zaufanych infrastrukturach (GitHub + Cloudflare CDN).

---

## 🚀 Jak uruchomić maszynę dla gotowego produktu?

1. Wpisz dane produktu do: [`saas_core/product_profile.json`](saas_core/product_profile.json) (nazwa, link, problem klienta).
2. Podepnij konta lub Webhook w: [`config/accounts.json`](config/accounts.json).
3. Maszyna na GitHub Actions i Cloudflare automatycznie zaczyna generować treści dedykowane wyłącznie pod Twój produkt!
