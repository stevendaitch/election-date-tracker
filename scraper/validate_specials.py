#!/usr/bin/env python3
"""
Validate special elections data and generate JSON output.
Reads from special_elections.csv and outputs special_elections.json.
"""

import csv
import json
import shutil
from datetime import datetime, date
from pathlib import Path

# Paths
SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR / "data"
CSV_PATH = DATA_DIR / "special_elections.csv"
JSON_PATH = DATA_DIR / "special_elections.json"

# Output destinations
MCP_DATA_DIR = SCRIPT_DIR.parent / "mcp-server" / "data"
WEBSITE_PUBLIC_DIR = SCRIPT_DIR.parent / "website" / "public"

# Valid values
VALID_LEVELS = {"federal", "state_legislative", "statewide"}
VALID_STATUSES = {"announced", "scheduled", "runoff_pending", "completed", "cancelled"}
VALID_CONFIDENCE = {"High", "Medium", "Low"}

# State name lookup
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
    "VA": "Virginia", "WA": "Washington", "WV": "West Virginia", "WI": "Wisconsin", "WY": "Wyoming",
    "DC": "District of Columbia"
}


def parse_date(date_str):
    """Parse a date string in YYYY-MM-DD format."""
    if not date_str or date_str.strip() == "":
        return None
    try:
        return datetime.strptime(date_str.strip(), "%Y-%m-%d").date()
    except ValueError:
        return None


def validate_row(row, row_num):
    """Validate a single CSV row. Returns (is_valid, errors, warnings)."""
    errors = []
    warnings = []

    # Required fields
    required = ["id", "state_code", "office", "level", "status", "confidence"]
    for field in required:
        if not row.get(field, "").strip():
            errors.append(f"Missing required field: {field}")

    # Validate state code
    state_code = row.get("state_code", "").strip()
    if state_code and state_code not in STATE_NAMES:
        errors.append(f"Invalid state_code: {state_code}")

    # Validate level
    level = row.get("level", "").strip()
    if level and level not in VALID_LEVELS:
        errors.append(f"Invalid level: {level}. Must be one of {VALID_LEVELS}")

    # Validate status
    status = row.get("status", "").strip()
    if status and status not in VALID_STATUSES:
        errors.append(f"Invalid status: {status}. Must be one of {VALID_STATUSES}")

    # Validate confidence
    confidence = row.get("confidence", "").strip()
    if confidence and confidence not in VALID_CONFIDENCE:
        errors.append(f"Invalid confidence: {confidence}. Must be one of {VALID_CONFIDENCE}")

    # Validate dates
    for date_field in ["vacancy_date", "primary_date", "general_date", "runoff_date"]:
        date_str = row.get(date_field, "").strip()
        if date_str:
            parsed = parse_date(date_str)
            if parsed is None:
                errors.append(f"Invalid date format for {date_field}: {date_str}. Use YYYY-MM-DD")

    # Must have at least one election date
    has_date = any(row.get(f, "").strip() for f in ["primary_date", "general_date", "runoff_date"])
    if not has_date and status not in ["announced", "cancelled"]:
        warnings.append("No election date specified (primary, general, or runoff)")

    return len(errors) == 0, errors, warnings


def load_and_validate_csv():
    """Load CSV and validate all rows."""
    special_elections = []
    all_errors = []
    all_warnings = []

    with open(CSV_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is row 1)
            # Skip empty rows
            if not row.get("id", "").strip():
                continue

            is_valid, errors, warnings = validate_row(row, row_num)

            if errors:
                all_errors.append((row_num, row.get("id", "unknown"), errors))
            if warnings:
                all_warnings.append((row_num, row.get("id", "unknown"), warnings))

            if is_valid:
                # Build the election object
                state_code = row["state_code"].strip()
                election = {
                    "id": row["id"].strip(),
                    "state_code": state_code,
                    "state_name": row.get("state_name", "").strip() or STATE_NAMES.get(state_code, ""),
                    "office": row["office"].strip(),
                    "district": row.get("district", "").strip() or None,
                    "level": row["level"].strip(),
                    "reason": row.get("reason", "").strip() or None,
                    "dates": {
                        "vacancy": row.get("vacancy_date", "").strip() or None,
                        "primary": row.get("primary_date", "").strip() or None,
                        "general": row.get("general_date", "").strip() or None,
                        "runoff": row.get("runoff_date", "").strip() or None,
                    },
                    "status": row["status"].strip(),
                    "confidence": row["confidence"].strip(),
                    "source_url": row.get("source_url", "").strip() or None,
                    "notes": row.get("notes", "").strip() or None,
                }
                special_elections.append(election)

    return special_elections, all_errors, all_warnings


