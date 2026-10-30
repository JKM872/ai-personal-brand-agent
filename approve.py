"""
Kolejka akceptacji człowieka (CLI).

  python approve.py list [--status pending_approval|approved|rejected|legacy]
  python approve.py show <paczka>
  python approve.py approve <paczka> [--only website_article,linkedin] [--note "..."]
  python approve.py reject <paczka> [--note "..."]

<paczka> = nazwa folderu w queue/ lub jej unikalny prefiks.
Approve właściciela (tenant is_owner) kopiuje artykuł do public/articles/ (bez nadpisywania),
odświeża sitemap.xml, llms.txt, listę artykułów w blog.html i archiwum newslettera.
Zewnętrzne kanały wysyła dopiero `python publish.py`.
Kody wyjścia: 0 ok, 2 brak/niejednoznaczna paczka lub złe argumenty, 3 uszkodzony APPROVAL.json.
"""

import argparse
import html
import json
import re
import sys
from datetime import datetime
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_DIR = Path(__file__).parent.resolve()
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

ITEMS = ("website_article", "linkedin", "newsletter", "webhook", "telegram")
ART_START, ART_END = "<!-- ARTICLES:START -->", "<!-- ARTICLES:END -->"


class ApprovalError(Exception):
    def __init__(self, msg, code):
        super().__init__(msg)
        self.code = code


def is_owner_tenant(tenant_id: str, base: Path) -> bool:
    from saas_core.tenants import load_tenant
    try:
        return load_tenant(tenant_id or "default", base)["is_owner"] is True
    except ValueError:
        return False


def new_approval(folder: Path) -> dict:
    parts = folder.name.split("_")
    project_id = "_".join(parts[2:4]) if len(parts) >= 4 else "proj_default"
    return {"status": "legacy", "tenant_id": "default", "project_id": project_id,
            "created_at": None, "decided_at": None, "decided_by": None, "note": "",
            "items": {k: "pending" for k in ITEMS}, "published": {}}


def read_approval(folder: Path):
    """Returns (data, exists). Raises ApprovalError(code=3) on corrupt JSON."""
    p = folder / "APPROVAL.json"
    if not p.exists():
        return new_approval(folder), False
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("nie jest obiektem JSON")
        return data, True
    except Exception as e:
        raise ApprovalError(f"[ERROR] Uszkodzony {p}: {e}", 3)


def write_approval(folder: Path, data: dict) -> None:
    (folder / "APPROVAL.json").write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def bundles(base: Path) -> list:
    q = base / "queue"
    return sorted([d for d in q.iterdir() if d.is_dir()], key=lambda d: d.name) if q.exists() else []


def find_bundle(base: Path, ref: str) -> Path:
    all_b = bundles(base)
    exact = [b for b in all_b if b.name == ref]
    if exact:
        return exact[0]
    matches = [b for b in all_b if b.name.startswith(ref)]
    if not matches:
        raise ApprovalError(f"Nie znaleziono paczki: {ref}", 2)
    if len(matches) > 1:
        raise ApprovalError(f"Niejednoznaczny prefiks {ref}: " + ", ".join(m.name for m in matches[:5]), 2)
    return matches[0]


def _slug(text: str) -> str:
    from agents.geo_seo_engine import slugify
    return slugify(text) or "artykul"


def _article_slug(md: str, folder: Path) -> str:
    for line in md.splitlines():
        if line.startswith("# "):
            return _slug(line[2:])
    return _slug(folder.name)


def _unique_path(directory: Path, slug: str, ext: str) -> Path:
    p = directory / f"{slug}{ext}"
    n = 2
    while p.exists():
        p = directory / f"{slug}-{n}{ext}"
        n += 1
    return p


def _md_to_html(md: str) -> str:
    out = []
    for line in md.splitlines():
        esc = html.escape(line)
        if line.startswith("### "):
            out.append(f"<h3>{html.escape(line[4:])}</h3>")
        elif line.startswith("## "):
            out.append(f"<h2>{html.escape(line[3:])}</h2>")
        elif line.startswith("# "):
            out.append(f"<h1>{html.escape(line[2:])}</h1>")
        elif line.strip():
            out.append(f"<p>{esc}</p>")
    return "\n".join(out)


def _owner_profile(base: Path) -> dict:
    try:
        projects = json.loads((base / "saas_core" / "projects.json").read_text(encoding="utf-8"))
        for p in projects:
            if p.get("tenant_id", "default") == "default":
                return p
    except Exception:
        pass
    return {}


def refresh_blog_list(public: Path) -> None:
    blog = public / "blog.html"
    if not blog.exists():
        return
    arts = sorted((public / "articles").glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)
    items = []
    for a in arts[:50]:
        title = a.stem.replace("-", " ")
        for line in a.read_text(encoding="utf-8").splitlines():
            if line.startswith("# "):
                title = line[2:].strip()
                break
        items.append(f'<li><a href="/articles/{html.escape(a.name)}">{html.escape(title)}</a></li>')
    block = f'{ART_START}\n<ul class="article-list">\n' + "\n".join(items) + f"\n</ul>\n{ART_END}"
    txt = blog.read_text(encoding="utf-8")
    if ART_START in txt and ART_END in txt:
        s, e = txt.index(ART_START), txt.index(ART_END) + len(ART_END)
        txt = txt[:s] + block + txt[e:]
    else:
        anchor = txt.find("<!-- LEADFORM:START -->")
        if anchor == -1:
            anchor = txt.rfind("</body>")
        txt = txt[:anchor] + block + "\n" + txt[anchor:]
    blog.write_text(txt, encoding="utf-8")


