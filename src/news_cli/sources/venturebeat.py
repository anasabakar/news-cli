from __future__ import annotations

from urllib.parse import quote_plus, urljoin

from bs4 import BeautifulSoup

from news_cli.http_client import fetch_html
from news_cli.sources.base import SearchResult

BASE = "https://venturebeat.com/"
SOURCE_ID = "venturebeat"


def search_url(query: str) -> str:
    return f"{BASE}?s={quote_plus(query)}"


def parse_search_results(html: str, limit: int = 20) -> list[SearchResult]:
    soup = BeautifulSoup(html, "lxml")
    seen: set[str] = set()
    out: list[SearchResult] = []

    for art in soup.select("article"):
        a = art.select_one("h2 > a")
        if not a:
            continue
        href = (a.get("href") or "").strip()
        if not href:
            continue
        url = urljoin(BASE, href)
        if url in seen:
            continue
        title = a.get_text(strip=True)
        if not title:
            continue
        auth_el = art.select_one('a[href*="/author/"]')
        author = auth_el.get_text(strip=True) if auth_el else "—"
        seen.add(url)
        out.append(SearchResult(title=title, url=url, author=author, source=SOURCE_ID))
        if len(out) >= limit:
            break

    return out


def search(query: str, limit: int = 20) -> list[SearchResult]:
    url = search_url(query)
    html = fetch_html(url)
    return parse_search_results(html, limit=limit)
