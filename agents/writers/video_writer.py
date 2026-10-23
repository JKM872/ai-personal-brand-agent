"""
Video & Shorts Script Ghostwriter Agent (Polsia Multi-Tenant SaaS).
Generates a high-retention 60-second vertical video script (YouTube Shorts, Reels, TikTok)
tailored 100% in Polish to the active client project, pain point, and value proposition.
"""

from agents.geo_seo_engine import load_product_profile, derive_seo_headline

def generate_video_content(topic, persona):
    profile = load_product_profile()
    pname = profile.get("product_name", "Polsia Zero")
    paud = profile.get("target_audience", "właścicieli firm")
    pproblem = profile.get("primary_problem_solved", "")
    features = profile.get("key_features", ["Pełna automatyzacja w chmurze"])
    meta = derive_seo_headline(profile, topic)

    script = f"""# 🎬 Scenariusz Wideo 60s (Shorts / Reels / TikTok) — {pname}

**Temat odcinka:** {meta['short_topic']}
**Grupa docelowa:** {paud}
**Styl narracji:** {persona.get('active_style', 'analityk_danych')}

---

| Sekunda | Obraz / B-Roll na ekranie | Lektor (Co mówisz do kamery) |
|---|---|---|
| **0:00 - 0:04** | **Mocny Hook:** Zbliżenie na twarz, dynamiczny napis na środku ekranu: *"PRZESTAŃ ROBIĆ TO RĘCZNIE W 2026!"* | "Większość firm z grupy {paud} traci kilkanaście godzin tygodniowo na proces, który dziś można zautomatyzować w 5 minut." |
| **0:05 - 0:16** | Przebitka na konkretny wskaźnik na ekranie: *{meta['metric_highlight']}*. | "Najnowsze dane z rynku pokazują jasno: {meta['metric_highlight']}." |
| **0:17 - 0:34** | Pokazanie ekranu platformy **{pname}** i jej głównego panelu. | "Dlatego stworzyliśmy {pname}. Nasz system rozwiązuje główny ból: {pproblem}" |
| **0:35 - 0:48** | Szybkie wyliczenie na ekranie 2 kluczowych korzyści z zielonymi ikonami ✅. | "Po pierwsze: {features[0] if len(features) > 0 else 'Działa 24/7'}. Po drugie: masz pełną kontrolę i zero ryzyka blokad." |
| **0:49 - 0:58** | Wskazanie na opis profilu / pierwszy komentarz. Napis: *"Link w komentarzu!"* | "Chcesz zobaczyć, jak to zadziała w Twojej firmie? Sprawdź pierwszy komentarz pod filmem i przetestuj {pname}!" |
"""
    return {"video_script": script.strip()}
