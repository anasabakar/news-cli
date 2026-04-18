# Roadmap

Direction for **news-cli**: a small, respectful **multi-source** news reader in the terminal. Items are **aspirational**, not commitments.

## Adding sources (ongoing)

We expect to **add new outlets over time**—each release may ship more `sources/*.py` entries.

**Process (for contributors):**

1. Implement `search(query, limit) -> list[SearchResult]` in `src/news_cli/sources/<name>.py` (see [CONTRIBUTING.md](CONTRIBUTING.md)).
2. Register the source in `src/news_cli/sources/__init__.py` (`_REGISTRY`, optional `_ALIASES`).
3. Update the **Supported sources** table in [README.md](README.md).
4. Prefer **documented APIs or RSS** when possible; if you rely on HTML scraping, note breakage risk in the module docstring.

**Users:** run `cli-news --list-sources` to see which sources your installed version supports—do not rely only on static docs.

## Near term (0.x)

- **Tests**: fixtures for HTML parsers; no live network in default CI.
- **PyPI**: publish as `news-cli`; document `pipx install news-cli` / `uv tool install`.
- **CI**: lint + tests on pull requests.
- **License**: add `LICENSE` (often MIT) and SPDX metadata in `pyproject.toml`.

## Medium term (1.x)

- **More sources** (rolling): same adapter pattern; optional per-source caps and timeouts.
- **Pagination** flags where a site supports next pages (`--page`, conservative defaults).
- **Config**: env vars or a small config file for default `--source`, timeout, `--limit`.
- **Output**: `NO_COLOR`, optional column width for non-TTY.

## Broader vision

- **Stable adapter contract**: `search` + metadata (display name, base URL, rate-limit hints).
- **Optional extras**: `pip install news-cli[extra]` only if a source needs heavy dependencies.

## Non-goals

- Paywall circumvention, bulk archival at scale, or mandatory headless browsers in core.

## Input

Open an issue or a small PR; see [CONTRIBUTING.md](CONTRIBUTING.md).