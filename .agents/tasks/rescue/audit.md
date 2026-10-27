# Audyt projektu „Autonoma AI” (mysterious-darwin) — krok 1, tylko odczyt

Data audytu: 2026-10-26. Python 3.14.0 (Windows, PowerShell). Repozytorium czyste (`git status` bez zmian przed i po audycie). Brak `.env`, brak `config/accounts.local.json`, brak zmiennych środowiskowych z kluczami — system działa wyłącznie w trybie bez kluczy.

## 1. Mapa architektury

Projekt to **czysta biblioteka standardowa Pythona** (urllib, sqlite3, http.server) — brak `requirements.txt`, brak zależności zewnętrznych. Zostawić tak.

### Punkty wejścia
| Plik | Rola |
|---|---|
| `engine.py` | Orkiestrator jednego cyklu (`run_brand_engine()`), uruchamiany ręcznie, z CI i z demona |
| `run_daemon.py` | Pętla `while True` → `subprocess engine.py` co `schedule_interval_hours` (config/accounts.json, domyślnie 6h) |
| `local_server.py` | Serwer HTTP :3000 serwujący `public/` + `/api/save-keys`, `/api/load-keys`, `/api/save-projects` |
| `web_generator.py` | `build_web_dashboard()` — generuje `public/index.html` (szablon HTML/JS ~1700 linii w f-stringu) i `public/data.json` |
| `src/index.js` + `wrangler.toml` | Cloudflare Worker (assets z `public/`, `/api/ai-generate`, `/api/status`, pusty cron) |
| `functions/api/*.js` | Cloudflare Pages Functions (`ai-generate.js`, `status.js`) — duplikat logiki workera |
| `.github/workflows/agent_24_7.yml` | Cron co 6h: `python engine.py` + commit/push `queue/ memory/ DASHBOARD.md public/ logs/` |
| `Dockerfile` | `python:3.12-slim`, `CMD python run_daemon.py` |

### Przepływ danych jednego cyklu (`engine.py`)
1. `db.get_active_projects()` → Supabase `projects` (jeśli klucze) → `saas_core/projects.json` (`subscription_status == "active"`) → `saas_core/product_profile.json`.
2. Scouting (sieć, tylko GET, bez kluczy): `sources/github_scout.py` (GitHub Search API), `sources/hacker_news_scout.py`, `sources/arxiv_scout.py`. Błędy → `[WARN]` i pusta lista.
3. Dla każdego projektu (`run_single_project_cycle`):
   - `analyst_agent.pick_best_persona()` (bandit 80/20 na tabeli `agent_strategy`),
   - `memory.filter_unseen_items` + `curator.curate_topics` (heurystyczny scoring),
   - **zapis projektu do `saas_core/product_profile.json`** (engine.py ~l.147) — to jest jedyny kanał, którym writery dostają dane projektu,
   - 8 writerów (`agents/writers/*`) → każdy: jeśli `has_live_ai_key()` → `ask_free_ai`, inaczej szablon f-string,
   - `geo_seo_engine.generate_geo_article` → zapis `public/articles/<slug>.md` + `public/llms.txt`,
   - `cms_connector.publish_article_to_website` (bramka właściciela) → ew. `indexnow.submit_to_indexnow`,
   - zapis 12 plików do `queue/<YYYY-MM-DD_HHMM>_<proj_id>_<slug>/`,
   - `db.insert_content` (SQLite/Supabase `content_pipeline`, `scheduled_for = now + randint(18,95) min`),
   - `memory.save_to_memory` → `memory/seen_topics.json`,
   - `social_publisher.dispatch_content_bundle` → `7_API_PAYLOAD_READY.json`, `PUBLISH_STATUS.json` (+ wysyłki w trybie live).
4. `analyst_agent.run_nightly_optimization()` → przelicza score, `public/raport_statystyczny.md`.
5. `update_markdown_dashboard` → `DASHBOARD.md`; `build_web_dashboard` → `public/index.html`, `public/data.json`.

