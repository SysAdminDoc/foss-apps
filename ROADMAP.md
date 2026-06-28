# Roadmap

## Research-Driven Additions

- [ ] P1 - Generate a searchable static catalog page
  Why: The current README/category Markdown is readable but weak for users comparing 116 apps by category, install source, maintenance status, and privacy criteria.
  Evidence: https://alternativeto.net/, https://www.appbrain.com/, https://github.com/offa/android-foss, `README.md`, `categories/*.md`
  Touches: `scripts/build.py`, `docs` or generated static assets, `_config.yml`, `apps/*.json`
  Acceptance: The published static site provides search, category filter, install-source filter, source-host filter, sort by name/status/category, and shareable URLs while keeping Markdown generation intact.
  Complexity: L

- [ ] P1 - Add local link-health and badge-health reporting
  Why: The catalog depends on external source, install, website, stars, and last-commit URLs, but there is no maintainer report for dead links or badge failures.
  Evidence: `scripts/build.py`, `scripts/add.py`, https://shields.io/, https://docs.github.com/en/rest
  Touches: `scripts/check_links.py`, `scripts/validate.py`, `CLAUDE.md`, `README.md`
  Acceptance: A local command checks stored URLs with timeouts, distinguishes hard failures from rate limits, and writes a concise console report without modifying catalog data.
  Complexity: M

- [ ] P2 - Add accessibility and mobile polish to generated pages
  Why: Generated category pages are plain Markdown with badge images and repeated link text, which is scanable but not optimized for screen readers or mobile comparison.
  Evidence: `categories/*.md`, https://www.privacyguides.org/en/android/
  Touches: `scripts/build.py`, `README.md`, `categories/*.md`, static CSS/assets if added
  Acceptance: Generated output has descriptive badge alt text, consistent link labels, mobile-friendly spacing, and category/app headings that remain clear on GitHub and GitHub Pages.
  Complexity: M

- [ ] P2 - Add lightweight regression tests for generator behavior
  Why: `scripts/build.py` constructs badges, parses source hosts, writes UTF-8 files, and updates marked README chunks without test coverage.
  Evidence: `scripts/build.py`, `CHANGELOG.md`, https://docs.pytest.org/
  Touches: `tests/`, `scripts/build.py`, `scripts/validate.py`
  Acceptance: Local tests cover app counting, category ordering, GitHub/GitLab badge generation, non-GitHub source fallback, UTF-8 emoji output, and README marker replacement.
  Complexity: M

- [ ] P2 - Add Android platform-readiness fields
  Why: Android target-SDK and sideloading policy changes make package ID, target SDK, signing/source provenance, and update source more important for users choosing FOSS replacements.
  Evidence: https://developer.android.com/google/play/requirements/target-sdk, https://android-developers.googleblog.com/, https://github.com/ImranR98/Obtainium
  Touches: `apps/*.json`, `scripts/build.py`, `CONTRIBUTING.md`, `.github/ISSUE_TEMPLATE/app-suggestion.md`
  Acceptance: App records can capture package name, current target SDK when known, update source, signing/provenance notes, and sideload caveats; generated pages omit unknown values cleanly.
  Complexity: L

- [ ] P3 - Add optional machine-readable catalog export
  Why: A normalized JSON export lets other static tools, personal launchers, or audits reuse the curated data without scraping Markdown.
  Evidence: `apps/*.json`, https://f-droid.org/docs/Build_Metadata_Reference/, https://json-schema.org/
  Touches: `scripts/build.py`, generated `catalog.json`, `README.md`
  Acceptance: A deterministic generated export includes normalized category/app records, schema version, generated timestamp, and source URLs; validation confirms it matches source JSON.
  Complexity: M
