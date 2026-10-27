# Wymagania — „Ratunek” i produktyzacja Autonoma AI (mysterious-darwin)

## Podsumowanie
Projekt to system agentów AI w czystym Pythonie (stdlib), który generuje treści marki osobistej (SEO/GEO, social, newsletter, outreach). Celem jest zamiana go w działające narzędzie zarabiające: niezawodny pipeline bez kluczy API, publiczna strona z ofertą i formularzem leadów, prosty CRM leadów, fundament multi-tenant pod przyszły płatny SaaS oraz strategia monetyzacji. Budżet 0 zł — tylko darmowe plany. Wszystkie zmiany są przyrostowe; zachowanie z audytu (`audit.md`, sekcja 13) musi zostać zachowane.

Założenia (wywnioskowane, do potwierdzenia w przeglądzie):
- Z1. Właściciel sprzedaje teraz usługi (wdrożenia agentów AI / content marketing), a SaaS dopiero później. Strona publiczna promuje właściciela, nie fikcyjny produkt.
- Z2. Wdrożeniem strony jest Cloudflare Pages (`functions/`); Worker (`src/index.js`) zostaje bez zmian funkcjonalnych.
- Z3. „Publikacja” na własnej stronie = skopiowanie zatwierdzonego artykułu do `public/articles/` w repo (deploy robi Cloudflare Pages po pushu). Bez akceptacji człowieka nic nie trafia publicznie.
- Z4. Język treści i UI: polski.

## Wymagania funkcjonalne

### R-DRY: Tryb bez kluczy (dry-run)
- R-DRY-1. Jeden przełącznik `DRY_RUN` (`1`/`0`/brak). Brak zmiennej = auto: dry-run, gdy nie skonfigurowano żadnego klucza zapisu (publikacja/wysyłka). `DRY_RUN=1` wymusza dry-run nawet z kluczami.
- R-DRY-2. Każde wywołanie zewnętrzne, które coś zapisuje/wysyła (webhook, Telegram, LinkedIn, Brevo, Resend, IndexNow, CMS GitHub/WP/webhook, Supabase write), w dry-run jest pomijane i loguje jedną linię `[DRY_RUN] <usługa>: <akcja> pominięta`.
- R-DRY-3. Zmienna `OFFLINE=1` sprawia, że scouty (GitHub/HN/arXiv) używają lokalnych fixture'ów zamiast sieci i logują `[OFFLINE]`.
- R-DRY-4. Wywołania AI bez klucza logują `[MOCK] AI: użyto szablonu (<writer>)`.
- R-DRY-5. IndexNow nigdy nie wysyła żądania bez skonfigurowanego `INDEXNOW_KEY` (usunięty domyślny klucz).
- R-DRY-6. Pojedynczy klucz kanału nie przełącza innych kanałów w tryb live — tryb live jest per kanał i tylko gdy `DRY_RUN` nie jest wymuszony.
- R-DRY-7. `.env.example` jest śledzony przez git (poprawka `.gitignore`) i dokumentuje każdy klucz: nazwę, darmowy plan, co odblokowuje. Brak realnych wartości.

### R-ETH: Etyka i zgodność z platformami
- R-ETH-1. `agents/anti_ban_commenter.py` usunięty; zastąpiony `agents/reply_drafter.py`, który tylko tworzy szkic odpowiedzi do kolejki akceptacji (bez opóźnień maskujących, bez godzin „aktywności”).
- R-ETH-2. Usunięty losowy jitter `randint(18,95)` z `engine.py`; nazewnictwo „Anti-Ban” usunięte z kodu, UI, DASHBOARD i dokumentacji.
- R-ETH-3. Usunięta mechanika „skomentuj START” / auto-DM / „Human-Delay” z `community_writer.py` i `web_generator.py`.
- R-ETH-4. Outreach to wyłącznie szablony do ręcznego, indywidualnego użycia; bez limitów „N dziennie”, z informacją o podstawie (uzasadniony interes / zgoda) i możliwością rezygnacji; brak kodu wysyłającego masowo DM/cold e-mail.
- R-ETH-5. Newsletter: brak `time.sleep(random…)`; wysyłka tylko do subskrybentów z `consent_at` i bez `unsubscribed_at`; każdy e-mail zawiera link wypisu.
- R-ETH-6. Każda publikacja/wysyłka zewnętrzna wymaga statusu `approved` w `queue/<paczka>/APPROVAL.json` nadanego przez człowieka (CLI). Domyślny status nowej paczki: `pending_approval`.
- R-ETH-7. Usunięte zmyślone statystyki z treści publicznych (`geo_seo_engine.py`, szablony writerów) i fikcyjne seedy kliknięć/konwersji w bazie; bandit startuje neutralnie (wszystkie score 1.0, liczniki 0 dla nowych baz).
- R-ETH-8. Sekcja „Tarcza bezpieczeństwa / nie dostaniesz bana” w `PLAN_ROZWOJU_AGENCI_AI.md` i README zastąpiona opisem zasad zgodności.

