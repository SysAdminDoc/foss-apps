import json
import pathlib
import re
from urllib.parse import urlparse


ENCODING = "utf-8"
SOURCE_RE = re.compile(
    r"https://(gitlab|github)\.com/([a-zA-Z0-9\-_.]+)/([a-zA-Z0-9\-_.]+)"
)
INSTALL_SOURCE_FIELDS = (
    ("fdroid", "F-Droid"),
    ("izzyondroid", "IzzyOnDroid"),
    ("accrescent", "Accrescent"),
    ("obtainium", "Obtainium"),
    ("playstore", "Play Store"),
    ("website", "Website"),
)

CATALOG_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="Search and filter open source Android app alternatives by category, install source, source host, maintenance status, and trust metadata.">
  <meta name="theme-color" content="#0d1117">
  <link rel="icon" href="data:,">
  <title>Cool FOSS Android Apps Catalog</title>
  <style>
    :root {
      color-scheme: dark;
      --bg: #0d1117;
      --panel: #111820;
      --panel-2: #151d27;
      --border: #2a3442;
      --text: #e6edf3;
      --muted: #9aa7b6;
      --accent: #38d6c9;
      --accent-2: #f0b84a;
      --ok: #5fd38d;
      --warn: #f0b84a;
      --danger: #ff7b72;
      --radius: 8px;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      background: radial-gradient(circle at top left, rgba(56, 214, 201, 0.10), transparent 34rem), var(--bg);
      color: var(--text);
      min-height: 100vh;
    }
    .shell { width: min(1480px, calc(100% - 40px)); margin: 0 auto; padding: 28px 0 24px; }
    header { display: flex; align-items: start; justify-content: space-between; gap: 20px; margin-bottom: 22px; }
    .brand { display: flex; gap: 14px; align-items: center; }
    .mark { width: 34px; height: 34px; color: var(--accent); flex: 0 0 auto; }
    h1 { font-size: clamp(1.55rem, 1.2rem + 1vw, 2.25rem); line-height: 1.1; margin: 0; letter-spacing: 0; }
    .count { display: inline-flex; margin-left: 10px; padding: 5px 8px; border: 1px solid rgba(56, 214, 201, .35); border-radius: 6px; color: var(--accent); background: rgba(56, 214, 201, .10); font-size: .9rem; vertical-align: middle; }
    .subtitle { margin: 12px 0 0; color: var(--muted); max-width: 720px; }
    a { color: var(--accent); text-decoration: none; }
    a:hover { text-decoration: underline; }
    .back { white-space: nowrap; padding-top: 4px; }
    .toolbar { display: grid; gap: 16px; margin-bottom: 18px; }
    .search-wrap { position: relative; }
    .search-wrap input {
      width: 100%;
      min-height: 52px;
      border: 1px solid var(--border);
      border-radius: var(--radius);
      background: rgba(17, 24, 32, .92);
      color: var(--text);
      padding: 0 16px;
      font: inherit;
      outline: none;
    }
    .search-wrap input:focus, select:focus, button:focus { border-color: var(--accent); box-shadow: 0 0 0 3px rgba(56, 214, 201, .14); }
    .filters { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 14px; align-items: end; }
    label { display: grid; gap: 7px; color: var(--text); font-size: .92rem; }
    select, button {
      border: 1px solid var(--border);
      border-radius: 6px;
      background: var(--panel);
      color: var(--text);
      min-height: 46px;
      padding: 0 12px;
      font: inherit;
    }
    select { width: 100%; }
    button { cursor: pointer; width: auto; }
    .summary { display: flex; align-items: center; justify-content: space-between; gap: 14px; color: var(--muted); margin: 8px 0 14px; }
    .summary strong { color: var(--accent); font-size: 1.08rem; }
    .summary button { min-width: 132px; }
    .table-wrap { border: 1px solid var(--border); border-radius: var(--radius); overflow: hidden; background: rgba(17, 24, 32, .82); }
    table { width: 100%; border-collapse: collapse; table-layout: fixed; }
    th:nth-child(1), td:nth-child(1) { width: 28%; }
    th:nth-child(2), td:nth-child(2) { width: 16%; }
    th:nth-child(3), td:nth-child(3) { width: 16%; }
    th:nth-child(4), td:nth-child(4) { width: 12%; }
    th:nth-child(5), td:nth-child(5) { width: 13%; }
    th:nth-child(6), td:nth-child(6) { width: 15%; }
    thead { background: rgba(21, 29, 39, .96); }
    th, td { padding: 16px 14px; border-bottom: 1px solid var(--border); text-align: left; vertical-align: top; }
    th { color: var(--text); font-size: .86rem; font-weight: 650; }
    tbody tr:hover { background: rgba(56, 214, 201, .055); }
    tbody tr:last-child td { border-bottom: 0; }
    .app-name { font-weight: 700; margin-bottom: 4px; }
    .desc { color: var(--muted); line-height: 1.38; }
    .tag-row { display: flex; flex-wrap: wrap; gap: 6px; }
    .tag { display: inline-flex; align-items: center; border: 1px solid var(--border); border-radius: 6px; padding: 4px 7px; color: var(--muted); background: rgba(13, 17, 23, .38); font-size: .82rem; }
    .tag.install { border-color: rgba(56, 214, 201, .35); color: var(--accent); }
    .status { display: inline-flex; gap: 7px; align-items: center; color: var(--muted); }
    .dot { width: 8px; height: 8px; border-radius: 50%; background: var(--muted); }
    .status.active .dot { background: var(--ok); }
    .status.stale .dot, .status.deprecated .dot, .status.archived .dot { background: var(--warn); }
    .status.unknown .dot { background: var(--muted); }
    .meta { color: var(--muted); line-height: 1.45; }
    .empty { padding: 28px; color: var(--muted); text-align: center; }
    footer { display: flex; justify-content: space-between; gap: 16px; margin-top: 18px; color: var(--muted); font-size: .9rem; }
    @media (max-width: 980px) {
      .filters { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      th:nth-child(4), td:nth-child(4) { display: none; }
    }
    @media (max-width: 720px) {
      .shell { width: min(100% - 24px, 1480px); padding-top: 18px; }
      header, .summary, footer { display: grid; }
      .back { padding-top: 0; }
      .filters { grid-template-columns: 1fr; }
      table, thead, tbody, tr, td { display: block; width: 100%; }
      th:nth-child(n), td:nth-child(n) { width: 100%; }
      thead { display: none; }
      tr { border-bottom: 1px solid var(--border); padding: 12px 0; }
      td { border: 0; padding: 8px 14px; }
      td::before { content: attr(data-label); display: block; color: var(--muted); font-size: .75rem; margin-bottom: 5px; text-transform: uppercase; letter-spacing: .04em; }
    }
  </style>
</head>
<body>
  <main class="shell">
    <header>
      <div>
        <div class="brand">
          <svg class="mark" viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M7.2 6.8 5.7 4.2a.7.7 0 0 1 1.2-.7l1.6 2.8a7.7 7.7 0 0 1 7 0l1.6-2.8a.7.7 0 1 1 1.2.7l-1.5 2.6A7.4 7.4 0 0 1 20 12.6V20a1.5 1.5 0 0 1-1.5 1.5h-13A1.5 1.5 0 0 1 4 20v-7.4a7.4 7.4 0 0 1 3.2-5.8ZM8 11a1 1 0 1 0 0-2 1 1 0 0 0 0 2Zm8 0a1 1 0 1 0 0-2 1 1 0 0 0 0 2ZM2 13h1v6H2v-6Zm19 0h1v6h-1v-6Z"/></svg>
          <h1>Cool FOSS Android Apps <span class="count">__COUNT__ apps</span></h1>
        </div>
        <p class="subtitle">Search and compare open source Android app alternatives by category, install source, source host, maintenance status, and trust metadata.</p>
      </div>
      <a class="back" href="README.md">Back to README</a>
    </header>
    <section class="toolbar" aria-label="Catalog filters">
      <div class="search-wrap">
        <input id="search" type="search" placeholder="Search apps by name, description, source, package, or notes" autocomplete="off">
      </div>
      <div class="filters">
        <label>Category<select id="category"></select></label>
        <label>Install source<select id="installSource"></select></label>
        <label>Source host<select id="sourceHost"></select></label>
        <label>Sort by<select id="sort"></select></label>
      </div>
    </section>
    <section class="summary" aria-live="polite">
      <div><strong id="resultCount">0 results</strong> <span id="filterNote"></span></div>
      <button id="clearFilters" type="button">Clear filters</button>
    </section>
    <section class="table-wrap">
      <table>
        <thead><tr><th>App</th><th>Category</th><th>Install sources</th><th>Source host</th><th>Maintenance</th><th>Trust & metadata</th></tr></thead>
        <tbody id="results"></tbody>
      </table>
      <div id="empty" class="empty" hidden>No apps match the current filters.</div>
    </section>
    <footer>
      <span>Filters update the URL so searches can be shared.</span>
      <span>Generated from apps/*.json by scripts/build.py.</span>
    </footer>
  </main>
  <script id="catalog-data" type="application/json">__DATA__</script>
  <script>
    const apps = JSON.parse(document.getElementById('catalog-data').textContent);
    const state = {
      search: document.getElementById('search'),
      category: document.getElementById('category'),
      installSource: document.getElementById('installSource'),
      sourceHost: document.getElementById('sourceHost'),
      sort: document.getElementById('sort'),
      resultCount: document.getElementById('resultCount'),
      filterNote: document.getElementById('filterNote'),
      clear: document.getElementById('clearFilters'),
      results: document.getElementById('results'),
      empty: document.getElementById('empty')
    };
    const sortOptions = [
      ['name', 'Name (A to Z)'],
      ['category', 'Category'],
      ['status', 'Maintenance status']
    ];
    function uniq(values) { return [...new Set(values.filter(Boolean))].sort((a, b) => a.localeCompare(b)); }
    function fillSelect(select, label, values) {
      select.innerHTML = `<option value="">${label}</option>` + values.map(value => `<option>${escapeHtml(value)}</option>`).join('');
    }
    function escapeHtml(value) {
      return String(value ?? '').replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
    }
    function installTags(app) {
      return app.install_sources.length ? app.install_sources.map(source => `<span class="tag install">${escapeHtml(source)}</span>`).join('') : '<span class="tag">Source only</span>';
    }
    function trustText(app) {
      const bits = [];
      if (app.package) bits.push(`Package: ${app.package}`);
      if (app.license) bits.push(`License: ${app.license}`);
      if (app.fdroid_package) bits.push(`F-Droid: ${app.fdroid_package}`);
      if (app.izzyondroid_package) bits.push(`Izzy: ${app.izzyondroid_package}`);
      if (app.anti_features.length) bits.push(`Anti-features: ${app.anti_features.join(', ')}`);
      if (app.successor) bits.push(`Successor: ${app.successor}`);
      return bits.length ? bits.map(escapeHtml).join('<br>') : '<span class="tag">No extra metadata</span>';
    }
    function matches(app, query) {
      const haystack = [app.name, app.description, app.category, app.source, app.source_host, app.package, app.license, app.successor, app.anti_features.join(' ')].join(' ').toLowerCase();
      return !query || haystack.includes(query);
    }
    function render() {
      const query = state.search.value.trim().toLowerCase();
      let filtered = apps.filter(app =>
        matches(app, query) &&
        (!state.category.value || app.category === state.category.value) &&
        (!state.installSource.value || app.install_sources.includes(state.installSource.value)) &&
        (!state.sourceHost.value || app.source_host === state.sourceHost.value)
      );
      const sort = state.sort.value;
      filtered.sort((a, b) => {
        if (sort === 'category') return (a.category + a.name).localeCompare(b.category + b.name);
        if (sort === 'status') return (a.maintenance_status + a.name).localeCompare(b.maintenance_status + b.name);
        return a.name.localeCompare(b.name);
      });
      state.resultCount.textContent = `${filtered.length} ${filtered.length === 1 ? 'result' : 'results'}`;
      state.filterNote.textContent = filtered.length === apps.length ? '' : `(filtered from ${apps.length} apps)`;
      state.empty.hidden = filtered.length !== 0;
      state.results.innerHTML = filtered.map(app => `
        <tr>
          <td data-label="App"><div class="app-name"><a href="${escapeHtml(app.source)}">${escapeHtml(app.name)}</a></div><div class="desc">${escapeHtml(app.description)}</div></td>
          <td data-label="Category"><span class="tag">${escapeHtml(app.category)}</span></td>
          <td data-label="Install sources"><div class="tag-row">${installTags(app)}</div></td>
          <td data-label="Source host">${escapeHtml(app.source_host || 'Unknown')}</td>
          <td data-label="Maintenance"><span class="status ${escapeHtml(app.maintenance_status)}"><span class="dot"></span>${escapeHtml(app.maintenance_status_label)}</span></td>
          <td data-label="Trust & metadata"><div class="meta">${trustText(app)}</div></td>
        </tr>`).join('');
      writeUrl();
    }
    function writeUrl() {
      const params = new URLSearchParams();
      if (state.search.value.trim()) params.set('q', state.search.value.trim());
      if (state.category.value) params.set('category', state.category.value);
      if (state.installSource.value) params.set('source', state.installSource.value);
      if (state.sourceHost.value) params.set('host', state.sourceHost.value);
      if (state.sort.value !== 'name') params.set('sort', state.sort.value);
      history.replaceState(null, '', `${location.pathname}${params.toString() ? '?' + params : ''}`);
    }
    function readUrl() {
      const params = new URLSearchParams(location.search);
      state.search.value = params.get('q') || '';
      state.category.value = params.get('category') || '';
      state.installSource.value = params.get('source') || '';
      state.sourceHost.value = params.get('host') || '';
      state.sort.value = params.get('sort') || 'name';
    }
    fillSelect(state.category, 'All categories', uniq(apps.map(app => app.category)));
    fillSelect(state.installSource, 'All sources', uniq(apps.flatMap(app => app.install_sources)));
    fillSelect(state.sourceHost, 'All hosts', uniq(apps.map(app => app.source_host)));
    state.sort.innerHTML = sortOptions.map(([value, label]) => `<option value="${value}">${label}</option>`).join('');
    readUrl();
    [state.search, state.category, state.installSource, state.sourceHost, state.sort].forEach(control => control.addEventListener('input', render));
    state.clear.addEventListener('click', () => {
      state.search.value = '';
      state.category.value = '';
      state.installSource.value = '';
      state.sourceHost.value = '';
      state.sort.value = 'name';
      render();
    });
    render();
  </script>
</body>
</html>
"""


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

    return "**Review:** " + " | ".join(parts)


def trust_metadata(app):
    parts = []
    package = app.get("package")
    if package:
        parts.append(f"package: {package}")

    license_name = app.get("license")
    if license_name:
        parts.append(f"license: {license_name}")

    source_host = app.get("source_host")
    if source_host:
        parts.append(f"source host: {source_host}")

    fdroid_package = app.get("fdroid_package")
    if fdroid_package:
        parts.append(f"f-droid package: {fdroid_package}")

    izzy_package = app.get("izzyondroid_package")
    if izzy_package:
        parts.append(f"izzyondroid package: {izzy_package}")

    anti_features = app.get("anti_features")
    if anti_features:
        parts.append("anti-features: " + ", ".join(anti_features))

    if not parts:
        return ""

    return "**Trust:** " + " | ".join(parts)


def install_links(app):
    labels = (
        ("source", "Source repository"),
        ("fdroid", "F-Droid"),
        ("playstore", "Play Store"),
        ("website", "Website"),
        ("izzyondroid", "IzzyOnDroid"),
        ("accrescent", "Accrescent"),
        ("obtainium", "Obtainium"),
    )
    links = [
        f"[{label}]({app.get(field)})"
        for field, label in labels
        if app.get(field)
    ]
    return " | ".join(links)


def render_category(cat):
    cat_json = load_category(cat)
    lines = [
        f'# {cat_json.get("emoji")} {cat_json.get("title")}',
        "",
        "[Back to README](../README.md)",
    ]

    for app in cat_json.get("apps"):
        name = app.get("name")
        description = app.get("description")

        stars_link, last_commit_link = badge_links(app)
        badges = []
        if stars_link:
            badges.append(f"![Star count badge for {name}]({stars_link})")
        if last_commit_link:
            badges.append(f"![Last commit badge for {name}]({last_commit_link})")
        links = install_links(app)

        app_lines = [
            "",
            f"## {name}",
            "",
            description,
        ]
        if badges:
            app_lines.extend(["", " ".join(badges)])
        review = review_metadata(app)
        if review:
            app_lines.extend(["", review])
        trust = trust_metadata(app)
        if trust:
            app_lines.extend(["", trust])
        app_lines.extend(
            [
                "",
                f"**Links:** {links}",
                "",
                "---",
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


def source_host(app):
    if app.get("source_host"):
        return app.get("source_host")

    parsed = urlparse(app.get("source") or "")
    host = parsed.netloc.lower()
    if host == "github.com":
        return "GitHub"
    if host == "gitlab.com":
        return "GitLab"
    return parsed.netloc or "Unknown"


def maintenance_label(status):
    labels = {
        "active": "Active",
        "stale": "Stale",
        "archived": "Archived",
        "deprecated": "Deprecated",
        "unknown": "Unknown",
    }
    return labels.get(status or "unknown", status or "Unknown")


def normalized_catalog(categories):
    records = []
    for category in categories:
        category_json = load_category(category)
        category_title = category_json.get("title")
        for app in category_json.get("apps", []):
            install_sources = [
                label for field, label in INSTALL_SOURCE_FIELDS if app.get(field)
            ]
            records.append(
                {
                    "name": app.get("name"),
                    "description": app.get("description"),
                    "category": category_title,
                    "category_slug": category.stem,
                    "source": app.get("source"),
                    "source_host": source_host(app),
                    "install_sources": install_sources,
                    "maintenance_status": app.get("maintenance_status", "unknown"),
                    "maintenance_status_label": maintenance_label(
                        app.get("maintenance_status", "unknown")
                    ),
                    "package": app.get("package", ""),
                    "license": app.get("license", ""),
                    "fdroid_package": app.get("fdroid_package", ""),
                    "izzyondroid_package": app.get("izzyondroid_package", ""),
                    "anti_features": app.get("anti_features", []),
                    "successor": app.get("successor", ""),
                }
            )
    return records


def render_catalog(root, categories):
    records = normalized_catalog(categories)
    data = json.dumps(records, ensure_ascii=False, sort_keys=True).replace("</", "<\\/")
    return (
        CATALOG_TEMPLATE.replace("__COUNT__", str(len(records)))
        .replace("__DATA__", data)
    )


def build_catalog(root, categories):
    (root / "catalog.html").write_text(render_catalog(root, categories), encoding=ENCODING)


def main():
    root = pathlib.Path(__file__).parent.parent.resolve()
    json_dir = root / "apps"
    categories_dir = root / "categories"

    if not categories_dir.exists():
        pathlib.Path.mkdir(categories_dir)

    categories = parse_categories(json_dir)
    build_readme(root, categories)
    build_catalog(root, categories)
    for category in categories:
        build_category(category, categories_dir)


if __name__ == "__main__":
    main()
