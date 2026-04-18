# Contributing

Thank you for helping improve **news-cli**. Keep changes focused and easy to review.

## Getting started

1. Clone the repository and create a branch.
2. Create a virtual environment:
  ```bash
   python3 -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   pip install -e .
  ```
3. Run the CLI:
  ```bash
   news --list-sources
   news techcrunch "test"
   PYTHONPATH=src python -m news_cli -s hn "openai"
   PYTHONPATH=src python -m news_cli -s venturebeat "ai"
  ```
4. Optional: install `**jq**` to match `--json` behavior in production.

## Adding a news source

1. Add a module under `src/news_cli/sources/` with a `search(query: str, limit: int) -> list[SearchResult]` function.
2. Each `SearchResult` must set `**source**` to the canonical id string.
3. Register the source in `src/news_cli/sources/__init__.py` (`_REGISTRY` and optional `_ALIASES`).
4. Prefer **official or documented** APIs when available; document HTML scraping assumptions in the module docstring.
5. Update **README.md** (supported sources table).

## Code style

- Python **3.11+**, type hints where they help.
- Match existing patterns in the repo.
- Avoid heavy new dependencies without maintainer agreement.

## Pull requests

Describe what changed and why. Keep scope small. If behavior changes, note it for README updates.

## Ethics and legal

Respect site terms, robots.txt, and rate limits. Do not add features aimed at bypassing paywalls or access controls.

## Conduct

Be constructive. Maintainers may close threads that derail collaboration.