# 🔌 Pakiet Integracyjny Strony (GEO Schema + Tracker + CMS) — Polsia Zero (Główna Platforma)

Gotowy pakiet wdrożeniowy dla domeny **https://twoja-domena.pl** (Tryb CMS: `github_markdown`).
Wklej poniższy znacznik `JSON-LD` w sekcji `<head>` swojej strony, aby roboty **ChatGPT Search (GPTBot)**, **Perplexity** oraz **Google** natychmiast indeksowały Twój produkt.

## 1. Kod Schema.org JSON-LD (Wklej do `<head>`)

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "Polsia Zero (Główna Platforma)",
  "url": "https://twoja-domena.pl",
  "applicationCategory": "SaaS & AI Growth Platform",
  "operatingSystem": "Web, Cloud",
  "description": "Autonomiczny system wzrostu i marketingu 24/7 dla startupów i SaaS",
  "offers": {
    "@type": "Offer",
    "price": "0",
    "priceCurrency": "PLN"
  }
}
</script>
<script src="/tracker.js" defer></script>
```