### Router AI (`agents/free_ai_router.py`)
`_load_key(name)`: env → `.env` → `config/accounts.local.json` → `config/accounts.json` (sekcja `ai_keys` lub top-level), z filtrem placeholderów (`TWÓJ_…`, `ghp_TWÓJ…`, `urn:li:person:TWOJE_ID`). Kaskada: Gemini (2.5/2.0/1.5-flash) → Groq (llama-3.3-70b-versatile) → Cloudflare Workers AI (`agents/cloudflare_ai.py`, `CF_ACCOUNT_ID`+`CF_API_TOKEN`) → `""` (writery przechodzą na szablony).

## 2. Co działa dziś (zachować)

- Wszystkie 29 plików `.py` kompilują się (`py_compile`), wszystkie 28 modułów importują się bez błędów.
- **Pełny cykl `python engine.py` bez kluczy kończy się sukcesem (exit 0, ~17 s)** — patrz sekcja 13.
- Graceful degradation AI: bez kluczy writery używają szablonów; router zwraca `""`.
- Supabase → lokalny SQLite fallback (`db/local_storage.db`, tabele tworzone automatycznie w `_init_local_db`).
- Social publisher automatycznie w `dry_run`, gdy brak `WEBHOOK_URL`/Telegram/LinkedIn/Brevo/Resend; zapisuje `PUBLISH_STATUS.json` z `QUEUED_FOR_AUTO_PUBLISH`.
- Bramka CMS (`publishers/cms_connector.py`): domyślnie `owner_authorized: false` → `AWAITING_OWNER_PERMISSION`, tryb `require_approval` → `PENDING_1CLICK_APPROVAL`. Oba projekty w `saas_core/projects.json` mają `owner_authorized: false`, więc żadnego zapisu do CMS i żadnego pingu IndexNow.
- Pamięć anty-duplikacyjna tematów (`memory/seen_topics.json`, 500 URL / 100 runów).
- Multi-tenant: pętla po projektach, nazwy folderów `queue/` zawierają `proj_id`.
- Generowanie `llms.txt`, JSON-LD (`schema_json`), UTM (`tracking/utm_builder.py`).
- `local_server.py` zapisuje klucze do `.env` (ignorowanego przez git).
- Treści użytkownika: 229 plików w `queue/` (~26 folderów), artykuły w `public/articles/` — **nie usuwać**.

## 3. Co jest zepsute / błędne (file:line)

Brak twardych wyjątków w baseline. Błędy logiczne i funkcjonalne:

