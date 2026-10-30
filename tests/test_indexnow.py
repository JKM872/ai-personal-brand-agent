import unittest
from unittest import mock

from publishers import indexnow


class IndexNowTests(unittest.TestCase):
    def test_no_key_skips_without_network(self):
        with mock.patch.object(indexnow, "_load_key", lambda n: ""), mock.patch("urllib.request.urlopen") as up:
            self.assertEqual(indexnow.submit_to_indexnow("example.com", ["https://example.com/a"]), {"status": "SKIPPED"})
            up.assert_not_called()

    def test_dry_run_skips_even_with_key(self):
        with mock.patch.object(indexnow, "is_dry_run", lambda: True), mock.patch("urllib.request.urlopen") as up:
            self.assertEqual(indexnow.submit_to_indexnow("example.com", ["u"], api_key="k"), {"status": "SKIPPED"})
            up.assert_not_called()


if __name__ == "__main__":
    unittest.main()
