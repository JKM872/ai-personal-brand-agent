# ⚡ Autonoma AI — 12-Agent Autonomous Growth OS (0,00 PLN Budget)

Kompletna, wieloprojektowa (**Multi-Tenant**) platforma autonomicznego wzrostu, SEO/GEO, social media i sprzedaży B2B napędzana przez **12 Wirtualnych Pracowników AI**. Zaprojektowana tak, aby rozwijać Twój biznes i strony Twoich klientów 24/7 przy zerowych kosztach infrastruktury (`0,00 PLN`).

---

## 🤖 Drużyna 12 Wirtualnych Pracowników AI

| # | Stanowisko Pracownika AI | Moduł w Kodzie | Zadanie Operacyjne 24/7 |
|---|---|---|---|
| **1** | **Radar Rynkowy & Trend Scout** | `sources/*` + `agents/curator.py` | Przeszukuje sygnały rynkowe, problemy klientów i trendy branżowe. |
| **2** | **Architekt SEO & GEO (AI Search)** | `agents/geo_seo_engine.py` | Pisze artykuły porównawcze, tabele ROI, sekcje FAQ i aktualizuje `/llms.txt` pod ChatGPT i Perplexity. |
| **3** | **Ghostwriter LinkedIn B2B** | `agents/writers/linkedin_writer.py` | Tworzy eksperckie posty B2B i konspekty 5-slajdowych karuzel PDF. |
| **4** | **Strateg Wątków X / Twitter** | `agents/writers/twitter_writer.py` | Buduje wiralowe nitki (5 tweetów) z twardymi wyliczeniami. |
| **5** | **Manager Własnej Grupy (FB / Discord)** | `agents/writers/community_writer.py` | Generuje posty przypięte z Lead Magnetem („Skomentuj START”), ankiety i szablony odpowiedzi. |
| **6** | **Inżynier Reklam Micro-Budget Ads** | `agents/writers/ads_writer.py` | Tworzy kreacje retargetingowe (0–20 zł/dzień) na Meta Ads i frazy Exact-Match w Google. |
| **7** | **Specjalista B2B Outreach & SDR** | `agents/writers/outreach_writer.py` | Pisze sekwencje LinkedIn DM, Cold Emaile i zbija obiekcje sprzedażowe. |
| **8** | **Redaktor Newslettera (Brevo / Resend)** | `agents/writers/newsletter_writer.py` | Komponuje cotygodniowe wydania biuletynu dla własnej bazy subskrybentów. |
| **9** | **Reżyser Wideo Shorts / Reels / TikTok** | `agents/writers/video_writer.py` | Rozpisuje 60-sekundowe scenariusze wideo (Hook w 1. sekundzie, B-Roll i lektor). |
| **10** | **Strażnik Komentarzy Anti-Ban** | `agents/anti_ban_commenter.py` | Wrzuca linki UTM w 1. komentarzu i odpowiada z ludzkim opóźnieniem (*Human Jitter* 18–95 min). |
| **11** | **Analityk Multi-Armed Bandit (ROI)** | `agents/analyst_agent.py` | Liczy skuteczność stylów pisania z kliknięć UTM i kieruje 80% ruchu na najlepszy styl. |
| **12** | **Inżynier Integracji CMS & JSON-LD** | `publishers/cms_connector.py` | Publikuje artykuły prosto na stronę klienta (GitHub / WordPress / Webhook) za zgodą właściciela. |

---

## 🚀 Szybki Start (Lokalnie i w Chmurze)

### 1. Uruchomienie cyklu 12 Pracowników AI dla wszystkich projektów:
```bash
python engine.py
```

### 2. Uruchomienie Panelu SaaS Studio w przeglądarce:
```bash
python -m http.server 3000 --directory public
```
Następnie otwórz **[http://localhost:3000](http://localhost:3000)**.

### 3. Praca 24/7 (Cloudflare Pages + GitHub Actions za 0 zł):
* **GitHub Actions (`.github/workflows/agent_24_7.yml`):** Uruchamia `python engine.py` automatycznie co 6 godzin i wypycha świeże paczki do repozytorium.
* **Cloudflare Pages:** Automatycznie publikuje zawartość katalogu `public` oraz funkcję Edge AI `/api/ai-generate`.
