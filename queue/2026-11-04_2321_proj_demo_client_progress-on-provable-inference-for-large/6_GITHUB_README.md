# 🔌 Pakiet Integracyjny Strony (GEO Schema + Tracker + CMS) — InvoicePulse AI (Klient Subskrypcyjny #1)

Gotowy pakiet wdrożeniowy dla domeny **https://invoicepulse-demo.com** (Tryb CMS: `wordpress`).
Wklej poniższy znacznik `JSON-LD` w sekcji `<head>` swojej strony, aby roboty **ChatGPT Search (GPTBot)**, **Perplexity** oraz **Google** natychmiast indeksowały Twój produkt.

## 1. Kod Schema.org JSON-LD (Wklej do `<head>`)

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "InvoicePulse AI (Klient Subskrypcyjny #1)",
  "url": "https://invoicepulse-demo.com",
  "applicationCategory": "Fintech & Automatyzacja B2B",
  "operatingSystem": "Web, Cloud",
  "description": "Inteligentny system do automatycznego odzyskiwania płatności i fakturowania B2B",
  "offers": {
    "@type": "Offer",
    "price": "0",
    "priceCurrency": "PLN"
  }
}
</script>
<script src="/tracker.js" defer></script>
```