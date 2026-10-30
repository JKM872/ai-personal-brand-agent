import pathlib, re
p = pathlib.Path("db/schema.sql")
s = p.read_bytes().decode("utf-8", errors="replace")
cut = s.find("-- 6. Tenanci, leady")
if cut != -1:
    s = s[:cut].rstrip() + "\n"
s = re.sub(r"followup_comment TEXT, --[^\n]*", "followup_comment TEXT, -- Szkic komentarza z linkiem do ręcznego użycia", s)
s = re.sub(r"-- 3\. Kolejka komentarzy[^\n]*", "-- 3. Kolejka szkiców odpowiedzi na komentarze (publikuje człowiek, ręcznie)", s)
s = re.sub(r"reply_at TIMESTAMP WITH TIME ZONE NOT NULL, --[^\n]*", "reply_at TIMESTAMP WITH TIME ZONE, -- kiedy autor opublikował odpowiedź (opcjonalnie)", s)
mig = pathlib.Path("db/migrations/002_leads_tenants.sql").read_text(encoding="utf-8").split("\n", 1)[1]
s += "\n-- 6. Tenanci, leady i zgody (te same definicje co db/migrations/002_leads_tenants.sql)\n" + mig
p.write_text(s, encoding="utf-8", newline="")
print("Anti-Ban" in s, "Human-like" in s, "NOT NULL, -- Losowy" in s)