| # | Miejsce | Problem |
|---|---|---|
| B1 | `agents/geo_seo_engine.py:210` i `:287` | Artykuł jest **zawsze** zapisywany do `public/articles/<slug>.md` (publiczny katalog Cloudflare Pages), zanim bramka CMS cokolwiek sprawdzi. Bramka `AWAITING_OWNER_PERMISSION` jest więc fikcją dla strony własnej — szkic trafia publicznie po pushu z CI. |
| B2 | `engine.py` (~l.147) + wszystkie `agents/writers/*.py` (`load_product_profile()`) | Writery ignorują przekazany projekt i czytają `saas_core/product_profile.json`, który engine nadpisuje w każdym cyklu (tracked file zmieniany przez każdy run). Ukryty kanał globalny; niebezpieczne przy równoległości / SaaS. |
| B3 | `.gitignore` (wzorzec `.env*`) | Ignoruje też `.env.example` — `git ls-files .env.example` zwraca pusto. Dokumentacja kluczy **nie jest w repo**. |
| B4 | `public/blog.html:~120-127` | Formularz leadów zapisuje e-mail tylko do `localStorage` przeglądarki odwiedzającego (`autonoma_captured_leads`) — lead nigdy nie dociera do właściciela. Komunikat sugeruje zapis do bazy. Brak zgody RODO. |
| B5 | `public/tracker.js` | Woła `rpc/increment_click`, której nie ma w `db/schema.sql`; brak polityk RLS dla `subscribers` (anon insert nie zadziała lub będzie otwarty dla wszystkich). Używa `window.SUPABASE_URL/ANON_KEY`, których nic nie ustawia. |
| B6 | `agents/analyst_agent.py` (`run_nightly_optimization`) + `db/supabase_client.py` (`INSERT OR IGNORE`, seedy 5/92/7 itd. i UPDATE „legacy zero rows”) | Statystyki bandita są **zmyślone** (seed z fikcyjnymi kliknięciami/konwersjami, `random.randint(10,45)` jako domyślne kliknięcia). Każdy run zwiększa `posts_count`, więc „ROI” tylko spada (baseline: 11.62/7.5/6.29). Brak realnego źródła kliknięć. |
| B7 | `agents/geo_seo_engine.py:71`, `:91`, `:121` i szablony writerów | Zmyślone „twarde dane” (64% firm, 45% decydentów, CAC −80%, DSO 28→6 dni), „zweryfikowana platforma”, „Rekomendacja Ekspertów”, ranking z produktem #1 — wprowadzające w błąd treści publikowane jako fakty (ryzyko prawne/reputacyjne, sprzeczne z wytycznymi Google dot. treści). |
| B8 | `local_server.py` | Docstring opisuje `/api/run-engine` — endpoint nie istnieje. `/api/load-keys` zwraca **wszystkie sekrety w czystym tekście**, `Access-Control-Allow-Origin: *`, bind na `""` (wszystkie interfejsy), brak uwierzytelnienia. `/api/save-keys` nadpisuje cały `.env` (gubi np. `SUPABASE_*`, `CF_*`, `TELEGRAM_CHAT_ID`). |
| B9 | `public/index.html` (generowany z `web_generator.py`) | Panel admina (pola na klucze API, wywołania Gemini z kluczem w URL z przeglądarki ~l.1323/1503/1667) jest **publiczną stroną główną** na Cloudflare Pages. `public/data.json` publikuje projekty, pipeline i konfigurację CMS (w tym `wp_user`, `gh_repo`). Brak strony ofertowej dla odwiedzających. |
| B10 | `logs/agent.log` | 7 linii, wyłącznie `OK` z 2026-10-23, mojibake (UTF-8 czytany jako cp1252, np. `â€“`). Żaden obecny kod nie pisze do tego pliku; CI robi `git add logs/`, ale `logs/*.log` jest w `.gitignore`. Brak powtarzających się błędów/tracebacków. |
| B11 | Konsola Windows | Wyjście `engine.py` przekierowane do pliku ma mojibake emoji/polskich znaków (reconfigure utf-8 działa tylko dla konsoli). Kosmetyka. |
| B12 | `run_daemon.py` | Czas w logu cyklu liczony przed uruchomieniem (`now` nieaktualizowane), brak obsługi SIGTERM; drobne. |
| B13 | `publishers/indexnow.py` | Domyślny klucz `ai_brand_agent_key` i brak dry-run — gdyby bramka była otwarta, wysyła realny POST do api.indexnow.org z fałszywym kluczem. |
| B14 | `publishers/social_publisher.py` (`load_accounts_config`) | Jeden klucz (np. tylko `BREVO_API_KEY`) przełącza **globalnie** `mode = "live"` dla wszystkich kanałów; brak flagi `DRY_RUN` niezależnej od kluczy. |
| B15 | `.github/workflows/agent_24_7.yml` | Nie przekazuje `RESEND_API_KEY`, `LINKEDIN_*`, `CF_ACCOUNT_ID`, `CF_API_TOKEN`, `INDEXNOW_KEY`, `CMS_*`; brak testów/py_compile; pushuje bezpośrednio na domyślną gałąź co 6h (szum w historii, ~12 plików/projekt/cykl). |

## 4. Zduplikowany kod

