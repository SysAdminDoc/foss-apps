# Changelog

## Unreleased

- Added a generated machine-readable `catalog.json` export with normalized category and app records.
- Added Android platform-readiness metadata for target SDK, update source, signing/source provenance, and sideload caveats.
- Added generator regression tests for app counts, category ordering, badge URLs, UTF-8 README output, and marker replacement.
- Improved generated category page accessibility with app headings, descriptive badge alt text, and cleaner mobile-friendly link blocks.
- Added a local link-health and badge-health report command.
- Added a generated searchable catalog page with category, install-source, source-host, and sort controls.
- Expanded app metadata support for package IDs, license, source host, install-source links, store package IDs, and anti-features.
- Added optional app review metadata for last-reviewed dates, maintenance status, archive/deprecation flags, and successor notes.
- Fixed interactive add-tool failures so fatal validation exits non-zero and link errors report HTTP status or exception class.
- Updated contributor intake docs, issue prompts, and the add script for split category JSON files and trust/install metadata.
- Added local catalog validation for required fields, duplicate sources, app sort order, URL shape, and generated Markdown drift.
- Removed the GitHub Actions content rebuild workflow so generated content is maintained through local builds.
- Added repository ignore rules for local roadmap notes, Python caches, virtual environments, editor files, and environment files.
- Fixed the Python content tooling to read and write UTF-8 consistently on Windows.
