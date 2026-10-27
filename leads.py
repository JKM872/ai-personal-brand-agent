"""
Lejek klientów (CRM) — prosty CLI na tabeli leads (SQLite lokalnie, Supabase opcjonalnie).

  python leads.py add --name "Jan" --email jan@example.com [--company --service --message --source]
  python leads.py list [--status new] [--tenant default]
  python leads.py show <id-prefix>
  python leads.py update <id-prefix> [--status contacted] [--value 2900] [--next-action "..."] [--next-at 2026-11-05]
  python leads.py note <id-prefix> "tekst"
  python leads.py export [--out exports/leads.csv]
  python leads.py sync            # Supabase -> SQLite (wymaga SUPABASE_URL + SUPABASE_KEY service role)
"""
import argparse
import csv
import sys
from datetime import datetime
from pathlib import Path

from crm.validation import LEAD_STATUSES, SERVICES, validate_email
from db.supabase_client import db

BASE_DIR = Path(__file__).parent.resolve()


def _err(msg: str, code: int = 2):
    print(msg, file=sys.stderr)
    sys.exit(code)


def cmd_add(a):
    email = (a.email or "").strip().lower()
    if not validate_email(email):
        _err(f"[ERROR] Nieprawidłowy e-mail: {a.email}")
    name = (a.name or "").strip()
    if not 1 <= len(name) <= 100:
        _err("[ERROR] --name jest wymagane (1–100 znaków)")
    if a.service and a.service not in SERVICES:
        _err(f"[ERROR] --service musi być jednym z: {', '.join(SERVICES)}")
    lead_id = db.insert_lead({
        "name": name, "email": email, "company": a.company, "service_interest": a.service,
        "message": a.message, "source_utm": a.source or "manual",
        "consent_text_version": "manual", "status": "new",
    })
    print(lead_id)


def cmd_list(a):
    if a.status and a.status not in LEAD_STATUSES:
        _err(f"[ERROR] Nieznany status: {a.status} (dozwolone: {', '.join(LEAD_STATUSES)})")
    rows = db.list_leads(tenant_id=a.tenant, status=a.status)
    if not rows:
        print("Brak leadów.")
        return
    for r in rows:
        print(f"{r['id'][:8]}  {r['status']:<10} {(r.get('created_at') or '')[:10]}  {r['name']} <{r['email']}>"
              f"  {r.get('service_interest') or '-'}  {r.get('value_pln') or ''}")


def _get_or_exit(prefix):
    lead = db.get_lead(prefix)
    if not lead:
        _err(f"[ERROR] Nie znaleziono jednoznacznie leada o id {prefix!r}")
    return lead


def cmd_show(a):
    lead = _get_or_exit(a.id)
    for k, v in lead.items():
        if k != "events":
            print(f"{k:>20}: {v if v is not None else ''}")
    print("Historia:")
    for e in lead["events"]:
        print(f"  {e['created_at'][:16]} {e['event']} {e.get('from_status') or ''} -> {e.get('to_status') or ''} {e.get('note') or ''}")


def cmd_update(a):
    fields = {}
    if a.status:
        if a.status not in LEAD_STATUSES:
            _err(f"[ERROR] Nieznany status: {a.status} (dozwolone: {', '.join(LEAD_STATUSES)})")
        fields["status"] = a.status
    if a.value is not None:
        fields["value_pln"] = a.value
    if a.next_action:
        fields["next_action"] = a.next_action
    if a.next_at:
        try:
            datetime.strptime(a.next_at, "%Y-%m-%d")
        except ValueError:
            _err("[ERROR] --next-at w formacie YYYY-MM-DD")
        fields["next_action_at"] = a.next_at
    if not fields:
        _err("[ERROR] Podaj co najmniej jedno pole do zmiany")
    lead = _get_or_exit(a.id)
    db.update_lead(lead["id"], **fields)
    print(f"Zaktualizowano {lead['id'][:8]}")


def cmd_note(a):
    lead = _get_or_exit(a.id)
    db.add_lead_note(lead["id"], a.text)
    print(f"Dodano notatkę do {lead['id'][:8]}")


def cmd_export(a):
    out = Path(a.out) if a.out else BASE_DIR / "exports" / f"leads_{datetime.now():%Y-%m-%d}.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    rows = db.list_leads()
    cols = ["id", "tenant_id", "status", "name", "email", "company", "service_interest", "message",
            "source_utm", "consent_at", "value_pln", "next_action", "next_action_at", "notes", "created_at"]
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    print(f"Wyeksportowano {len(rows)} leadów do {out}")


def cmd_sync(a):
    from agents.free_ai_router import _load_key
    if not (_load_key("SUPABASE_URL") and _load_key("SUPABASE_KEY")):
        print("[WARN] sync wymaga SUPABASE_URL i SUPABASE_KEY (service role) — pomijam")
        return
    try:
        remote = db.fetch_remote_leads()
    except Exception as e:
        _err(f"[ERROR] Supabase: {e}", 1)
    added = sum(1 for r in remote if db.upsert_local_lead(r))
    print(f"Zsynchronizowano: {added} nowych z {len(remote)}")


def main(argv=None):
    p = argparse.ArgumentParser(description="Lejek klientów (leady)")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("add"); s.add_argument("--name", required=True); s.add_argument("--email", required=True)
    s.add_argument("--company"); s.add_argument("--service"); s.add_argument("--message"); s.add_argument("--source")
    s.set_defaults(fn=cmd_add)
    s = sub.add_parser("list"); s.add_argument("--status"); s.add_argument("--tenant"); s.set_defaults(fn=cmd_list)
    s = sub.add_parser("show"); s.add_argument("id"); s.set_defaults(fn=cmd_show)
    s = sub.add_parser("update"); s.add_argument("id"); s.add_argument("--status"); s.add_argument("--value", type=float)
    s.add_argument("--next-action", dest="next_action"); s.add_argument("--next-at", dest="next_at"); s.set_defaults(fn=cmd_update)
    s = sub.add_parser("note"); s.add_argument("id"); s.add_argument("text"); s.set_defaults(fn=cmd_note)
    s = sub.add_parser("export"); s.add_argument("--out"); s.set_defaults(fn=cmd_export)
    s = sub.add_parser("sync"); s.set_defaults(fn=cmd_sync)
    a = p.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
