# Weryfikacja — rescue, iteracja 2 (poprawki po code-review pass 1)

Środowisko: Windows, PowerShell, Python 3.14.0, Node v24.12.0. Żadnych kluczy w env (skrypt dry-run usuwa zmienne `KEY|TOKEN|WEBHOOK|SUPABASE|CMS_|LINKEDIN|TELEGRAM|DRY_RUN|OFFLINE`), brak pliku `.env` w repo. Nic nie zostało wysłane na zewnętrzne platformy.

## Co poprawiono (mapowanie na findings)
| Finding | Poprawka |
|---|---|
| 1. brak verification.md | ten plik + `after/`, `after_compile_import.txt` |
| 2. brak endpointu leadów | `functions/api/lead.js` (405/403/413/400/200/502/503, honeypot `website`, pułapka czasowa `ts` ≥ 3 s, same-origin, limit 8 KB, Supabase REST anon + timeout 5 s, opcjonalny Telegram bez e-maila) + `functions/api/_lead_validate.js` |
| 3. brak strony oferty | `web_generator.build_public_site()` → `public/index.html` (hero + 2 CTA, problem→rozwiązanie, usługi z cenami z `tenants/default/offer.json`, proces, dowody/artykuły, FAQ, formularz `#kontakt`), `public/polityka-prywatnosci.html`, `public/robots.txt`, `public/sitemap.xml`; wspólny formularz `public/lead-form.js` + `public/lead-form.css`; `public/blog.html`: formularz `localStorage` zastąpiony tym samym formularzem (blok `<!-- LEADFORM:START/END -->`); `engine.py` woła `build_public_site()` po panelu |
| 4. brak tabel leadów | `db/migrations/002_leads_tenants.sql` (Supabase, RLS insert-only dla anon), dopisane do `db/schema.sql`; `db/supabase_client.py`: tabele `tenants/leads/lead_events` w SQLite, idempotentne `ALTER TABLE ADD COLUMN`, metody `insert_lead/list_leads/get_lead/update_lead/add_lead_note/lead_funnel/fetch_remote_leads/upsert_local_lead`, `LOCAL_DB_PATH` z env; `crm/validation.py`; CLI `leads.py`; sekcja „Lejek leadów” w `DASHBOARD.md` (tylko liczby) |
| 5. `.env.example` | przepisany wg design §7: każdy klucz z opisem darmowego planu i tego, co odblokowuje; komentarze w osobnych liniach (parser `_load_key` nie obsługuje komentarzy w linii); brak realnych wartości; `.gitignore`: `!.env.example`, `exports/` |

Dodatkowo: `db/schema.sql` — usunięte komentarze „Anti-Ban!”/„Human-like delay”, `reply_at` NULLABLE.

## Komendy i wyniki

### 1. Baseline (przed zmianami, iteracja 1) — `.agents/tasks/rescue/baseline/`
`powershell -File .agents/tasks/rescue/scripts/dryrun.ps1 -Out .agents/tasks/rescue/baseline` → `EXIT=0`, 2 paczki × 13 plików = 26 (`bundle_files.txt`), `compile_import.txt`.

### 2. Kompilacja + importy (po)
`powershell -NoProfile -File .agents/tasks/rescue/scripts/compile_import.ps1` → `py_compile FAIL=0 z 57`, `import FAIL=0 z 33` (pełny wynik: `after_compile_import.txt`; nowe moduły `crm.validation`, `leads` importują się bez efektów ubocznych).

### 3. Testy
`python -m unittest discover -s tests -v` → `Ran 8 tests ... OK`
(`tests/test_leads.py`: walidacja, spam, lejek w SQLite w katalogu tymczasowym, idempotentny init; `tests/test_public_html.py`: każdy `public/*.html` dobrze sformowany, formularze w `index.html` i `blog.html` mają `action="/api/lead"` i pola `name,email,company,service,message,consent,website,ts`, `name/email/consent` required, wszystkie lokalne `href/src` istnieją w `public/`, CTA `#kontakt` → `id="kontakt"`, `lang="pl"`).

### 4. Pages Function (Node, lokalnie, bez sieci, `env={}`)
`node --input-type=module -e "...validateLead / onRequest..."`:
- validateLead poprawny → `{lead:{...status:"new",consent_text_version:"v1"}}`; honeypot → `{spam:"honeypot"}`; złe pola → `{errors:{name:"required",email:"invalid",consent:"required"}}`
- `GET` → 405; `POST {bad` → 400 `invalid_json`; poprawny `POST` bez konfiguracji Supabase → 503 `{fallback:"mailto"}`; `Origin: https://evil.com` → 403.

### 5. End-to-end dry run bez kluczy (po) — `.agents/tasks/rescue/after/`
`powershell -NoProfile -File .agents/tasks/rescue/scripts/dryrun.ps1 -Out .agents/tasks/rescue/after` (kopia repo w `%TEMP%\md_dry`, `python engine.py`).

| | baseline | po zmianach |
|---|---|---|
| exit code | 0 | 0 |
| `Traceback` w run.txt | 0 | 0 |
| nowe paczki queue/ | 2 × 13 plików | 2 × 13 plików (te same nazwy plików) |
| `DASHBOARD.md` | M | M (+ sekcja „💼 Lejek leadów”) |
| `memory/seen_topics.json` | M | M |
| `public/raport_statystyczny.md` | M | M |
| `public/index.html` | M (panel SaaS) | strona ofertowa; w kopii brak `M`, bo repo zawiera już wygenerowaną wersję (generator deterministyczny) |
| `public/data.json` | M | bez zmian (panel pisze do `admin/data.json` — zmiana z iteracji 1) |
| `admin/index.html`, `admin/data.json` | — | nowe (lokalny panel) |
| `public/articles/*` (2 pliki) | M | M (zachowanie bez zmian w tej iteracji; bramka approve to zadanie 4 planu) |
| `saas_core/product_profile.json` | — | M (+`"tenant_id": "demo"` — engine kopiuje projekt do profilu; skutek `tenant_id` dodanego w iteracji 1; usunięcie zapisu to zadanie 9) |

Log zawiera `✅ Strona ofertowa wygenerowana`, brak `[ERROR]`/`[WARN]` generatorów.

### 6. CLI leadów (w kopii `%TEMP%\md_dry`, SQLite)
- `python leads.py add --name Test --email t@example.com` → uuid, exit 0
- `python leads.py list` → wiersz `new ... Test <t@example.com>`, exit 0
- `python leads.py update <id> --status zle` → `[ERROR] Nieznany status`, exit 2
- `python leads.py update <8 znaków> --status contacted --value 490` → exit 0; `note` → exit 0; `show` → historia `created`, `status new -> contacted`, `note`
- `python leads.py export` → `exports/leads_<data>.csv`, exit 0
- `python leads.py sync` bez kluczy → `[WARN] sync wymaga ...`, exit 0
- `python leads.py add --name X --email bad` → exit 2

### 7. Repo
- `git status --short` — brak `D` w `queue/` i `public/articles/`.
- `.env` nie istnieje i nie jest w indeksie; `.env.example` zawiera tylko puste wartości/placeholdery.

## Czego nie zweryfikowano
- Realny zapis do Supabase i powiadomienie Telegram (brak kluczy — celowo).
- Działanie Pages Function na Cloudflare (testowane lokalnie w Node z `Request`/`Response`).
- Pełna zgodność WCAG wymaga ręcznych testów z czytnikiem ekranu.
- Pozostałe zadania planu (4: bramka `approve.py`/`publish.py`, 9–12) nie były objęte findingami tej rundy.
