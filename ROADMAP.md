# Roadmap

## Research-Driven Additions

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
