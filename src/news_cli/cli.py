from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from dataclasses import asdict

import httpx

from news_cli import __version__
from news_cli.article import fetch_article_plain_text
from news_cli.sources import get_search, list_sources


def _resolve_jq() -> str | None:
    path = shutil.which("jq")
    if path:
        return path
    for candidate in ("/opt/homebrew/bin/jq", "/usr/local/bin/jq", "/usr/bin/jq"):
        if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
            return candidate
    return None


def _print_json_pretty(obj: object) -> None:
    raw = json.dumps(obj, ensure_ascii=False)
    jq = _resolve_jq()
    if not jq:
        print(
            "jq not found (install it and ensure it is on PATH). "
            "Falling back to Python JSON output.",
            file=sys.stderr,
        )
        print(json.dumps(obj, indent=2, ensure_ascii=False, sort_keys=True))
        return

    jq_args = [jq, "-S", "."]
    if sys.stdout.isatty():
        jq_args.insert(1, "-C")

    try:
        completed = subprocess.run(
            jq_args,
            input=raw,
            capture_output=True,
            text=True,
            check=True,
        )
    except OSError:
        print(json.dumps(obj, indent=2, ensure_ascii=False, sort_keys=True))
        return
    except subprocess.CalledProcessError as e:
        if e.stderr:
            print(e.stderr, file=sys.stderr, end="")
        print(json.dumps(obj, indent=2, ensure_ascii=False, sort_keys=True))
        return

    out = completed.stdout
    sys.stdout.write(out if out.endswith("\n") else out + "\n")


def _print_results(results, *, file=sys.stdout) -> None:
    for i, r in enumerate(results, start=1):
        print(f"{i}. {r.title}", file=file)
        print(f"   Author: {r.author}  ·  {r.source}", file=file)
        print(f"   {r.url}", file=file)
        print(file=file)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Search news sources and read articles as plain text.",
    )
    parser.add_argument(
        "--source",
        "-s",
        default="techcrunch",
        metavar="ID",
        help="News source id (default: techcrunch). Use --list-sources.",
    )
    parser.add_argument(
        "--list-sources",
        action="store_true",
        help="List available sources and exit",
    )
    parser.add_argument(
        "query",
        nargs="*",
        help="Search query words",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=20,
        metavar="N",
        help="Max number of search results (default: 20)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print search results as pretty JSON (jq), then continue to pick an article to read",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    args = parser.parse_args()

    if args.list_sources:
        for sid, name, site in list_sources():
            print(f"  {sid:12}  {name}  ({site})")
        raise SystemExit(0)

    if not args.query:
        parser.error("query is required (unless using --list-sources)")

    query = " ".join(args.query)

    try:
        search_fn = get_search(args.source)
    except KeyError:
        known = ", ".join(s[0] for s in list_sources())
        print(f"Unknown source {args.source!r}. Choose one of: {known}", file=sys.stderr)
        raise SystemExit(2) from None

    try:
        results = search_fn(query, limit=args.limit)
    except httpx.HTTPStatusError as e:
        print(f"HTTP error: {e.response.status_code} for {e.request.url}", file=sys.stderr)
        raise SystemExit(1) from e
    except httpx.HTTPError as e:
        print(f"Request failed: {e}", file=sys.stderr)
        raise SystemExit(1) from e

    if not results:
        print("No search results found.", file=sys.stderr)
        raise SystemExit(1)

    if args.json:
        _print_json_pretty([asdict(r) for r in results])
        sys.stdout.flush()
        try:
            cols = shutil.get_terminal_size((72, 20)).columns
        except OSError:
            cols = 72
        bar = "─" * max(40, min(72, cols - 1))
        print(file=sys.stderr)
        print(bar, file=sys.stderr)
        print("Articles (match numbers to the JSON order above):", file=sys.stderr)
        print(file=sys.stderr)
        _print_results(results, file=sys.stderr)

    else:
        _print_results(results)

    while True:
        try:
            print("Enter number to read (q to quit): ", end="", file=sys.stderr, flush=True)
            line = sys.stdin.readline()
            if line == "":
                raise EOFError
            line = line.strip()
        except (EOFError, KeyboardInterrupt):
            print(file=sys.stderr)
            return

        if line.lower() in ("q", "quit", ""):
            return

        try:
            idx = int(line)
        except ValueError:
            print("Enter a number, or q to quit.", file=sys.stderr)
            continue

        if idx < 1 or idx > len(results):
            print(f"Enter a number between 1 and {len(results)}.", file=sys.stderr)
            continue

        url = results[idx - 1].url
        try:
            text = fetch_article_plain_text(url)
        except httpx.HTTPStatusError as e:
            print(f"HTTP error: {e.response.status_code} for {e.request.url}", file=sys.stderr)
            continue
        except httpx.HTTPError as e:
            print(f"Request failed: {e}", file=sys.stderr)
            continue

        if not text:
            print("Could not extract article text.", file=sys.stderr)
            continue

        try:
            cols = shutil.get_terminal_size((72, 20)).columns
        except OSError:
            cols = 72
        rule = "═" * max(40, min(72, cols - 1))
        print()
        print(rule)
        print(text)
        print(rule)
        print()


if __name__ == "__main__":
    main()
