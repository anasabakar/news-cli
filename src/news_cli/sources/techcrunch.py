from __future__ import annotations

from urllib.parse import quote_plus, urljoin

from bs4 import BeautifulSoup

from news_cli.http_client import fetch_html
from news_cli.sources.base import SearchResult

BASE = "https://techcrunch.com/"
SOURCE_ID = "techcrunch"


def search_url(query: str) -> str:
    return f"{BASE}?s={quote_plus(query)}"


def _author_for_title_anchor(title_a) -> str:
    node = title_a
    for _ in range(12):
        if node is None:
            break
        auth = node.select_one("a.loop-card__author")
        if auth:
            return auth.get_text(strip=True)
        node = node.parent
    return ""


def parse_search_results(html: str, limit: int = 20) -> list[SearchResult]:
    soup = BeautifulSoup(html, "lxml")
    seen: set[str] = set()
    out: list[SearchResult] = []

    for a in soup.select("a.loop-card__title-link"):
        href = (a.get("href") or "").strip()
        if not href:
            continue
        url = urljoin(BASE, href)
        if url in seen:
            continue
        title = a.get_text(strip=True)
        if not title:
            continue
        author = _author_for_title_anchor(a) or "—"
        seen.add(url)
        out.append(SearchResult(title=title, url=url, author=author, source=SOURCE_ID))
        if len(out) >= limit:
            break

    return out


def search(query: str, limit: int = 20) -> list[SearchResult]:
    url = search_url(query)
    html = fetch_html(url)
    return parse_search_results(html, limit=limit)
