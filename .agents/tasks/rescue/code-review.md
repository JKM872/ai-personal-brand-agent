# Code review – rescue (pass 1)

Werdykt: CHANGES_REQUESTED

Co sprawdziłem: `git status`, `git diff --stat`, czy istnieją wymagane pliki w `.agents/tasks/rescue/`, `functions/api/`, `public/`, `db/`.

## Blokery

1. Brak dowodów weryfikacji. Plik `.agents/tasks/rescue/verification.md` nie istnieje, więc nie ma zapisanego dry-runu przed/po, kompilacji ani testów. Konsekwencja: nie da się potwierdzić, że pipeline scan → curate → write → queue → publish działa bez kluczy. Poprawka: uruchomić dry-run/testy i zapisać wyniki (komendy, wyjście, porównanie z `baseline/`) w `verification.md`.
2. Brak endpointu leadów. `functions/api/` zawiera tylko `ai-generate.js` i `status.js`; nie ma endpointu lead z walidacją i ochroną antyspamową (honeypot/limit). Poprawka: dodać `functions/api/lead.js` zgodnie z design.md.
3. Brak strony oferty z formularzem leadów i CTA w `public/` (są tylko `index.html`, `blog.html`, `articles/`, …). W diffie nie ma zmian w `public/`. Poprawka: dodać stronę oferty z formularzem kierującym na endpoint leadów.
4. Brak tabel leadów/klientów w bazie. `db/schema.sql` i `db/supabase_client.py` nie są zmienione (brak w diffie), więc brakuje schematu Supabase i fallbacku SQLite. Poprawka: dodać tabele `leads`/`clients` w obu.
5. `.env.example` nie zostało zmienione/dodane w diffie; wymaganie udokumentowania każdego klucza, darmowego limitu i tego, co odblokowuje, nie jest spełnione. Poprawka: uzupełnić `.env.example` bez prawdziwych wartości.

Uwaga pozytywna (niebloker): `agents/anti_ban_commenter.py` jest usunięty, dodano `agents/reply_drafter.py`, `saas_core/tenants.py`, `tenants/`. Nie widzę usunięć w `queue/` ani `public/articles/`.
