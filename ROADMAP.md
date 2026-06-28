# Roadmap

## Research-Driven Additions

- [ ] P3 - Add optional machine-readable catalog export
  Why: A normalized JSON export lets other static tools, personal launchers, or audits reuse the curated data without scraping Markdown.
  Evidence: `apps/*.json`, https://f-droid.org/docs/Build_Metadata_Reference/, https://json-schema.org/
  Touches: `scripts/build.py`, generated `catalog.json`, `README.md`
  Acceptance: A deterministic generated export includes normalized category/app records, schema version, generated timestamp, and source URLs; validation confirms it matches source JSON.
  Complexity: M
