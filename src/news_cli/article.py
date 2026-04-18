from __future__ import annotations

import re
import shutil
import textwrap
from dataclasses import dataclass

import trafilatura
from bs4 import BeautifulSoup


def _fallback_title(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")
    og = soup.find("meta", property="og:title")
    if og and og.get("content"):
        raw = og["content"].strip()
        return raw.split("|")[0].strip()
    title_tag = soup.find("title")
    if title_tag:
        raw = title_tag.get_text(strip=True)
        return raw.split("|")[0].strip()
    return ""


def _terminal_width() -> int:
    try:
        cols = shutil.get_terminal_size((88, 24)).columns
        return max(60, min(96, cols - 2))
    except OSError:
        return 88


def _split_body_paragraphs(body: str) -> list[str]:
    body = body.strip()
    if not body:
        return []
    parts = re.split(r"\n\s*\n+", body)
    return [p.strip() for p in parts if p.strip()]


@dataclass
class ArticleContent:
    title: str
    author: str
    date: str
    body_paragraphs: list[str]


def _article_content_from_extraction(html: str, data) -> ArticleContent:
    title = (data.title or "").strip() or _fallback_title(html)
    author = (data.author or "").strip()
    date = (data.date or "").strip()
    body_paragraphs = _split_body_paragraphs(data.text or "")
    return ArticleContent(title=title, author=author, date=date, body_paragraphs=body_paragraphs)


def format_article_content(content: ArticleContent, width: int | None = None) -> str:
    w = width if width is not None else _terminal_width()
    blocks: list[str] = []

    if content.title:
        blocks.append(
            textwrap.fill(content.title, width=w, break_long_words=False, break_on_hyphens=False)
        )

    meta_lines: list[str] = []
    if content.author:
        meta_lines.append(f"By {content.author}")
    if content.date:
        meta_lines.append(content.date)
    if meta_lines:
        blocks.append("\n".join(meta_lines))

    body_wrapped: list[str] = []
    for para in content.body_paragraphs:
        body_wrapped.append(
            textwrap.fill(para, width=w, break_long_words=False, break_on_hyphens=False)
        )
    body = "\n\n".join(body_wrapped)

    if not blocks and body:
        return body
    if blocks and body:
        sep = "─" * min(w, 64)
        header = "\n\n".join(blocks)
        return f"{header}\n\n{sep}\n\n{body}"
    if blocks:
        return "\n\n".join(blocks)
    return body


def article_plain_text(html: str, url: str) -> str:
    data = trafilatura.bare_extraction(
        html,
        url=url,
        include_comments=False,
        include_tables=False,
    )
    if not data:
        fallback = trafilatura.extract(html, url=url, include_comments=False, include_tables=False)
        if not fallback:
            return ""
        title = _fallback_title(html)
        paras = _split_body_paragraphs(fallback)
        content = ArticleContent(
            title=title,
            author="",
            date="",
            body_paragraphs=paras,
        )
        return format_article_content(content)

    content = _article_content_from_extraction(html, data)
    return format_article_content(content)


def fetch_article_plain_text(url: str) -> str:
    from news_cli.http_client import fetch_html

    html = fetch_html(url)
    return article_plain_text(html, url)
