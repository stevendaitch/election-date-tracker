"""
SOS Special Elections Scraper
Scrapes special elections from official state Secretary of State websites.

Usage:
    python scraper.py              # Scrape priority states
    python scraper.py --all        # Scrape all 50 states
    python scraper.py --state TX   # Scrape specific state
"""

import argparse
import csv
import json
import re
from datetime import datetime, date
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

# Paths
SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / "data"

# State names
STATE_NAMES = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas", "CA": "California",
    "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware", "FL": "Florida", "GA": "Georgia",
    "HI": "Hawaii", "ID": "Idaho", "IL": "Illinois", "IN": "Indiana", "IA": "Iowa",
    "KS": "Kansas", "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland",
    "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi", "MO": "Missouri",
    "MT": "Montana", "NE": "Nebraska", "NV": "Nevada", "NH": "New Hampshire", "NJ": "New Jersey",
    "NM": "New Mexico", "NY": "New York", "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio",
    "OK": "Oklahoma", "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina",
    "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas", "UT": "Utah", "VT": "Vermont",
    "VA": "Virginia", "WA": "Washington", "WV": "West Virginia", "WI": "Wisconsin", "WY": "Wyoming"
}

ALL_STATES = list(STATE_NAMES.keys())
PRIORITY_STATES = ["FL", "NJ", "AL", "TX", "MI", "MN", "PA", "GA", "OH", "CA", "NY"]

# Date parsing patterns
DATE_PATTERNS = [
    (r"(\w+ \d{1,2},? \d{4})", ["%B %d, %Y", "%B %d %Y"]),
    (r"(\d{1,2}/\d{1,2}/\d{4})", ["%m/%d/%Y"]),
    (r"(\d{4}-\d{2}-\d{2})", ["%Y-%m-%d"]),
]

SPECIAL_KEYWORDS = ["special", "vacancy", "runoff", "fill", "called"]


class SOSScraper:
    """Scraper for special elections from official SOS websites."""

    def __init__(self):
        self.results = {}
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0',
            'Accept': 'text/html,application/xhtml+xml',
        })
        self.registry = self._load_registry()

    def _load_registry(self):
        """Load SOS URL registry."""
        registry = {}
        path = SCRIPT_DIR / "sos_registry.csv"
        if path.exists():
            with open(path, encoding="utf-8") as f:
                for row in csv.DictReader(f):
                    registry[row["state_code"]] = row
        return registry

    def _parse_date(self, text):
        """Try to parse a date from text."""
        if not text:
            return None
        for pattern, formats in DATE_PATTERNS:
            for match in re.findall(pattern, text):
                for fmt in formats:
                    try:
                        return datetime.strptime(match, fmt).strftime("%Y-%m-%d")
                    except ValueError:
                        continue
        return None

    def _is_future(self, date_str):
        """Check if date is in the future."""
        if not date_str:
            return False
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").date() >= date.today()
        except ValueError:
            return False

    def scrape_state(self, state_code):
        """Scrape a single state's SOS website for special elections."""
        state_code = state_code.upper()
        state_name = STATE_NAMES.get(state_code, state_code)
        registry = self.registry.get(state_code, {})

        base_url = registry.get("elections_url") or registry.get("sos_url", "")
        if not base_url:
            print(f"[{state_code}] No URL - skipping")
            return []

        print(f"\n[{state_code}] {state_name}: {base_url}")

        found = []
        try:
            response = self.session.get(base_url, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')
            text = soup.get_text().lower()

            if any(kw in text for kw in SPECIAL_KEYWORDS):
                print(f"  Found special election keywords")
                # Look for date-like patterns near special election mentions
                for element in soup.find_all(['p', 'li', 'td', 'div', 'article']):
                    elem_text = element.get_text()
                    if any(kw in elem_text.lower() for kw in SPECIAL_KEYWORDS):
                        parsed_date = self._parse_date(elem_text)
                        if parsed_date and self._is_future(parsed_date):
                            found.append({
                                "state_code": state_code,
                                "state_name": state_name,
                                "date": parsed_date,
                                "text": elem_text[:200].strip(),
                                "source": base_url,
                            })
                            print(f"  + {parsed_date}: {elem_text[:60]}...")
            else:
                print(f"  No special election keywords found")

        except requests.RequestException as e:
            print(f"  ERROR: {str(e)[:60]}")
        except Exception as e:
            print(f"  PARSE ERROR: {str(e)[:60]}")

        self.results[state_code] = {
            "state_name": state_name,
            "count": len(found),
            "elections": found,
        }
        return found

    def scrape_states(self, states):
        """Scrape multiple states."""
        print("=" * 50)
        print("SOS SPECIAL ELECTIONS SCRAPER")
        print("=" * 50)

        for state in states:
            self.scrape_state(state)

        return self.results

    def save(self, filename="special_elections_from_sos.json"):
        """Save results to JSON."""
        output = DATA_DIR / filename
        DATA_DIR.mkdir(exist_ok=True)

        with open(output, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2)

        # Summary
        total = sum(r["count"] for r in self.results.values())
        with_specials = sum(1 for r in self.results.values() if r["count"] > 0)

        print(f"\n{'=' * 50}")
        print(f"Saved: {output}")
        print(f"States: {len(self.results)} | With specials: {with_specials} | Total found: {total}")
        print("=" * 50)

        return output


def main():
    parser = argparse.ArgumentParser(description="Scrape special elections from SOS websites")
    parser.add_argument("--all", action="store_true", help="Scrape all 50 states")
    parser.add_argument("--state", type=str, help="Scrape specific state (e.g., TX)")
    args = parser.parse_args()

    scraper = SOSScraper()

    if args.state:
        scraper.scrape_state(args.state)
    elif args.all:
        scraper.scrape_states(ALL_STATES)
    else:
        scraper.scrape_states(PRIORITY_STATES)

    scraper.save()

    print("\nNext: Manually verify results and update special_elections.csv")
    return 0


if __name__ == "__main__":
    exit(main())
