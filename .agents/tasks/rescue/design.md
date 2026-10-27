# Projekt techniczny — Ratunek i produktyzacja Autonoma AI

## Przegląd
System zostaje przy obecnym stosie: Python 3.12+ wyłącznie stdlib (urllib, sqlite3, http.server, json, unittest), Cloudflare Pages (statyczne `public/` + Pages Functions w `functions/api/*.js`, JavaScript bez zależności npm), Supabase Free (Postgres + REST) z lokalnym fallbackiem SQLite (`db/local_storage.db`), GitHub Actions. Żadnych nowych zależności. Zmiany są przyrostowe: dodajemy jeden moduł runtime (tryb dry-run/offline), bramkę akceptacji człowieka między generowaniem a publikacją, stronę ofertową z formularzem leadów, tabelę leadów z CLI, loader tenantów i dokument strategii. Zachowany kontrakt z audytu (sekcja 13): `python engine.py` bez kluczy → exit 0, paczka w `queue/` per projekt, zero zapisów zewnętrznych, aktualizacja dashboardu, raportu i pamięci.

Stos jest zablokowany: Python stdlib, vanilla JS/HTML/CSS, Cloudflare Pages Functions, Supabase REST (PostgREST), SQLite, unittest. Worker (`src/index.js`, `wrangler.toml`) zostaje bez zmian funkcjonalnych poza autoryzacją `/api/ai-generate` — docelowym deployem jest Pages (decyzja: `functions/` już istnieje i obsługuje routing `/api/*` bez konfiguracji; ujednolicenie/usunięcie Workera to backlog).

## Priorytety (kolejność implementacji)
| P | Pakiet | Dlaczego |
|---|---|---|
| P0-1 | Etyka: usunięcie anti-ban/jitter/START/auto-DM, bramka `APPROVAL.json` | ryzyko banów kont właściciela = utrata kanału sprzedaży; warunek wszystkiego innego |
| P0-2 | `agents/runtime.py`: `DRY_RUN`/`OFFLINE`, guardy we wszystkich wywołaniach zapisu, IndexNow, `.env.example` + `.gitignore` | bezpieczne działanie bez kluczy |
| P0-3 | Strona oferty `public/index.html` + `functions/api/lead.js` + polityka prywatności; panel admina → `admin/` | jedyne miejsce, gdzie powstaje przychód |
| P0-4 | Tabele `leads`/`lead_events` + `leads.py` + lejek w DASHBOARD | bez śledzenia leady przepadają |
| P1-5 | Pipeline: writery z jawnym `project`/`persona`, artykuły do `queue/`, `approve.py`, `publish.py`, llms.txt/sitemap marki, usunięcie zmyślonych danych | wiarygodność treści, poprawna publikacja |
| P1-6 | Tenanci: `tenants/`, `saas_core/tenants.py`, `tenant_id` w schemacie | fundament SaaS |
| P1-7 | Bezpieczeństwo: `local_server.py`, `ADMIN_TOKEN` w ai-generate, `.dockerignore` | panel admina i klucze nie wyciekają |
| P2-8 | CI: py_compile + unittest + dry-run; testy | regresje |
| P2-9 | `docs/STRATEGIA_MONETYZACJI.md`, poprawki README/PLAN | sprzedaż |

## 1. Tryb dry-run / offline — `agents/runtime.py` (nowy)
Jeden moduł, z którego korzystają wszystkie publishery i scouty. Ładowanie kluczy pozostaje w `agents/free_ai_router._load_key` (env → `.env` → `config/accounts.local.json` → `config/accounts.json`, filtr placeholderów); `runtime.py` go importuje, a `cms_connector.load_cms_permissions` przechodzi z `os.environ` na `_load_key` (by `.env` działał).

```python
WRITE_KEYS = ["WEBHOOK_URL","TELEGRAM_BOT_TOKEN","LINKEDIN_ACCESS_TOKEN","BREVO_API_KEY",
              "RESEND_API_KEY","INDEXNOW_KEY","CMS_GH_TOKEN","WP_APP_PASSWORD","CMS_WEBHOOK_URL"]
def is_dry_run() -> bool      # DRY_RUN in ("1","true","yes") -> True; ("0","false","no") -> False;
                              # brak/inna wartość -> True gdy żaden WRITE_KEYS nie jest ustawiony
def is_offline() -> bool      # OFFLINE in ("1","true","yes")
def log_skip(service, action) # print(f"[DRY_RUN] {service}: {action} pominięta")
def channel_live(*keys) -> bool  # not is_dry_run() and wszystkie podane klucze ustawione
```
Nieprawidłowa wartość `DRY_RUN` (np. `maybe`) → traktowana jak auto + `[WARN] DRY_RUN=<v> nierozpoznane, tryb auto`.

Strategia per usługa:
| Usługa | Plik | Dry-run / brak klucza |
|---|---|---|
| GitHub/HN/arXiv | `sources/*_scout.py` | `OFFLINE=1` → `sources/fixtures/{github,hn,arxiv}.json` (nowe, 3–6 pozycji), log `[OFFLINE] <scout>: fixture`. Błąd sieci → bez zmian (`[WARN]`, `[]`). |
| Gemini/Groq/CF AI | `free_ai_router.py` | bez zmian; `ask_free_ai` przy braku klucza loguje raz na cykl `[MOCK] AI: brak klucza, writery używają szablonów`. |
| Webhook/Telegram/LinkedIn | `social_publisher.py` | `load_accounts_config` zastąpione `resolve_channel_modes()` → `{"webhook":"live|dry_run", ...}` per kanał przez `channel_live`; globalne `mode` = `live` tylko gdy ≥1 kanał live. Każdy pominięty kanał → `log_skip`. |
| Brevo/Resend | `newsletter_agent.py` | dry-run zapisuje `queue/<paczka>/NEWSLETTER_PREVIEW.html` (zamiast globalnego `queue/last_newsletter_batch.html`, który zostaje nietknięty). |
| CMS GitHub/WP/webhook | `cms_connector.py` | wywoływany tylko z `publish.py` dla paczek `approved`; w dry-run `log_skip`, status `DRY_RUN_SKIPPED`. |
| IndexNow | `indexnow.py` | usunięty domyślny `ai_brand_agent_key`; brak klucza lub dry-run → `log_skip`, return `{"status":"SKIPPED"}`. |
| Supabase | `db/supabase_client.py` | bez kluczy SQLite (jak dziś). Zapis do Supabase nie jest blokowany przez `DRY_RUN` (to własna baza, nie platforma zewnętrzna wobec odbiorców). |

