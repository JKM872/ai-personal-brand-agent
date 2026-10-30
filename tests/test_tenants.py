import unittest
from unittest import mock

from saas_core import tenants


class TenantTests(unittest.TestCase):
    def setUp(self):
        tenants.clear_cache()

    def test_default_is_owner(self):
        with mock.patch.object(tenants, "_load_key", lambda n: ""):
            t = tenants.load_tenant("default")
        self.assertTrue(t["is_owner"])
        self.assertIn("services", t["offer"])

    def test_demo_not_owner(self):
        self.assertFalse(tenants.load_tenant("demo")["is_owner"])

    def test_missing_falls_back_to_default(self):
        self.assertEqual(tenants.load_tenant("nie-ma-takiego")["id"], "default")

    def test_invalid_id(self):
        with self.assertRaises(ValueError):
            tenants.load_tenant("../etc")

    def test_env_overrides_site_url(self):
        with mock.patch.object(tenants, "_load_key", lambda n: "https://moja.pl" if n == "SITE_URL" else ""):
            self.assertEqual(tenants.load_tenant("default")["site_url"], "https://moja.pl")

    def test_list(self):
        self.assertIn("default", tenants.list_tenants())


if __name__ == "__main__":
    unittest.main()
