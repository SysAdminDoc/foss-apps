import json
import pathlib
import sys
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import build
import validate


class ValidateCatalogTests(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.tmp = pathlib.Path(self.tmpdir.name)
        (self.tmp / "apps").mkdir()
        (self.tmp / "categories").mkdir()
        (self.tmp / "README.md").write_text(
            "<!-- apps-count starts -->\nold\n<!-- apps-count ends -->\n"
            "<!-- table-of-contents starts -->\nold\n<!-- table-of-contents ends -->\n",
            encoding="utf-8",
        )

    def tearDown(self):
        self.tmpdir.cleanup()

    def write_category(self, apps):
        payload = {"title": "Browsers", "emoji": "+", "apps": apps}
        (self.tmp / "apps" / "browsers.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def build_outputs(self):
        categories = build.parse_categories(self.tmp / "apps")
        build.build_readme(self.tmp, categories)
        for category in categories:
            build.build_category(category, self.tmp / "categories")

    def test_valid_catalog_passes(self):
        self.write_category(
            [
                {
                    "name": "Alpha",
                    "description": "A browser.",
                    "source": "https://github.com/example/alpha",
                }
            ]
        )
        self.build_outputs()

        self.assertEqual(validate.validate_catalog(self.tmp), [])

    def test_reports_required_duplicate_sort_url_and_drift_errors(self):
        self.write_category(
            [
                {
                    "name": "Zulu",
                    "description": "A browser.",
                    "source": "https://github.com/example/shared",
                },
                {
                    "name": "Alpha",
                    "source": "not-a-url",
                    "website": "example.com",
                },
                {
                    "name": "Beta",
                    "description": "Another browser.",
                    "source": "https://github.com/example/shared",
                },
            ]
        )

        errors = validate.validate_catalog(self.tmp)
        joined = "\n".join(errors)
        self.assertIn("missing required field 'description'", joined)
        self.assertIn("field 'source' must be an HTTP(S) URL", joined)
        self.assertIn("field 'website' must be an HTTP(S) URL", joined)
        self.assertIn("duplicate source URL", joined)
        self.assertIn("apps must be sorted alphabetically", joined)

        fixed_apps = [
            {
                "name": "Alpha",
                "description": "A browser.",
                "source": "https://github.com/example/alpha",
            }
        ]
        self.write_category(fixed_apps)
        self.assertIn(
            "generated category file is missing",
            "\n".join(validate.validate_catalog(self.tmp)),
        )


if __name__ == "__main__":
    unittest.main()
