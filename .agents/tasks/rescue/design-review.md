# Przegląd projektu technicznego: ratunek Autonoma AI (iteracja 2)

Werdykt: APPROVED (0 × HIGH, 0 × MEDIUM, 3 × NIT)

Wszystkie 5 ustaleń MEDIUM i 4 NIT z iteracji 1 zostały rozwiązane i sprawdziłem je w tekście projektu. (a) Pipeline bez kluczy: engine nie publikuje, zapisuje tylko paczkę i `APPROVAL.json` przez `dispatch_content_bundle(..., dry_run_only=True)`. Publikacja idzie tylko przez `approve.py`/`publish.py`. (b) Oferta, formularz i CTA są opisane, a `lead.js` ma walidację, honeypot, kontrolę Origin i nie zawiera sekretów. (c) Są `leads`/`lead_events` z CHECK i RLS oraz `leads.py`. (d) Jest `tenants/` i `tenant_id`, bez billingu. (e) Dokument monetyzacji istnieje i ma wymagane sekcje. Etyka: `anti_ban_commenter` usunięty, jest bramka akceptacji, lista literałów i kontrolny grep. Plan weryfikacji ma baseline przed i po zmianach.

## Ustalenia

1. NIT: kto zapisuje `NEWSLETTER_PREVIEW.html` (sekcja 1 kontra tabela `publish.py` w sekcji 2).
   Sekcja 1 mówi, że newsletter w dry-run zapisuje `queue/<paczka>/NEWSLETTER_PREVIEW.html`. Według tabeli w sekcji 2 `publish.py` w dry-run w ogóle nie woła `send_newsletter_batch` (`DRY_RUN_SKIPPED`). Ta funkcja i tak nie dostaje ścieżki paczki: sygnatura to `(subject, html_content, sender_name, sender_email)`, `agents/newsletter_agent.py:21`.
   Poprawka: podglądu nie zapisuje `newsletter_agent`, tylko `publish.py` przy pomijaniu kanału newsletter: `(paczka / "NEWSLETTER_PREVIEW.html").write_text(html, encoding="utf-8")`. Sygnatura `send_newsletter_batch` zostaje bez zmian.

2. NIT: niepełne ścieżki `social_publisher.py`, `cms_connector.py`, `indexnow.py` w tabeli w sekcji 1.
   Te pliki leżą w `publishers/`, nie w `agents/` (`engine.py:51-53`). Poprawka: w tabeli podać `publishers/social_publisher.py`, `publishers/cms_connector.py`, `publishers/indexnow.py`.

3. NIT: `_post_linkedin`/`_post_webhook`/`_post_telegram` dublują istniejące funkcje.
   `publishers/social_publisher.py` ma już `post_to_linkedin` (l.98), `send_webhook` (l.59) i `send_telegram_notification` (l.81). Poprawka: `_post_*` mają być cienkimi nakładkami, które wołają istniejące funkcje i zamieniają status HTTP i wyjątek na `{"status":"ok"|"error:<msg>"}`. Istniejących funkcji nie przepisujemy.

## Zweryfikowane założenia
- `engine.py:164-170` woła `publish_article_to_website` i `submit_to_indexnow`. `engine.py:221` woła `dispatch_content_bundle(primary_topic, bundle, queue_dir)`. Projekt usuwa te wywołania wprost (sekcja 3, punkty (a) do (c)).
- `publishers/social_publisher.py:125` `dispatch_content_bundle(topic, bundle, queue_dir)` nie ma dziś `dry_run_only`, a l.194-199 wysyła newsletter. Projekt to opisuje zgodnie z kodem.
- Literały etyczne są w `engine.py:13` (docstring), `:101`, `:184` i `:198`. Wszystkie są na liście zmian w projekcie.
- `agents/newsletter_agent.send_newsletter_batch` ma parametr `sender_email`, więc wywołanie z tabeli `publish.py` jest poprawne.
- `agents/geo_seo_engine.slugify` (l.20) istnieje. `generate_geo_article(trend_topic, profile=None)` (l.139) nie ma dziś `write_public`, a projekt jawnie go dodaje.
- `docs/STRATEGIA_MONETYZACJI.md` ma sekcje: usługi (etap 1), SaaS (etap 2), playbook pierwszych klientów (etyczny, opt-in, ręczny), go-to-market za 0 zł, metryki.
- Ustalenia z iteracji 1 (anti_ban_commenter nieimportowany, `random.randint(18,95)`, `time.sleep` w newsletterze, domyślny klucz IndexNow, `localStorage` w blog.html, UUID kontra TEXT) przyjmuję z tamtego przeglądu.

## Założenia niezweryfikowane lub błędne
- NIEZWERYFIKOWANE: czy `agents/cloudflare_ai.py` kończy działanie przed `urlopen`, gdy brak kluczy. Projekt zleca implementującemu sprawdzenie i dodanie guardu, więc to akceptowalne.
- NIEZWERYFIKOWANE: numery linii w `web_generator.py`. Projekt każe szukać po treści.
- BŁĘDNE (drobne): ścieżki modułów publisherów w tabeli w sekcji 1, zob. ustalenie 2.
