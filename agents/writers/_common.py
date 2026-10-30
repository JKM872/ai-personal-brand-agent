"""Shared helpers for writers: explicit project profile + brand persona of the tenant."""

from agents.geo_seo_engine import load_product_profile, derive_seo_headline

QUALITATIVE_EFFECT = "mniej ręcznej, powtarzalnej pracy i więcej czasu na klientów"


def resolve_profile(project=None) -> dict:
    """Explicit project dict wins; falls back to the legacy single-profile loader."""
    return project if isinstance(project, dict) and project else load_product_profile()


def headline(profile: dict, topic) -> dict:
    """derive_seo_headline without invented metrics: empty metric -> qualitative wording."""
    meta = dict(derive_seo_headline(profile, topic))
    if not meta.get("metric_highlight"):
        meta["metric_highlight"] = QUALITATIVE_EFFECT
    return meta


def brand_prompt(brand=None) -> str:
    """Short system-prompt addition describing the tenant's voice."""
    if not isinstance(brand, dict) or not brand:
        return ""
    tone = brand.get("tone_of_voice") or {}
    parts = []
    if brand.get("name"):
        parts.append(f"Piszesz w imieniu: {brand['name']}.")
    if tone.get("style"):
        parts.append(f"Styl: {tone['style']}.")
    if tone.get("rules"):
        parts.append("Zasady: " + " ".join(tone["rules"]))
    if brand.get("content_pillars"):
        parts.append("Filary treści: " + ", ".join(brand["content_pillars"]) + ".")
    if brand.get("target_audience"):
        parts.append(f"Odbiorcy: {brand['target_audience']}.")
    parts.append("Nie wymyślaj liczb ani badań; w razie potrzeby wstaw [UZUPEŁNIJ: źródło].")
    return " " + " ".join(parts)
