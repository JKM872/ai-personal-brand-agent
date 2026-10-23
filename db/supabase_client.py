"""
Supabase REST Client with zero-dependency direct API + Local Fallback.
Connects directly to Supabase PostgREST API without needing external libraries.
If SUPABASE_URL / SUPABASE_KEY are not yet configured, gracefully falls back to local JSON/SQLite storage.
"""

import os
import json
import sqlite3
import urllib.request
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.resolve()
LOCAL_DB_PATH = BASE_DIR / "db" / "local_storage.db"

class SupabaseClient:
    def __init__(self):
        self.url = os.environ.get("SUPABASE_URL", "").rstrip("/")
        self.key = os.environ.get("SUPABASE_KEY", os.environ.get("SUPABASE_ANON_KEY", ""))
        self.is_connected = bool(self.url and self.key)
        
        if not self.is_connected:
            self._init_local_db()

    def _init_local_db(self):
        """Initializes local SQLite database matching the Supabase schema for zero-config offline runs."""
        LOCAL_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(LOCAL_DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS agent_strategy (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                persona_name TEXT UNIQUE,
                system_prompt TEXT,
                posts_count INT DEFAULT 0,
                total_clicks INT DEFAULT 0,
                conversions INT DEFAULT 0,
                effectiveness_score REAL DEFAULT 1.0,
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
            # Default personas
            cursor.execute("""
            INSERT OR IGNORE INTO agent_strategy (persona_name, system_prompt, effectiveness_score)
            VALUES 
                ('analityk_danych', 'Jesteś chłodnym inżynierem i analitykiem. Operujesz liczbami, architekturą, benchmarkami i wyliczeniami. Zero lania wody.', 1.0),
                ('case_study', 'Jesteś praktykiem biznesowym. Pokazujesz realne case studies, problem klienta, krok po kroku rozwiązanie i wymierne rezultaty.', 1.0),
                ('kontrowersyjny_ekspert', 'Jesteś bezkompromisowym ekspertem. Podważasz powszechne mity i hype rynkowy, wskazujesz ukryte koszty i błędy popełniane przez większość firm.', 1.0);
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

    # --- Strategy / Personas ---
    def get_personas(self):
        if self.is_connected:
            try:
                return self._api_request("agent_strategy", method="GET")
            except Exception as e:
                print(f"[WARN] Supabase get_personas error: {e}")
        
        with sqlite3.connect(LOCAL_DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("SELECT * FROM agent_strategy").fetchall()
            return [dict(r) for r in rows]

    def update_persona_score(self, persona_name, score, clicks, conversions):
        if self.is_connected:
            try:
                self._api_request(
                    "agent_strategy",
                    method="PATCH",
                    data={"effectiveness_score": score, "total_clicks": clicks, "conversions": conversions},
                    params={"persona_name": f"eq.{persona_name}"}
                )
                return True
            except Exception as e:
                print(f"[WARN] Supabase update_persona_score error: {e}")

        with sqlite3.connect(LOCAL_DB_PATH) as conn:
            conn.execute(
                "UPDATE agent_strategy SET effectiveness_score = ?, total_clicks = ?, conversions = ? WHERE persona_name = ?",
                (score, clicks, conversions, persona_name)
            )
            conn.commit()
            return True

    # --- Content Pipeline ---
    def insert_content(self, content_dict):
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

    # --- Subscribers ---
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

    def add_subscriber(self, email, source_utm="organic"):
        if self.is_connected:
            try:
                return self._api_request("subscribers", method="POST", data={"email": email, "source_utm": source_utm})
            except Exception as e:
                print(f"[WARN] Supabase add_subscriber error: {e}")

        with sqlite3.connect(LOCAL_DB_PATH) as conn:
            conn.execute("INSERT OR IGNORE INTO subscribers (email, source_utm) VALUES (?, ?)", (email, source_utm))
            conn.commit()
            return True

db = SupabaseClient()
