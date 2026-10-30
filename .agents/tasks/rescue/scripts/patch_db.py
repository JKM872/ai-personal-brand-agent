import pathlib, re
p = pathlib.Path("db/supabase_client.py")
s = p.read_text(encoding="utf-8")
s = s.replace("# Seed 3 distinct strategic personas with realistic initial metrics",
              "# Seed 3 personas with neutral stats (no invented clicks). Existing rows are kept;\n"
              "            # reset via: python -m agents.analyst_agent --reset-stats --yes")
s = s.replace("benchmarkami i wyliczeniami. Zero lania wody.', 5, 92, 7, 25.4, ?)", "benchmarkami i wyliczeniami. Zero lania wody.', 0, 0, 0, 1.0, ?)")
s = s.replace("wymierne rezultaty.', 4, 64, 4, 21.0, ?)", "wymierne rezultaty.', 0, 0, 0, 1.0, ?)")
s = s.replace("większość firm.', 3, 39, 2, 16.3, ?)", "większość firm.', 0, 0, 0, 1.0, ?)")
a = s.index("            # Fix any legacy zero rows")
b = s.index("            conn.commit()", a)
s = s[:a] + s[b:]
s = s.replace(
    'params={"is_active": "eq.true", "limit": str(limit)})',
    'params={"is_active": "eq.true", "consent_at": "not.is.null", "unsubscribed_at": "is.null", "limit": str(limit)})')
s = s.replace(
    '            rows = conn.execute("SELECT * FROM subscribers WHERE is_active = 1 LIMIT ?", (limit,)).fetchall()',
    '            cols = [r[1] for r in conn.execute("PRAGMA table_info(subscribers)").fetchall()]\n'
    '            if "consent_at" not in cols or "unsubscribed_at" not in cols:\n'
    '                return []\n'
    '            rows = conn.execute("SELECT * FROM subscribers WHERE is_active = 1 AND consent_at IS NOT NULL "\n'
    '                                "AND unsubscribed_at IS NULL LIMIT ?", (limit,)).fetchall()')
p.write_text(s, encoding="utf-8", newline="")
print("92, 7" in s, "legacy zero" in s, "consent_at IS NOT NULL" in s)