- `src/index.js` ↔ `functions/api/ai-generate.js` + `functions/api/status.js` — identyczna logika `/api/ai-generate` i `/api/status` (Worker vs Pages Functions); `wrangler.toml` wskazuje Workera, README mówi o Pages.
- `slugify()` w `engine.py` i `agents/geo_seo_engine.py` (różne zachowanie: druga obsługuje polskie znaki, długość 40 vs 55).
- Szablony treści: writery Pythona ↔ JS `synthesizeBundleForProject` w `web_generator.py` (~l.880–1010, „Anti-Ban 1st Comment”, „START”, „Cold Email”) ↔ prompty w `functions/api/ai-generate.js`.
- Wywołania Gemini/Groq: `agents/free_ai_router.py` ↔ JS w `web_generator.py` (trzy miejsca z `generativelanguage.googleapis.com`).
- Wzorzec writera (`load_product_profile` + `derive_seo_headline` + `if has_live_ai_key(): ask_free_ai(...)` + szablon) powtórzony 8×.
- `sys.stdout.reconfigure` w 5+ plikach.
- Ładowanie konfiguracji kont: `free_ai_router._load_key`, `social_publisher.load_accounts_config`, `local_server`, `run_daemon.get_interval_hours`, `cms_connector.load_cms_permissions` (os.environ bezpośrednio, pomija `.env`).

## 5. Martwy kod

- `agents/anti_ban_commenter.py` — nieimportowany nigdzie (tylko `__main__`); UI ma własną JS-ową kopię.
- `agents/project_scanner.py` (`scan_website_dna`) — nieużywany przez Pythona (UI robi skan w JS).
- `agents/newsletter_agent.py` — wywoływany tylko w trybie live z `social_publisher`.
- `brand_core/persona.json` — nie czytany przez żaden kod (persona marki osobistej nie wpływa na treści!).
- Tabela `comments_queue` — tworzona, nigdy nie zapisywana/czytana.
- `workers-site/index.js` — wymaga `@cloudflare/kv-asset-handler` (brak package.json), nieużywany przez `wrangler.toml`.
- `load_memory` importowane w `engine.py`, nieużywane; `db.save_project`, `get_scheduled_pipeline` tylko w web_generator.
- `config/accounts.json` sekcje `twitter_x`, `github` — brak implementacji publikacji X i GitHub (status „QUEUED_FOR_AUTO_PUBLISH” jest mylący).
- Cron `scheduled()` w `src/index.js` — tylko `console.log`.
- `__pycache__` w folderach `queue/*` (z kompilacji `6_GITHUB_SNIPPET.py`; ignorowane przez git).

## 6. Funkcje łamiące zasady platform (do usunięcia / zneutralizowania)

| Plik / funkcja | Problem |
|---|---|
| `agents/anti_ban_commenter.py` — `calculate_safe_delay_minutes`, `is_within_active_hours`, `generate_safe_reply`, `safety_checks` | Celowe udawanie człowieka (losowy „Human Jitter” 18–95 min, godziny aktywności) „żeby nie wykryły algorytmy wykrywania botów” — omijanie detekcji automatyzacji. Odpowiedzi AI publikowane jako ludzkie. Zastąpić: szkic odpowiedzi → kolejka do ręcznej akceptacji, bez opóźnień maskujących. |
| `engine.py:198` („Anti-Ban 1st Comment”), `engine.py:216` (`scheduled_for = now + randint(18,95)`) | Planowanie publikacji z losowym jitterem w celu obejścia detekcji; link w 1. komentarzu jako „anti-ban”. |
| `web_generator.py:54, 329, 560, 762–815, 1782–1808, 1872–1888` | Zakładka „Kolejka Anti-Ban”, rola „Strażnik Komentarzy Anti-Ban”, generator odpowiedzi z jitterem, harmonogram „Publikacja (Jitter)”. |
| `agents/writers/community_writer.py` (sekcja 3) + `web_generator.py:982` | Mechanika „skomentuj START” (engagement bait — zakazane m.in. przez Meta) i auto-odpowiedzi „asystenta” z opóźnieniem „Human-Delay”; obietnica automatycznego DM. |
| `agents/writers/outreach_writer.py` + `web_generator.py:470, 1008` | Szablony zimnych DM/cold e-maili „15–20 dziennie”; brak podstawy prawnej (RODO/UŚUDE w PL wymaga zgody na informację handlową e-mailem), brak opt-out. Zostawić jako **szablony do ręcznego, indywidualnego użycia**, nie wysyłkę. |
| `agents/newsletter_agent.py` (`time.sleep(random.uniform(...))` „anti-spam pacing”) | Pacing maskujący; brak linku wypisu, brak double opt-in; nadawca `newsletter@twojadomena.pl`. Wysyłka tylko do zweryfikowanych subskrybentów z zgodą. |
| `publishers/social_publisher.py` (`post_to_linkedin`, webhook do Make/n8n „rozsyła na wszystkie konta naraz”) | Automatyczna publikacja bez akceptacji człowieka; cross-posting tej samej treści na wiele kont. Musi przejść przez kolejkę zatwierdzeń. |
| `PLAN_ROZWOJU_AGENCI_AI.md` sekcja „Tarcza Bezpieczeństwa (Dlaczego nie dostaniesz bana?)”, README #10 | Dokumentacja obiecuje obchodzenie detekcji. |
| Zmyślone metryki (B6/B7) | Fałszywe dane w treściach publicznych — nieuczciwe praktyki rynkowe. |

