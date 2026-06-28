#!/usr/bin/env python3
import argparse
import pathlib
import sys
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import build
import validate


USER_AGENT = "foss-apps-link-check/1.0"


@dataclass
class LinkTarget:
    url: str
    labels: list[str]


@dataclass
class LinkResult:
    target: LinkTarget
    status: str
    detail: str


def add_target(targets, url, label):
    if not url:
        return
    if url not in targets:
        targets[url] = LinkTarget(url=url, labels=[])
    targets[url].labels.append(label)


def collect_links(root, include_badges=True):
    root = pathlib.Path(root)
    targets = {}
    for category in build.parse_categories(root / "apps"):
        category_json = build.load_category(category)
        for app in category_json.get("apps", []):
            name = app.get("name", "<unnamed app>")
            for field in validate.URL_FIELDS:
                add_target(targets, app.get(field), f"{name} {field}")

            if include_badges:
                stars_link, last_commit_link = build.badge_links(app)
                add_target(targets, stars_link, f"{name} stars badge")
                add_target(targets, last_commit_link, f"{name} last-commit badge")

    return list(targets.values())


def classify_status(status, headers):
    remaining = headers.get("x-ratelimit-remaining") if headers else None
    if status == 429 or remaining == "0":
        return "rate-limited"
    if 200 <= status < 400:
        return "ok"
    return "failed"


def request_once(url, timeout, opener, method):
    request = Request(url, headers={"User-Agent": USER_AGENT}, method=method)
    with opener(request, timeout=timeout) as response:
        return response.status, response.headers


def check_target(target, timeout=10, opener=urlopen):
    try:
        status, headers = request_once(target.url, timeout, opener, "HEAD")
    except HTTPError as exc:
        if exc.code in {403, 405}:
            exc.close()
            try:
                status, headers = request_once(target.url, timeout, opener, "GET")
            except HTTPError as retry_exc:
                status = retry_exc.code
                headers = retry_exc.headers
                retry_exc.close()
            except URLError as retry_exc:
                return LinkResult(target, "failed", retry_exc.reason.__class__.__name__)
        else:
            status = exc.code
            headers = exc.headers
            exc.close()
    except URLError as exc:
        return LinkResult(target, "failed", exc.reason.__class__.__name__)
    except TimeoutError:
        return LinkResult(target, "failed", "TimeoutError")

    status_name = classify_status(status, headers)
    return LinkResult(target, status_name, f"HTTP {status}")


def check_links(root, timeout=10, include_badges=True, opener=urlopen, max_workers=12):
    targets = collect_links(root, include_badges=include_badges)
    if not targets:
        return []

    worker_count = min(max(1, max_workers), len(targets))
    with ThreadPoolExecutor(max_workers=worker_count) as executor:
        return list(
            executor.map(
                lambda target: check_target(target, timeout=timeout, opener=opener),
                targets,
            )
        )


def print_report(results):
    counts = {"ok": 0, "rate-limited": 0, "failed": 0}
    for result in results:
        counts[result.status] += 1

    print(
        "Checked "
        f"{len(results)} URLs: {counts['ok']} ok, "
        f"{counts['rate-limited']} rate-limited, {counts['failed']} failed."
    )

    for result in results:
        if result.status == "ok":
            continue
        labels = "; ".join(result.target.labels[:3])
        if len(result.target.labels) > 3:
            labels += f"; +{len(result.target.labels) - 3} more"
        print(f"[{result.status}] {result.detail} {result.target.url} ({labels})")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Check foss-apps catalog link health.")
    parser.add_argument(
        "--root",
        default=pathlib.Path(__file__).parent.parent,
        type=pathlib.Path,
        help="Repository root to check.",
    )
    parser.add_argument("--timeout", type=float, default=10, help="HTTP timeout in seconds.")
    parser.add_argument(
        "--no-badges",
        action="store_true",
        help="Skip generated stars and last-commit badge URLs.",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=12,
        help="Maximum concurrent HTTP checks.",
    )
    args = parser.parse_args(argv)

    results = check_links(
        args.root.resolve(),
        timeout=args.timeout,
        include_badges=not args.no_badges,
        max_workers=max(1, args.workers),
    )
    print_report(results)
    return 1 if any(result.status == "failed" for result in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
