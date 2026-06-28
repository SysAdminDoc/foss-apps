#!/usr/bin/env python3
import argparse
import datetime as dt
import json
import pathlib
import re
import sys
from urllib.parse import urlparse

import build


ENCODING = "utf-8"
REQUIRED_CATEGORY_FIELDS = ("title", "emoji", "apps")
REQUIRED_APP_FIELDS = ("name", "description", "source")
URL_FIELDS = (
    "source",
    "fdroid",
    "playstore",
    "website",
    "izzyondroid",
    "accrescent",
    "obtainium",
    "stars_link",
    "last_commit_link",
)
MAINTENANCE_STATUSES = {"active", "stale", "archived", "deprecated", "unknown"}
BOOLEAN_FIELDS = ("archived", "deprecated")
TEXT_FIELDS = (
    "successor",
    "review_notes",
    "license",
    "source_host",
    "install_sources",
    "maintenance_notes",
    "privacy_security_notes",
)
PACKAGE_FIELDS = ("package", "fdroid_package", "izzyondroid_package")
PACKAGE_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]*(\.[A-Za-z][A-Za-z0-9_]*)+$")


def _label(path, app=None):
    if app:
        name = app.get("name") or "<unnamed app>"
        return f"{path}: {name}"
    return str(path)


def _is_http_url(value):
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def _is_iso_date(value):
    try:
        dt.date.fromisoformat(value)
    except ValueError:
        return False
    return True


def load_json(path, errors):
    try:
        return json.loads(path.read_text(encoding=ENCODING))
    except json.JSONDecodeError as exc:
        errors.append(
            f"{path}: invalid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}"
        )
    except OSError as exc:
        errors.append(f"{path}: cannot read file: {exc}")
    return None


def validate_category(path, seen_sources):
    errors = []
    data = load_json(path, errors)
    if data is None:
        return errors

    if not isinstance(data, dict):
        return [f"{path}: category file must contain a JSON object"]

    for field in REQUIRED_CATEGORY_FIELDS:
        if field not in data:
            errors.append(f"{path}: missing required field '{field}'")

    apps = data.get("apps")
    if not isinstance(apps, list):
        errors.append(f"{path}: field 'apps' must be a list")
        return errors

    names = []
    for index, app in enumerate(apps, start=1):
        if not isinstance(app, dict):
            errors.append(f"{path}: app #{index} must be a JSON object")
            continue

        for field in REQUIRED_APP_FIELDS:
            if not app.get(field):
                errors.append(f"{_label(path, app)}: missing required field '{field}'")

        name = app.get("name")
        if isinstance(name, str):
            names.append(name)

        source = app.get("source")
        if source:
            previous = seen_sources.get(source)
            if previous:
                errors.append(
                    f"{_label(path, app)}: duplicate source URL '{source}' already used by {previous}"
                )
            else:
                seen_sources[source] = _label(path, app)

        for field in URL_FIELDS:
            value = app.get(field)
            if value and not _is_http_url(value):
                errors.append(
                    f"{_label(path, app)}: field '{field}' must be an HTTP(S) URL: {value}"
                )

        last_reviewed = app.get("last_reviewed")
        if last_reviewed and not _is_iso_date(last_reviewed):
            errors.append(
                f"{_label(path, app)}: field 'last_reviewed' must be an ISO date: {last_reviewed}"
            )

        status = app.get("maintenance_status")
        if status and status not in MAINTENANCE_STATUSES:
            allowed = ", ".join(sorted(MAINTENANCE_STATUSES))
            errors.append(
                f"{_label(path, app)}: field 'maintenance_status' must be one of: {allowed}"
            )

        for field in BOOLEAN_FIELDS:
            if field in app and not isinstance(app[field], bool):
                errors.append(f"{_label(path, app)}: field '{field}' must be boolean")

        for field in TEXT_FIELDS:
            if field in app and not isinstance(app[field], str):
                errors.append(f"{_label(path, app)}: field '{field}' must be text")

        for field in PACKAGE_FIELDS:
            value = app.get(field)
            if value and not PACKAGE_RE.match(value):
                errors.append(
                    f"{_label(path, app)}: field '{field}' must be an Android package ID"
                )

        anti_features = app.get("anti_features")
        if anti_features is not None:
            if not isinstance(anti_features, list) or not all(
                isinstance(item, str) and item for item in anti_features
            ):
                errors.append(
                    f"{_label(path, app)}: field 'anti_features' must be a list of text values"
                )

    sorted_names = sorted(names, key=str.lower)
    if names != sorted_names:
        errors.append(
            f"{path}: apps must be sorted alphabetically by name; expected order: "
            + ", ".join(sorted_names)
        )

    return errors


def validate_generated_output(root, categories):
    errors = []
    readme = root / "README.md"
    expected_readme = build.render_readme(root, categories)
    if readme.read_text(encoding=ENCODING) != expected_readme:
        errors.append("README.md: generated content drift; run py -3 scripts/build.py")

    catalog = root / "catalog.html"
    expected_catalog = build.render_catalog(root, categories)
    if not catalog.exists():
        errors.append("catalog.html: generated catalog file is missing")
    elif catalog.read_text(encoding=ENCODING) != expected_catalog:
        errors.append("catalog.html: generated content drift; run py -3 scripts/build.py")

    categories_dir = root / "categories"
    for category in categories:
        md_file = categories_dir / f"{category.stem}.md"
        if not md_file.exists():
            errors.append(f"{md_file}: generated category file is missing")
            continue
        expected = build.render_category(category)
        if md_file.read_text(encoding=ENCODING) != expected:
            errors.append(f"{md_file}: generated content drift; run py -3 scripts/build.py")

    return errors


def validate_catalog(root):
    root = pathlib.Path(root)
    apps_dir = root / "apps"
    categories = build.parse_categories(apps_dir)
    errors = []

    if not categories:
        errors.append(f"{apps_dir}: no category JSON files found")
        return errors

    seen_sources = {}
    for category in categories:
        errors.extend(validate_category(category, seen_sources))

    if not errors:
        errors.extend(validate_generated_output(root, categories))

    return errors


def main(argv=None):
    parser = argparse.ArgumentParser(description="Validate the foss-apps catalog.")
    parser.add_argument(
        "--root",
        default=pathlib.Path(__file__).parent.parent,
        type=pathlib.Path,
        help="Repository root to validate.",
    )
    args = parser.parse_args(argv)

    errors = validate_catalog(args.root.resolve())
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    print("Catalog validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