## 2. Etyka i bramka akceptacji
- Usunąć `agents/anti_ban_commenter.py` (nieimportowany). Nowy `agents/reply_drafter.py`: `draft_reply(comment_text, context, persona) -> dict` zwraca `{"draft": str, "status": "pending_approval"}` (AI lub szablon), bez opóźnień. Nie jest wołany przez engine (brak źródła komentarzy) — dostępny dla `approve.py` w przyszłości.
- `engine.py`: usunąć „Anti-Ban” z docstringu (pracownik #10 → „Kolejka akceptacji człowieka”), sekcja w `3_TWITTER_THREAD.md` → `### Link do dodania ręcznie (opcjonalnie w komentarzu):`; `scheduled_for = now_dt.isoformat()`, `status = "pending_approval"`; usunąć `import random` jeśli nieużywany. Pełna lista literałów do usunięcia/zmiany (kryterium etyczne): `engine.py:101` wiersz dashboardu „(Strateg X + Anti-Ban)” → „(Strateg X)”; `engine.py:184` komentarz „Employee #10 — Anti-Ban Guard” → „#10 — Kolejka akceptacji człowieka”; `engine.py:198` „Anti-Ban 1st Comment”; `agents/geo_seo_engine.py:45` („ochrony anti-ban”) i `:243` („Anti-Ban Guard”) → neutralne opisy; `db/schema.sql:33` komentarz „Anti-Ban!” usunięty (kolumna `followup_comment` zostaje jako zwykły szkic do ręcznego użycia); `agents/writers/github_writer.py:52` domyślny token `"twoj_sekretny_klucz_wlasciciela"` → `os.environ.get("CMS_API_KEY", "")`, a pusta wartość w wygenerowanym snippecie → odmowa 401. Implementujący dodatkowo robi `grep -riE "anti.?ban|jitter|human.?delay|START"` po `*.py`, `*.js`, `*.sql`, `*.md` (poza `queue/`, `public/articles/`, `.agents/`) i usuwa resztę trafień w kodzie/dokumentacji.
- `community_writer.py` sekcja 3: zamiast „skomentuj START” → zaproszenie do grupy z linkiem i pytaniem otwartym do dyskusji; bez auto-DM.
- `outreach_writer.py`: nagłówek „Szablony do ręcznego, spersonalizowanego kontaktu (1:1). Pisz tylko do osób, z którymi masz relację lub uzasadniony interes; zawsze dodaj zdanie o możliwości rezygnacji.” Usunąć „15–20 dziennie”. Zostaje generowanie pliku `10_B2B_OUTREACH_SDR.md`.
- `newsletter_agent.py`: usunąć `time.sleep(random.uniform…)`; `get_active_subscribers` filtruje `consent_at IS NOT NULL AND unsubscribed_at IS NULL`; stopka z `{SITE_URL}/wypisz?email=…` → realizowane jako `mailto:{CONTACT_EMAIL}?subject=Wypisz` (decyzja: brak endpointu wypisu w P0, mailto działa za 0 zł i spełnia obowiązek łatwej rezygnacji; endpoint `/api/unsubscribe` w backlogu). Nadawca z `NEWSLETTER_FROM` (wymagany w live; brak → kanał dry-run).
- `web_generator.py`: zakładka „Kolejka Anti-Ban” → „Do akceptacji” (lista paczek z `APPROVAL.json`), usunąć generator odpowiedzi z jitterem (l.762–815, 1782–1808, 1872–1888) i szablony „START”/„Anti-Ban 1st Comment”/„Cold Email” w `synthesizeBundleForProject` (zastąpić tymi samymi nagłówkami co w Pythonie).
- `db/schema.sql`: `comments_queue` — komentarz bez „Human-like delay”, kolumna `reply_at` NULLABLE (nowa instalacja); tabela pozostaje (dane nieużywane).
- `PLAN_ROZWOJU_AGENCI_AI.md`, `README.md`: sekcja „Tarcza…” → „Zasady zgodności” (człowiek zatwierdza każdą publikację, brak maskowania automatyzacji, zgoda na e-mail, brak zmyślonych danych).
- Zmyślone dane: `geo_seo_engine.py:71/91/121` i szablony writerów — zdania z konkretnymi procentami zastąpić sformułowaniami jakościowymi („wiele zespołów zgłasza…”) albo znacznikiem `[UZUPEŁNIJ: własna liczba/źródło]`; usunąć „zweryfikowana platforma”, „Rekomendacja Ekspertów”; ranking: produkt właściciela opisany jako „nasze rozwiązanie (autor artykułu)” — jawne ujawnienie konfliktu interesów. `derive_seo_headline` przestaje zwracać `metric_highlight` z liczbą (zwraca pusty string; writery pomijają pusty).
- Bandit: `db/supabase_client._init_local_db` — seedy z `total_clicks=0, conversions=0, effectiveness_score=1.0`; usunąć UPDATE „legacy zero rows”. `analyst_agent.run_nightly_optimization`: usunąć `random.randint(10,45)`; kliknięcia tylko z `content_pipeline.clicks`; brak danych → score 1.0 i raport z dopiskiem „brak realnych danych o kliknięciach”. Istniejących wierszy w lokalnej bazie nie kasujemy (ignorowany plik użytkownika) — `python -m agents.analyst_agent --reset-stats --yes` (bez `--yes` → komunikat i exit 2) zeruje statystyki bandyty.
- Subskrybenci: po migracji istniejące wiersze `subscribers` mają `consent_at NULL`, więc newsletter nie trafi do nikogo, dopóki subskrybent nie zapisze się ponownie ze zgodą. Istniejących subskrybentów bez udokumentowanej zgody nie migrujemy automatycznie — zapisane w README (sekcja „Zasady zgodności”).
- `agents/cloudflare_ai.py`: implementujący sprawdza, że bez `CF_ACCOUNT_ID`/`CF_API_TOKEN` funkcja zwraca `""` przed `urlopen`; jeśli nie — dodaje guard na początku (wymagane dla kryterium „zero żądań zapisu/AI bez kluczy”).

### Format `queue/<paczka>/APPROVAL.json`
```json
{"status":"pending_approval","tenant_id":"default","project_id":"proj_autonoma_os",
 "created_at":"ISO","decided_at":null,"decided_by":null,"note":"",
 "items":{"website_article":"pending","linkedin":"pending","newsletter":"pending","webhook":"pending","telegram":"pending"},
 "published":{}}
```
Statusy paczki: `pending_approval` → `approved` | `rejected`; `published` wypełnia `publish.py` (kanał → `{status, at}`). Starsze paczki bez `APPROVAL.json` są traktowane przez `approve.py list` jako `legacy` i nigdy nie publikowane automatycznie (można je zatwierdzić ręcznie — wtedy plik jest tworzony). Właścicielem niezmiennika „nic nie wychodzi bez approved” jest `publish.py` (jedyne miejsce wołające sendery i `publish_article_to_website`). Dziś engine robi to w każdym cyklu (`engine.py:163-170` CMS + IndexNow, `engine.py:221` → `dispatch_content_bundle` → `send_newsletter_batch`, `social_publisher.py:194-199`) — zmiany usuwające to są wypisane w sekcji 3 („Zmiany w engine.py”). Po zmianie engine wywołuje `dispatch_content_bundle(topic, bundle, queue_dir, dry_run_only=True)`, który tylko zapisuje `7_API_PAYLOAD_READY.json` i `PUBLISH_STATUS.json` (`mode: "dry_run"`, kanały `AWAITING_APPROVAL`) — zachowuje pliki z baseline.

### `approve.py` (nowy, root)
`list [--status S]`, `show <paczka>`, `approve <paczka> [--only website_article,linkedin] [--note]`, `reject <paczka> [--note]`. `<paczka>` = nazwa folderu lub unikalny prefiks. Błędy: nieistniejąca/niejednoznaczna paczka → stderr + exit 2; uszkodzony JSON → stderr `[ERROR]` + exit 3 (bez nadpisywania). Jedna reguła strony własnej: `approve` dla `website_article` kopiuje do `public/` wtedy i tylko wtedy, gdy `load_tenant(approval["tenant_id"])["is_owner"] is True` (ustawień CMS, w tym `gh_path_prefix`, nie sprawdzamy). Dla tenanta z `is_owner: false` `website_article` zostaje `approved` i publikuje go `publish.py` przez `cms_connector`. Dla właściciela approve: kopiuje `0_WEBSITE_SEO_ARTICLE.md` do `public/articles/<slug>.md` (istniejący plik o tym samym slugu → dopisek `-2`, `-3`; nigdy nie nadpisuje), regeneruje `public/sitemap.xml`, `public/llms.txt` (marka tenanta default), listę artykułów w `public/blog.html` (blok między `<!-- ARTICLES:START -->` i `<!-- ARTICLES:END -->`), archiwum `public/newsletter/<YYYY-MM-DD>-<slug>.html` z `4_NEWSLETTER_EDITION.md`. To operacje lokalne — dozwolone w dry-run. Po kopiowaniu approve ustawia `published.website_article = {"status":"ok","via":"approve","at":ISO}`, więc `publish.py` go nie publikuje drugi raz. Commit/push robi użytkownik lub CI.

### `publish.py` (nowy, root)
Iteruje paczki `approved`, dla każdego zatwierdzonego kanału, który nie ma `published[kanał].status == "ok"`: wywołuje sender wg tabeli. W `social_publisher.py` z obecnego `dispatch_content_bundle` wydzielamy funkcje `_post_linkedin(text, cfg) -> dict`, `_post_webhook(payload, cfg) -> dict`, `_post_telegram(text, cfg) -> dict` (każda zwraca `{"status":"ok"|"error:<msg>"}`); `dispatch_content_bundle` zostaje cienką nakładką na nie (dla zgodności), a `publish.py` woła je bezpośrednio.

| item | funkcja | wejście z paczki | warunek live (inaczej `DRY_RUN_SKIPPED` + `log_skip`) |
|---|---|---|---|
| website_article | owner (`is_owner`): brak — zrobione w approve (`via:"approve"`); non-owner: `cms_connector.publish_article_to_website(geo_res, project)` + `indexnow.submit_to_indexnow(url)` | `0_WEBSITE_SEO_ARTICLE.md` | `channel_live` dla kluczy wybranego `CMS_TYPE` (`CMS_GH_TOKEN` / `WP_APP_PASSWORD` / `CMS_WEBHOOK_URL`) oraz `CMS_OWNER_AUTHORIZED=true`; IndexNow dodatkowo `INDEXNOW_KEY` |
| linkedin | `social_publisher._post_linkedin` | `1_LINKEDIN_POST.md` | `channel_live("LINKEDIN_ACCESS_TOKEN","LINKEDIN_AUTHOR_URN")` |
| webhook | `social_publisher._post_webhook` | `7_API_PAYLOAD_READY.json` | `channel_live("WEBHOOK_URL")` |
| telegram | `social_publisher._post_telegram` | podsumowanie: temat + lista plików paczki | `channel_live("TELEGRAM_BOT_TOKEN","TELEGRAM_CHAT_ID")` |
| newsletter | `newsletter_agent.send_newsletter_batch(subject, html, sender_email=NEWSLETTER_FROM)` | `4_NEWSLETTER_EDITION.md` → HTML + stopka wypisu | (`channel_live("BREVO_API_KEY","NEWSLETTER_FROM")` lub `channel_live("RESEND_API_KEY","NEWSLETTER_FROM")`) |

Wynik per kanał: `ok` | `DRY_RUN_SKIPPED` | `error:<msg>`. Błędy HTTP/sieci są odwracalne: zapis `error`, log `[ERROR] publish <paczka>/<kanał>: <msg>`, kontynuacja; ponowne uruchomienie ponawia. Exit 0, chyba że wszystkie próby live padły (exit 1).

## 3. Pipeline i writery
- Wszystkie 8 writerów: sygnatura `generate_x(topic, persona, project=None, brand=None)`; `profile = project or load_product_profile()` (wsteczna kompatybilność). `brand` = persona tenanta (dict z `persona.json`): prompt AI dostaje `tone_of_voice.style`, `rules`, `content_pillars`, `target_audience`; szablony używają `brand["name"]` w podpisie i `brand["tone_of_voice"]["style"]` w CTA. Wspólny helper `agents/writers/_common.py`: `resolve_profile(project)`, `brand_prompt(brand) -> str`.
- Zmiany w `engine.py` (wyszukiwać po treści, numery linii orientacyjne): (a) usunąć `engine.py:165-170` — wywołania `publish_article_to_website` i `submit_to_indexnow`; zostaje `geo_res = generate_geo_article(primary_topic, project, write_public=False)` i zapis do `queue/`; (b) `social_publisher.dispatch_content_bundle(topic, bundle, queue_dir, dry_run_only: bool = False)` — przy `dry_run_only=True` zapisuje `7_API_PAYLOAD_READY.json` i `PUBLISH_STATUS.json` (`mode:"dry_run"`, kanały `AWAITING_APPROVAL`) i zwraca wynik przed jakimkolwiek senderem, także przed gałęzią newslettera; (c) `engine.py:221` woła ją z `dry_run_only=True`; (d) zapis `APPROVAL.json` do paczki.
- `engine.py`: usunąć zapis `saas_core/product_profile.json`; przekazywać `project`, `brand=load_tenant(project.tenant_id)["persona"]`. Pętla projektów w `try/except Exception` → `[ERROR] Projekt <id>: <exc>` + traceback do `logs/engine.log` (append, utf-8); exit code: 1 gdy 0 sukcesów, inaczej 0 (`sys.exit` w `__main__`).
- `geo_seo_engine.generate_geo_article(topic, profile, write_public=False)`: przy `False` nie zapisuje do `public/articles/` ani `llms.txt`; zwraca markdown (zapis do queue robi engine — już tak jest). `generate_llms_txt` wołane tylko z `approve.py` i `web_generator.build_public_site` z danymi tenanta default.
- `slugify`: engine używa `agents.geo_seo_engine.slugify` dla slugów artykułów; slug folderu w `queue/` zostaje bez zmian (engine.slugify, 40 znaków) — zachowanie nazewnictwa.
- `run_daemon.py`: aktualizacja `now` po cyklu, obsługa `SIGTERM`/`KeyboardInterrupt` (czyste wyjście). Drobne.

## 4. Strona publiczna i formularz leadów
### Podział plików
`web_generator.build_web_dashboard()` zapisuje panel do `admin/index.html` i `admin/data.json` (nowy katalog; dodany do `.gitignore`? — nie: zawiera tylko wygenerowane dane bez sekretów, ale nie jest deployowany, bo Pages deployuje `public/`). Nowa funkcja `build_public_site()` generuje `public/index.html` (oferta) z `tenants/default/offer.json` + persona, `public/sitemap.xml`, `public/robots.txt`. Wywoływana z engine po panelu. `public/data.json` — usunięcie pliku z deployu: generator przestaje go pisać; istniejący plik nadpisujemy zawartością publiczną `{"brand":…, "articles":[…]}` (bez CMS/pipeline). `local_server.py` serwuje `/admin/*` z `admin/` (tylko localhost).

### Konspekt oferty (`public/index.html`, generowany; treść z `offer.json`)
1. Hero: imię/marka, jedno zdanie wartości („Wdrażam agentów AI, którzy piszą i dystrybuują Twoje treści eksperckie — Ty zatwierdzasz jednym kliknięciem”), CTA „Umów bezpłatną 30-min konsultację” → `#kontakt`, drugie CTA „Zobacz przykłady” → `/blog.html`.
2. Problem → rozwiązanie (3 punkty).
3. Usługi (karty, ceny „od”, z `offer.json`): Audyt marki i treści (od 490 zł), Wdrożenie systemu agentów treści (od 2 900 zł), Abonament „Content Ops” (od 1 200 zł/mies.).
4. Jak pracuję: konsultacja → audyt → wdrożenie → raport miesięczny.
5. Dowody: link do bloga/artykułów; miejsce na case studies (`offer.json.case_studies`, pusta lista → sekcja ukryta; bez zmyślonych opinii).
6. FAQ (4–6 pytań: koszty narzędzi 0 zł, kto zatwierdza treści, RODO, czas wdrożenia).
7. Formularz `#kontakt` + link do polityki prywatności; stopka z e-mailem kontaktowym.
`<html lang="pl">`, meta description, OG, JSON-LD `Person` + `Service` (bez ocen/opinii).

### Formularz (HTML, vanilla JS)
Pola: `name`, `email`, `company`, `service` (select: `audyt|wdrozenie|abonament|inne`), `message`, `consent` (checkbox, tekst: „Wyrażam zgodę na kontakt w sprawie mojego zapytania. Administratorem danych jest … Szczegóły: polityka prywatności.”), ukryte: `website` (honeypot, CSS off-screen, `tabindex=-1`, `autocomplete=off`), `ts` (Date.now() przy renderze), `utm_source/medium/campaign` z `location.search`. `fetch('/api/lead', {method:'POST', JSON})`. Odpowiedzi: 200 → komunikat sukcesu w `role="status" aria-live="polite"`; 400 → błędy przy polach (`aria-invalid`, `aria-describedby`); 503 z `fallback:"mailto"` lub błąd sieci → komunikat i link `mailto:CONTACT_EMAIL` z wypełnionym tematem/treścią. `CONTACT_EMAIL` wstrzyknięty przez generator z `offer.json.contact_email`. Ten sam formularz w `public/blog.html` (zastępuje zapis do `localStorage`; usunąć `autonoma_captured_leads`).

### `functions/api/lead.js` (nowy, Pages Function)
- `onRequestPost({request, env})`; inne metody → 405. Same-origin, brak CORS `*`: `const o = request.headers.get("Origin"); if (o && new URL(o).host !== new URL(request.url).host) return 403;` (nieparsowalny `Origin` → 403). Brak `Origin` → przepuszczamy (walidacja i honeypot nadal działają). `SITE_URL` nie bierze udziału w tej kontroli, więc podglądy `*.pages.dev`, `www` i ukośniki nie blokują leadów.
- `Content-Length` > 8192 lub body > 8192 → 413. Nie-JSON → 400 `{ok:false, errors:{_:"invalid_json"}}`.
- Honeypot `website` niepusty lub `Date.now() - ts < 3000` lub `ts` nie liczba → 200 `{ok:true}` bez zapisu (cicha odmowa, by nie uczyć botów); `console.log("lead_spam", reason)`.
- Walidacja (trim): `email` wymagany, ≤254, regex `^[^\s@]+@[^\s@]+\.[^\s@]{2,}$`; `name` wymagany 1–100; `company` ≤150; `message` ≤2000; `service` ∈ lista lub pusty; `consent === true`; `utm_*` ≤100. Usunięcie znaków kontrolnych. Błędy → 400 `{ok:false, errors:{pole:kod}}`.
- Zapis: jeśli `env.SUPABASE_URL` i `env.SUPABASE_ANON_KEY` → `POST {SUPABASE_URL}/rest/v1/leads` z `apikey`, `Authorization: Bearer`, `Prefer: return=minimal`, body `{tenant_id: env.TENANT_ID||"default", name, email, company, service_interest, message, source_utm, consent_at: now, consent_text_version: "v1", status:"new"}`. 2xx → 200 `{ok:true}`. Błąd Supabase (non-2xx/timeout 5 s przez AbortController) → 502 `{ok:false, fallback:"mailto"}`, `console.error("lead_store_failed", status)` (bez danych osobowych w logu). Brak konfiguracji → 503 `{ok:false, fallback:"mailto"}`.
- Opcjonalne powiadomienie: jeśli `env.TELEGRAM_BOT_TOKEN` i `env.TELEGRAM_CHAT_ID` → `sendMessage` „Nowy lead: <name>, <service>” (bez e-maila), błąd ignorowany z `console.error`. To jedyne live-wywołanie niezależne od `DRY_RUN` — Pages działa w produkcji; brak kluczy = pominięte.
- Rate limiting: poza honeypotem i pułapką czasową brak (darmowe Pages nie mają stanu; Cloudflare WAF free rule opisany w dokumentacji jako opcja ręczna). Ryzyko akceptowane.
- Logika walidacji w `functions/api/_lead_validate.js` (eksport czystej funkcji `validateLead(body, now)`), testowalna `node --test tests/js/lead.test.mjs` gdy Node jest dostępny (CI: `actions/setup-node` jest darmowe — krok opcjonalny).

### Lokalnie: `local_server.py`
- Bind `127.0.0.1` (zmienna `LOCAL_BIND`, domyślnie 127.0.0.1). CORS `*` usunięty (same-origin).
- `POST /api/lead`: ta sama walidacja w Pythonie (`crm/validation.py: validate_lead(dict, now_ms) -> (clean, errors)`), zapis `db.insert_lead()` do SQLite (lub Supabase, gdy klucze). Odpowiedzi jak w Pages.
- `/api/load-keys` → wartości maskowane (`abcd…wxyz` lub `***` gdy <8 znaków) + `set: bool`. `/api/save-keys` → merge z istniejącym `.env` (zachowanie nieznanych kluczy, pusta wartość = bez zmiany). Usunąć wzmiankę o `/api/run-engine` z docstringu.
- `/admin/` → pliki z `admin/`.

### Bezpieczeństwo `/api/ai-generate`
`functions/api/ai-generate.js` i `src/index.js`: wymagany nagłówek `X-Admin-Token` == `env.ADMIN_TOKEN`; brak `ADMIN_TOKEN` w env → 503 `{error:"disabled"}`; zły token → 401. `env.AI` niezdefiniowane → 503 `{error:"ai_binding_missing"}` zamiast 500. Panel admina (lokalny) wysyła token z pola w UI (przechowywany w `sessionStorage`). Wywołania Gemini z kluczem w URL w JS panelu — panel jest teraz tylko lokalny, więc zostają (backlog: przenieść przez `local_server`).

### Polityka prywatności, robots, sitemap
`public/polityka-prywatnosci.html` (statyczny, generowany z `offer.json`: administrator, cel — odpowiedź na zapytanie, podstawa art. 6 ust. 1 lit. a/b RODO, odbiorcy — Supabase (hosting UE, region wybrany przy zakładaniu projektu), czas przechowywania 24 mies. od ostatniego kontaktu, prawa, kontakt). Placeholdery `[UZUPEŁNIJ]` dla danych administratora. `robots.txt`: `Allow: /`, `Sitemap: {SITE_URL}/sitemap.xml`. `sitemap.xml`: `/`, `/blog.html`, `/polityka-prywatnosci.html`, wszystkie `public/articles/*.md` jako `/articles/<slug>` (zgodnie z obecnym linkowaniem w blog.html).

## 5. Baza danych
### Supabase — `db/migrations/002_leads_tenants.sql` (nowy) + aktualizacja `db/schema.sql` (świeże instalacje)
```sql
CREATE TABLE IF NOT EXISTS tenants (
  id TEXT PRIMARY KEY, display_name TEXT NOT NULL, plan TEXT DEFAULT 'owner',
  status TEXT DEFAULT 'active' CHECK (status IN ('active','trial','paused','cancelled')),
  config JSONB DEFAULT '{}'::jsonb, created_at TIMESTAMPTZ DEFAULT NOW());
INSERT INTO tenants (id, display_name) VALUES ('default','Marka właściciela') ON CONFLICT DO NOTHING;

CREATE TABLE IF NOT EXISTS leads (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id TEXT NOT NULL DEFAULT 'default' REFERENCES tenants(id),
  name TEXT NOT NULL CHECK (char_length(name) BETWEEN 1 AND 100),
  email TEXT NOT NULL CHECK (char_length(email) <= 254),
  company TEXT CHECK (char_length(company) <= 150),
  service_interest TEXT, message TEXT CHECK (char_length(message) <= 2000),
  source_utm TEXT, consent_at TIMESTAMPTZ NOT NULL, consent_text_version TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'new' CHECK (status IN ('new','contacted','qualified','proposal','won','lost')),
  value_pln NUMERIC(10,2), next_action TEXT, next_action_at TIMESTAMPTZ, notes TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(), updated_at TIMESTAMPTZ DEFAULT NOW());
CREATE INDEX IF NOT EXISTS idx_leads_tenant_status ON leads(tenant_id, status);

CREATE TABLE IF NOT EXISTS lead_events (
  id BIGSERIAL PRIMARY KEY, lead_id UUID REFERENCES leads(id) ON DELETE CASCADE,
  event TEXT NOT NULL, from_status TEXT, to_status TEXT, note TEXT, created_at TIMESTAMPTZ DEFAULT NOW());

ALTER TABLE leads ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS leads_anon_insert ON leads;
CREATE POLICY leads_anon_insert ON leads FOR INSERT TO anon
  WITH CHECK (tenant_id = 'default' AND status = 'new' AND consent_at IS NOT NULL AND value_pln IS NULL AND notes IS NULL);
-- brak SELECT/UPDATE dla anon; odczyt przez service key (tylko lokalnie w leads.py sync)
ALTER TABLE lead_events ENABLE ROW LEVEL SECURITY;  -- brak polityk dla anon
ALTER TABLE subscribers ADD COLUMN IF NOT EXISTS consent_at TIMESTAMPTZ;
ALTER TABLE subscribers ADD COLUMN IF NOT EXISTS unsubscribed_at TIMESTAMPTZ;
ALTER TABLE subscribers ADD COLUMN IF NOT EXISTS tenant_id TEXT DEFAULT 'default';
ALTER TABLE projects ADD COLUMN IF NOT EXISTS tenant_id TEXT DEFAULT 'default';
ALTER TABLE content_pipeline ADD COLUMN IF NOT EXISTS tenant_id TEXT DEFAULT 'default';
ALTER TABLE content_pipeline ALTER COLUMN id DROP DEFAULT, ALTER COLUMN id TYPE TEXT USING id::text;
```
Ostatnia linia naprawia niezgodność UUID vs tekstowe ID z audytu. Niezmienniki statusu i długości egzekwuje baza (CHECK) — jedyna warstwa, przez którą przechodzą wszystkie zapisy (Pages, local_server, CLI); walidacja w aplikacji daje przyjazne komunikaty. `SUPABASE_KEY` (service role) używany wyłącznie lokalnie/CI przez Pythona, nigdy w `public/` ani w Pages Functions.

### SQLite — `db/supabase_client._init_local_db`
Te same tabele z typami TEXT/INTEGER/REAL, `id` leadów = `uuid.uuid4().hex`, CHECK-i identyczne. Kolumny dla istniejących tabel dodawane przez `PRAGMA table_info` + `ALTER TABLE ADD COLUMN` (idempotentnie). Nowe metody `SupabaseDB`: `insert_lead(d) -> id`, `list_leads(tenant_id=None, status=None)`, `get_lead(id)`, `update_lead(id, **fields)` (zapisuje `lead_events` przy zmianie statusu, `updated_at`), `add_lead_note(id, note)`, `lead_funnel(tenant_id) -> {status: count, won_value}`, `fetch_remote_leads(since)` (Supabase service key). Zapis do Supabase z fallbackiem do SQLite i `[WARN]` (istniejący wzorzec).

### `leads.py` (nowy, root, argparse)
`add --name --email [--company --service --message --source]` (ręczne leady z networkingu; `consent_text_version="manual"`), `list [--status --tenant]`, `show <id-prefix>`, `update <id> [--status --value --next-action --next-at YYYY-MM-DD]`, `note <id> "tekst"`, `export [--out leads.csv]` (domyślnie `exports/leads_<data>.csv`, `exports/` w `.gitignore` — dane osobowe nie trafiają do repo), `sync` (Supabase → SQLite, dedup po `id`; wymaga `SUPABASE_URL` i `SUPABASE_KEY` (service role) — sam anon key przez RLS zwróciłby pustą listę; bez nich → `[WARN] sync wymaga SUPABASE_KEY (service role)`, exit 0). Walidacja jak w `crm/validation.py`; zły status/e-mail → stderr + exit 2. `DASHBOARD.md` dostaje sekcję „Lejek leadów” z `lead_funnel` (tylko liczby, bez danych osobowych — DASHBOARD jest commitowany).

## 6. Multi-tenant
```
tenants/
  default/
    tenant.json   {"id":"default","display_name":"…","persona_file":"brand_core/persona.json",
                   "offer_file":"tenants/default/offer.json","site_url":"https://twoja-domena.pl",
                   "contact_email":"kontakt@twoja-domena.pl","is_owner":true}
    offer.json    {"headline","subheadline","services":[{"id","name","price_from_pln","unit","bullets"}],
                   "process":[…],"faq":[{"q","a"}],"case_studies":[],"contact_email","privacy":{…}}
  demo/
    tenant.json   {"id":"demo","display_name":"InvoicePulse (demo)","persona_file":"tenants/demo/persona.json","is_owner":false}
    persona.json
```
`saas_core/tenants.py`: `load_tenant(tenant_id) -> {"id","persona","offer","site_url","contact_email","is_owner"}` (ścieżki względem repo, cache w module); `list_tenants()`. Walidacja: `id` regex `^[a-z0-9][a-z0-9-]{0,39}$` (brak → `default`; zły → `ValueError`); brak `tenant.json` dla wskazanego id → `[WARN]` i fallback `default` (nie przerywa cyklu); brak/uszkodzony `persona_file` → persona minimalna `{"name": display_name}` + `[WARN]`. `SITE_URL`/`CONTACT_EMAIL` z env nadpisują wartości tenanta default. W `saas_core/projects.json` dodajemy `"tenant_id": "default"` do `proj_autonoma_os` i `"tenant_id": "demo"` do `proj_demo_client`. Publikacja do `public/` (approve) tylko dla tenanta z `is_owner: true` — niezmiennik egzekwuje `approve.py`, bo to jedyny kod zapisujący do `public/articles/`.

## 7. `.env.example` (śledzony; `.gitignore`: dodać `!.env.example`)
```dotenv
# ===== Tryb pracy =====
DRY_RUN=            # 1 = nic nie wysyłaj; 0 = live tam, gdzie są klucze; puste = auto (dry-run gdy brak kluczy zapisu)
OFFLINE=            # 1 = scouty używają sources/fixtures (bez sieci), np. w testach
SITE_URL=https://twoja-domena.pl        # adres strony (sitemap, llms.txt, linki UTM)
CONTACT_EMAIL=kontakt@twoja-domena.pl   # fallback mailto w formularzu, link wypisu z newslettera
ADMIN_TOKEN=        # dowolny długi losowy ciąg; odblokowuje /api/ai-generate (Pages) i panel admina
# ===== AI (darmowe plany) =====
GEMINI_API_KEY=     # Google AI Studio free tier – generowanie treści przez LLM zamiast szablonów
GROQ_API_KEY=       # Groq free tier – zapasowy LLM (llama-3.3-70b)
CF_ACCOUNT_ID=      # Cloudflare free – Workers AI (10k neuronów/dzień)
CF_API_TOKEN=       # Cloudflare API token z uprawnieniem Workers AI
# ===== Baza (Supabase Free) =====
SUPABASE_URL=       # Supabase Free – zdalna baza zamiast lokalnego SQLite
SUPABASE_KEY=       # service role – TYLKO lokalnie/GitHub Secrets (leads.py sync, engine); nigdy w Pages/public
SUPABASE_ANON_KEY=  # anon – w Cloudflare Pages env dla /api/lead (RLS: tylko INSERT do leads)
TENANT_ID=default   # (Pages env) tenant przypisany leadom ze strony
# ===== Powiadomienia / publikacja (wymagają APPROVED w kolejce) =====
TELEGRAM_BOT_TOKEN= # Telegram (darmowy) – powiadomienia o paczkach i nowych leadach
TELEGRAM_CHAT_ID=
WEBHOOK_URL=        # Make/n8n/Discord webhook (plany free) – przekazanie zatwierdzonych treści
LINKEDIN_ACCESS_TOKEN= # LinkedIn API (darmowe, wymaga aplikacji) – publikacja zatwierdzonego posta
LINKEDIN_AUTHOR_URN=   # urn:li:person:<id>
# ===== Newsletter (tylko subskrybenci ze zgodą) =====
BREVO_API_KEY=      # Brevo free (300 e-maili/dzień)
RESEND_API_KEY=     # Resend free (100 e-maili/dzień) – alternatywa
NEWSLETTER_FROM=    # zweryfikowany adres nadawcy; brak = newsletter w dry-run
# ===== Strona / SEO =====
INDEXNOW_KEY=       # IndexNow (darmowe) – ping wyszukiwarek po publikacji; plik klucza w public/<key>.txt
CMS_OWNER_AUTHORIZED=false  # true = zgoda właściciela na publikację na zewnętrznym CMS
CMS_PUBLISH_MODE=require_approval
CMS_TYPE=github_markdown    # github_markdown | wordpress | webhook
CMS_GH_REPO=        # owner/repo (GitHub free) dla github_markdown
CMS_GH_TOKEN=       # fine-grained PAT z contents:write tylko do tego repo
CMS_GH_PATH=public/articles
WP_SITE_URL=
WP_USERNAME=
WP_APP_PASSWORD=    # WordPress Application Password
CMS_WEBHOOK_URL=
CMS_API_KEY=
LOCAL_BIND=127.0.0.1  # adres local_server.py
```
Usuwamy domyślną wartość `CMS_GH_REPO=JKM872/...`.

## 8. CI, Docker
- `.github/workflows/agent_24_7.yml`: przed engine kroki `python -m compileall -q agents publishers sources db saas_core tracking crm *.py` i `python -m unittest discover -s tests -v`; `env: DRY_RUN: ${{ vars.DRY_RUN || '1' }}` (domyślnie dry-run w CI; użytkownik zmienia zmienną repo); przekazanie brakujących sekretów z audytu B15 + `NEWSLETTER_FROM`, `SITE_URL`. Dodać `publish.py` po engine (publikuje tylko approved). Push zostaje (istniejące zachowanie), `git add` bez `logs/`. Nowy `.github/workflows/ci.yml` na `pull_request`/`push`: compile + unittest + `OFFLINE=1 DRY_RUN=1 python engine.py` w kopii roboczej runnera (bez commitu) + opcjonalny `node --test` (setup-node@v4).
- `.dockerignore`: `.git`, `.env`, `.env.*`, `!.env.example`, `db/*.db`, `config/accounts.local.json`, `__pycache__`, `exports/`, `.agents/`. `Dockerfile`: `RUN useradd -m app && chown -R app /app`, `USER app`, `ENV DRY_RUN=1` jako domyślny.

## 9. Obsługa błędów (podsumowanie)
| Operacja | Awaria | Odwracalna? | Wynik dla wołającego | Log |
|---|---|---|---|---|
| Scout HTTP | timeout/HTTP/JSON | tak | `[]` | `[WARN]` |
| AI router | brak klucza / błąd API | tak | `""` → szablon | `[MOCK]` raz / `[WARN]` |
| Writer/projekt w engine | wyjątek | tak (inne projekty) | wynik pominięty | `[ERROR]` + traceback do `logs/engine.log` |
| Wszystkie projekty padły | — | nie | exit 1 | `[ERROR]` |
| Zapis Supabase (Python) | HTTP/sieć | tak | fallback SQLite | `[WARN]` |
| SQLite | brak zapisu/locked | nie dla operacji | wyjątek do CLI → exit 1 | `[ERROR]` |
| `APPROVAL.json` uszkodzony | JSON | nie automatycznie | approve exit 3; publish pomija paczkę | `[ERROR]` |
| publish kanał | HTTP/sieć | tak (retry przy następnym uruchomieniu) | `error:<msg>` w `published` | `[ERROR]` |
| `/api/lead` | walidacja | tak | 400 z polami | brak (bez PII) |
| `/api/lead` | spam | — | 200 udawany | `console.log` powód |
| `/api/lead` | Supabase down/brak konfiguracji | tak | 502/503 + mailto | `console.error` status |
| Tenant brak/uszkodzony | plik | tak | fallback default / persona minimalna | `[WARN]` |

## 10. Testowalność i plan weryfikacji
Testy jednostkowe (`tests/`, unittest, bez sieci — `urllib.request.urlopen` patchowany `unittest.mock`): `test_runtime.py` (DRY_RUN auto/1/0/zła wartość, `channel_live`), `test_social_modes.py` (kryterium 8, 9), `test_indexnow.py` (7), `test_approval.py` (approve/reject/legacy, brak nadpisania slugu, publish pomija pending — 10, 11; na katalogu tymczasowym przez parametr `base_dir`), `test_lead_validation.py` (`crm/validation.py` — przypadki z kryterium 12), `test_leads_db.py` (SQLite w `:memory:`/tmp: insert, update → event, funnel — 16), `test_tenants.py` (18), `test_public_html.py` (15, 14), `test_ethics_grep.py` (5, 6, 19 — skan plików z wykluczeniami). Integracyjne: `test_engine_dry_run.py` — kopia repo do tmp (wykluczenia jak w audycie), `OFFLINE=1`, `subprocess python engine.py`, asercje kryteriów 1–3 i 17. JS: `tests/js/lead.test.mjs` (opcjonalny).

Kolejność weryfikacji przez implementującego:
1. Przed zmianami: baseline z audytu (sekcja 13) w kopii `%TEMP%` — zapisać listę plików paczki i exit code.
2. Po każdym pakiecie P: `python -m py_compile` wszystkich `.py` poza `queue/`, import wszystkich modułów (lista z audytu + nowe: `agents.runtime`, `agents.reply_drafter`, `saas_core.tenants`, `crm.validation`, `approve`, `publish`, `leads`), `python -m unittest discover -s tests`.
3. Końcowo w kopii: `python engine.py` (z siecią) i `OFFLINE=1 python engine.py` → exit 0, porównanie z baseline (te same pliki + `APPROVAL.json`, brak zmian `saas_core/product_profile.json`, brak nowych `public/articles/`), `approve.py approve` na nowej paczce → artykuł, sitemap, llms.txt; `publish.py` → `DRY_RUN_SKIPPED`.
4. `local_server.py` + ręczny POST `/api/lead` (curl/`Invoke-RestMethod`) → wiersz w SQLite; `/api/load-keys` zamaskowany.
5. HTML: `test_public_html.py`; ręcznie w przeglądarce: nawigacja klawiaturą po formularzu, komunikaty błędów. Pełna zgodność WCAG wymaga testów z czytnikami ekranu — poza automatem.
6. `git status` w repo użytkownika: brak usuniętych plików w `queue/` i `public/articles/`; `git ls-files .env.example` niepusty; brak sekretów (`git grep -nE "AIza|gsk_|ghp_[A-Za-z0-9]{20}"` → 0).

## 11. Poza zakresem (jawnie)
Billing/płatności i faktury (Stripe/Przelewy24), rejestracja/logowanie klientów, panel klienta online, izolacja danych tenantów przez RLS per użytkownik, automatyczne odpowiedzi na komentarze i pobieranie komentarzy, publikacja X/GitHub, endpoint `/api/unsubscribe` i double opt-in (backlog P2 — dziś mailto), realne śledzenie kliknięć (`increment_click`, tracker.js — backlog), usunięcie Workera/`workers-site/`, refaktor JS panelu admina, przepisanie `web_generator.py`.

## Uwagi do przeglądu
Iteracja 2 — odpowiedzi na `design-review.json` (iteracja 1, CHANGES_REQUESTED):
1. MEDIUM engine publikuje CMS/IndexNow/newsletter — ROZWIĄZANE: usunięto fałszywe twierdzenie; sekcja 3 „Zmiany w engine.py” (a)–(d), sygnatura `dispatch_content_bundle(..., dry_run_only=False)`.
2. MEDIUM sprzeczna reguła approve — ROZWIĄZANE: jedyna reguła `is_owner is True`, bez sprawdzania CMS.
3. MEDIUM mapowanie publish.py — ROZWIĄZANE: tabela kanał → funkcja → wejście → warunek live, nazwy wydzielonych funkcji `_post_linkedin/_post_webhook/_post_telegram`, `via:"approve"` dla właściciela.
4. MEDIUM Origin — ROZWIĄZANE: porównanie z hostem żądania, brak Origin przepuszczany, bez `SITE_URL`.
5. MEDIUM lista literałów — ROZWIĄZANE: dopisano engine.py:101/184, geo_seo_engine.py:45/243, schema.sql:33, github_writer.py:52 (+ grep kontrolny).
6. NIT sync — ROZWIĄZANE: wymaga `SUPABASE_KEY`, inaczej `[WARN]`, exit 0.
7. NIT polityka — ROZWIĄZANE: `DROP POLICY IF EXISTS` + `tenant_id = 'default'`.
8. NIT subskrybenci — ROZWIĄZANE: udokumentowane (sekcja 2 + README).
9. NIT reset-stats — ROZWIĄZANE: przeniesione do `python -m agents.analyst_agent --reset-stats --yes`.
Niezweryfikowane założenia z przeglądu: guard w `cloudflare_ai.py` dopisany jako obowiązek implementującego; numery linii `web_generator.py` — wyszukiwanie po treści (dopisane).
