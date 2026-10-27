import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from crm.validation import validate_lead
import db.supabase_client as sc

NOW = 1_800_000_000_000
VALID = {"name": "Jan", "email": "Jan@Example.com", "consent": True, "ts": NOW - 10_000, "website": "", "service": "audyt"}


class TestLeadValidation(unittest.TestCase):
    def test_valid(self):
        clean, errors = validate_lead(dict(VALID), NOW)
        self.assertEqual(errors, {})
        self.assertEqual(clean["email"], "jan@example.com")
        self.assertEqual(clean["status"], "new")

    def test_honeypot_and_timing_are_spam(self):
        self.assertIn("_spam", validate_lead({**VALID, "website": "x"}, NOW)[1])
        self.assertIn("_spam", validate_lead({**VALID, "ts": NOW - 500}, NOW)[1])
        self.assertIn("_spam", validate_lead({**VALID, "ts": "abc"}, NOW)[1])

    def test_field_errors(self):
        _, errors = validate_lead({**VALID, "email": "bad", "consent": False, "name": "", "service": "zle"}, NOW)
        self.assertEqual(errors, {"email": "invalid", "consent": "required", "name": "required", "service": "invalid"})


class TestLeadsDb(unittest.TestCase):
    def setUp(self):
        # sqlite3 "with" does not close connections; Windows keeps the file locked until GC
        self.tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.patch = mock.patch.object(sc, "LOCAL_DB_PATH", Path(self.tmp.name) / "t.db")
        self.patch.start()
        with mock.patch("agents.free_ai_router._load_key", return_value=""):
            self.db = sc.SupabaseClient()

    def tearDown(self):
        self.patch.stop()
        self.tmp.cleanup()

    def test_pipeline(self):
        clean, _ = validate_lead(dict(VALID), NOW)
        lid = self.db.insert_lead(clean)
        self.assertEqual(len(self.db.list_leads()), 1)
        self.db.update_lead(lid[:8], status="won", value_pln=2900)
        self.db.add_lead_note(lid, "telefon")
        lead = self.db.get_lead(lid[:8])
        self.assertEqual(lead["status"], "won")
        self.assertEqual([e["event"] for e in lead["events"]], ["created", "status", "note"])
        funnel = self.db.lead_funnel()
        self.assertEqual(funnel["won"], 1)
        self.assertEqual(funnel["won_value"], 2900)
        with self.assertRaises(ValueError):
            self.db.update_lead(lid, status="zle")

    def test_init_is_idempotent(self):
        self.db._init_local_db()
        self.db._init_local_db()


if __name__ == "__main__":
    unittest.main()