## 7. Brak trybu dry-run/mock per zależność zewnętrzna

| Zależność | Plik | Stan bez kluczy | Brakuje |
|---|---|---|---|
| GitHub Search API | `sources/github_scout.py` | realne GET, przy błędzie `[]` | trybu offline/fixture (CI/testy zależne od sieci i limitu 60 req/h) |
| Hacker News API | `sources/hacker_news_scout.py` | realne GET | j.w. |
| arXiv API | `sources/arxiv_scout.py` | realne GET | j.w. |
| Gemini / Groq / CF AI | `free_ai_router.py`, `cloudflare_ai.py` | pomijane bez klucza ✔ | jawnej flagi mock; logu „użyto szablonu” |
| Supabase | `db/supabase_client.py` | SQLite ✔ | — (ale seedy z fikcyjnymi danymi) |
| Webhook/Telegram/LinkedIn | `social_publisher.py` | dry_run ✔ | globalnej flagi `DRY_RUN`; kolejki akceptacji; jeden klucz włącza live wszystkiego |
| Brevo/Resend | `newsletter_agent.py` | dry_run zapisuje `queue/last_newsletter_batch.html` ✔ | consent/unsubscribe |
| CMS GitHub/WP/Webhook | `cms_connector.py` | bramka ✔ | ale artykuł i tak w `public/articles` (B1); fallback „PUBLISHED_LOCAL” |
| IndexNow | `indexnow.py` | **brak dry-run** (realny POST z fałszywym kluczem) | guard na brak `INDEXNOW_KEY` |
| Skan strony | `project_scanner.py` | realne GET | — (nieużywany) |
| Workers AI w Pages | `functions/api/ai-generate.js`, `src/index.js` | `env.AI` niezdefiniowane → 500 | fallbacku/komunikatu, limitu, auth (publiczny endpoint zużywa darmowy limit właściciela) |

## 8. Klucze API / zmienne środowiskowe per moduł (tylko nazwy)

