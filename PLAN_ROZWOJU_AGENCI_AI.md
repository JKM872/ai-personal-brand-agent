# Plan: agenci AI dla Twojej marki

Ten dokument opisuje, co system robi naprawdę. Agenci przygotowują treści i porządkują sprzedaż; decyzję o publikacji zawsze podejmujesz Ty.

## Kto za co odpowiada

| Rola | Zadanie | Kod | Efekt |
|---|---|---|---|
| Zwiad trendów | przegląd GitHub / HN / arXiv, wybór tematu, pamięć bez powtórek | `sources/`, `agents/curator.py`, `agents/memory.py` | temat na dziś |
| Redaktor SEO/GEO | artykuł porównawczy z FAQ i JSON-LD, `llms.txt` po akceptacji | `agents/geo_seo_engine.py` | ruch z Google i asystentów AI |
| Pisarze kanałów | LinkedIn, X, newsletter, wideo, grupa, reklamy, szablony kontaktu 1:1 | `agents/writers/` | gotowe szkice na 10 kanałów |
| Kolejka akceptacji | paczka czeka na decyzję; publikacja dopiero po `approve.py` / `publish.py` | `approve.py`, `publish.py` | nic nie wychodzi bez Ciebie |
| Szkice odpowiedzi | szkic odpowiedzi na komentarz do ręcznego użycia | `agents/reply_drafter.py` | szybsze odpowiedzi, pisane przez Ciebie |
| Analityk | wybór stylu pisania (bandyta) na podstawie realnych kliknięć; bez danych wynik równy | `agents/analyst_agent.py` | lepsze style z czasem |
| Lejek leadów | formularz na stronie → baza → `leads.py` → lejek w `DASHBOARD.md` | `functions/api/lead.js`, `crm/`, `leads.py` | żaden lead nie przepada |
| Koordynator | cykl co 6 h w GitHub Actions | `.github/workflows/` | system pracuje bez laptopa |

## Cykl tygodniowy (realny)

1. Codziennie: `python approve.py list` → przeczytaj, popraw, zatwierdź 1 paczkę, opublikuj post ręcznie lub przez `publish.py`.
2. Codziennie: odpowiedz na nowe leady w < 24 h (`python leads.py list --status new`).
3. Raz w tygodniu: przegląd lejka w `DASHBOARD.md`, zaległych `next_action`, korekta persony w `brand_core/persona.json`.

## Zasady zgodności

- Człowiek zatwierdza każdą publikację.
- Brak maskowania automatyzacji (żadnych losowych opóźnień, automatycznych komentarzy ani DM).
- E-mail tylko do osób ze zgodą; kontakt 1:1 z możliwością rezygnacji.
- Brak zmyślonych liczb i opinii; wszędzie, gdzie potrzebne są dane, wpisz własne źródło.
- Subskrybenci bez zapisanej zgody (`consent_at`) nie dostają newslettera.

## Jak uruchomić dla swojego produktu

1. Uzupełnij `tenants/default/offer.json` (marka, dane administratora, ceny) i `brand_core/persona.json`.
2. Wpisz produkt w `saas_core/projects.json` (`tenant_id: "default"`).
3. Opcjonalnie dodaj darmowe klucze wg `.env.example` (najpierw: Gemini, Supabase anon + URL, Telegram).
4. `python engine.py` → `python approve.py list`.
