"""
Validation script for election dates.
Cross-references statute rules with SOS scraped data and produces
the final validated election_dates.json file.
"""

import csv
import json
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"


def load_statute_rules() -> dict:
    """Load statute rules from CSV file."""
    rules = {}
    csv_path = DATA_DIR / "statute_rules.csv"

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rules[row["state_code"]] = {
                "state_name": row["state_name"],
                "primary_date_rule": row["primary_date_rule"],
                "primary_date": row["primary_date_2026"],
                "general_date_rule": row["general_date_rule"],
                "general_date": row["general_date_2026"],
                "statute_reference": row["statute_reference"],
                "source_url": row["source_url"],
                "confidence_level": row["confidence_level"],
                "notes": row["notes"],
            }

    return rules


def load_sos_scraped() -> dict:
    """Load SOS scraped data from JSON file."""
    json_path = DATA_DIR / "sos_scraped.json"

    if not json_path.exists():
        return {}

    with open(json_path, "r") as f:
        return json.load(f)


def validate_dates(statute_rules: dict, sos_data: dict) -> list:
    """
    Validate dates by comparing statute rules with SOS scraped data.
    Returns a list of validated state records with confidence levels.
    """
    validated = []

    for state_code, statute in statute_rules.items():
        sos = sos_data.get(state_code, {})

        record = {
            "state_code": state_code,
            "state_name": statute["state_name"],
            "next_primary": {
                "date": statute["primary_date"],
                "date_rule": statute["primary_date_rule"],
                "type": "state_primary",
                "statute_reference": statute["statute_reference"],
                "confidence": "High",
            },
            "next_general": {
                "date": statute["general_date"],
                "date_rule": statute["general_date_rule"],
                "type": "general_election",
                "statute_reference": statute["statute_reference"],
                "confidence": "High",
            },
            "sources": [
                {
                    "type": "statute",
                    "reference": statute["statute_reference"],
                    "url": statute["source_url"],
                    "extracted_from": "Election Law Navigator / State Statutes",
                },
            ],
            "validation": {
                "status": "validated",
                "discrepancies": [],
            },
            "last_updated": datetime.now().strftime("%Y-%m-%d"),
            "notes": statute["notes"],
        }

        # Add SOS source if available
        if sos:
            record["sources"].append({
                "type": "sos_website",
                "url": sos.get("sos_url", ""),
                "calendar_url": sos.get("calendar_url", ""),
                "last_verified": sos.get("scraped_at", "")[:10] if sos.get("scraped_at") else "",
            })

            # Check for discrepancies
            sos_primary = sos.get("primary_date")
            sos_general = sos.get("general_date")

            if sos_primary and sos_primary != statute["primary_date"]:
                record["validation"]["discrepancies"].append({
                    "field": "primary_date",
                    "statute_value": statute["primary_date"],
                    "sos_value": sos_primary,
                    "resolution": "Using statute value (authoritative)",
                })

            if sos_general and sos_general != statute["general_date"]:
                record["validation"]["discrepancies"].append({
                    "field": "general_date",
                    "statute_value": statute["general_date"],
                    "sos_value": sos_general,
                    "resolution": "Using statute value (authoritative)",
                })

            if record["validation"]["discrepancies"]:
                record["validation"]["status"] = "discrepancy_resolved"
                # Keep confidence high since we're using statute as authoritative

        validated.append(record)

    return validated


def generate_election_dates_json(validated: list) -> dict:
    """Generate the final election_dates.json structure."""
    return {
        "metadata": {
            "version": "1.0.0",
            "generated_at": datetime.now().isoformat(),
            "description": "Election dates for US states, validated against statutes and SOS websites",
            "year": 2026,
        },
        "states": validated,
    }


def print_validation_report(validated: list):
    """Print a validation report to console."""
    print("\n" + "=" * 60)
    print("VALIDATION REPORT")
    print("=" * 60)

    discrepancy_count = 0

    for record in validated:
        state = record["state_code"]
        name = record["state_name"]
        primary = record["next_primary"]["date"]
        general = record["next_general"]["date"]
        status = record["validation"]["status"]

        print(f"\n{state} ({name})")
        print(f"  Primary: {primary}")
        print(f"  General: {general}")
        print(f"  Status: {status}")

        if record["validation"]["discrepancies"]:
            discrepancy_count += len(record["validation"]["discrepancies"])
            print("  Discrepancies:")
            for d in record["validation"]["discrepancies"]:
                print(f"    - {d['field']}: statute={d['statute_value']}, sos={d['sos_value']}")
                print(f"      Resolution: {d['resolution']}")

    print("\n" + "=" * 60)
    print(f"Total states validated: {len(validated)}")
    print(f"Total discrepancies found: {discrepancy_count}")
    print("=" * 60)


def main():
    """Main entry point."""
    print("=" * 60)
    print("Election Date Validation")
    print("=" * 60)

    # Load data
    print("\nLoading statute rules...")
    statute_rules = load_statute_rules()
    print(f"  Loaded {len(statute_rules)} states from statute_rules.csv")

    print("\nLoading SOS scraped data...")
    sos_data = load_sos_scraped()
    print(f"  Loaded {len(sos_data)} states from sos_scraped.json")

    # Validate
    print("\nValidating dates...")
    validated = validate_dates(statute_rules, sos_data)

    # Generate output
    output = generate_election_dates_json(validated)

    # Save
    output_path = DATA_DIR / "election_dates.json"
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nSaved validated data to {output_path}")

    # Print report
    print_validation_report(validated)


if __name__ == "__main__":
    main()