def get_next_date(election):
    """Get the next upcoming date for an election."""
    today = date.today()
    dates = []

    for date_type in ["primary", "general", "runoff"]:
        date_str = election["dates"].get(date_type)
        if date_str:
            parsed = parse_date(date_str)
            if parsed and parsed >= today:
                dates.append((parsed, date_type))

    if dates:
        dates.sort(key=lambda x: x[0])
        return dates[0][0].isoformat(), dates[0][1]
    return None, None


def generate_json(special_elections):
    """Generate the JSON output structure."""
    # Add next_date info to each election
    for election in special_elections:
        next_date, next_type = get_next_date(election)
        election["next_date"] = next_date
        election["next_date_type"] = next_type

    # Sort by next date (elections without dates go to end)
    def sort_key(e):
        if e["next_date"]:
            return (0, e["next_date"])
        return (1, "")

    special_elections.sort(key=sort_key)

    # Build by-state lookup
    by_state = {}
    for election in special_elections:
        state = election["state_code"]
        if state not in by_state:
            by_state[state] = []
        by_state[state].append(election["id"])

    # Count by level
    level_counts = {}
    for election in special_elections:
        level = election["level"]
        level_counts[level] = level_counts.get(level, 0) + 1

    output = {
        "metadata": {
            "last_updated": date.today().isoformat(),
            "sources": ["Ballotpedia", "State SOS Websites"],
            "election_count": len(special_elections),
            "by_level": level_counts,
            "states_with_specials": list(by_state.keys()),
        },
        "special_elections": special_elections,
        "by_state": by_state,
    }

    return output


def main():
    print("=" * 60)
    print("Special Elections Validation")
    print("=" * 60)

    if not CSV_PATH.exists():
        print(f"ERROR: CSV file not found: {CSV_PATH}")
        return 1

    print(f"\nReading: {CSV_PATH}")
    special_elections, errors, warnings = load_and_validate_csv()

    # Report errors
    if errors:
        print(f"\n{len(errors)} ERRORS found:")
        for row_num, election_id, err_list in errors:
            print(f"  Row {row_num} ({election_id}):")
            for err in err_list:
                print(f"    - {err}")

    # Report warnings
    if warnings:
        print(f"\n{len(warnings)} WARNINGS:")
        for row_num, election_id, warn_list in warnings:
            print(f"  Row {row_num} ({election_id}):")
            for warn in warn_list:
                print(f"    - {warn}")

    if errors:
        print("\nValidation FAILED. Fix errors before generating JSON.")
        return 1

    print(f"\nValidation PASSED: {len(special_elections)} special elections loaded")

    # Generate JSON
    output = generate_json(special_elections)

    # Write to data directory
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)
    print(f"\nGenerated: {JSON_PATH}")

    # Copy to MCP server
    MCP_DATA_DIR.mkdir(parents=True, exist_ok=True)
    mcp_dest = MCP_DATA_DIR / "special_elections.json"
    shutil.copy(JSON_PATH, mcp_dest)
    print(f"Copied to: {mcp_dest}")

    # Copy to website public
    WEBSITE_PUBLIC_DIR.mkdir(parents=True, exist_ok=True)
    web_dest = WEBSITE_PUBLIC_DIR / "special_elections.json"
    shutil.copy(JSON_PATH, web_dest)
    print(f"Copied to: {web_dest}")

    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"Total special elections: {output['metadata']['election_count']}")
    print(f"By level:")
    for level, count in output['metadata']['by_level'].items():
        print(f"  - {level}: {count}")
    print(f"States with specials: {', '.join(output['metadata']['states_with_specials'])}")

    return 0


if __name__ == "__main__":
    exit(main())
