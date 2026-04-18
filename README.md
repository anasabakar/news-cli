# news-cli

A small **open-source command-line tool** to search tech news sources and read articles as **plain text** in your terminal.

**Sources are added over time.** The list below is a snapshot—run `news --list-sources` anytime to see what your installed version supports, and see [ROADMAP.md](ROADMAP.md) for how we plan to grow coverage.

## Choosing and searching a source

Every search uses **one** backend at a time:


| Flag                  | Meaning                                                                 |
| --------------------- | ----------------------------------------------------------------------- |
| `**--source` / `-s`** | Which site to search (default: `**techcrunch`**).                       |
| `**--list-sources**`  | Print all built-in source ids, display names, and home URLs, then exit. |


Examples:

```bash
news --list-sources
news "sam altman"                         # default source: techcrunch
news -s techcrunch "openai"
news -s hn "openai chatgpt"               # HN: all words must appear in the story title
news -s venturebeat "salesforce"
news --source venturebeat "agents" --limit 10
python -m news_cli -s hn "rust"
```

Other flags:

- `**--limit**`: max results (default: 20).
- `**--json**`: pretty JSON on stdout (uses `**jq**` when available), then the interactive article picker (list + prompts on stderr).

## Supported sources (current)


| ID            | Outlet                                       | How search works                                                                                          |
| ------------- | -------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| `techcrunch`  | [TechCrunch](https://techcrunch.com/)        | HTML search (`?s=`)                                                                                       |
| `hn`          | [Hacker News](https://news.ycombinator.com/) | **Scrapes** `/newest` (paginated); titles must contain **all** query words (aliases: `hackernews`, `yc`). |
| `venturebeat` | [VentureBeat](https://venturebeat.com/)      | HTML search (`?s=`) (alias: `vb`)                                                                         |


Article text is extracted with **trafilatura** from each result URL (HN often links out to the publisher).

## Requirements

- **Python 3.11+**
- Optional: `**jq`** for colored JSON with `--json`.

## Install (from clone)

```bash
cd news-cli
python3 -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -e .
```

This installs the `**news**` command.

## Project layout

```
src/news_cli/
  cli.py              # CLI: --source, --list-sources, interactive read
  article.py
  http_client.py
  sources/
    base.py
    techcrunch.py
    hackernews.py
    venturebeat.py
    __init__.py       # source registry (add new sources here)
```

## Responsible use

Respect each site’s terms, `robots.txt`, and rate limits. For **Hacker News**, modest queries and limits reduce how many listing pages are fetched.

## Roadmap / contributing

- [ROADMAP.md](ROADMAP.md) — how we add sources and evolve the tool  
- [CONTRIBUTING.md](CONTRIBUTING.md) — how to add a new source and open a PR

## License

Add a `LICENSE` file when you publish (for example MIT).