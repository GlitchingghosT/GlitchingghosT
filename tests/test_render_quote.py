import datetime as dt
import unittest
import xml.etree.ElementTree as ET

from scripts import render_quote


class DeveloperLogTests(unittest.TestCase):
    def test_consecutive_dates_cycle_through_every_quote(self) -> None:
        quotes = render_quote.load_quotes()
        start = dt.date(2026, 1, 1)
        selections = [
            render_quote.quote_for_date(quotes, start + dt.timedelta(days=offset))[0]
            for offset in range(len(quotes))
        ]
        self.assertEqual(len(set(selections)), len(quotes))

    def test_svg_is_valid_and_contains_date_and_attribution(self) -> None:
        quote = {
            "text": "Readable code outlives clever code.",
            "author": "Example Author",
            "source": "Example Source",
        }
        date = dt.date(2026, 7, 22)
        svg = render_quote.render_svg(quote, date)

        ET.fromstring(svg)
        self.assertIn(date.isoformat(), svg)
        self.assertIn(quote["text"], svg)
        self.assertIn(quote["author"], svg)
        self.assertIn(quote["source"], svg)

    def test_every_quote_wraps_within_the_card_safe_width(self) -> None:
        date = dt.date(2026, 7, 22)
        namespace = {"svg": "http://www.w3.org/2000/svg"}

        for quote in render_quote.load_quotes():
            root = ET.fromstring(render_quote.render_svg(quote, date))
            lines = [
                element.text or ""
                for element in root.findall(".//svg:tspan", namespace)
            ]
            self.assertTrue(lines)
            self.assertTrue(
                all(len(line) <= render_quote.QUOTE_WRAP_WIDTH for line in lines),
                msg=f"Quote line exceeded safe width: {quote['text']}",
            )

    def test_readme_cache_version_is_inserted_and_replaced(self) -> None:
        first = render_quote.update_readme_text(
            "![Daily Developer's Log quote card](assets/developers-log.svg)",
            dt.date(2026, 7, 22),
        )
        second = render_quote.update_readme_text(first, dt.date(2026, 7, 23))

        self.assertIn("developers-log.svg?v=2026-07-23", second)
        self.assertNotIn("v=2026-07-22", second)


if __name__ == "__main__":
    unittest.main()
