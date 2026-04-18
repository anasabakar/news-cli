from __future__ import annotations

from urllib.parse import urljoin

from bs4 import BeautifulSoup

from news_cli.http_client import fetch_html
from news_cli.sources.base import SearchResult

SOURCE_ID = "hn"
HN_BASE = "https://news.ycombinator.com"
MAX_PAGES = 15


def _query_words(query: str) -> list[str]:
    return [w for w in query.lower().split() if w]


def _title_matches(title: str, words: list[str]) -> bool:
    if not words:
        return True
    t = title.lower()
    return all(w in t for w in words)


def _normalize_story_url(href: str) -> str:
    href = (href or "").strip()
    if not href:
        return ""
    if href.startswith("http://") or href.startswith("https://"):
        return href
    if href.startswith("item?"):
        return f"{HN_BASE}/{href}"
    return urljoin(HN_BASE + "/", href)


def _parse_page(html: str) -> list[tuple[str, str, str]]:
    soup = BeautifulSoup(html, "lxml")
    rows: list[tuple[str, str, str]] = []
    for row in soup.select("tr.athing"):
        title_a = row.select_one("span.titleline > a")
        if not title_a:
            continue
        title = title_a.get_text(strip=True)
        href = title_a.get("href") or ""
        sub = row.find_next_sibling("tr")
        author = "—"
        if sub:
            u = sub.select_one("a.hnuser")
            if u:
                author = u.get_text(strip=True)
        rows.append((title, href, author))
    return rows


def _next_page_url(html: str) -> str | None:
    soup = BeautifulSoup(html, "lxml")
    more = soup.select_one("a.morelink")
    if not more:
        return None
    href = (more.get("href") or "").strip()
    if not href:
        return None
    return urljoin(HN_BASE + "/", href)


def search(query: str, limit: int = 20) -> list[SearchResult]:
    """
    Scrape HN /newest (paginated) and keep stories whose titles contain all query words.
    This is not Algolia full-text search—broader queries match more stories.
    """
    words = _query_words(query)
    page_url = f"{HN_BASE}/newest"
    out: list[SearchResult] = []
    seen_urls: set[str] = set()

    for _ in range(MAX_PAGES):
        html = fetch_html(page_url)
        for title, href, author in _parse_page(html):
            if not _title_matches(title, words):
                continue
            url = _normalize_story_url(href)
            if not url or url in seen_urls:
                continue
            seen_urls.add(url)
            out.append(SearchResult(title=title, url=url, author=author, source=SOURCE_ID))
            if len(out) >= limit:
                return out

        nxt = _next_page_url(html)
        if not nxt:
            break
        page_url = nxt

    return out
