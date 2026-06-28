import json
import pathlib
import sys
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import build


class BuildGeneratorTests(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self.tmpdir.name)
        self.apps = self.root / "apps"
        self.apps.mkdir()
        (self.root / "README.md").write_text(
            "Top\n"
            "<!-- apps-count starts -->\nold count\n<!-- apps-count ends -->\n"
            "<!-- table-of-contents starts -->\nold toc\n<!-- table-of-contents ends -->\n"
            "Bottom\n",
            encoding="utf-8",
        )

    def tearDown(self):
        self.tmpdir.cleanup()

    def write_category(self, filename, title, emoji, apps):
        (self.apps / filename).write_text(
            json.dumps(
                {"title": title, "emoji": emoji, "apps": apps},
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

    def test_counts_apps_and_orders_categories_in_readme(self):
        self.write_category(
            "zeta.json",
            "Zeta",
            "🧪",
            [
                {
                    "name": "Zulu",
                    "description": "Last app.",
                    "source": "https://github.com/example/zulu",
                }
            ],
        )
        self.write_category(
            "alpha.json",
            "Alpha",
            "🌐",
            [
                {
                    "name": "Alpha",
                    "description": "First app.",
                    "source": "https://github.com/example/alpha",
                    "fdroid": "https://f-droid.org/packages/org.example.alpha",
                    "last_reviewed": "2026-06-28",
                },
                {
                    "name": "Beta",
                    "description": "Second app.",
                    "source": "https://gitlab.com/example/beta",
                },
            ],
        )

        categories = build.parse_categories(self.apps)
        self.assertEqual([category.name for category in categories], ["alpha.json", "zeta.json"])
        self.assertEqual(build.count_apps(categories), 3)

        rendered = build.render_readme(self.root, categories)
        self.assertIn("https://img.shields.io/badge/3-apps-red", rendered)
        self.assertLess(rendered.index("🌐 Alpha"), rendered.index("🧪 Zeta"))
        self.assertNotIn("old count", rendered)
        self.assertNotIn("old toc", rendered)

        export = json.loads(build.render_export(self.root, categories))
        self.assertEqual(export["schema_version"], 1)
        self.assertEqual(export["generated_at"], "2026-06-28T00:00:00Z")
        self.assertEqual(export["source_urls"]["repository"], "https://github.com/SysAdminDoc/foss-apps")
        self.assertEqual(export["category_count"], 2)
        self.assertEqual(export["app_count"], 3)
        self.assertEqual(export["categories"][0]["slug"], "alpha")
        self.assertEqual(export["categories"][0]["source_file"], "apps/alpha.json")
        self.assertEqual(export["apps"][0]["name"], "Alpha")
        self.assertEqual(
            export["apps"][0]["install_urls"]["fdroid"],
            "https://f-droid.org/packages/org.example.alpha",
        )
        self.assertEqual(
            export["apps"][0]["source_urls"]["source"],
            "https://github.com/example/alpha",
        )

    def test_badge_links_for_supported_hosts_and_fallbacks(self):
        self.assertEqual(
            build.badge_links({"source": "https://github.com/example/alpha"}),
            (
                "https://badgen.net/github/stars/example/alpha",
                "https://img.shields.io/github/last-commit/example/alpha",
            ),
        )
        self.assertEqual(
            build.badge_links({"source": "https://gitlab.com/example/beta"}),
            (
                "https://badgen.net/gitlab/stars/example/beta",
                "https://img.shields.io/gitlab/last-commit/example/beta",
            ),
        )
        self.assertEqual(
            build.badge_links(
                {
                    "source": "https://codeberg.org/example/gamma",
                    "stars_link": "https://badges.example/stars",
                    "last_commit_link": "https://badges.example/commit",
                }
            ),
            ("https://badges.example/stars", "https://badges.example/commit"),
        )
        self.assertEqual(
            build.badge_links({"source": "https://codeberg.org/example/gamma"}),
            (None, None),
        )

    def test_replace_chunk_preserves_outer_content(self):
        content = "before\n<!-- marker starts -->old<!-- marker ends -->\nafter"
        replaced = build.replace_chunk(content, "marker", "new")
        self.assertEqual(
            replaced,
            "before\n<!-- marker starts -->\nnew\n<!-- marker ends -->\nafter",
        )


if __name__ == "__main__":
    unittest.main()