### R-PIPE (a): Niezawodny pipeline end-to-end bez kluczy
- R-PIPE-1. `python engine.py` bez kluczy: scan → curate → write → queue kończy się exit 0, tworzy paczkę per aktywny projekt w `queue/` z `APPROVAL.json` (`pending_approval`).
- R-PIPE-2. Nowe artykuły nie są zapisywane bezpośrednio do `public/articles/` przez generator; trafiają do paczki w `queue/`. Istniejące pliki w `public/articles/` pozostają.
- R-PIPE-3. `python approve.py list|show|approve|reject <paczka>` zarządza akceptacją. `approve` dla projektu właściciela publikuje artykuł do `public/articles/`, aktualizuje `public/blog.html`(listę), `public/llms.txt`, `public/sitemap.xml` i archiwum newslettera `public/newsletter/<data>.html`.
- R-PIPE-4. `python publish.py` wysyła do kanałów zewnętrznych tylko paczki `approved` i nieopublikowane; w dry-run tylko loguje i zapisuje `PUBLISH_STATUS.json` ze statusem `DRY_RUN_SKIPPED`.
- R-PIPE-5. Writery otrzymują projekt i personę jawnie (parametr); engine przestaje nadpisywać `saas_core/product_profile.json`.
- R-PIPE-6. `brand_core/persona.json` (persona domyślnego tenanta) wpływa na treści (ton, filary, odbiorcy) w szablonach i promptach.
- R-PIPE-7. `public/llms.txt` opisuje markę właściciela (domyślny tenant), nie ostatni projekt z pętli.
- R-PIPE-8. Awaria jednego projektu nie przerywa cyklu pozostałych (log `[ERROR]` + kontynuacja; exit 0 jeśli ≥1 projekt się udał, exit 1 jeśli wszystkie zawiodły).

### R-LEAD (b): Strona ofertowa i przechwytywanie leadów
- R-LEAD-1. `public/index.html` to strona marki/oferty (kim jestem, usługi z cenami „od”, proces, FAQ, CTA „Umów bezpłatną konsultację”, formularz). Panel admina przeniesiony poza `public/` do `admin/index.html` (serwowany tylko lokalnie).
- R-LEAD-2. Formularz (`public/index.html#kontakt` i `public/blog.html`) wysyła POST do `/api/lead` (Cloudflare Pages Function `functions/api/lead.js`).
- R-LEAD-3. Walidacja po stronie serwera: e-mail (wymagany, ≤254 znaki, format), imię (wymagane, 1–100), firma (opcjonalna, ≤150), wiadomość (opcjonalna, ≤2000), usługa (opcjonalna, z listy dozwolonych), zgoda RODO (wymagana, `true`), UTM (opcjonalne, ≤100 każdy). Body ≤ 8 KB. Błąd → 400 z listą pól.
- R-LEAD-4. Ochrona antyspamowa bez płatnych usług: honeypot (`website` niepuste → 200 udawany sukces, brak zapisu), pułapka czasowa (wysłanie < 3 s od renderu → odrzucenie jako spam, 200 udawany sukces).
- R-LEAD-5. Zapis do Supabase `leads` (anon key + RLS insert-only). Bez konfiguracji Supabase → 503 z `fallback: "mailto"`, a frontend pokazuje link `mailto:` z adresem właściciela (lead nie ginie po cichu). Lokalnie `local_server.py` obsługuje `POST /api/lead` do SQLite.
- R-LEAD-6. `public/polityka-prywatnosci.html`, `public/robots.txt`, `public/sitemap.xml` istnieją. Formularz linkuje politykę.
- R-LEAD-7. `public/data.json` nie zawiera konfiguracji CMS ani danych wewnętrznych (przeniesiony do `admin/data.json`).
- R-LEAD-8. Usunięty zapis leadów do `localStorage` w `blog.html`.

