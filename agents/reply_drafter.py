"""
Reply drafter (human-in-the-loop).
Drafts a reply to a comment for the owner to review and post manually.
It never posts anything and never schedules or delays anything.
"""

from agents.free_ai_router import has_live_ai_key, ask_free_ai


def draft_reply(comment_text: str, context: str, persona: dict) -> dict:
    persona = persona or {}
    name = persona.get("name", "")
    style = (persona.get("tone_of_voice") or {}).get("style", "rzeczowy i uprzejmy")
    draft = ""
    if has_live_ai_key():
        draft = ask_free_ai(
            f"Piszesz szkic odpowiedzi na komentarz w stylu: {style}. Po polsku, 2-4 zdania, bez linków. "
            "Szkic zostanie przeczytany i ewentualnie opublikowany ręcznie przez autora.",
            f"Kontekst: {context}\nKomentarz: {comment_text}",
        )
    if not draft:
        draft = (
            f"Dziękuję za komentarz! Odnośnie „{comment_text.strip()[:200]}” — "
            f"w kontekście: {context.strip()[:200]} chętnie rozwinę temat. "
            "Daj znać, który aspekt jest dla Ciebie najważniejszy."
        )
        if name:
            draft += f" — {name}"
    return {"draft": draft.strip(), "status": "pending_approval"}
