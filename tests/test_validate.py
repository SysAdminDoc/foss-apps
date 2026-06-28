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
        build.build_catalog(self.tmp, categories)
        for category in categories:
            build.build_category(category, self.tmp / "categories")

    def test_valid_catalog_passes(self):
        self.write_category(
            [
                {
                    "name": "Alpha",
                    "description": "A browser.",
                    "source": "https://github.com/example/alpha",
                    "last_reviewed": "2026-06-28",
                    "maintenance_status": "stale",
                    "deprecated": True,
                    "successor": "Review a maintained replacement.",
                    "package": "org.example.alpha",
                    "license": "GPL-3.0-only",
                    "fdroid_package": "org.example.alpha",
                    "source_host": "GitHub",
                    "anti_features": ["NonFreeNet"],
                    "izzyondroid": "https://apt.izzysoft.de/fdroid/index/apk/org.example.alpha",
                    "accrescent": "https://accrescent.app/app/org.example.alpha",
                    "obtainium": "https://github.com/example/alpha/releases",
                }
            ]
        )
        self.build_outputs()

        self.assertEqual(validate.validate_catalog(self.tmp), [])
        rendered = build.render_category(self.tmp / "apps" / "browsers.json")
        self.assertIn("_Review:_ status: stale", rendered)
        self.assertIn("reviewed: 2026-06-28", rendered)
        self.assertIn("flags: deprecated", rendered)
        self.assertIn("successor: Review a maintained replacement.", rendered)
        self.assertIn("_Trust:_ package: org.example.alpha", rendered)
        self.assertIn("license: GPL-3.0-only", rendered)
        self.assertIn("source host: GitHub", rendered)
        self.assertIn("anti-features: NonFreeNet", rendered)
        self.assertIn("[`[izzyondroid]`]", rendered)
        self.assertIn("[`[accrescent]`]", rendered)
        self.assertIn("[`[obtainium]`]", rendered)
        catalog = build.render_catalog(self.tmp, [self.tmp / "apps" / "browsers.json"])
        self.assertIn("catalog-data", catalog)
        self.assertIn("installSource", catalog)
        self.assertIn("org.example.alpha", catalog)

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

        self.write_category(
            [
                {
                    "name": "Alpha",
                    "description": "A browser.",
                    "source": "https://github.com/example/alpha",
                    "last_reviewed": "28-06-2026",
                    "maintenance_status": "maybe",
                    "archived": "yes",
                    "successor": ["bad"],
                    "package": "bad package",
                    "anti_features": "NonFreeNet",
                }
            ]
        )
        metadata_errors = "\n".join(validate.validate_catalog(self.tmp))
        self.assertIn("field 'last_reviewed' must be an ISO date", metadata_errors)
        self.assertIn("field 'maintenance_status' must be one of", metadata_errors)
        self.assertIn("field 'archived' must be boolean", metadata_errors)
        self.assertIn("field 'successor' must be text", metadata_errors)
        self.assertIn("field 'package' must be an Android package ID", metadata_errors)
        self.assertIn("field 'anti_features' must be a list", metadata_errors)

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