### R-CRM (c): Śledzenie leadów/klientów
- R-CRM-1. Tabele `leads` i `lead_events` w `db/schema.sql` (Supabase) i w SQLite (`_init_local_db`).
- R-CRM-2. Statusy: `new → contacted → qualified → proposal → won | lost`; zmiana statusu zapisuje zdarzenie w `lead_events`.
- R-CRM-3. CLI `python leads.py add|list|show|update|note|export|sync`: `sync` pobiera nowe leady z Supabase do SQLite (gdy klucze są), `export` zapisuje CSV.
- R-CRM-4. `DASHBOARD.md` pokazuje lejek: liczba leadów per status, wartość `won` (PLN), leady z zaległą `next_action_at`.

### R-TEN (d): Fundament multi-tenant
- R-TEN-1. Katalog `tenants/<slug>/` z `tenant.json` (+ opcjonalnie `persona.json`, `offer.json`). Tenant `default` wskazuje na `brand_core/persona.json` (bez duplikacji).
- R-TEN-2. Projekt ma pole `tenant_id` (brak = `default`); engine ładuje personę i ofertę tenanta projektu.
- R-TEN-3. Tabela `tenants` w Supabase i SQLite; kolumna `tenant_id` w `projects`, `content_pipeline`, `leads`.
- R-TEN-4. Paczki w `queue/` i wpisy w bazie zawierają `tenant_id`.
- R-TEN-5. Brak billingu i auth klientów (patrz Poza zakresem).

### R-DOC (e): Strategia monetyzacji
- R-DOC-1. `docs/STRATEGIA_MONETYZACJI.md`: progi cenowe usług (teraz) i SaaS (później), playbook pierwszych klientów (etyczny, opt-in, ręczny), go-to-market za 0 zł, metryki.

### R-KEEP: Zachowanie działania
- R-KEEP-1. Po zmianach baseline z audytu nadal działa: `python engine.py` bez kluczy → exit 0, paczka per aktywny projekt w `queue/` (te same pliki 0–10 + `PUBLISH_STATUS.json` + nowy `APPROVAL.json`), brak zapisów zewnętrznych, aktualizacja `DASHBOARD.md`, raportu i pamięci.
- R-KEEP-2. Nie usuwa się treści w `queue/` ani `public/articles/`.
- R-KEEP-3. Brak nowych zależności (stdlib). Jeśli konieczna — przypięta wersja.
- R-KEEP-4. Supabase → SQLite fallback zachowany.

## Wymagania niefunkcjonalne
- NF-1. Bezpieczeństwo: `local_server.py` nasłuchuje tylko na `127.0.0.1`, `/api/load-keys` zwraca wartości zamaskowane, `/api/save-keys` scala zamiast nadpisywać `.env`. `/api/ai-generate` wymaga nagłówka `X-Admin-Token` równego `ADMIN_TOKEN`.
- NF-2. Brak sekretów w repo; `.dockerignore` wyklucza `.env`, `.git`, `db/*.db`.
- NF-3. Koszt 0 zł: tylko darmowe plany (Supabase Free, Cloudflare Pages/Workers AI free, GitHub Actions, Gemini/Groq free).
- NF-4. Dostępność formularza: etykiety `<label for>`, komunikaty błędów w `aria-live`, obsługa klawiatury.
- NF-5. Testy w `unittest` (stdlib), uruchamiane w CI.

