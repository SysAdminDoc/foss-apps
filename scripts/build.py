import json
import pathlib
import re


ENCODING = "utf-8"
SOURCE_RE = re.compile(
    r"https://(gitlab|github)\.com/([a-zA-Z0-9\-_.]+)/([a-zA-Z0-9\-_.]+)"
)


def parse_categories(json_dir):
    return sorted(json_dir.glob("*.json"))


def load_category(category):
    with category.open("r", encoding=ENCODING) as f:
        return json.load(f)


def replace_chunk(content, marker, chunk):
    # replaces the text between the comments with the specified marker with the content
    r = re.compile(f"<!-- {marker} starts -->.*<!-- {marker} ends -->", re.DOTALL)
    chunk = f"<!-- {marker} starts -->\n{chunk}\n<!-- {marker} ends -->"
    return r.sub(chunk, content)


def count_apps(categories):
    count = 0
    for cat in categories:
        cat_json = load_category(cat)
        count += len(cat_json.get("apps"))

    return count


def badge_links(app):
    source = app.get("source")
    m = SOURCE_RE.match(source or "")
    if m is None:
        return app.get("stars_link"), app.get("last_commit_link")

    repo = "/".join(m.group(2, 3))
    return (
        f"https://badgen.net/{m.group(1)}/stars/{repo}",
        f"https://img.shields.io/{m.group(1)}/last-commit/{repo}",
    )


def review_metadata(app):
    parts = []
    status = app.get("maintenance_status")
    if status:
        parts.append(f"status: {status}")

    last_reviewed = app.get("last_reviewed")
    if last_reviewed:
        parts.append(f"reviewed: {last_reviewed}")

    flags = []
    if app.get("archived"):
        flags.append("archived")
    if app.get("deprecated"):
        flags.append("deprecated")
    if flags:
        parts.append("flags: " + ", ".join(flags))

    successor = app.get("successor")
    if successor:
        parts.append(f"successor: {successor}")

    if not parts:
        return ""

    return "    _Review:_ " + " | ".join(parts)


def render_category(cat):
    cat_json = load_category(cat)
    lines = [
        f'# {cat_json.get("emoji")} {cat_json.get("title")}',
        "[`< go back home`](../README.md)",
    ]

    for app in cat_json.get("apps"):
        name = app.get("name")
        description = app.get("description")
        source = app.get("source")
        fdroid = app.get("fdroid")
        playstore = app.get("playstore")
        website = app.get("website")

        stars_link, last_commit_link = badge_links(app)
        badge_stars = f"![Stars]({stars_link})" if stars_link else ""
        badge_commit = f"![last commit]({last_commit_link})" if last_commit_link else ""
        link_source = f'[`[source]`]({source} "source")'
        link_fdroid = f'[`[f-droid]`]({fdroid} "f-droid")' if fdroid else ""
        link_playstore = (
            f'[`[playstore]`]({playstore} "playstore")' if playstore else ""
        )
        link_website = f'[`[website]`]({website} "website")' if website else ""

        app_lines = [
            "",
            f"- **{name}**: {description}",
            "",
            f"    {badge_stars} {badge_commit}",
        ]
        review = review_metadata(app)
        if review:
            app_lines.extend(["", review])
        app_lines.extend(
            [
                "",
                f"    {link_source} {link_fdroid} {link_playstore} {link_website}",
            ]
        )
        lines.append("\n".join(app_lines))

    return "\n".join(lines)


def build_category(cat, categories_dir):
    md_file = categories_dir / (cat.stem + ".md")
    md_file.write_text(render_category(cat), encoding=ENCODING)


def render_readme(root, categories):
    readme_contents = (root / "README.md").read_text(encoding=ENCODING)

    n_apps = count_apps(categories)
    app_count_md = (
        f'<img src="https://img.shields.io/badge/{n_apps}-apps-red?style=for-the-badge" '
        'alt="App count"/>'
    )
    readme_contents = replace_chunk(readme_contents, "apps-count", app_count_md)

    toc_lines = [""]
    for category in categories:
        json_cat = load_category(category)
        title = json_cat.get("title")
        emoji = json_cat.get("emoji")
        link = category.stem
        toc_lines.append(f"- [{emoji} {title}](categories/{link}.md)")
    readme_contents = replace_chunk(
        readme_contents, "table-of-contents", "\n".join(toc_lines)
    )

    return readme_contents


def build_readme(root, categories):
    readme_contents = render_readme(root, categories)
    (root / "README.md").write_text(readme_contents, encoding=ENCODING)


def main():
    root = pathlib.Path(__file__).parent.parent.resolve()
    json_dir = root / "apps"
    categories_dir = root / "categories"

    if not categories_dir.exists():
        pathlib.Path.mkdir(categories_dir)

    categories = parse_categories(json_dir)
    build_readme(root, categories)
    for category in categories:
        build_category(category, categories_dir)


if __name__ == "__main__":
    main()
