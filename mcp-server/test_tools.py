"""
Test script for MCP server tools.
Tests the core functions without running the full MCP protocol.
"""

import json
import asyncio
from pathlib import Path

# Add parent to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent))

from server import load_election_data, get_state_by_code, days_until

def test_load_data():
    """Test loading election data."""
    print("Testing load_election_data()...")
    data = load_election_data()
    assert "states" in data
    assert "metadata" in data
    print(f"  Loaded {len(data['states'])} states")
    print("  OK")

def test_get_state():
    """Test getting a state by code."""
    print("\nTesting get_state_by_code()...")
    data = load_election_data()

    # Test valid state
    mi = get_state_by_code(data, "MI")
    assert mi is not None
    assert mi["state_name"] == "Michigan"
    print(f"  MI: {mi['state_name']} - Primary: {mi['next_primary']['date']}")

    # Test lowercase
    ca = get_state_by_code(data, "ca")
    assert ca is not None
    assert ca["state_name"] == "California"
    print(f"  ca: {ca['state_name']} - Primary: {ca['next_primary']['date']}")

    # Test invalid state
    invalid = get_state_by_code(data, "XX")
    assert invalid is None
    print("  XX: None (as expected)")

    print("  OK")

def test_days_until():
    """Test days until calculation."""
    print("\nTesting days_until()...")
    days = days_until("2026-11-03")
    print(f"  Days until Nov 3, 2026: {days}")
    assert days > 0
    print("  OK")

def test_tool_outputs():
    """Test the expected tool outputs."""
    print("\nTesting tool output formats...")
    data = load_election_data()

    # Simulate get_next_election for MI
    state = get_state_by_code(data, "MI")
    result = {
        "state": state["state_code"],
        "state_name": state["state_name"],
        "next_primary": state["next_primary"]["date"],
        "primary_days_until": days_until(state["next_primary"]["date"]),
        "next_general": state["next_general"]["date"],
        "general_days_until": days_until(state["next_general"]["date"]),
        "confidence_level": state["next_primary"]["confidence"],
    }
    print(f"  get_next_election('MI'):")
    print(f"    {json.dumps(result, indent=4)}")

    # Simulate get_all_upcoming_elections
    elections = []
    for s in data["states"]:
        elections.append({
            "state": s["state_code"],
            "date": s["next_primary"]["date"],
            "type": "primary",
        })
        elections.append({
            "state": s["state_code"],
            "date": s["next_general"]["date"],
            "type": "general",
        })
    elections.sort(key=lambda x: x["date"])
    print(f"\n  get_all_upcoming_elections():")
    print(f"    Total elections: {len(elections)}")
    print(f"    First 5: {elections[:5]}")

    print("  OK")

def main():
    print("=" * 60)
    print("MCP Server Tool Tests")
    print("=" * 60)

    test_load_data()
    test_get_state()
    test_days_until()
    test_tool_outputs()

    print("\n" + "=" * 60)
    print("All tests passed!")
    print("=" * 60)

if __name__ == "__main__":
    main()
