import json
import pathlib
import sys
import tempfile
import unittest
from io import BytesIO
from urllib.error import HTTPError, URLError


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import check_links


class FakeResponse:
    def __init__(self, status, headers=None):
        self.status = status
        self.headers = headers or {}

    def __enter__(self):
        return self

    def __exit__(self, _exc_type, _exc, _traceback):
        return False


class LinkCheckTests(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self.tmpdir.name)
        (self.root / "apps").mkdir()
        (self.root / "apps" / "browsers.json").write_text(
            json.dumps(
                {
                    "title": "Browsers",
                    "emoji": "+",
                    "apps": [
                        {
                            "name": "Alpha",
                            "description": "A browser.",
                            "source": "https://github.com/example/alpha",
                            "fdroid": "https://f-droid.org/packages/org.example.alpha",
                            "website": "https://example.org",
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_collects_app_and_badge_links(self):
        targets = check_links.collect_links(self.root)
        urls = {target.url for target in targets}
        self.assertIn("https://github.com/example/alpha", urls)
        self.assertIn("https://f-droid.org/packages/org.example.alpha", urls)
        self.assertIn("https://badgen.net/github/stars/example/alpha", urls)
        self.assertIn("https://img.shields.io/github/last-commit/example/alpha", urls)

    def test_classifies_ok_rate_limited_and_failed(self):
        target = check_links.LinkTarget("https://example.org", ["Alpha source"])
        ok = check_links.check_target(target, opener=lambda _request, timeout: FakeResponse(204))
        self.assertEqual(ok.status, "ok")

        limited = check_links.check_target(
            target,
            opener=lambda _request, timeout: FakeResponse(
                200, {"x-ratelimit-remaining": "0"}
            ),
        )
        self.assertEqual(limited.status, "rate-limited")

        failed = check_links.check_target(
            target,
            opener=lambda request, timeout: (_ for _ in ()).throw(
                HTTPError(request.full_url, 404, "Not Found", {}, BytesIO(b""))
            ),
        )
        self.assertEqual(failed.status, "failed")
        self.assertEqual(failed.detail, "HTTP 404")

    def test_reports_url_errors_as_failed_without_mutating_data(self):
        before = (self.root / "apps" / "browsers.json").read_text(encoding="utf-8")
        target = check_links.LinkTarget("https://example.invalid", ["Alpha source"])
        result = check_links.check_target(
            target,
            opener=lambda _request, timeout: (_ for _ in ()).throw(
                URLError(TimeoutError("slow"))
            ),
        )
        after = (self.root / "apps" / "browsers.json").read_text(encoding="utf-8")
        self.assertEqual(result.status, "failed")
        self.assertEqual(result.detail, "TimeoutError")
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