def publish_owner_article(folder: Path, base: Path) -> str:
    """Copies the article into public/ and refreshes local site files. Returns the new path."""
    src = folder / "0_WEBSITE_SEO_ARTICLE.md"
    if not src.exists():
        raise ApprovalError(f"Brak {src.name} w paczce {folder.name}", 2)
    md = src.read_text(encoding="utf-8")
    public = base / "public"
    art_dir = public / "articles"
    art_dir.mkdir(parents=True, exist_ok=True)
    slug = _article_slug(md, folder)
    dest = _unique_path(art_dir, slug, ".md")
    dest.write_text(md, encoding="utf-8")

    nl = folder / "4_NEWSLETTER_EDITION.md"
    if nl.exists():
        nl_dir = public / "newsletter"
        nl_dir.mkdir(parents=True, exist_ok=True)
        archive = _unique_path(nl_dir, f"{datetime.now():%Y-%m-%d}-{dest.stem}", ".html")
        body = _md_to_html(nl.read_text(encoding="utf-8"))
        archive.write_text(f'<!DOCTYPE html>\n<html lang="pl"><head><meta charset="utf-8"><title>Newsletter</title></head>'
                           f'<body>\n{body}\n<p><a href="/">Strona główna</a></p></body></html>\n', encoding="utf-8")

    from agents.geo_seo_engine import generate_llms_txt
    from saas_core.tenants import load_tenant
    profile = dict(_owner_profile(base))
    profile["website_url"] = load_tenant("default", base)["site_url"]
    generate_llms_txt(profile, public / "llms.txt")
    refresh_blog_list(public)
    try:
        from web_generator import build_public_site
        build_public_site(base)
    except Exception as e:
        print(f"[WARN] Nie odświeżono strony ofertowej/sitemap: {e}")
    return str(dest.relative_to(base))


def cmd_list(base: Path, status: str = None) -> int:
    rows = 0
    for b in bundles(base):
        try:
            data, exists = read_approval(b)
            st = data.get("status", "pending_approval") if exists else "legacy"
        except ApprovalError:
            st = "error"
        if status and st != status:
            continue
        rows += 1
        print(f"{st:17} {b.name}")
    if not rows:
        print("(brak paczek)")
    return 0


def cmd_show(base: Path, ref: str) -> int:
    b = find_bundle(base, ref)
    data, exists = read_approval(b)
    print(f"Paczka: {b.name}{'' if exists else ' (legacy — brak APPROVAL.json)'}")
    print(json.dumps(data, indent=2, ensure_ascii=False))
    print("Pliki: " + ", ".join(sorted(p.name for p in b.iterdir())))
    return 0


def cmd_decide(base: Path, ref: str, decision: str, only: str = None, note: str = "") -> int:
    b = find_bundle(base, ref)
    data, _ = read_approval(b)
    items = data.setdefault("items", {k: "pending" for k in ITEMS})
    chosen = list(ITEMS)
    if only:
        chosen = [x.strip() for x in only.split(",") if x.strip()]
        bad = [x for x in chosen if x not in ITEMS]
        if bad:
            raise ApprovalError(f"Nieznane kanały: {', '.join(bad)} (dozwolone: {', '.join(ITEMS)})", 2)
    now = datetime.now().isoformat(timespec="seconds")
    if decision == "approved":
        for k in ITEMS:
            items[k] = "approved" if k in chosen else ("rejected" if only else items.get(k, "pending"))
    else:
        for k in ITEMS:
            items[k] = "rejected"
    data.update({"status": decision, "decided_at": now, "decided_by": "owner", "note": note or data.get("note", "")})
    data.setdefault("published", {})

    if decision == "approved" and items.get("website_article") == "approved" \
            and data["published"].get("website_article", {}).get("status") != "ok" \
            and is_owner_tenant(data.get("tenant_id", "default"), base):
        path = publish_owner_article(b, base)
        data["published"]["website_article"] = {"status": "ok", "via": "approve", "at": now, "path": path}
        print(f"🌐 Artykuł opublikowany lokalnie: {path} (commit/push wykonuje użytkownik lub CI)")
    write_approval(b, data)
    print(f"{decision}: {b.name}")
    if decision == "approved":
        print("Następny krok dla kanałów zewnętrznych: python publish.py")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Kolejka akceptacji paczek treści")
    ap.add_argument("--base-dir", default=str(BASE_DIR), help=argparse.SUPPRESS)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("list"); p.add_argument("--status")
    p = sub.add_parser("show"); p.add_argument("bundle")
    p = sub.add_parser("approve"); p.add_argument("bundle"); p.add_argument("--only"); p.add_argument("--note", default="")
    p = sub.add_parser("reject"); p.add_argument("bundle"); p.add_argument("--note", default="")
    args = ap.parse_args(argv)
    base = Path(args.base_dir).resolve()
    try:
        if args.cmd == "list":
            return cmd_list(base, args.status)
        if args.cmd == "show":
            return cmd_show(base, args.bundle)
        if args.cmd == "approve":
            return cmd_decide(base, args.bundle, "approved", args.only, args.note)
        return cmd_decide(base, args.bundle, "rejected", None, args.note)
    except ApprovalError as e:
        print(str(e), file=sys.stderr)
        return e.code


if __name__ == "__main__":
    sys.exit(main())
