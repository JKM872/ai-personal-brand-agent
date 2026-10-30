import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from agents import runtime
from publishers import social_publisher as sp

BUNDLE = {
    "linkedin": {"post": "p", "carousel": "c"},
    "twitter": {"thread": "t", "standalone_hooks": []},
    "newsletter": {"newsletter": "n"},
    "video": {"video_script": "v"},
    "github": {"demo_code": "g"},
}


def keys(**present):
    return lambda name: present.get(name, "")


class SocialModeTests(unittest.TestCase):
    def test_one_key_enables_only_its_channel(self):
        k = keys(WEBHOOK_URL="https://hook.example")
        with mock.patch.dict("os.environ", {"DRY_RUN": "0"}), mock.patch.object(runtime, "_load_key", k), \
                mock.patch.object(sp, "_load_key", k), mock.patch.object(sp, "_load_file_channels", lambda: {}):
            modes = sp.resolve_channel_modes()
        self.assertEqual(modes["webhook"], "live")
        self.assertEqual(modes["telegram"], "dry_run")
        self.assertEqual(modes["linkedin"], "dry_run")
        self.assertEqual(modes["newsletter"], "dry_run")

    def test_dry_run_only_never_calls_network(self):
        k = keys(WEBHOOK_URL="https://hook.example", TELEGRAM_BOT_TOKEN="t", TELEGRAM_CHAT_ID="c")
        with tempfile.TemporaryDirectory() as d, mock.patch.dict("os.environ", {"DRY_RUN": "0"}), \
                mock.patch.object(runtime, "_load_key", k), mock.patch.object(sp, "_load_key", k), \
                mock.patch("urllib.request.urlopen") as up:
            res = sp.dispatch_content_bundle({"title": "x"}, BUNDLE, Path(d), dry_run_only=True)
            up.assert_not_called()
            status = json.loads((Path(d) / "PUBLISH_STATUS.json").read_text(encoding="utf-8"))
            self.assertTrue((Path(d) / "7_API_PAYLOAD_READY.json").exists())
        self.assertEqual(res["mode"], "dry_run")
        self.assertTrue(all(v == "AWAITING_APPROVAL" for v in status["dispatches"].values()))


if __name__ == "__main__":
    unittest.main()
