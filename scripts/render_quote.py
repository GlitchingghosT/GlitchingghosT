#!/usr/bin/env python3
"""Render and cache-bust the daily Developer's Log quote card."""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import re
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QUOTES_PATH = ROOT / "data" / "quotes.json"
OUTPUT_PATH = ROOT / "assets" / "developers-log.svg"
README_PATH = ROOT / "README.md"
QUOTE_WRAP_WIDTH = 54


def load_quotes(path: Path = QUOTES_PATH) -> list[dict[str, str]]:
    quotes = json.loads(path.read_text(encoding="utf-8"))["quotes"]
    if not quotes:
        raise ValueError("The Developer's Log quote collection is empty")

    required = {"text", "author", "source"}
    for index, quote in enumerate(quotes):
        missing = required.difference(quote)
        if missing:
            raise ValueError(f"Quote {index} is missing: {', '.join(sorted(missing))}")
    return quotes


def quote_for_date(quotes: list[dict[str, str]], date: dt.date) -> tuple[int, dict[str, str]]:
    index = date.toordinal() % len(quotes)
    return index, quotes[index]


def render_svg(quote: dict[str, str], date: dt.date) -> str:
    lines = textwrap.wrap(quote["text"], width=QUOTE_WRAP_WIDTH) or [quote["text"]]
    line_spans = "".join(
        f'<tspan x="72" dy="{0 if index == 0 else 38}">{html.escape(line)}</tspan>'
        for index, line in enumerate(lines)
    )
    author_y = 150 + max(0, len(lines) - 1) * 38

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="300" viewBox="0 0 1000 300" role="img" aria-labelledby="title desc">
  <title id="title">Developer's Log quote by {html.escape(quote['author'])}</title>
  <desc id="desc">{html.escape(quote['text'])}</desc>
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#0a0d1a"/><stop offset="1" stop-color="#151334"/></linearGradient>
    <linearGradient id="accent" x1="0" y1="0" x2="1" y2="0"><stop stop-color="#61dbfb"/><stop offset=".52" stop-color="#7e5bff"/><stop offset="1" stop-color="#eebe5c"/></linearGradient>
  </defs>
  <rect x="1" y="1" width="998" height="298" rx="16" fill="url(#bg)" stroke="#313858"/>
  <rect x="0" y="0" width="8" height="300" rx="4" fill="url(#accent)"/>
  <text x="72" y="56" fill="#eebe5c" font-family="DejaVu Sans Mono, monospace" font-size="15" letter-spacing="2">DEVELOPER'S LOG / {date.isoformat()}</text>
  <text x="72" y="112" fill="#edf0f8" font-family="DejaVu Sans, Arial, sans-serif" font-size="28">{line_spans}</text>
  <text x="72" y="{author_y}" fill="#a6aec4" font-family="DejaVu Sans, Arial, sans-serif" font-size="17">— {html.escape(quote['author'])} · {html.escape(quote['source'])}</text>
  <g transform="translate(902 224)" fill="none" stroke="url(#accent)" stroke-width="3"><path d="M0 24h48M24 0v48"/><circle cx="24" cy="24" r="5" fill="#eebe5c" stroke="none"/></g>
</svg>'''


def update_readme_text(readme: str, date: dt.date) -> str:
    pattern = r"assets/developers-log\.svg(?:\?v=\d{4}-\d{2}-\d{2})?"
    replacement = f"assets/developers-log.svg?v={date.isoformat()}"
    updated, count = re.subn(pattern, replacement, readme)
    if count != 1:
        raise ValueError(f"Expected one Developer's Log image in README.md, found {count}")
    return updated


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", type=dt.date.fromisoformat, help="Render a specific YYYY-MM-DD date")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    date = args.date or dt.datetime.now(dt.timezone.utc).date()
    quotes = load_quotes()
    index, quote = quote_for_date(quotes, date)

    OUTPUT_PATH.write_text(render_svg(quote, date), encoding="utf-8")
    README_PATH.write_text(
        update_readme_text(README_PATH.read_text(encoding="utf-8"), date),
        encoding="utf-8",
    )

    print(f"date={date.isoformat()}")
    print(f"quote_index={index}")
    print(f"generated={OUTPUT_PATH}")
    print(f"updated={README_PATH}")


if __name__ == "__main__":
    main()
