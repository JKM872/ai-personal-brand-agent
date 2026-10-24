# 🔌 Pakiet Integracyjny Strony (GEO Schema + Tracker + CMS) — Autonoma AI (Główna Platforma)

Gotowy pakiet wdrożeniowy dla domeny **https://twoja-domena.pl** (Tryb CMS: `github_markdown`).
Wklej poniższy znacznik `JSON-LD` w sekcji `<head>` swojej strony, aby roboty **ChatGPT Search (GPTBot)**, **Perplexity** oraz **Google** natychmiast indeksowały Twój produkt.

## 1. Kod Schema.org JSON-LD (Wklej do `<head>`)

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "Autonoma AI (Główna Platforma)",
  "url": "https://twoja-domena.pl",
  "applicationCategory": "SaaS & AI Workforce Platform",
  "operatingSystem": "Web, Cloud",
  "description": "Autonomiczny system wzrostu i marketingu 24/7 napędzany 12 wirtualnymi pracownikami AI",
  "offers": {
    "@type": "Offer",
    "price": "0",
    "priceCurrency": "PLN"
  }
}
</script>
<script src="/tracker.js" defer></script>
```