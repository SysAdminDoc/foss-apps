# Research - foss-apps

## Executive Summary
foss-apps is a static, JSON-backed catalog of open-source Android app alternatives. Its strongest current shape is simplicity: `apps/*.json` is easy to review, `scripts/build.py` deterministically regenerates `README.md` and `categories/*.md`, and the public output remains lightweight. The highest-value direction is to keep that simplicity while adding trust and discoverability: schema validation, stale-app checks, accurate contribution docs, searchable static output, richer install/source metadata, and Android distribution readiness for current sideloading and target-SDK changes. Top opportunities: add a fail-fast data validator; repair contributor docs and issue templates for split category files; detect stale, archived, duplicate, and unsorted app entries; expose search/filter/sort in the generated site; add license, anti-feature, last-release, package-name, and repository metadata; support F-Droid, IzzyOnDroid, Accrescent, Obtainium, and APK/release sources distinctly; add link-health and generated-diff checks for local maintainers; preserve Markdown output for low-friction forks.

## Product Map
- Core workflows: maintain app records in `apps/*.json`; regenerate `README.md` and `categories/*.md` via `scripts/build.py`; use `scripts/add.py` interactively for new app/category insertion; accept app suggestions through `.github/ISSUE_TEMPLATE/app-suggestion.md`; publish via GitHub Pages/Jekyll using `_config.yml`.
- User personas: Android users looking for proprietary-app replacements; F-Droid/Izzy users checking install sources; contributors submitting one app at a time; maintainers reviewing JSON changes and regenerated Markdown; privacy-focused users evaluating trust before install.
- Platforms and distribution: static Markdown/GitHub Pages; Android app links to source repositories, F-Droid, Play Store, and websites; no packaged binary or runtime service.
- Key integrations and data flows: per-category JSON -> Python generator -> README/category Markdown; external badge services for stars and last commit; optional link probing in `scripts/add.py` using `requests`.

## Competitive Landscape
- F-Droid: strong metadata model with source, license, anti-features, package IDs, versions, and reproducible-build signals. Learn from its trust metadata and update cadence; avoid turning this repo into a full package repository.
- IzzyOnDroid: strong coverage for apps missing from F-Droid plus anti-feature and reproducible-build transparency. Learn from install-source diversity; avoid mirroring APK hosting responsibilities.
- Obtainium: strong source-to-update mapping for GitHub/GitLab/F-Droid/other app sources. Learn from explicit release-source modeling; avoid app-update logic in this static catalog.
- offa/android-foss: strong table-style discoverability with concise categories and cross-links. Learn from compact scanability; avoid losing foss-apps' curated replacement framing.
- Privacy Guides Android recommendations: strong privacy/security framing and explicit warnings. Learn from rationale and risk notes; avoid subjective ranking without evidence.
- AlternativeTo: strong search, filtering, tags, and alternatives graph. Learn from alternative-oriented browsing; avoid proprietary-tracking-heavy UX patterns.
- AppBrain/APKPure/Uptodown: strong screenshots, versions, app IDs, rankings, and version history. Learn from app detail richness; avoid redistributing APKs or implying endorsement of closed app-store trust models.
- Awesome lists: strong low-maintenance Markdown convention and broad community linking. Learn from contribution simplicity; avoid becoming an unvalidated link dump.

## Security, Privacy, and Reliability
- Verified: `scripts/add.py` has `exit_with_error()` with `sys.exit(1)` commented out at line 19, so some duplicate/category validation errors can print red text without stopping the workflow.
- Verified: `scripts/add.py` uses broad `except:` handlers around link probing, making validation failures harder to diagnose and test.
- Verified: `CONTRIBUTING.md` says "The only file that should be edited is `apps.json`", but the repo now stores category files under `apps/*.json`.
- Verified: `.github/ISSUE_TEMPLATE/app-suggestion.md` asks for app name, category, description, and links, but not package name, license, install source, anti-features, maintenance status, privacy/security notes, or source/release provenance.
- Verified: all required local fields are present in the current JSON corpus, but only 94/116 entries have F-Droid links, 90/116 have Play links, 58/116 have websites, and 3/116 still carry manual `stars_link` fields.
- Verified: `media-viewers-and-players.json` is not fully alphabetized (`Librera Reader` appears before `Just (Video) Player`), while the contributor guide requires alphabetical ordering.
- Missing guardrails: no schema, no local command that fails on bad JSON semantics, no duplicate-source gate, no generated-output drift gate, no link health report, no stale/archived repository review queue, and no license/anti-feature checks.
- Recovery and rollback needs: generated files should remain reproducible from JSON, and validation should provide precise file/app names before maintainers edit or regenerate.

