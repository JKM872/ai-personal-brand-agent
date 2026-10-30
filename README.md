# Autonoma AI — agenci AI dla marki osobistej (budżet 0 zł)

System agentów AI, który co cykl przegląda trendy (GitHub, Hacker News, arXiv), wybiera temat i przygotowuje paczkę treści na 10 kanałów: artykuł SEO/GEO, post i karuzela LinkedIn, wątek X, newsletter, scenariusz wideo, plan grupy, kampania reklamowa, szablony kontaktu 1:1 i snippet integracyjny. **Każda paczka czeka na Twoją akceptację** — nic nie jest publikowane automatycznie. Strona publiczna (`public/`) to oferta usług z formularzem leadów, a leady trafiają do prostego lejka sprzedaży.

Bez żadnego klucza API wszystko działa w trybie dry-run: AI używa szablonów, baza to lokalny SQLite, nic nie wychodzi na zewnątrz.

## Szybki start

```bash
python engine.py                      # cykl agentów → nowe paczki w queue/ (status pending_approval)
OFFLINE=1 python engine.py            # to samo bez sieci (scouty czytają sources/fixtures/)
python approve.py list                # paczki i ich status
python approve.py show <paczka>       # podgląd (nazwa folderu lub unikalny prefiks)
python approve.py approve <paczka>    # zatwierdź; artykuł właściciela trafia do public/articles/
python approve.py approve <paczka> --only website_article,linkedin
python approve.py reject <paczka> --note "za ogólne"
python publish.py                     # wysyła tylko zatwierdzone kanały (bez kluczy: DRY_RUN_SKIPPED)
python leads.py add --name "Jan" --email jan@example.com --service audyt
python leads.py list | show <id> | update <id> --status contacted --next-at 2026-11-03 | note <id> "tekst"
python leads.py export                # CSV do exports/ (nie trafia do repo)
python local_server.py                # http://127.0.0.1:3000/ (strona) i /admin/ (panel)
python -m unittest discover -s tests -v
```

W PowerShell zmienne ustawiasz tak: `$env:OFFLINE="1"; python engine.py`.

## Przepływ

1. `engine.py`: scan → curate → write → `queue/<data>_<projekt>_<temat>/` + `APPROVAL.json` (`pending_approval`). Odświeża `DASHBOARD.md` (z lejkiem leadów), panel `admin/` i stronę ofertową `public/index.html`.
2. `approve.py`: decyzja człowieka. Dla marki właściciela (tenant `default`) kopiuje artykuł do `public/articles/` (nigdy nie nadpisuje), odświeża `sitemap.xml`, `llms.txt`, listę w `blog.html` i archiwum `public/newsletter/`.
3. `publish.py`: jedyne miejsce, które woła LinkedIn / webhook / Telegram / newsletter / zewnętrzny CMS — tylko dla zatwierdzonych kanałów i tylko gdy są klucze i `DRY_RUN` nie jest włączony.
4. Cloudflare Pages publikuje `public/` oraz `functions/api/lead.js` (formularz → Supabase).

## Zasady zgodności

- Człowiek zatwierdza każdą publikację (`approve.py`). Agenci przygotowują szkice, nie publikują sami.
- Brak maskowania automatyzacji: żadnych losowych opóźnień „udających człowieka”, żadnego omijania limitów platform, żadnych automatycznych komentarzy ani wiadomości prywatnych. Szkice odpowiedzi (`agents/reply_drafter.py`) publikujesz ręcznie.
- Kontakt 1:1 tylko do osób, z którymi masz relację lub uzasadniony interes, zawsze z możliwością rezygnacji. Bez kupowania baz i wysyłek seryjnych.
- Newsletter tylko do subskrybentów z zapisaną zgodą (`consent_at`), z linkiem wypisu. **Istniejący subskrybenci bez udokumentowanej zgody nie dostaną newslettera**, dopóki nie zapiszą się ponownie ze zgodą.
- Brak zmyślonych danych: szablony nie podają wymyślonych procentów; tam gdzie potrzebna liczba, jest `[UZUPEŁNIJ: źródło]`. Ranking w artykule ujawnia, że opisujemy własne rozwiązanie.
- Formularz leadów: zgoda, honeypot, pułapka czasowa, polityka prywatności (`public/polityka-prywatnosci.html` — uzupełnij dane administratora).

## Klucze → co odblokowują (szczegóły w `.env.example`)

| Klucz | Darmowy plan | Co odblokowuje | Bez klucza |
|---|---|---|---|
| `GEMINI_API_KEY` / `GROQ_API_KEY` / `CF_ACCOUNT_ID`+`CF_API_TOKEN` | Google AI Studio / Groq / Workers AI | treści pisane przez LLM | szablony |
| `SUPABASE_URL` + `SUPABASE_KEY` (service, lokalnie/CI) | Supabase Free | zdalna baza, `leads.py sync` | SQLite |
| `SUPABASE_ANON_KEY` (Cloudflare Pages env) | Supabase Free | zapis leadów z formularza `/api/lead` | formularz pokazuje mailto |
| `TELEGRAM_BOT_TOKEN` + `TELEGRAM_CHAT_ID` | Telegram | powiadomienia o paczkach/leadach | pominięte |
| `WEBHOOK_URL` | Make / n8n / Discord | przekazanie zatwierdzonych treści | `DRY_RUN_SKIPPED` |
| `LINKEDIN_ACCESS_TOKEN` + `LINKEDIN_AUTHOR_URN` | LinkedIn API | publikacja zatwierdzonego posta | `DRY_RUN_SKIPPED` |
| `BREVO_API_KEY` lub `RESEND_API_KEY` + `NEWSLETTER_FROM` | 300 / 100 e-maili dziennie | wysyłka newslettera | `NEWSLETTER_PREVIEW.html` |
| `INDEXNOW_KEY` | IndexNow | ping wyszukiwarek po publikacji | pominięte |
| `CMS_*`, `WP_*` + `CMS_OWNER_AUTHORIZED=true` | GitHub / WordPress | publikacja artykułów klientów (tenant inny niż `default`) | `DRY_RUN_SKIPPED` |
| `ADMIN_TOKEN` | — | `/api/ai-generate` na Pages | 503 `disabled` |
| `DRY_RUN` | — | `1` nic nie wysyła, `0` live tam, gdzie są klucze, puste = auto | auto (dry-run) |

## Multi-tenant (fundament pod SaaS)

`tenants/<id>/tenant.json` (+ persona, oferta). `default` = Twoja marka (`is_owner: true`, publikowana do `public/`), `demo` = przykładowy klient. Projekt w `saas_core/projects.json` wskazuje `tenant_id`. Billing poza zakresem.

## Infrastruktura 0 zł

- GitHub Actions: `.github/workflows/agent_24_7.yml` (cykl co 6 h, domyślnie `DRY_RUN=1` — zmień zmienną repozytorium), `.github/workflows/ci.yml` (kompilacja, testy, dry run).
- Cloudflare Pages: katalog `public/` + `functions/api/*`. Panel `admin/` nie jest publikowany.
- Supabase Free: `db/schema.sql` (nowa instalacja) lub `db/migrations/002_leads_tenants.sql`.

Strategia zarabiania: [`docs/STRATEGIA_MONETYZACJI.md`](docs/STRATEGIA_MONETYZACJI.md).