| Moduł | Zmienne |
|---|---|
| `agents/free_ai_router.py` | `GEMINI_API_KEY`, `GROQ_API_KEY`, `CF_ACCOUNT_ID`, `CF_API_TOKEN` |
| `agents/cloudflare_ai.py` | `CF_ACCOUNT_ID`, `CF_API_TOKEN` |
| `publishers/social_publisher.py` | `WEBHOOK_URL`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`, `LINKEDIN_ACCESS_TOKEN`, `LINKEDIN_AUTHOR_URN`, `BREVO_API_KEY`, `RESEND_API_KEY` |
| `agents/newsletter_agent.py` | `BREVO_API_KEY`, `RESEND_API_KEY` |
| `db/supabase_client.py` | `SUPABASE_URL`, `SUPABASE_KEY`, `SUPABASE_ANON_KEY` |
| `publishers/cms_connector.py` (tylko `os.environ`, bez `.env`) | `CMS_OWNER_AUTHORIZED`, `CMS_PUBLISH_MODE`, `CMS_TYPE`, `CMS_WEBHOOK_URL`, `CMS_API_KEY`, `WP_SITE_URL`, `WP_USERNAME`, `WP_APP_PASSWORD`, `CMS_GH_REPO`, `CMS_GH_TOKEN`, `CMS_GH_PATH` (+ `cms_permissions` z projektu) |
| `publishers/indexnow.py` | `INDEXNOW_KEY` |
| `local_server.py` | czyta/zapisuje: `GEMINI_API_KEY`, `GROQ_API_KEY`, `WEBHOOK_URL`, `LINKEDIN_ACCESS_TOKEN`, `BREVO_API_KEY`, `TELEGRAM_BOT_TOKEN`, `CMS_WEBHOOK_URL`, `CMS_API_KEY` |
| `public/tracker.js` | `window.SUPABASE_URL`, `window.SUPABASE_ANON_KEY` (nieustawiane) |
| Cloudflare (`wrangler.toml`) | binding `AI`, `ASSETS` |

`.env.example` (nietrackowany, B3) brakuje: `CF_ACCOUNT_ID`, `CF_API_TOKEN`, `LINKEDIN_ACCESS_TOKEN`, `LINKEDIN_AUTHOR_URN`, `SUPABASE_ANON_KEY`, `INDEXNOW_KEY`, `CMS_OWNER_AUTHORIZED`, `CMS_PUBLISH_MODE`, `CMS_TYPE`, `CMS_GH_PATH`. Zawiera domyślną wartość `CMS_GH_REPO=JKM872/ai-personal-brand-agent` (nie sekret). W `config/accounts.json` tylko placeholdery — żadnych realnych sekretów w repo nie znaleziono.

## 9. Stan strony publicznej (`public/`)

- `index.html` (1606 l., generowany) — **panel administracyjny SaaS**, nie strona marki: przełącznik projektów, pola na klucze API, „Bramka CMS”, „Kolejka Anti-Ban”. Brak oferty usług, cennika, opisu osoby/marki, CTA „umów rozmowę”, case studies.
- `blog.html` — portal artykułów z formularzem e-mail (lead tylko w `localStorage`, B4), bez zgody RODO i polityki prywatności.
- `articles/` — artykuły generowane (szablonowe rankingi z fikcyjnymi danymi, slugi per projekt, także demo „InvoicePulse”).
- `llms.txt` — nadpisywany przy każdym artykule przez ostatni projekt w pętli (obecnie demo klienta → strona marki opisuje cudzy/fikcyjny produkt).
- `data.json` — publiczny zrzut stanu (projekty, pipeline, persony).
- `raport_statystyczny.md` — publiczny raport z fikcyjnymi liczbami.
- `tracker.js` — niepodłączony (B5).
- **Oferta / CTA / działający formularz leadów: brak.** Brak `robots.txt`, `sitemap.xml`, polityki prywatności.

## 10. Stan bazy danych

- `db/schema.sql` (Supabase/Postgres): `agent_strategy`, `content_pipeline` (id UUID), `comments_queue`, `subscribers`, `projects` + indeksy. Brak: RLS i polityk, funkcji `increment_click`, tabel `leads`/`approvals`/`clicks`, kolumn zgody (`consent_at`, `unsubscribed_at`, `double_opt_in`). `content_pipeline.id UUID` vs Python wysyła tekstowe ID (`2026-10-26_2201_proj_…`) → insert do Supabase by się nie powiódł (fallback do SQLite po `[WARN]`).
- `db/local_storage.db` (SQLite, ignorowany przez git): te same 4 tabele (bez `projects` — projekty w `saas_core/projects.json`). `agent_strategy` obecnie: analityk_danych 8/68/5/11.62, case_study 8/45/3/7.5, kontrowersyjny_ekspert 7/34/2/6.29 (wartości z seedów, nie z realnych kliknięć).

## 11. CI / Docker / Cloudflare

- **CI**: tylko jeden workflow; brak lint/test; `permissions: contents: write`; pushuje wygenerowane treści co 6h (konflikty z lokalną pracą użytkownika, rosnące repo). Działa bez sekretów (dry-run). Akcje przypięte do majorów (`@v4`, `@v5`).
- **Docker**: brak `.dockerignore` (kopiuje `.git`, `db/*.db`, ewentualny `.env` do obrazu!), root user, Python 3.12 vs lokalnie 3.14, brak HEALTHCHECK. Działa (stdlib).
- **Cloudflare**: `wrangler.toml` = Worker z assets; równolegle `functions/` dla Pages — niespójne. `compatibility_date = "2026-10-01"`. Endpoint `/api/ai-generate` publiczny, CORS `*`, bez auth/rate-limit.

## 12. PLAN_ROZWOJU_AGENCI_AI.md vs rzeczywistość

| Plan | Rzeczywistość |
|---|---|
| 5 agentów (README/engine mówią o 12) | 12 „pracowników” to w praktyce 8 szablonów + scouting + bandit; #10 martwy, #12 bramka |
| Harmonogram 06/12/18 + noc | Jeden cron co 6h robi wszystko naraz |
| „Odpowiedzi na komentarze z opóźnieniem 15–45 min” | Brak pobierania komentarzy z jakiejkolwiek platformy; kod niewywoływany; schema mówi 15–95, kod 18–95 |
| „Tarcza: nie dostaniesz bana” | Techniki maskowania automatyzacji — do usunięcia (sekcja 6) |
| „Treści dedykowane pod Twój produkt” | Writery czytają globalny `product_profile.json`; `brand_core/persona.json` (marka osobista) nieużywany |
| Konta/Webhook w `config/accounts.json` | X i GitHub niezaimplementowane; LinkedIn ugcPosts (stare API), webhook OK |
| Brak w planie | Zarabianie: oferta, lejek leadów, płatności, onboarding klientów SaaS — nie istnieją |

## 13. BASELINE — komenda i wyniki

Brak dedykowanej flagi `--dry-run`/zmiennej `DRY_RUN`. Dry-run jest **niejawny**: brak kluczy ⇒ `social_publisher` `mode=dry_run`, writery na szablonach, `owner_authorized=false` ⇒ brak CMS/IndexNow. Przed uruchomieniem zweryfikowano: brak `.env`, brak `accounts.local.json`, brak zmiennych z kluczami, oba projekty `owner_authorized: false` ⇒ bezpieczne (jedyny ruch sieciowy to GET do GitHub/HN/arXiv).

Aby nie zmieniać checkoutu użytkownika, run wykonano w **kopii** repo (bez `.git`, `.agents`, `__pycache__`) w `%TEMP%\md_baseline` z tymczasowym gitem do diffu; kopię usunięto.

```powershell
$t="$env:TEMP\md_baseline"; robocopy . $t /E /XD .git .agents __pycache__
cd $t; git init -q; git add -A; git -c user.name=a -c user.email=a@a commit -qm base
python engine.py *> run.txt      # exit=0, ~17 s
git status --short
```

Wynik konsoli (skrót): „Liczba aktywnych projektów: 2” → dla `proj_autonoma_os` (persona `case_study`, temat „GPT-6.1 Terra” z HN) i `proj_demo_client` (persona `analityk_danych`): „Wygenerowano: LinkedIn, Karuzelę, X Thread, …”, „Artykuł: Najlepsze narzędzia do …”, „Bramka CMS: AWAITING_OWNER_PERMISSION”, „Kompletna paczka 10 formatów … zapisana w queue/…”; raport statystyczny (lider `analityk_danych` 10.33 pkt); „Przebudowany panel … public/index.html”. Żadnych `[WARN]`/tracebacków.

Pliki zmienione/utworzone przez jeden run:
```
 M DASHBOARD.md
 M memory/seen_topics.json
 M public/articles/proj-autonoma-os-autonomiczne-systemy-wzrostu-seo-i-mar.md
 M public/articles/proj-demo-client-automatyzacja-plynnosci-finansowej-i-f.md
 M public/data.json
 M public/index.html
 M public/raport_statystyczny.md
?? queue/2026-10-26_2201_proj_autonoma_os_gpt-6-1-terra/
?? queue/2026-10-26_2201_proj_demo_client_concerning-behavior-from-a-popular-open-/
(+ ignorowane: db/local_storage.db — insert do content_pipeline, posts_count++, score)
(+ nadpisywane bez zmiany treści: saas_core/product_profile.json, public/llms.txt)
```
Każdy folder `queue/…` zawiera 13 plików: `0_WEBSITE_SEO_ARTICLE.md`, `1_LINKEDIN_POST.md`, `2_LINKEDIN_CAROUSEL.md`, `3_TWITTER_THREAD.md`, `4_NEWSLETTER_EDITION.md`, `5_VIDEO_SHORTS_SCRIPT.md`, `6_GITHUB_README.md`, `6_GITHUB_SNIPPET.py`, `7_API_PAYLOAD_READY.json`, `8_COMMUNITY_GROUP_PLAN.md`, `9_MICRO_ADS_CAMPAIGN.md`, `10_B2B_OUTREACH_SDR.md`, `PUBLISH_STATUS.json` (`"mode": "dry_run"`, wszystkie kanały `QUEUED_FOR_AUTO_PUBLISH`).

**Kontrakt do zachowania przez kolejne kroki:** `python engine.py` bez kluczy kończy się exit 0, generuje paczkę per aktywny projekt w `queue/`, nie wykonuje żadnych zapisów do zewnętrznych platform, aktualizuje dashboard/raport/pamięć.

## 14. Wykonane komendy i wyniki

| Komenda | Wynik |
|---|---|
| `New-Item -ItemType Directory -Force .agents/tasks/rescue` | OK |
| `Get-ChildItem -Recurse …` (drzewo, liczniki) | 16 plików w `public/`, 229 w `queue/` |
| `git log --oneline`, `git status --short` | ostatni commit `baf519b`; drzewo czyste |
| `git ls-files .env.example db/local_storage.db` | pusto (oba nietrackowane) |
| `python --version` | Python 3.14.0 |
| `python -m py_compile` na 29 plikach `.py` (+ `queue/*/6_GITHUB_SNIPPET.py`) | 0 błędów |
| `python -c "import <moduł>"` ×28 (agents.*, agents.writers.*, publishers.*, db.supabase_client, tracking.utm_builder, sources.*, web_generator, local_server, run_daemon) | wszystkie OK |
| `Select-String logs/agent.log -Pattern 'Error|Traceback|WARN|Exception|failed'` | 0 trafień; 7 linii `OK` (2026-10-23), mojibake |
| Sprawdzenie `.env`, `accounts.local.json`, env vars (tylko nazwy) | brak |
| Baseline `python engine.py` w kopii tymczasowej | exit 0, 17 s, zmiany jak w sekcji 13 |
| `sqlite3` odczyt `agent_strategy` z repo | 3 persony z wartościami seedów |
| Usunięcie `%TEMP%\md_baseline`, `git status` w repo | repo bez zmian |

## 15. Priorytety dla kolejnych kroków (rekomendacja)

1. Etyka: zneutralizować `anti_ban_commenter.py`, jitter w `engine.py`, „START”/auto-DM, auto-publikację → kolejka „do akceptacji człowieka” (`queue/…/APPROVAL.json` lub `status='pending_approval'`).
2. Jawna flaga `DRY_RUN` (domyślnie włączona bez kluczy), guard w IndexNow, social publisher i newsletterze; fixture offline dla scoutów.
3. Usunąć zmyślone statystyki i seedy; bandit tylko na realnych danych (lub neutralny start).
4. Strona publiczna: oferta marki osobistej + CTA + działający formularz leadów (Pages Function → Supabase/fallback), polityka prywatności; panel admina poza publicznym `index.html`.
5. Writery przyjmują `project` jawnie; `brand_core/persona.json` wpięty w treści; `llms.txt` per marka właściciela.
6. Naprawić `.gitignore` (`!.env.example`), uzupełnić `.env.example`, zabezpieczyć `local_server.py` (127.0.0.1, bez zwracania sekretów).
7. CI: py_compile + testy (unittest, stdlib) + baseline dry-run; ograniczyć auto-push; Docker `.dockerignore`, non-root.
8. Ujednolicić Cloudflare (Pages Functions albo Worker), usunąć `workers-site/`.
