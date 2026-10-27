# Plan implementacji — Ratunek i produktyzacja Autonoma AI

Źródła (zatwierdzone): `.agents/tasks/rescue/audit.md`, `requirements.md`, `design.md`, `docs/STRATEGIA_MONETYZACJI.md`. Projekt techniczny jest wiążący — ten plan tylko go sekwencjonuje. Numery linii z audytu są orientacyjne: szukaj po treści.

Katalog repo (dalej `R`): `C:\Users\hp\Documents\antigravity\mysterious-darwin`. Pracujemy bezpośrednio w checkoutcie użytkownika.

## Zasady obowiązujące w KAŻDYM zadaniu
- Zmiany przyrostowe (`str_replace`), żadnych przepisań całych plików od zera (wyjątek: nowe pliki). Nie przepisywać `web_generator.py` — tylko punktowe edycje.
- Nie usuwać ani nie modyfikować niczego w `R\queue\` i `R\public\articles\` (poza dopisywaniem nowych plików przez `approve.py` w testach w katalogu tymczasowym).
- Zero nowych zależności (Python stdlib, vanilla JS). Nigdy nie zapisywać realnych kluczy; `.env` nie tworzyć w repo.
- Dry run przed i po: każde zadanie kończy się „Weryfikacją standardową” (WS) poniżej, poza zadaniami, które mówią inaczej.
- Engine uruchamiamy WYŁĄCZNIE w kopii tymczasowej (komenda `DRYRUN` niżej), żeby nie dopisywać paczek do `queue/` użytkownika.

### Komenda DRYRUN (PowerShell, Windows) — kopia + run bez kluczy
```powershell
$R="C:\Users\hp\Documents\antigravity\mysterious-darwin"; $t="$env:TEMP\md_dry"; if(Test-Path $t){Remove-Item $t -Recurse -Force}
robocopy $R $t /E /XD .git .agents __pycache__ /NFL /NDL /NJH /NJS | Out-Null
Push-Location $t; git init -q; git add -A; git -c user.name=a -c user.email=a@a commit -qm base
Get-ChildItem Env: | ? { $_.Name -match 'KEY|TOKEN|WEBHOOK|SUPABASE|CMS_|LINKEDIN|TELEGRAM|DRY_RUN|OFFLINE' } | % { Remove-Item "Env:$($_.Name)" }
$env:PYTHONIOENCODING="utf-8"; python engine.py *> run.txt; "EXIT=$LASTEXITCODE"
git status --short --untracked-files=all | Out-File status.txt -Encoding utf8; Pop-Location
```
Wariant offline: przed `python engine.py` ustaw `$env:OFFLINE="1"` (dostępny od zadania 3).

### Weryfikacja standardowa (WS)
```powershell
cd C:\Users\hp\Documents\antigravity\mysterious-darwin
Get-ChildItem -Recurse -Filter *.py | ? { $_.FullName -notmatch '\\queue\\|\\.agents\\|__pycache__' } | % { python -m py_compile $_.FullName; if($LASTEXITCODE){"FAIL $($_.FullName)"} }
python -m unittest discover -s tests -v     # od zadania 2
```
+ DRYRUN → `EXIT=0`, porównanie `status.txt` z baseline (`.agents/tasks/rescue/baseline/`), brak `Traceback` w `run.txt`. Po każdym zadaniu `git status --short` w `R` nie pokazuje `D` dla `queue/` ani `public/articles/`.

---

# Zadania (kolejność wg zależności; P0 = krytyczne dla przychodu)

- [ ] 0. BASELINE — uruchomić komendę z audytu §13 (DRYRUN powyżej, przed jakąkolwiek zmianą) i zapisać wynik.
      Zapisać `run.txt`, `status.txt`, exit code oraz listę plików nowych paczek `queue/*` (13 plików/paczkę) do `R\.agents\tasks\rescue\baseline\` (`run.txt`, `status.txt`, `bundle_files.txt`, `exit.txt`). Dodatkowo zapisać wynik py_compile (29 plików) i importów 28 modułów (lista z audytu §14) do `baseline\compile_import.txt`.
      Files: `R\.agents\tasks\rescue\baseline\*` (nowe)
      Verify: `exit.txt` zawiera `0`; `status.txt` zawiera 2 nowe foldery `queue/...` i `M DASHBOARD.md`, `M public/index.html`; `git status` w `R` bez zmian poza `.agents/`.

## P0-1 Etyka i bramka akceptacji

- [ ] 1. Usunąć mechanizmy omijania detekcji / spamu i dodać szkicownik odpowiedzi do ręcznej akceptacji (design §2).
      - Usunąć `R\agents\anti_ban_commenter.py` (nieimportowany); utworzyć `R\agents\reply_drafter.py` z `draft_reply(comment_text, context, persona) -> {"draft", "status":"pending_approval"}` (AI przez `ask_free_ai` gdy `has_live_ai_key()`, inaczej szablon; bez sleep/jitter).
      - `R\engine.py`: docstring #10 → „Kolejka akceptacji człowieka”; wiersz dashboardu „(Strateg X + Anti-Ban)” → „(Strateg X)”; nagłówek w `3_TWITTER_THREAD.md` → `### Link do dodania ręcznie (opcjonalnie w komentarzu):`; `scheduled_for = now_dt.isoformat()`, `status="pending_approval"` w `insert_content`; usunąć `import random` jeśli nieużywany.
      - `R\agents\geo_seo_engine.py` (~l.45, ~l.243) neutralne opisy; `R\db\schema.sql` usunąć komentarze „Anti-Ban!”/„Human-like delay”, `reply_at` NULLABLE.
      - `R\agents\writers\community_writer.py` sekcja 3: zaproszenie do grupy + pytanie otwarte, bez „START”/auto-DM.
      - `R\agents\writers\outreach_writer.py`: nagłówek o ręcznym kontakcie 1:1 z opcją rezygnacji (tekst z design §2), usunąć „15–20 dziennie”.
      - `R\agents\writers\github_writer.py`: domyślny token → `os.environ.get("CMS_API_KEY", "")`, pusty → snippet odmawia 401.
      - `R\agents\newsletter_agent.py`: usunąć `time.sleep(random.uniform…)`; filtr `consent_at IS NOT NULL AND unsubscribed_at IS NULL` (w SQLite kolumny dodaje zadanie 7 — do tego czasu zapytanie musi tolerować brak kolumny: sprawdzić `PRAGMA table_info` i zwrócić `[]`); stopka wypisu `mailto:{CONTACT_EMAIL}?subject=Wypisz`; nadawca z `NEWSLETTER_FROM`.
      - `R\web_generator.py`: zakładka „Kolejka Anti-Ban” → „Do akceptacji”, rola „Strażnik Komentarzy Anti-Ban” → „Kolejka akceptacji”, usunąć generator odpowiedzi z jitterem i „Publikacja (Jitter)”, szablony „START”/„Anti-Ban 1st Comment”/„Cold Email” w `synthesizeBundleForProject` zastąpić nagłówkami jak w Pythonie (edycje punktowe, wyszukiwanie po treści).
      - `R\README.md`, `R\PLAN_ROZWOJU_AGENCI_AI.md`: sekcja „Tarcza…” → „Zasady zgodności” (człowiek zatwierdza każdą publikację, brak maskowania automatyzacji, zgoda na e-mail, brak zmyślonych danych, info o subskrybentach bez `consent_at`).
      - Kontrola: `Select-String -Pattern 'anti.?ban|jitter|human.?delay|\bSTART\b' -Path` po `*.py,*.js,*.sql,*.md` (poza `queue/`, `public/articles/`, `.agents/`) → usunąć resztę trafień w kodzie/dokumentacji (fałszywe trafienia np. `ARTICLES:START` dozwolone).
      Files: jak wyżej
      Verify: WS; DRYRUN exit 0, paczki nadal mają 13 plików; `python -c "import agents.reply_drafter as r; print(r.draft_reply('x','y',{})['status'])"` → `pending_approval`.

- [ ] 2. Dodać moduł runtime i szkielet testów (design §1, §10).
      - Nowy `R\agents\runtime.py`: `WRITE_KEYS`, `is_dry_run()`, `is_offline()`, `log_skip()`, `channel_live(*keys)`; klucze przez `free_ai_router._load_key`; zła wartość `DRY_RUN` → `[WARN] … tryb auto`.
      - `R\agents\cloudflare_ai.py`: guard — brak `CF_ACCOUNT_ID`/`CF_API_TOKEN` → `return ""` przed `urlopen` (sprawdzić, dodać jeśli brak).
      - `R\agents\free_ai_router.py`: jednorazowy log `[MOCK] AI: brak klucza, writery używają szablonów` na proces.
      - Nowe `R\tests\__init__.py`, `R\tests\test_runtime.py` (DRY_RUN auto/1/0/`maybe`, `channel_live`; env patchowany `unittest.mock.patch.dict`, `_load_key` patchowany, by nie czytać `.env`).
      Files: `R\agents\runtime.py`, `R\agents\cloudflare_ai.py`, `R\agents\free_ai_router.py`, `R\tests\*`
      Verify: `python -m unittest discover -s tests -v` → OK; WS.

- [ ] 3. Guardy dry-run we wszystkich zapisach zewnętrznych + fixture offline (design §1).
      - `R\publishers\indexnow.py`: usunąć domyślny `ai_brand_agent_key`; brak klucza lub dry-run → `log_skip`, `{"status":"SKIPPED"}`.
      - `R\publishers\social_publisher.py`: `resolve_channel_modes()` per kanał przez `channel_live`; wydzielić `_post_linkedin(text,cfg)`, `_post_webhook(payload,cfg)`, `_post_telegram(text,cfg)` → `{"status":"ok"|"error:<msg>"}`; `dispatch_content_bundle(topic, bundle, queue_dir, dry_run_only=False)` — przy `True` zapisuje tylko `7_API_PAYLOAD_READY.json` + `PUBLISH_STATUS.json` (`mode:"dry_run"`, kanały `AWAITING_APPROVAL`) i wraca przed senderami i newsletterem.
      - `R\agents\newsletter_agent.py`: dry-run zapisuje `queue/<paczka>/NEWSLETTER_PREVIEW.html` (parametr `queue_dir`), globalny `queue/last_newsletter_batch.html` nietknięty.
      - `R\publishers\cms_connector.py`: `load_cms_permissions` przez `_load_key`; dry-run → `log_skip`, status `DRY_RUN_SKIPPED`.
      - `R\sources\github_scout.py`, `hacker_news_scout.py`, `arxiv_scout.py`: `is_offline()` → `R\sources\fixtures\{github,hn,arxiv}.json` (nowe, 3–6 pozycji w formacie zwracanym przez scouta), log `[OFFLINE] <scout>: fixture`.
      - Testy: `R\tests\test_social_modes.py` (jeden klucz nie włącza innych kanałów; `dry_run_only` nie woła `urlopen`), `R\tests\test_indexnow.py` (brak klucza → SKIPPED, `urlopen` nie wołany).
      Files: jak wyżej
      Verify: unittest OK; WS; DRYRUN z `$env:OFFLINE="1"` → exit 0, w `run.txt` 3× `[OFFLINE]`.

- [ ] 4. Bramka `APPROVAL.json` w engine + `approve.py` + `publish.py` (design §2, §3 „Zmiany w engine.py”).
      Zależy od 3 (dry_run_only, wydzielone sendery) — tenant w tym zadaniu: `"default"` stałe, `is_owner` dla `default`=True, inne=False (helper tymczasowy w `approve.py`; zadanie 9 podmienia go na `saas_core.tenants.load_tenant`).
      - `R\engine.py`: usunąć wywołania `publish_article_to_website` i `submit_to_indexnow`; `generate_geo_article(..., write_public=False)`; `dispatch_content_bundle(..., dry_run_only=True)`; zapis `APPROVAL.json` (format z design §2); pętla projektów w `try/except` → `[ERROR] Projekt <id>: <exc>` + traceback do `R\logs\engine.log` (utf-8, append); `sys.exit(1)` gdy 0 sukcesów.
      - `R\agents\geo_seo_engine.py`: parametr `write_public=False` — przy False brak zapisu do `public/articles/` i `public/llms.txt`.
      - Nowy `R\approve.py` (argparse: `list [--status]`, `show`, `approve [--only] [--note]`, `reject [--note]`, parametr `--base-dir` dla testów; prefiks paczki; exit 2/3 jak w design; legacy bez `APPROVAL.json`). Approve właściciela: kopiuje artykuł do `public/articles/<slug>.md` bez nadpisywania (`-2`, `-3`), regeneruje `public/sitemap.xml`, `public/llms.txt`, blok `<!-- ARTICLES:START -->…<!-- ARTICLES:END -->` w `public/blog.html` (dodać znaczniki wokół obecnej listy, jeśli ich brak), archiwum `public/newsletter/<data>-<slug>.html`; `published.website_article={"status":"ok","via":"approve"}`.
      - Nowy `R\publish.py`: tylko paczki `approved`, kanały wg tabeli design §2, wynik `ok|DRY_RUN_SKIPPED|error:<msg>` zapisywany w `published`; exit 1 tylko gdy wszystkie próby live padły; uszkodzony JSON → `[ERROR]`, paczka pominięta.
      - `R\tests\test_approval.py` (katalog tymczasowy: approve/reject/legacy, brak nadpisania slugu, publish pomija pending, dry-run → `DRY_RUN_SKIPPED`).
      Files: `R\engine.py`, `R\agents\geo_seo_engine.py`, `R\approve.py`, `R\publish.py`, `R\public\blog.html` (tylko znaczniki), `R\tests\test_approval.py`
      Verify: unittest OK; DRYRUN → exit 0, każda nowa paczka = 13 plików z baseline + `APPROVAL.json`, `PUBLISH_STATUS.json` ma `AWAITING_APPROVAL`; `status.txt` NIE zawiera `M public/articles/...` ani `public/llms.txt`; w kopii `$t`: `python approve.py list` pokazuje nowe paczki `pending_approval`, `python approve.py approve <prefiks>` → nowy plik w `public/articles/`, `python publish.py` → `DRY_RUN_SKIPPED`, exit 0.

## P0-3 Strona oferty i leady

- [ ] 5. Tryb runtime: `.env.example`, `.gitignore`, `.dockerignore` (design §7, §8).
      - `R\.env.example`: zastąpić treścią z design §7 (bez `CMS_GH_REPO=JKM872/...`, wszystkie wartości puste/placeholder).
      - `R\.gitignore`: dopisać `!.env.example`, `exports/`; `R\.dockerignore` (nowy) wg design §8.
      Files: `R\.env.example`, `R\.gitignore`, `R\.dockerignore`
      Verify: `git check-ignore .env.example` → brak wyniku (exit 1); `git check-ignore .env` → `.env`; `git grep -nE "AIza|gsk_|ghp_[A-Za-z0-9]{20}"` → 0 trafień; WS.

- [ ] 6. Tenanci (fundament dla oferty) — design §6.
      - Nowe `R\tenants\default\tenant.json`, `R\tenants\default\offer.json` (usługi i ceny z design §4 / `docs/STRATEGIA_MONETYZACJI.md`, `case_studies: []`, `[UZUPEŁNIJ]` w danych administratora), `R\tenants\demo\tenant.json`, `R\tenants\demo\persona.json`.
      - Nowy `R\saas_core\tenants.py`: `load_tenant`, `list_tenants`, walidacja id, fallbacki z `[WARN]`, nadpisanie `SITE_URL`/`CONTACT_EMAIL` z env dla default.
      - `R\saas_core\projects.json`: dodać `tenant_id` (`default`/`demo`) — tylko dopisanie pól.
      - `R\tests\test_tenants.py`.
      Files: jak wyżej
      Verify: unittest OK; `python -c "from saas_core.tenants import load_tenant; print(load_tenant('default')['is_owner'])"` → `True`; WS.

- [ ] 7. Leady: schemat, SQLite, walidacja, `leads.py`, lejek w dashboardzie (design §5).
      - Nowy `R\db\migrations\002_leads_tenants.sql` (SQL z design §5); `R\db\schema.sql` — te same tabele/kolumny dla świeżych instalacji.
      - `R\db\supabase_client.py`: tabele `tenants/leads/lead_events` w `_init_local_db`, idempotentne `ALTER TABLE ADD COLUMN` (`consent_at`, `unsubscribed_at`, `tenant_id`) przez `PRAGMA table_info`; metody `insert_lead`, `list_leads`, `get_lead`, `update_lead` (+event), `add_lead_note`, `lead_funnel`, `fetch_remote_leads`. Seedy bandyty: `0/0/1.0`, usunąć UPDATE „legacy zero rows” (istniejących wierszy nie kasować). Ścieżka bazy konfigurowalna (np. `LOCAL_DB_PATH`) dla testów.
      - `R\agents\analyst_agent.py`: usunąć `random.randint(10,45)`; brak danych → 1.0 + dopisek „brak realnych danych o kliknięciach”; `--reset-stats --yes` (bez `--yes` exit 2).
      - Nowy `R\crm\__init__.py`, `R\crm\validation.py` (`validate_lead(dict, now_ms) -> (clean, errors)` — reguły z design §4).
      - Nowy `R\leads.py` (add/list/show/update/note/export/sync; eksport do `exports/`).
      - `R\engine.py` (`update_markdown_dashboard`): sekcja „Lejek leadów” (tylko liczby).
      - Testy: `R\tests\test_lead_validation.py`, `R\tests\test_leads_db.py` (baza w katalogu tymczasowym).
      Files: jak wyżej
      Verify: unittest OK; w kopii DRYRUN `python leads.py add --name Test --email t@example.com` → id, `python leads.py list` pokazuje lead, `python leads.py update <id> --status zle` → exit 2; DRYRUN exit 0, `DASHBOARD.md` ma „Lejek leadów”.

- [ ] 8. Strona oferty, formularz leadów, polityka prywatności; panel admina do `admin/` (design §4). Zależy od 6 i 7.
      - `R\web_generator.py`: `build_web_dashboard()` pisze do `R\admin\index.html` i `R\admin\data.json` (zmiana ścieżek wyjścia); nowa `build_public_site()` → `public/index.html` (oferta, 7 sekcji, `lang="pl"`, meta/OG, JSON-LD `Person`+`Service`), `public/polityka-prywatnosci.html`, `public/robots.txt`, `public/sitemap.xml`, `public/data.json` w wersji publicznej `{"brand","articles"}`. Wspólny fragment formularza (funkcja zwracająca HTML+JS) z polami `name,email,company,service,message,consent`, honeypot `website`, `ts`, `utm_*`, obsługa 200/400/503/mailto z `role="status" aria-live="polite"`, `aria-invalid`/`aria-describedby`, etykiety `<label for>`.
      - `R\engine.py`: wołać `build_public_site()` po panelu.
      - `R\public\blog.html`: zastąpić formularz `localStorage` tym samym formularzem (usunąć `autonoma_captured_leads`); edycja punktowa.
      - Nowe `R\functions\api\_lead_validate.js` (`validateLead(body, now)`) i `R\functions\api\lead.js` (`onRequestPost`, 405/403/413/400/200/502/503 wg design, Supabase REST z anon key i timeoutem 5 s, opcjonalny Telegram bez e-maila).
      - `R\tests\test_public_html.py` (parsowanie `html.parser`: zbalansowane tagi, pola formularza, `consent` required, wszystkie lokalne `href` istnieją w `public/`); opcjonalnie `R\tests\js\lead.test.mjs` (`node --test`, tylko gdy `node` dostępny).
      Files: jak wyżej
      Verify: unittest OK; DRYRUN exit 0, `status.txt` pokazuje `public/index.html` (oferta, bez „Bramka CMS”/pól kluczy) i nowe `admin/`; `if (Get-Command node -EA 0) { node --test tests/js }`.

## P1 — pipeline, bezpieczeństwo

- [ ] 9. Writery z jawnym `project`/`brand`, usunięcie zmyślonych danych, persona marki (design §3, §2 „Zmyślone dane”). Zależy od 6.
      - Nowy `R\agents\writers\_common.py` (`resolve_profile`, `brand_prompt`); 8 writerów w `R\agents\writers\*.py`: sygnatura `generate_x(topic, persona, project=None, brand=None)` z kompatybilnością wsteczną.
      - `R\engine.py`: przekazywać `project` i `brand=load_tenant(project.get("tenant_id","default"))["persona"]`; usunąć zapis `saas_core/product_profile.json`; slug artykułu przez `geo_seo_engine.slugify` (slug folderu queue bez zmian). `approve.py`: podmienić tymczasowy helper na `load_tenant`.
      - `R\agents\geo_seo_engine.py` + szablony writerów: liczby/„zweryfikowana platforma”/„Rekomendacja Ekspertów” → sformułowania jakościowe lub `[UZUPEŁNIJ: …]`; ranking z ujawnieniem „nasze rozwiązanie (autor artykułu)”; `derive_seo_headline` → `metric_highlight=""`.
      - `R\run_daemon.py`: aktualizacja `now` po cyklu, czyste wyjście na `KeyboardInterrupt`/`SIGTERM`.
      - `R\tests\test_ethics_grep.py` (skan: brak anti-ban/jitter/START, brak „64%”, „zweryfikowana platforma” w kodzie poza `queue/`, `public/articles/`, `.agents/`).
      Files: jak wyżej
      Verify: unittest OK; DRYRUN exit 0, `status.txt` nie zawiera `saas_core/product_profile.json`; `Select-String '64%' $t\queue\*\0_WEBSITE_SEO_ARTICLE.md` dla nowych paczek → 0.

- [ ] 10. Bezpieczeństwo `local_server.py` i `/api/ai-generate` (design §4 „Lokalnie”, „Bezpieczeństwo”). Zależy od 7, 8.
      - `R\local_server.py`: bind `LOCAL_BIND` (127.0.0.1), bez CORS `*`, `/api/load-keys` maskowane + `set`, `/api/save-keys` merge z `.env`, `POST /api/lead` przez `crm.validation` + `db.insert_lead`, `/admin/` z `admin/`, usunąć wzmiankę `/api/run-engine`.
      - `R\functions\api\ai-generate.js`, `R\src\index.js`: `X-Admin-Token` vs `env.ADMIN_TOKEN` (brak → 503 `disabled`, zły → 401), `env.AI` brak → 503 `ai_binding_missing`. Panel admina (w `web_generator.py`) wysyła token z pola w `sessionStorage`.
      - `R\tests\test_local_server.py` (serwer na wolnym porcie w wątku, `LOCAL_DB_PATH` tymczasowy: POST lead 200/400, load-keys zamaskowane).
      Files: jak wyżej
      Verify: unittest OK; WS.

## P2 — CI, Docker, dokumentacja

- [ ] 11. CI i Docker (design §8).
      - `R\.github\workflows\agent_24_7.yml`: kroki compileall + unittest przed engine, `DRY_RUN: ${{ vars.DRY_RUN || '1' }}`, brakujące sekrety (B15 + `NEWSLETTER_FROM`, `SITE_URL`), `python publish.py` po engine, `git add` bez `logs/`, dodać `admin/`.
      - Nowy `R\.github\workflows\ci.yml` (push/pull_request: compile, unittest, `OFFLINE=1 DRY_RUN=1 python engine.py`, opcjonalny node test).
      - `R\Dockerfile`: user `app`, `ENV DRY_RUN=1`.
      - Test integracyjny `R\tests\test_engine_dry_run.py` (kopia repo do tmp, `OFFLINE=1`, subprocess, asercje: exit 0, `APPROVAL.json`, brak zmian `product_profile.json`, brak nowych `public/articles/`) — oznaczony do pominięcia, gdy `SKIP_E2E=1`.
      Files: jak wyżej
      Verify: unittest OK (z e2e `test_engine_dry_run`); WS; YAML przejrzany ręcznie (brak parsera YAML w stdlib — wcięcia, klucze `on/jobs/steps`).

- [ ] 12. Dokumentacja (design §11, P2-9).
      - `R\README.md`: jak uruchomić (dry-run, approve, publish, leads, local_server), „Zasady zgodności”, tabela kluczy → co odblokowują (zgodna z `.env.example`). `R\PLAN_ROZWOJU_AGENCI_AI.md`: zgodność z rzeczywistością (12 pracowników → realny opis). `R\docs\STRATEGIA_MONETYZACJI.md`: tylko uzupełnić odwołania do nowych plików (`tenants/default/offer.json`, `leads.py`), bez przepisywania.
      Files: jak wyżej
      Verify: wszystkie komendy z README uruchomione w kopii DRYRUN kończą się exit 0.

---

# Weryfikacja końcowa (obowiązkowa, po zadaniu 12)

1. Kompilacja wszystkich .py:
```powershell
cd C:\Users\hp\Documents\antigravity\mysterious-darwin
$f = Get-ChildItem -Recurse -Filter *.py | ? { $_.FullName -notmatch '\\.agents\\|__pycache__' }; $bad=0
$f | % { python -m py_compile $_.FullName; if($LASTEXITCODE){$bad++; "FAIL $($_.FullName)"} }; "py_compile FAIL=$bad z $($f.Count)"
```
Oczekiwane: `FAIL=0` (dotyczy też `queue/*/6_GITHUB_SNIPPET.py`, jak w baseline).

2. Import każdego modułu:
```powershell
$mods = Get-ChildItem -Recurse -Filter *.py | ? { $_.FullName -notmatch '\\queue\\|\\.agents\\|__pycache__|\\tests\\' } | % { $_.FullName.Substring((Get-Location).Path.Length+1) -replace '\.py$','' -replace '\\','.' } | ? { $_ -notmatch '__init__$' }
$mods | % { python -c "import importlib; importlib.import_module('$_')" 2>$null; if($LASTEXITCODE){"IMPORT FAIL $_"} }; "modułów: $($mods.Count)"
```
Oczekiwane: brak `IMPORT FAIL`; lista obejmuje 28 modułów z baseline (bez `agents.anti_ban_commenter`) + `agents.runtime`, `agents.reply_drafter`, `agents.writers._common`, `saas_core.tenants`, `crm.validation`, `approve`, `publish`, `leads`. Import nie może uruchamiać engine/serwera (guard `if __name__ == "__main__"`).

3. Testy: `python -m unittest discover -s tests -v` → OK.

4. End-to-end dry run bez kluczy: uruchomić komendę DRYRUN (sekcja „Komenda DRYRUN”) dwukrotnie — z siecią i z `$env:OFFLINE="1"`. Porównać z `baseline\`:
   - `EXIT=0` w obu;
   - te same 13 plików na paczkę co `baseline\bundle_files.txt` + `APPROVAL.json` (+ ewentualnie `NEWSLETTER_PREVIEW.html`), po jednej paczce na aktywny projekt;
   - `status.txt`: brak `public/articles/*`, `public/llms.txt`, `saas_core/product_profile.json`; obecne `DASHBOARD.md`, `memory/seen_topics.json`, `public/index.html`, `admin/`;
   - `run.txt`: brak `Traceback`, obecne `[DRY_RUN]`/`[MOCK]`; brak żądań zapisu (żadnego `log` z `ok` dla senderów);
   - w kopii: `python approve.py approve <prefiks pierwszej paczki>` → nowy artykuł + sitemap + llms.txt; `python publish.py` → wyłącznie `DRY_RUN_SKIPPED`, exit 0.
   Zapisać wyniki do `R\.agents\tasks\rescue\final\` (`run.txt`, `status.txt`, `diff_vs_baseline.txt`).

5. Walidacja `public/*.html`: `python -m unittest tests.test_public_html -v` oraz ręczny skrypt: każdy plik `R\public\*.html` parsuje się `html.parser` bez niezamkniętych tagów; `index.html` i `blog.html` mają formularz z polami `name`, `email`, `company`, `service`, `message`, `consent` (required), `website` (honeypot), action do `/api/lead`; każdy lokalny `href`/`src` (bez `http`, `mailto:`, `#`) wskazuje istniejący plik w `public/` (`/articles/<slug>` → `public/articles/<slug>.md`). Oczekiwane: 0 błędów.

6. Repo: `git status --short` w `R` — brak `D` w `queue/` i `public/articles/`; `git ls-files .env.example` po `git add` niepuste; `git grep -nE "AIza|gsk_|ghp_[A-Za-z0-9]{20}"` → 0; brak pliku `.env` dodanego do indeksu. Usunąć `$env:TEMP\md_dry`.

Uwagi/założenia: commitów w repo nie robimy bez prośby użytkownika (zmiany zostają w drzewie roboczym). Node.js jest opcjonalny — brak `node` nie blokuje weryfikacji. Finalny krok workflow pisze `R\PODSUMOWANIE.md` (po polsku: co naprawiono, jak uruchomić, które darmowe klucze dodać najpierw — Gemini, Supabase anon/URL dla leadów, Telegram — i gdzie je wpisać).
