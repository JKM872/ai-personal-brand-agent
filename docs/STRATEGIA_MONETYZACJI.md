# Strategia monetyzacji — Autonoma AI

Cel: najpierw zarabiać na usługach dla własnych klientów (szybka gotówka, dowody skuteczności), potem sprzedawać narzędzie jako SaaS. Budżet startowy: 0 zł. Zasada nadrzędna: tylko etyczne, zgodne z regulaminami platform i RODO działania — człowiek zatwierdza każdą publikację, żadnego spamu, fałszywego zaangażowania ani masowych wiadomości.

## 1. Etap 1 (teraz): usługi
| Pakiet | Co zawiera | Cena (netto) | Czas |
|---|---|---|---|
| Audyt marki i treści | analiza profilu LinkedIn/strony, 10 tematów eksperckich, plan 30 dni, 3 gotowe posty | od 490 zł jednorazowo | 3–5 dni |
| Wdrożenie systemu agentów treści | konfiguracja Autonoma AI dla klienta (persona, oferta, kanały), kolejka akceptacji, strona z formularzem leadów, szkolenie 1 h | od 2 900 zł jednorazowo | 1–2 tyg. |
| Abonament „Content Ops” | 8 postów + 2 artykuły SEO/GEO + 2 newslettery miesięcznie (generowane, redagowane i zatwierdzane z klientem), raport miesięczny | od 1 200 zł/mies. (min. 3 mies.) | stały |
| Konsultacja | 30 min diagnozy | 0 zł (lead magnet) | — |

Zasady cenowe: ceny „od” na stronie, wycena po konsultacji; pierwszych 3 klientów może dostać 30–40% rabatu w zamian za zgodę na case study i opinię (tylko prawdziwe, za pisemną zgodą). Podnoś ceny o 20–30% po każdych 3 zamkniętych klientach.

## 2. Etap 2 (później): SaaS
| Plan | Dla kogo | Zakres | Cena |
|---|---|---|---|
| Starter | solo-ekspert | 1 tenant, 1 projekt, 3 kanały, 8 paczek/mies., kolejka akceptacji | 79 zł/mies. |
| Pro | freelancer/konsultant | 1 tenant, 3 projekty, wszystkie kanały, newsletter, strona z formularzem leadów, CRM leadów | 199 zł/mies. |
| Agency | agencja | do 10 tenantów, white-label strony, eksport raportów | 699 zł/mies. |
| Done-for-you | firma | Pro + redakcja przez człowieka | od 1 500 zł/mies. |

Warunki wejścia w SaaS: ≥5 płacących klientów usług, powtarzalny proces onboardingu < 2 h, billing (osobny projekt — poza bieżącym zakresem). Klienci usług są pierwszymi użytkownikami SaaS (migracja na plan Pro lub Done-for-you).

## 3. Playbook pierwszych klientów (etyczny, opt-in, ręczny)
1. Dogfooding (tydz. 1–2): system pracuje dla Twojej marki. Codziennie zatwierdzasz 1 post, co tydzień 1 artykuł i newsletter. To jest portfolio.
2. Lista ciepłych kontaktów (tydz. 1): 30–50 osób, które Cię znają (byli współpracownicy, klienci, znajomi z branży). Bez kupowania baz i scrapowania.
3. Ręczne, spersonalizowane wiadomości 1:1 (max kilka dziennie, każda pisana pod osobę): odniesienie do ich sytuacji, konkretna propozycja (bezpłatny mini-audyt), łatwa możliwość odmowy („jeśli nie temat — daj znać, nie będę wracać”). Szablony z `10_B2B_OUTREACH_SDR.md` traktuj jako punkt wyjścia, nie do wysyłki seryjnej. Cold e-mail do nieznanych osób w PL wymaga zgody na informację handlową — nie wysyłaj.
4. Treść z CTA: każdy post kończy się zaproszeniem do bezpłatnej konsultacji (link do `#kontakt`). Leady trafiają do formularza → `leads.py list`.
5. Bezpłatne mini-audyty (3–5 sztuk): realna wartość, opublikowana za zgodą jako case study.
6. Konsultacja → oferta w 24 h → follow-up po 3 i 7 dniach (`leads.py update --next-at`), potem status `lost` i koniec kontaktu.
7. Polecenia: po każdym udanym projekcie poproś o 1 polecenie i opinię.

## 4. Go-to-market za 0 zł
| Kanał | Narzędzie (darmowe) | Działanie |
|---|---|---|
| LinkedIn osobisty | ręczna publikacja z kolejki | 3–4 posty/tydz., komentarze pisane osobiście pod postami ludzi z branży |
| Strona + blog | Cloudflare Pages | oferta, formularz, artykuły SEO/GEO, `llms.txt`, sitemap |
| Wyszukiwarki | Google Search Console, Bing Webmaster, IndexNow | zgłoszenie sitemap, monitoring fraz |
| Newsletter | Brevo free (300/dzień) | tylko osoby zapisane ze zgodą; co 2 tyg. |
| Społeczności | grupy/Discord, w których już jesteś | pomoc i odpowiedzi zgodnie z regulaminem grupy, bez linkowania w każdym wpisie |
| Open source | GitHub | publiczne przykłady/snippety jako dowód kompetencji |
| Powiadomienia | Telegram bot | info o nowym leadzie — szybka odpowiedź (< 2 h) |

Infrastruktura: GitHub Actions (cron), Supabase Free (leady), Cloudflare Pages/Workers AI free, Gemini/Groq free. Koszt: 0 zł; jedyny opcjonalny wydatek to domena (~50 zł/rok) — zalecany, gdy pojawi się pierwszy przychód.

## 5. Metryki
| Metryka | Źródło | Cel 90 dni |
|---|---|---|
| Opublikowane (zatwierdzone) treści / tydz. | `approve.py list --status approved` | 4+ |
| Wejścia na stronę | Cloudflare Web Analytics (free) | trend rosnący |
| Leady / mies. | `leads.py list` | 8+ |
| Konwersja wizyta → lead | analytics + leads | ≥ 1,5% |
| Lead → konsultacja → oferta → wygrana | statusy w `leads` / lejek w `DASHBOARD.md` | 50% / 60% / 30% |
| Przychód (`won`, PLN) | `leads.value_pln` | 3 klientów, ≥ 5 000 zł |
| Czas odpowiedzi na lead | `lead_events` | < 24 h |
| Subskrybenci newslettera (ze zgodą) | `subscribers` | 100+ |
| Odsetek treści odrzuconych w akceptacji | `APPROVAL.json` | spada → lepsza persona |

Przegląd co tydzień (30 min): lejek, zaległe `next_action`, co z treści przyniosło leady (UTM), korekta tematów i persony w `brand_core/persona.json`.