## Kryteria akceptacji
1. Bez `.env` i zmiennych: `DRY_RUN` nieustawiony, `OFFLINE=1 python engine.py` → exit 0, w logu ≥1 linia `[DRY_RUN]` lub `[OFFLINE]`, zero żądań sieciowych (test z podmienionym `urllib.request.urlopen` rzucającym wyjątek).
2. `python engine.py` (z siecią, bez kluczy) → exit 0; każdy nowy folder `queue/…` zawiera pliki z audytu (sekcja 13) oraz `APPROVAL.json` ze `"status": "pending_approval"` i `tenant_id`.
3. Po cyklu `git status` nie pokazuje zmian w `saas_core/product_profile.json` ani nowych plików w `public/articles/`.
4. `git ls-files .env.example` zwraca plik; zawiera wszystkie zmienne z audytu sekcja 8 + `DRY_RUN`, `OFFLINE`, `ADMIN_TOKEN`, `CONTACT_EMAIL`, `SITE_URL`; każda z komentarzem „darmowy plan / odblokowuje”.
5. `agents/anti_ban_commenter.py` nie istnieje; `grep -ri "anti-ban\|anti_ban\|jitter\|human-delay\|skomentuj START"` w `*.py`, `*.js`, `*.html`, `README.md`, `PLAN_ROZWOJU_AGENCI_AI.md` (poza `queue/`, `public/articles/`, `.agents/`) → 0 trafień.
6. `grep -n "randint(18" engine.py` i `time.sleep(random` w `agents/newsletter_agent.py` → 0 trafień.
7. `submit_to_indexnow` bez `INDEXNOW_KEY` nie woła sieci i loguje `[DRY_RUN] IndexNow`.
8. Z ustawionym tylko `BREVO_API_KEY` (fałszywym) i bez `DRY_RUN`: webhook/Telegram/LinkedIn pozostają w dry-run (test jednostkowy na `resolve_channel_modes`).
9. `DRY_RUN=1` + dowolne klucze → `PUBLISH_STATUS.json` ma `"mode": "dry_run"` i brak wywołań sieci.
10. `python publish.py` nie wysyła paczki o statusie `pending_approval` (test).
11. `python approve.py approve <paczka>` dla projektu właściciela tworzy `public/articles/<slug>.md`, dopisuje wpis w `public/sitemap.xml` i aktualizuje `public/llms.txt` opisem marki domyślnego tenanta.
12. `functions/api/lead.js`: testy (Node `node --test`, jeśli Node dostępny; inaczej ręczny `wrangler pages dev`) — brak e-maila → 400; zły e-mail → 400; brak zgody → 400; honeypot wypełniony → 200 bez zapisu; < 3 s → 200 bez zapisu; poprawne dane bez Supabase → 503 `fallback:"mailto"`; body > 8 KB → 413.
13. `local_server.py`: `POST /api/lead` z poprawnymi danymi → rekord w SQLite `leads` ze statusem `new` i `consent_at`; serwer bind `127.0.0.1`; `/api/load-keys` nie zwraca pełnych wartości.
14. `public/index.html` zawiera sekcje: hero z CTA, usługi z cenami „od”, proces, FAQ, formularz `#kontakt`, link do polityki prywatności; nie zawiera pól kluczy API ani słowa „Gemini API Key”. `public/polityka-prywatnosci.html`, `robots.txt`, `sitemap.xml` istnieją.
15. Strony w `public/*.html` przechodzą walidację parsera (`html.parser` bez błędów niezamkniętych tagów — skrypt `tests/test_public_html.py`) i mają `<html lang="pl">`, `<title>`, `<meta name="description">`.
16. `python leads.py add --email a@example.com --name Test` → `list` pokazuje lead; `update <id> --status contacted` dodaje wpis w `lead_events`; `export` tworzy CSV.
17. `DASHBOARD.md` zawiera sekcję „Lejek leadów” z liczbami per status.
18. Projekt bez `tenant_id` jest obsługiwany jako `default`; projekt z `tenant_id: "demo"` używa `tenants/demo/persona.json` (test jednostkowy loadera).
19. Nowa baza SQLite: `agent_strategy` ma `total_clicks = 0` i `conversions = 0` dla wszystkich person; teksty artykułów nie zawierają „64%”, „45% decydentów”, „zweryfikowana platforma”.
20. `python -m py_compile` na wszystkich `.py` (poza `queue/`) i import każdego modułu → 0 błędów; `python -m unittest discover tests` → OK; CI wykonuje te kroki.
21. `docs/STRATEGIA_MONETYZACJI.md` istnieje i zawiera sekcje: cennik usług, progi SaaS, playbook pierwszych klientów, GTM 0 zł, metryki.

## Poza zakresem
- Billing/płatności (Stripe, faktury), rejestracja i logowanie klientów SaaS, panel klienta online.
- Pobieranie komentarzy z platform i automatyczne odpowiedzi.
- Implementacja publikacji na X i GitHub (pozostają kanałami ręcznymi).
- Przepisanie `web_generator.py` od zera, migracja z Worker na inny hosting, usunięcie `src/index.js`.
- Realne śledzenie kliknięć `increment_click` (backlog — wymaga osobnego endpointu).
