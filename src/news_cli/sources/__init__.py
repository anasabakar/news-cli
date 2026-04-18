from __future__ import annotations

from news_cli.sources import hackernews, techcrunch, venturebeat

# id -> (human name, home page URL, search callable)
_REGISTRY: dict[str, tuple[str, str, object]] = {
    "techcrunch": (
        "TechCrunch",
        "https://techcrunch.com/",
        techcrunch.search,
    ),
    "hn": (
        "Hacker News",
        "https://news.ycombinator.com/",
        hackernews.search,
    ),
    "venturebeat": (
        "VentureBeat",
        "https://venturebeat.com/",
        venturebeat.search,
    ),
}

_ALIASES: dict[str, str] = {
    "hackernews": "hn",
    "yc": "hn",
    "tc": "techcrunch",
    "vb": "venturebeat",
}


def normalize_source_id(raw: str) -> str:
    key = raw.lower().strip()
    key = _ALIASES.get(key, key)
    if key not in _REGISTRY:
        raise KeyError(key)
    return key


def list_sources() -> list[tuple[str, str, str]]:
    """Return (id, display name, site URL) for each source."""
    return [(sid, meta[0], meta[1]) for sid, meta in _REGISTRY.items()]


def get_search(source_id: str):
    sid = normalize_source_id(source_id)
    return _REGISTRY[sid][2]
