# Weryfikacja — rescue (iteracja 2)

Środowisko: Windows, PowerShell, Python 3.14.0. Żadnych kluczy (zmienne `*KEY*`, `*TOKEN*`, `WEBHOOK*`, `SUPABASE*`, `CMS_*`, `LINKEDIN*`, `TELEGRAM*`, `DRY_RUN` usuwane przed każdym uruchomieniem). Nic nie zostało wysłane na zewnątrz.

Skrypty: `.agents/tasks/rescue/scripts/dryrun.ps1` (kopia repo do `%TEMP%\md_dry` bez `.git/.agents/__pycache__`, `git init`, `python engine.py`, `git status`), `compile_import.ps1`, `final_checks.ps1`. Surowe wyniki: `baseline/`, `final/`.

## Uwaga o równoległej sesji
W trakcie pracy inna sesja zrobiła commit `3f62fbe` (lead.js, offer page, leads.py, crm/validation.py, tabele leadów, .env.example, tests/test_leads.py, tests/test_public_html.py). Ta iteracja nie duplikuje tych zmian: moje edycje `db/supabase_client.py`/`db/schema.sql` z duplikatami metod cofnięto (`git checkout`) i zastosowano tylko brakujące poprawki. Zduplikowane wywołanie `build_public_site()` i podwójny lejek w `engine.py` usunięto.

## 1. Baseline (przed zmianami, kod `baf519b`)
| Komenda | Wynik |
|---|---|
| `dryrun.ps1 -Out baseline` | `EXIT=0`; 2 paczki × 13 plików; zmiany: `DASHBOARD.md`, `memory/seen_topics.json`, **`public/articles/*.md` (2 pliki nadpisane)**, `public/data.json`, `public/index.html`, `public/raport_statystyczny.md` |
| `compile_import.ps1` | `py_compile FAIL=0 z 49`, `import FAIL=0 z 29` |

## 2. Po zmianach
| Komenda | Wynik |
|---|---|
| `python -m unittest discover -s tests -v` (z e2e `test_engine_dry_run`) | `OK`, exit 0 (`final/unittest.txt`) |
| `compile_import.ps1` (wszystkie .py, łącznie z `queue/*`; import każdego modułu z roota) | `py_compile FAIL=0 z 67`, `import FAIL=0 z 36` (nowe: `agents.runtime`, `agents.reply_drafter`, `agents.writers._common`, `saas_core.tenants`, `crm.validation`, `approve`, `publish`, `leads`; usunięty `agents.anti_ban_commenter`) |
| `dryrun.ps1 -Out final/online` (z siecią) | `EXIT=0`, 0× `Traceback` |
| `dryrun.ps1 -Out final/offline -Offline` | `EXIT=0`, 0× `Traceback`, 3× `[OFFLINE] … fixture`, `[MOCK] AI: brak klucza…` |
| `python approve.py list` (kopia) | exit 0, nowe paczki `pending_approval`, stare `legacy` |
| `python approve.py approve <pierwsza paczka>` | exit 0, nowy plik `public/articles/najlepsze-narzedzia-…md`, odświeżone `sitemap.xml`, `llms.txt`, `blog.html`, archiwum `public/newsletter/` |
| `python publish.py` | exit 0, linkedin/newsletter/webhook/telegram = `DRY_RUN_SKIPPED`, `urlopen` niewołany |
| `python approve.py approve nie-ma-takiej` | exit 2 |
| `python leads.py add --name Test --email t@example.com` / `list` (baza tymczasowa `LOCAL_DB_PATH`) | exit 0 / exit 0, lead widoczny |
| `python -m agents.analyst_agent --reset-stats` (bez `--yes`) | exit 2 |
| `python -m unittest tests.test_public_html -v` | exit 0 (zbalansowane tagi, pola `name,email,company,service,message,consent(required),website`, action `/api/lead`, lokalne `href` istnieją) |
| `git grep -nE "AIza\|gsk_\|ghp_[A-Za-z0-9]{20}"` | 0 trafień |
| `git status` — `D` w `queue/` lub `public/articles/` | brak |

## 3. Porównanie dry-run: baseline → po
| | Baseline | Po |
|---|---|---|
| Exit code | 0 | 0 (online i offline) |
| Paczki | 2 × 13 plików | 2 × 14 plików: te same 13 + `APPROVAL.json` (`Compare-Object` → jedyna różnica `=> APPROVAL.json`) |
| `PUBLISH_STATUS.json` | `QUEUED_FOR_AUTO_PUBLISH` | `mode: dry_run`, kanały `AWAITING_APPROVAL` |
| `public/articles/*` | **nadpisywane w każdym cyklu** | nietknięte (publikuje tylko `approve.py`) |
| `public/llms.txt`, `saas_core/product_profile.json` | zmieniane | nietknięte |
| `public/data.json` | pełne dane panelu | nietknięty; panel → `admin/index.html`, `admin/data.json` |
| `public/index.html` | panel admina z polami kluczy | strona ofertowa (generowana z `tenants/default/offer.json`; bez zmian względem commitu) |
| `DASHBOARD.md`, `memory/seen_topics.json`, `public/raport_statystyczny.md` | zmieniane | zmieniane (bez zmian zachowania) |
| Zapisy zewnętrzne | IndexNow ping z domyślnym kluczem | brak (IndexNow/CMS/social/newsletter → `SKIPPED`/`DRY_RUN_SKIPPED`) |

Wszystko, co działało w baseline (scan → curate → write → queue, dashboard, raport, pamięć), działa nadal.

## 4. Nierozwiązane / świadome
- Node.js nie był uruchamiany (brak `tests/js`), JS sprawdzony przeglądem; `ci.yml` uruchamia `node --test` warunkowo.
- `DASHBOARD.md` zawierał stary napis „+ Anti-Ban” — poprawiony ręcznie; kolejne cykle generują nowy tekst.
- Istniejące wiersze bandyty w lokalnej (ignorowanej) bazie użytkownika nie są kasowane; reset: `python -m agents.analyst_agent --reset-stats --yes`.
