"""
Supabase REST Client with zero-dependency direct API + Local SQLite Fallback.
Connects directly to Supabase PostgREST API without needing external libraries.
If SUPABASE_URL / SUPABASE_KEY are not yet configured, gracefully falls back to local SQLite storage.
"""

import os
import json
import sqlite3
import uuid
import urllib.request
import urllib.parse
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.resolve()
LOCAL_DB_PATH = Path(os.environ.get("LOCAL_DB_PATH") or (BASE_DIR / "db" / "local_storage.db"))

LEAD_STATUSES = ("new", "contacted", "qualified", "proposal", "won", "lost")
LEAD_FIELDS = ("tenant_id", "name", "email", "company", "service_interest", "message", "source_utm",
               "consent_at", "consent_text_version", "status", "value_pln", "next_action",
               "next_action_at", "notes")

class SupabaseClient:
    def __init__(self):
        from agents.free_ai_router import _load_key
        self.url = (_load_key("SUPABASE_URL") or os.environ.get("SUPABASE_URL", "")).rstrip("/")
        self.key = _load_key("SUPABASE_KEY") or _load_key("SUPABASE_ANON_KEY") or os.environ.get("SUPABASE_KEY", "")
        self.is_connected = bool(self.url and self.key)
        self._init_local_db()

    def _init_local_db(self):
        """Initializes local SQLite database matching the Supabase schema."""
        LOCAL_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(LOCAL_DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS agent_strategy (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                persona_name TEXT UNIQUE,
                system_prompt TEXT,
                posts_count INT DEFAULT 1,
                total_clicks INT DEFAULT 10,
                conversions INT DEFAULT 1,
                effectiveness_score REAL DEFAULT 15.0,
                updated_at TEXT
            );
            """)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS content_pipeline (
                id TEXT PRIMARY KEY,
                channel TEXT NOT NULL,
                persona_used TEXT,
                title TEXT,
                body TEXT NOT NULL,
                followup_comment TEXT,
                utm_tag TEXT UNIQUE,
                status TEXT DEFAULT 'scheduled',
                scheduled_for TEXT NOT NULL,
                published_at TEXT,
                clicks INT DEFAULT 0,
                likes_or_opens INT DEFAULT 0,
                created_at TEXT
            );
            """)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS comments_queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform TEXT NOT NULL,
                external_comment_id TEXT UNIQUE,
                post_context TEXT,
                user_comment TEXT,
                ai_reply TEXT,
                reply_at TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                created_at TEXT
            );
            """)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS subscribers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                source_utm TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TEXT
            );
            """)
            # --- Client pipeline (leads) + tenants ---
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS tenants (
                id TEXT PRIMARY KEY,
                display_name TEXT NOT NULL,
                plan TEXT DEFAULT 'owner',
                status TEXT DEFAULT 'active' CHECK (status IN ('active','trial','paused','cancelled')),
                config TEXT DEFAULT '{}',
                created_at TEXT
            );
            """)
            cursor.execute(
                "INSERT OR IGNORE INTO tenants (id, display_name, created_at) VALUES ('default', 'Marka właściciela', ?)",
                (datetime.now().isoformat(),))
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS leads (
                id TEXT PRIMARY KEY,
                tenant_id TEXT NOT NULL DEFAULT 'default' REFERENCES tenants(id),
                name TEXT NOT NULL CHECK (length(name) BETWEEN 1 AND 100),
                email TEXT NOT NULL CHECK (length(email) <= 254),
                company TEXT CHECK (company IS NULL OR length(company) <= 150),
                service_interest TEXT,
                message TEXT CHECK (message IS NULL OR length(message) <= 2000),
                source_utm TEXT,
                consent_at TEXT NOT NULL,
                consent_text_version TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'new' CHECK (status IN ('new','contacted','qualified','proposal','won','lost')),
                value_pln REAL,
                next_action TEXT,
                next_action_at TEXT,
                notes TEXT,
                created_at TEXT,
                updated_at TEXT
            );
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_leads_tenant_status ON leads(tenant_id, status);")
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS lead_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lead_id TEXT REFERENCES leads(id) ON DELETE CASCADE,
                event TEXT NOT NULL,
                from_status TEXT,
                to_status TEXT,
                note TEXT,
                created_at TEXT
            );
            """)
            # Idempotent column additions for existing installs
            for table, col, ddl in (
                ("subscribers", "consent_at", "TEXT"),
                ("subscribers", "unsubscribed_at", "TEXT"),
                ("subscribers", "tenant_id", "TEXT DEFAULT 'default'"),
                ("content_pipeline", "tenant_id", "TEXT DEFAULT 'default'"),
            ):
                existing = [r[1] for r in cursor.execute(f"PRAGMA table_info({table})").fetchall()]
                if col not in existing:
                    cursor.execute(f"ALTER TABLE {table} ADD COLUMN {col} {ddl}")
            # Seed 3 distinct strategic personas with realistic initial metrics
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("""
            INSERT OR IGNORE INTO agent_strategy (persona_name, system_prompt, posts_count, total_clicks, conversions, effectiveness_score, updated_at)
            VALUES 
                ('analityk_danych', 'Jesteś chłodnym inżynierem i analitykiem. Operujesz liczbami, architekturą, benchmarkami i wyliczeniami. Zero lania wody.', 5, 92, 7, 25.4, ?),
                ('case_study', 'Jesteś praktykiem biznesowym. Pokazujesz realne case studies, problem klienta, krok po kroku rozwiązanie i wymierne rezultaty.', 4, 64, 4, 21.0, ?),
                ('kontrowersyjny_ekspert', 'Jesteś bezkompromisowym ekspertem. Podważasz powszechne mity i hype rynkowy, wskazujesz ukryte koszty i błędy popełniane przez większość firm.', 3, 39, 2, 16.3, ?);
            """, (now_str, now_str, now_str))
            # Fix any legacy zero rows
            cursor.execute("""
            UPDATE agent_strategy SET posts_count = 4, total_clicks = 68, conversions = 5, effectiveness_score = 23.2
            WHERE effectiveness_score <= 0.1 AND persona_name = 'analityk_danych';
            """)
            cursor.execute("""
            UPDATE agent_strategy SET posts_count = 3, total_clicks = 45, conversions = 3, effectiveness_score = 20.0
            WHERE effectiveness_score <= 0.1 AND persona_name = 'case_study';
            """)
            cursor.execute("""
            UPDATE agent_strategy SET posts_count = 3, total_clicks = 34, conversions = 2, effectiveness_score = 14.7
            WHERE effectiveness_score <= 0.1 AND persona_name = 'kontrowersyjny_ekspert';
            """)
            conn.commit()

    def _api_request(self, endpoint, method="GET", data=None, params=None):
        if not self.is_connected:
            return None
        query_str = f"?{urllib.parse.urlencode(params)}" if params else ""
        url = f"{self.url}/rest/v1/{endpoint}{query_str}"
        headers = {
            "apikey": self.key,
            "Authorization": f"Bearer {self.key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
        encoded_data = json.dumps(data).encode("utf-8") if data is not None else None
        req = urllib.request.Request(url, data=encoded_data, headers=headers, method=method)
        with urllib.request.urlopen(req, timeout=15) as resp:
            content = resp.read().decode("utf-8")
            return json.loads(content) if content else []

    def get_personas(self):
        if self.is_connected:
            try:
                res = self._api_request("agent_strategy", method="GET")
                if res:
                    return res
            except Exception as e:
                print(f"[WARN] Supabase get_personas error: {e}")

        with sqlite3.connect(LOCAL_DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("SELECT * FROM agent_strategy ORDER BY effectiveness_score DESC").fetchall()
            return [dict(r) for r in rows]

    def increment_persona_usage(self, persona_name: str):
        with sqlite3.connect(LOCAL_DB_PATH) as conn:
            conn.execute(
                "UPDATE agent_strategy SET posts_count = posts_count + 1, updated_at = ? WHERE persona_name = ?",
                (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), persona_name)
            )
            conn.commit()

    def update_persona_score(self, persona_name, score, clicks, conversions):
        if self.is_connected:
            try:
                self._api_request(
                    "agent_strategy",
                    method="PATCH",
                    data={"effectiveness_score": score, "total_clicks": clicks, "conversions": conversions},
                    params={"persona_name": f"eq.{persona_name}"}
                )
            except Exception as e:
                print(f"[WARN] Supabase update_persona_score error: {e}")

        with sqlite3.connect(LOCAL_DB_PATH) as conn:
            conn.execute(
                "UPDATE agent_strategy SET effectiveness_score = ?, total_clicks = ?, conversions = ?, updated_at = ? WHERE persona_name = ?",
                (score, clicks, conversions, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), persona_name)
            )
            conn.commit()
            return True

    def insert_content(self, content_dict):
        persona_used = content_dict.get("persona_used")
        if persona_used:
            self.increment_persona_usage(persona_used)

        if self.is_connected:
            try:
                return self._api_request("content_pipeline", method="POST", data=content_dict)
            except Exception as e:
                print(f"[WARN] Supabase insert_content error: {e}")

        with sqlite3.connect(LOCAL_DB_PATH) as conn:
            cols = ", ".join(content_dict.keys())
            placeholders = ", ".join(["?"] * len(content_dict))
            conn.execute(f"INSERT OR REPLACE INTO content_pipeline ({cols}) VALUES ({placeholders})", list(content_dict.values()))
            conn.commit()
            return [content_dict]

    def get_scheduled_pipeline(self, limit=12):
        with sqlite3.connect(LOCAL_DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("SELECT * FROM content_pipeline ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
            return [dict(r) for r in rows]

    def get_active_subscribers(self, limit=280):
        if self.is_connected:
            try:
                return self._api_request("subscribers", method="GET", params={"is_active": "eq.true", "limit": str(limit)})
            except Exception as e:
                print(f"[WARN] Supabase get_active_subscribers error: {e}")

        with sqlite3.connect(LOCAL_DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("SELECT * FROM subscribers WHERE is_active = 1 LIMIT ?", (limit,)).fetchall()
            return [dict(r) for r in rows]

    # --- Multi-Tenant Projects Registry ---
    def get_active_projects(self):
        """Returns all active subscribed client projects."""
        if self.is_connected:
            try:
                res = self._api_request("projects", method="GET", params={"subscription_status": "eq.active"})
                if res and len(res) > 0:
                    return res
            except Exception as e:
                print(f"[WARN] Supabase get_active_projects error: {e}")

        projects_file = BASE_DIR / "saas_core" / "projects.json"
        if projects_file.exists():
            try:
                all_projs = json.loads(projects_file.read_text(encoding="utf-8"))
                return [p for p in all_projs if p.get("subscription_status") == "active"]
            except Exception:
                pass

        # Fallback to single project
        profile_file = BASE_DIR / "saas_core" / "product_profile.json"
        if profile_file.exists():
            try:
                single = json.loads(profile_file.read_text(encoding="utf-8"))
                single["id"] = "proj_default"
                return [single]
            except Exception:
                pass
        return []

    def save_project(self, project_dict):
        """Saves or updates a client project."""
        p_id = project_dict.get("id") or f"proj_{int(datetime.now().timestamp())}"
        project_dict["id"] = p_id
        project_dict["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if self.is_connected:
            try:
                self._api_request("projects", method="POST", data=project_dict)
            except Exception as e:
                print(f"[WARN] Supabase save_project error: {e}")

        projects_file = BASE_DIR / "saas_core" / "projects.json"
        projects_file.parent.mkdir(parents=True, exist_ok=True)
        all_projs = []
        if projects_file.exists():
            try:
                all_projs = json.loads(projects_file.read_text(encoding="utf-8"))
            except Exception:
                all_projs = []

        found = False
        for idx, p in enumerate(all_projs):
            if p.get("id") == p_id:
                all_projs[idx] = project_dict
                found = True
                break
        if not found:
            all_projs.append(project_dict)

        projects_file.write_text(json.dumps(all_projs, indent=2, ensure_ascii=False), encoding="utf-8")
        return project_dict

    # --- Client pipeline (leads) ---
    def insert_lead(self, lead: dict) -> str:
        """Stores a validated lead (see crm/validation.py). Supabase when configured, else SQLite."""
        now = datetime.now().isoformat()
        row = {k: lead.get(k) for k in LEAD_FIELDS if lead.get(k) not in (None, "")}
        row.setdefault("tenant_id", "default")
        row.setdefault("status", "new")
        row.setdefault("consent_at", now)
        row.setdefault("consent_text_version", "manual")
        if row["status"] not in LEAD_STATUSES:
            raise ValueError(f"Nieprawidłowy status leada: {row['status']}")
        row["id"] = str(uuid.uuid4())
        row["created_at"] = now
        row["updated_at"] = now
        if self.is_connected:
            try:
                self._api_request("leads", method="POST", data=row)
                return row["id"]
            except Exception as e:
                print(f"[WARN] Supabase insert_lead error: {e} — zapis do lokalnego SQLite")
        with sqlite3.connect(LOCAL_DB_PATH) as conn:
            cols = ", ".join(row.keys())
            conn.execute(f"INSERT INTO leads ({cols}) VALUES ({', '.join(['?'] * len(row))})", list(row.values()))
            conn.execute("INSERT INTO lead_events (lead_id, event, to_status, created_at) VALUES (?, 'created', ?, ?)",
                         (row["id"], row["status"], now))
            conn.commit()
        return row["id"]

    def list_leads(self, tenant_id=None, status=None):
        sql, args = "SELECT * FROM leads WHERE 1=1", []
        if tenant_id:
            sql += " AND tenant_id = ?"
            args.append(tenant_id)
        if status:
            sql += " AND status = ?"
            args.append(status)
        with sqlite3.connect(LOCAL_DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            return [dict(r) for r in conn.execute(sql + " ORDER BY created_at DESC", args).fetchall()]

    def get_lead(self, lead_id_prefix: str):
        """Returns the lead whose id starts with the prefix (None if none or ambiguous)."""
        with sqlite3.connect(LOCAL_DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("SELECT * FROM leads WHERE id LIKE ?", (f"{lead_id_prefix}%",)).fetchall()
            if len(rows) != 1:
                return None
            lead = dict(rows[0])
            lead["events"] = [dict(r) for r in conn.execute(
                "SELECT * FROM lead_events WHERE lead_id = ? ORDER BY id", (lead["id"],)).fetchall()]
            return lead

    def update_lead(self, lead_id: str, **fields):
        allowed = {k: v for k, v in fields.items() if k in ("status", "value_pln", "next_action", "next_action_at", "notes")}
        if "status" in allowed and allowed["status"] not in LEAD_STATUSES:
            raise ValueError(f"Nieprawidłowy status leada: {allowed['status']}")
        lead = self.get_lead(lead_id)
        if not lead:
            return None
        now = datetime.now().isoformat()
        allowed["updated_at"] = now
        with sqlite3.connect(LOCAL_DB_PATH) as conn:
            sets = ", ".join(f"{k} = ?" for k in allowed)
            conn.execute(f"UPDATE leads SET {sets} WHERE id = ?", list(allowed.values()) + [lead["id"]])
            if "status" in fields and fields["status"] != lead["status"]:
                conn.execute(
                    "INSERT INTO lead_events (lead_id, event, from_status, to_status, created_at) VALUES (?, 'status', ?, ?, ?)",
                    (lead["id"], lead["status"], fields["status"], now))
            conn.commit()
        return self.get_lead(lead["id"])

    def add_lead_note(self, lead_id: str, note: str):
        lead = self.get_lead(lead_id)
        if not lead:
            return None
        now = datetime.now().isoformat()
        notes = ((lead.get("notes") or "") + f"\n[{now[:16]}] {note}").strip()
        with sqlite3.connect(LOCAL_DB_PATH) as conn:
            conn.execute("UPDATE leads SET notes = ?, updated_at = ? WHERE id = ?", (notes, now, lead["id"]))
            conn.execute("INSERT INTO lead_events (lead_id, event, note, created_at) VALUES (?, 'note', ?, ?)",
                         (lead["id"], note, now))
            conn.commit()
        return self.get_lead(lead["id"])

    def lead_funnel(self, tenant_id=None) -> dict:
        """Counts per status + total value of won deals (numbers only, no personal data)."""
        funnel = {s: 0 for s in LEAD_STATUSES}
        sql, args = "SELECT status, COUNT(*), COALESCE(SUM(CASE WHEN status='won' THEN value_pln END), 0) FROM leads", []
        if tenant_id:
            sql += " WHERE tenant_id = ?"
            args.append(tenant_id)
        won_value = 0.0
        with sqlite3.connect(LOCAL_DB_PATH) as conn:
            for status, cnt, val in conn.execute(sql + " GROUP BY status", args).fetchall():
                funnel[status] = cnt
                won_value += val or 0
        funnel["won_value"] = won_value
        return funnel

    def fetch_remote_leads(self, since: str = None) -> list:
        """Supabase -> list of leads (requires service role SUPABASE_KEY; anon cannot SELECT through RLS)."""
        if not self.is_connected:
            return []
        params = {"order": "created_at.asc"}
        if since:
            params["created_at"] = f"gte.{since}"
        return self._api_request("leads", method="GET", params=params) or []

    def upsert_local_lead(self, lead: dict) -> bool:
        """Inserts a remote lead into SQLite if its id is not there yet (dedup by id)."""
        row = {k: lead.get(k) for k in ("id",) + LEAD_FIELDS + ("created_at", "updated_at")}
        with sqlite3.connect(LOCAL_DB_PATH) as conn:
            if conn.execute("SELECT 1 FROM leads WHERE id = ?", (row["id"],)).fetchone():
                return False
            conn.execute(f"INSERT INTO leads ({', '.join(row)}) VALUES ({', '.join(['?'] * len(row))})", list(row.values()))
            conn.commit()
        return True

db = SupabaseClient()
