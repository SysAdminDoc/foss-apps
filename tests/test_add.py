import json
import pathlib
import sys
import tempfile
import unittest
from contextlib import contextmanager, redirect_stderr, redirect_stdout
from io import StringIO
from unittest.mock import patch


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import add


def ok_requester(_link):
    return 200


@contextmanager
def quiet_io():
    with redirect_stdout(StringIO()), redirect_stderr(StringIO()):
        yield


class AddToolTests(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self.tmpdir.name)
        (self.root / "apps").mkdir()
        self.category_file = self.root / "apps" / "browsers.json"
        self.category_file.write_text(
            json.dumps(
                {
                    "title": "Browsers",
                    "emoji": "+",
                    "apps": [
                        {
                            "name": "Alpha",
                            "description": "Existing app.",
                            "source": "https://github.com/example/alpha",
                        },
                        {
                            "name": "Gamma",
                            "description": "Existing app.",
                            "source": "https://github.com/example/gamma",
                        },
                    ],
                },
                indent=2,
            ),
            encoding="utf-8",
        )

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_duplicate_category_exits_nonzero(self):
        with quiet_io(), patch("builtins.input", side_effect=["browsers"]):
            with self.assertRaises(SystemExit) as raised:
                add.new_category(self.root, ["browsers"], ["+"])
        self.assertEqual(raised.exception.code, 1)

    def test_duplicate_source_exits_nonzero(self):
        inputs = ["browsers", "https://github.com/example/alpha"]
        with quiet_io(), patch("builtins.input", side_effect=inputs):
            with self.assertRaises(SystemExit) as raised:
                add.new_app(
                    self.root,
                    ["browsers"],
                    ["https://github.com/example/alpha"],
                    requester=ok_requester,
                )
        self.assertEqual(raised.exception.code, 1)

    def test_required_field_exits_nonzero(self):
        inputs = ["browsers", "https://github.com/example/beta", ""]
        with quiet_io(), patch("builtins.input", side_effect=inputs):
            with self.assertRaises(SystemExit) as raised:
                add.new_app(self.root, ["browsers"], [], requester=ok_requester)
        self.assertEqual(raised.exception.code, 1)

    def test_required_source_exits_nonzero(self):
        inputs = ["browsers", ""]
        with quiet_io(), patch("builtins.input", side_effect=inputs):
            with self.assertRaises(SystemExit) as raised:
                add.new_app(self.root, ["browsers"], [], requester=ok_requester)
        self.assertEqual(raised.exception.code, 1)

    def test_link_errors_include_status_or_exception_class(self):
        with quiet_io(), self.assertRaises(add.AddToolError) as status_error:
            add.test_link("https://example.test/app", requester=lambda _link: 500)
        self.assertIn("HTTP 500", str(status_error.exception))

        def timeout_requester(_link):
            raise TimeoutError("slow")

        with quiet_io(), self.assertRaises(add.AddToolError) as exception_error:
            add.test_link("https://example.test/app", requester=timeout_requester)
        self.assertIn("TimeoutError", str(exception_error.exception))

    def test_successful_insert_preserves_sort_order_and_utf8(self):
        inputs = [
            "browsers",
            "https://github.com/example/beta",
            "Béta",
            "Café browser.",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
        ]
        with quiet_io(), patch("builtins.input", side_effect=inputs):
            add.new_app(self.root, ["browsers"], [], requester=ok_requester)

        raw = self.category_file.read_bytes()
        self.assertIn("Café".encode("utf-8"), raw)

        data = json.loads(raw.decode("utf-8"))
        self.assertEqual([app["name"] for app in data["apps"]], ["Alpha", "Béta", "Gamma"])


if __name__ == "__main__":
    unittest.main()