## Architecture Assessment
- `scripts/build.py` should stay small but gain shared data-loading/validation helpers instead of duplicating parsing in future tools.
- `scripts/add.py` should use the same validator, fail non-zero for invalid input, and avoid broad exception swallowing.
- `apps/*.json` needs an explicit schema with current required fields plus optional structured metadata: package name, license, source host, install sources, anti-features, last reviewed date, archive/deprecation status, and replacement relationship.
- Generated pages should remain static, but a small data export and client-side search page would unlock category, install-source, license, maintenance, and privacy filters without requiring a backend.
- Tests are absent. Add lightweight local checks for JSON validity, sort order, schema compliance, generated-output drift, badge URL construction, and non-GitHub/GitLab source handling.
- Documentation gaps are concentrated in `CONTRIBUTING.md`, `.github/ISSUE_TEMPLATE/app-suggestion.md`, and `CLAUDE.md` command notes after validation tooling exists.

## Rejected Ideas
- Full APK hosting mirror: F-Droid and IzzyOnDroid already solve repository distribution; this catalog should link and classify, not become an app store.
- User accounts, ratings, reviews, or comments: AlternativeTo-style community features require moderation and storage that conflicts with the static repo model.
- Automated removal of stale apps: stale/archived signals need maintainer review because some Android apps are stable despite infrequent commits.
- CI-only validation: this fork intentionally removed GitHub Actions, so checks should run locally and be documented instead.
- Mobile-native companion app: Obtainium, Neo Store, Droid-ify, and F-Droid clients already serve install/update workflows; this project should improve catalog data first.
- Proprietary ranking/recommendation scoring: privacy/security recommendations need explicit evidence, not opaque scoring.

## Sources
### Direct Catalogs and Stores
- https://github.com/albertomosconi/foss-apps
- https://github.com/SysAdminDoc/foss-apps
- https://github.com/offa/android-foss
- https://github.com/pcqpcq/open-source-android-apps
- https://github.com/LinuxCafeFederation/awesome-android
- https://f-droid.org/docs/Build_Metadata_Reference/
- https://f-droid.org/docs/Anti-Features/
- https://f-droid.org/docs/Reproducible_Builds/
- https://gitlab.com/IzzyOnDroid/repo
- https://apt.izzysoft.de/fdroid/
- https://github.com/ImranR98/Obtainium
- https://github.com/NeoApplications/Neo-Store
- https://github.com/Droid-ify/client
- https://accrescent.app/

### Commercial and Adjacent Products
- https://alternativeto.net/
- https://www.appbrain.com/
- https://apkpure.com/
- https://www.uptodown.com/android
- https://www.privacyguides.org/en/android/

### Platform, Tooling, and Security
- https://developer.android.com/google/play/requirements/target-sdk
- https://android-developers.googleblog.com/
- https://docs.github.com/en/rest
- https://json-schema.org/
- https://python-jsonschema.readthedocs.io/
- https://docs.pytest.org/
- https://pre-commit.com/
- https://pypi.org/project/requests/
- https://github.com/advisories?query=requests
- https://github.com/ossf/scorecard
- https://shields.io/

## Open Questions
- Should the curated catalog prefer "best current replacement" status over historical inclusion when an app is archived but still installable?
- Should Play Store links remain first-class for privacy-focused FOSS recommendations, or be treated as optional convenience links behind F-Droid/Izzy/source releases?
