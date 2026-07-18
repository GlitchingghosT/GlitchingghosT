#!/usr/bin/env python3
"""Render a deterministic daily Developer's Log quote card."""

from __future__ import annotations

import datetime as dt
import html
import json
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
quotes = json.loads((ROOT / "data" / "quotes.json").read_text())["quotes"]
index = dt.date.today().toordinal() % len(quotes)
quote = quotes[index]
lines = textwrap.wrap(quote["text"], width=78)
line_spans = "".join(
    f'<tspan x="72" dy="{0 if i == 0 else 38}">{html.escape(line)}</tspan>'
    for i, line in enumerate(lines)
)
author_y = 150 + max(0, len(lines) - 1) * 38
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="300" viewBox="0 0 1000 300" role="img" aria-labelledby="title desc">
  <title id="title">Developer's Log quote by {html.escape(quote['author'])}</title>
  <desc id="desc">{html.escape(quote['text'])}</desc>
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#0a0d1a"/><stop offset="1" stop-color="#151334"/></linearGradient>
    <linearGradient id="accent" x1="0" y1="0" x2="1" y2="0"><stop stop-color="#61dbfb"/><stop offset=".52" stop-color="#7e5bff"/><stop offset="1" stop-color="#eebe5c"/></linearGradient>
  </defs>
  <rect x="1" y="1" width="998" height="298" rx="16" fill="url(#bg)" stroke="#313858"/>
  <rect x="0" y="0" width="8" height="300" rx="4" fill="url(#accent)"/>
  <text x="72" y="56" fill="#eebe5c" font-family="DejaVu Sans Mono, monospace" font-size="15" letter-spacing="2">DEVELOPER'S LOG / {dt.date.today().isoformat()}</text>
  <text x="72" y="112" fill="#edf0f8" font-family="DejaVu Sans, Arial, sans-serif" font-size="28">{line_spans}</text>
  <text x="72" y="{author_y}" fill="#a6aec4" font-family="DejaVu Sans, Arial, sans-serif" font-size="17">— {html.escape(quote['author'])} · {html.escape(quote['source'])}</text>
  <g transform="translate(902 224)" fill="none" stroke="url(#accent)" stroke-width="3"><path d="M0 24h48M24 0v48"/><circle cx="24" cy="24" r="5" fill="#eebe5c" stroke="none"/></g>
</svg>'''
output = ROOT / "assets" / "developers-log.svg"
output.write_text(svg)
print(f"quote_index={index}")
print(f"generated={output}")
