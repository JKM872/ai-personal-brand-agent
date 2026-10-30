import unittest
from unittest import mock

from agents import runtime


def keys(**present):
    return lambda name: present.get(name, "")


class RuntimeTests(unittest.TestCase):
    def test_auto_without_keys_is_dry_run(self):
        with mock.patch.dict("os.environ", {"DRY_RUN": ""}), mock.patch.object(runtime, "_load_key", keys()):
            self.assertTrue(runtime.is_dry_run())

    def test_auto_with_write_key_is_live(self):
        with mock.patch.dict("os.environ", {"DRY_RUN": ""}), mock.patch.object(runtime, "_load_key", keys(WEBHOOK_URL="x")):
            self.assertFalse(runtime.is_dry_run())

    def test_explicit_values(self):
        with mock.patch.object(runtime, "_load_key", keys(WEBHOOK_URL="x")):
            with mock.patch.dict("os.environ", {"DRY_RUN": "1"}):
                self.assertTrue(runtime.is_dry_run())
            with mock.patch.dict("os.environ", {"DRY_RUN": "0"}):
                self.assertFalse(runtime.is_dry_run())

    def test_unknown_value_is_auto(self):
        with mock.patch.dict("os.environ", {"DRY_RUN": "maybe"}), mock.patch.object(runtime, "_load_key", keys()):
            self.assertTrue(runtime.is_dry_run())

    def test_channel_live_needs_all_keys(self):
        with mock.patch.dict("os.environ", {"DRY_RUN": "0"}), \
                mock.patch.object(runtime, "_load_key", keys(TELEGRAM_BOT_TOKEN="t")):
            self.assertFalse(runtime.channel_live("TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID"))
            self.assertTrue(runtime.channel_live("TELEGRAM_BOT_TOKEN"))

    def test_offline(self):
        with mock.patch.dict("os.environ", {"OFFLINE": "1"}):
            self.assertTrue(runtime.is_offline())
            self.assertTrue(runtime.load_fixture("github", "test", 2))


if __name__ == "__main__":
    unittest.main()
