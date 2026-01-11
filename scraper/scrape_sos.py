"""
Scraper for State Secretary of State election calendar websites.
Fetches election dates from official state sources.
"""

import json
import re
from datetime import datetime
from pathlib import Path

import requests
from bs4 import BeautifulSoup

from config import STATE_SOURCES, KNOWN_2026_DATES, PILOT_STATES, STATE_NAMES

# Common date patterns found on election websites
DATE_PATTERNS = [
    # "August 4, 2026" or "August 04, 2026"
    r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2}),?\s+(\d{4})",
    # "08/04/2026" or "8/4/2026"
    r"(\d{1,2})/(\d{1,2})/(\d{4})",
    # "2026-08-04"
    r"(\d{4})-(\d{2})-(\d{2})",
]

# Keywords that indicate primary or general elections
PRIMARY_KEYWORDS = ["primary", "primary election", "primaries"]
GENERAL_KEYWORDS = ["general", "general election", "november"]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


def fetch_page(url: str, timeout: int = 15) -> str | None:
    """Fetch a web page and return its HTML content."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=timeout)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"  Error fetching {url}: {e}")
        return None


def extract_dates_from_text(text: str) -> list[dict]:
    """Extract dates from text using regex patterns."""
    dates = []

    # Pattern 1: Month DD, YYYY
    for match in re.finditer(DATE_PATTERNS[0], text, re.IGNORECASE):
        month_name, day, year = match.groups()
        try:
            date_str = f"{month_name} {day}, {year}"
            parsed = datetime.strptime(date_str, "%B %d, %Y")
            dates.append({
                "date": parsed.strftime("%Y-%m-%d"),
                "original": match.group(0),
                "context": text[max(0, match.start()-50):match.end()+50]
            })
        except ValueError:
            pass

    return dates


def classify_election_type(context: str) -> str | None:
    """Determine if a date is for primary or general election based on context."""
    context_lower = context.lower()

    for keyword in PRIMARY_KEYWORDS:
        if keyword in context_lower:
            return "primary"

    for keyword in GENERAL_KEYWORDS:
        if keyword in context_lower:
            return "general"

    return None


def scrape_state(state_code: str) -> dict:
    """Scrape election dates from a state's SOS website."""
    config = STATE_SOURCES.get(state_code)
    if not config:
        return {
            "state_code": state_code,
            "state_name": STATE_NAMES.get(state_code, "Unknown"),
            "error": "No configuration found",
            "scraped_at": datetime.now().isoformat(),
        }

    print(f"Scraping {state_code} ({config['state_name']})...")

    result = {
        "state_code": state_code,
        "state_name": config["state_name"],
        "sos_url": config["sos_url"],
        "calendar_url": config["calendar_url"],
        "calendar_type": config["calendar_type"],
        "scraped_at": datetime.now().isoformat(),
        "dates_found": [],
        "primary_date": None,
        "general_date": None,
        "scrape_status": "pending",
    }

    # Skip PDF sources for now (would need different handling)
    if config["calendar_type"] == "pdf":
        result["scrape_status"] = "skipped_pdf"
        result["notes"] = "PDF calendar - using known dates instead"
        # Use known dates
        known = KNOWN_2026_DATES.get(state_code, {})
        result["primary_date"] = known.get("primary")
        result["general_date"] = known.get("general")
        result["source"] = "known_dates"
        return result

    # Fetch and parse HTML
    html = fetch_page(config["calendar_url"])
    if not html:
        result["scrape_status"] = "fetch_failed"
        # Fall back to known dates
        known = KNOWN_2026_DATES.get(state_code, {})
        result["primary_date"] = known.get("primary")
        result["general_date"] = known.get("general")
        result["source"] = "known_dates_fallback"
        return result

    # Parse HTML
    soup = BeautifulSoup(html, "lxml")

    # Get text content
    text = soup.get_text(separator=" ", strip=True)

    # Extract dates
    dates_found = extract_dates_from_text(text)
    result["dates_found"] = dates_found

    # Try to identify primary and general dates
    for date_info in dates_found:
        election_type = classify_election_type(date_info["context"])
        date_val = date_info["date"]

        # Only consider 2026 dates
        if not date_val.startswith("2026"):
            continue

        if election_type == "primary" and not result["primary_date"]:
            result["primary_date"] = date_val
        elif election_type == "general" and not result["general_date"]:
            result["general_date"] = date_val

    # If we couldn't find dates, use known dates
    if not result["primary_date"] or not result["general_date"]:
        known = KNOWN_2026_DATES.get(state_code, {})
        if not result["primary_date"]:
            result["primary_date"] = known.get("primary")
        if not result["general_date"]:
            result["general_date"] = known.get("general")
        result["source"] = "partial_scrape_with_known"
    else:
        result["source"] = "scraped"

    result["scrape_status"] = "completed"
    return result


def scrape_all_pilot_states() -> dict:
    """Scrape all pilot states and return results."""
    results = {}

    print(f"\nScraping {len(PILOT_STATES)} pilot states...\n")

    for state_code in PILOT_STATES:
        results[state_code] = scrape_state(state_code)
        print(f"  Primary: {results[state_code]['primary_date']}")
        print(f"  General: {results[state_code]['general_date']}")
        print()

    return results


def save_results(results: dict, output_path: str = "data/sos_scraped.json"):
    """Save scrape results to JSON file."""
    output_file = Path(__file__).parent / output_path
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"Results saved to {output_file}")


def main():
    """Main entry point."""
    print("=" * 60)
    print("Election Date Scraper - SOS Websites")
    print("=" * 60)

    results = scrape_all_pilot_states()
    save_results(results)

    # Print summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    for state_code, data in results.items():
        status = data.get("source", "unknown")
        print(f"{state_code} ({data['state_name']}): {status}")
        print(f"    Primary: {data['primary_date']}")
        print(f"    General: {data['general_date']}")


if __name__ == "__main__":
    main()
