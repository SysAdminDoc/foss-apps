#!/usr/bin/env python3
import bisect
import json
import math
import pathlib
import sys
from urllib.error import HTTPError
from urllib.request import Request, urlopen


ENCODING = "utf-8"
ROOT = pathlib.Path(__file__).parent.parent.resolve()
OPTIONAL_URL_FIELDS = [
    "fdroid",
    "izzyondroid",
    "accrescent",
    "obtainium",
    "playstore",
    "website",
]
OPTIONAL_TEXT_FIELDS = [
    "package",
    "license",
    "fdroid_package",
    "izzyondroid_package",
    "source_host",
    "install_sources",
    "maintenance_notes",
    "privacy_security_notes",
    "update_source",
    "signing_provenance",
    "source_provenance",
    "sideload_caveats",
]
OPTIONAL_INT_FIELDS = ["target_sdk"]
OPTIONAL_LIST_FIELDS = ["anti_features"]


class AddToolError(Exception):
    pass


def print_error(message):
    print(f"\033[01m\033[31m{message}\033[0m", file=sys.stderr)


def exit_with_error(message):
    print_error(message)
    raise SystemExit(1)


def load_catalog(root):
    category_sources = sorted((root / "apps").glob("*.json"))
    category_names = [c.stem for c in category_sources]
    emojis = []
    sources = []

    for category in category_sources:
        with category.open("r", encoding=ENCODING) as f:
            category_json = json.load(f)
        emojis.append(category_json.get("emoji"))
        for app in category_json.get("apps", []):
            sources.append(app.get("source"))

    return category_names, emojis, sources


def request_status(link, timeout=10):
    request = Request(link, headers={"User-Agent": "foss-apps-add/1.0"})
    with urlopen(request, timeout=timeout) as response:
        return response.status


def test_link(link, empty=True, requester=request_status):
    if link == "":
        if empty:
            return
        raise AddToolError("- link is required")

    testing_message = "- testing link..."
    print(testing_message, end="\r")
    try:
        status = requester(link)
    except HTTPError as exc:
        raise AddToolError(f"{testing_message} ERROR HTTP {exc.code}") from exc
    except Exception as exc:
        raise AddToolError(
            f"{testing_message} ERROR {exc.__class__.__name__}: {exc}"
        ) from exc

    if 200 <= status < 400:
        print(f"{testing_message} OK")
        return

    raise AddToolError(f"{testing_message} ERROR HTTP {status}")


def display_categories(category_names):
    if not category_names:
        print()
        return

    n = math.ceil(len(category_names) / 3)

    col1 = category_names[:n]
    col2 = category_names[n : 2 * n]
    col3 = category_names[2 * n :]
    for column in (col1, col2, col3):
        while len(column) < n:
            column.append("")
    maxlen1 = len(max(col1, key=len))
    maxlen2 = len(max(col2, key=len))

    for i, j, k in zip(col1, col2, col3):
        print(f"{i.ljust(maxlen1, ' ')}\t{j.ljust(maxlen2, ' ')}\t{k}")
    print()


def prompt_required_text(field):
    value = input(f"{field}: ").strip()
    if not value:
        exit_with_error(f"ERROR: {field} is required")
    return value


def prompt_url(field, required=False, requester=request_status):
    while True:
        value = input(f"{field}: ").strip()
        if required and not value:
            exit_with_error(f"ERROR: {field} is required")
        try:
            test_link(value, empty=not required, requester=requester)
        except AddToolError as exc:
            print_error(str(exc))
            continue
        return value


def new_category(root, category_names, emojis):
    display_categories(category_names)
    name = prompt_required_text("name").lower()
    if name in category_names:
        exit_with_error("ERROR: category already exists")

    print("https://unicode.org/emoji/charts/full-emoji-list.html")
    emoji = prompt_required_text("emoji")
    if emoji in emojis:
        exit_with_error("ERROR: emoji is already taken")

    title = " ".join(x.title() if x != "and" else "and" for x in name.split("-"))
    with open(root / "apps" / f"{name}.json", "w", encoding=ENCODING) as f:
        json.dump({"title": title, "emoji": emoji, "apps": []}, f, indent=4, ensure_ascii=False)


def insert_app(root, category, new_app):
    category_file = root / "apps" / f"{category}.json"
    with open(category_file, "r", encoding=ENCODING) as f:
        category_json = json.load(f)

    bisect.insort(category_json["apps"], new_app, key=lambda x: x.get("name").lower())

    with open(category_file, "w", encoding=ENCODING) as f:
        json.dump(category_json, f, indent=4, ensure_ascii=False)


def new_app(root, category_names, sources, requester=request_status):
    new_app_record = {}
    display_categories(category_names)
    category = prompt_required_text("category").lower()
    if category not in category_names:
        exit_with_error("ERROR: category doesn't exist")

    source = prompt_url("source", required=True, requester=requester)
    if source in sources:
        exit_with_error("ERROR: source already exists")
    new_app_record["source"] = source

    for field in ["name", "description"]:
        new_app_record[field] = prompt_required_text(field)

    for field in OPTIONAL_URL_FIELDS:
        value = prompt_url(field, requester=requester)
        if value:
            new_app_record[field] = value

    for field in OPTIONAL_TEXT_FIELDS:
        value = input(f"{field}: ").strip()
        if value:
            new_app_record[field] = value

    for field in OPTIONAL_INT_FIELDS:
        value = input(f"{field}: ").strip()
        if value:
            try:
                new_app_record[field] = int(value)
            except ValueError:
                exit_with_error(f"ERROR: {field} must be an integer")

    for field in OPTIONAL_LIST_FIELDS:
        value = input(f"{field} (comma-separated): ").strip()
        if value:
            new_app_record[field] = [
                item.strip() for item in value.split(",") if item.strip()
            ]

    insert_app(root, category, new_app_record)


def main():
    category_names, emojis, sources = load_catalog(ROOT)
    try:
        cmd = int(input("[0] new app\t[1] new category\n> "))
    except ValueError:
        exit_with_error("ERROR: expected 0 or 1")

    if cmd == 0:
        new_app(ROOT, category_names, sources)
    elif cmd == 1:
        new_category(ROOT, category_names, emojis)
    else:
        exit_with_error("ERROR: expected 0 or 1")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        exit_with_error("\nTerminating")
