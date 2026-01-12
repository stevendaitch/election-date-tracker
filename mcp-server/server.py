"""
MCP Server for Election Date Queries.
Exposes tools for querying election dates across US states.
"""

import json
from datetime import datetime, date
from pathlib import Path

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Load election data
DATA_PATH = Path(__file__).parent / "data" / "election_dates.json"
SPECIAL_DATA_PATH = Path(__file__).parent / "data" / "special_elections.json"
EAVS_DATA_PATH = Path(__file__).parent / "data" / "eavs_state_data.json"

def load_election_data() -> dict:
    """Load election dates from JSON file."""
    with open(DATA_PATH, "r") as f:
        return json.load(f)

def load_special_elections() -> dict:
    """Load special elections from JSON file."""
    if not SPECIAL_DATA_PATH.exists():
        return {"special_elections": [], "metadata": {}, "by_state": {}}
    with open(SPECIAL_DATA_PATH, "r") as f:
        return json.load(f)

def load_eavs_data() -> dict:
    """Load EAVS (Election Administration and Voting Survey) data."""
    if not EAVS_DATA_PATH.exists():
        return {"metadata": {}, "states": {}}
    with open(EAVS_DATA_PATH, "r") as f:
        return json.load(f)

def get_state_by_code(data: dict, state_code: str) -> dict | None:
    """Find a state by its code."""
    state_code = state_code.upper()
    for state in data["states"]:
        if state["state_code"] == state_code:
            return state
    return None

def days_until(date_str: str) -> int:
    """Calculate days until a given date."""
    target = datetime.strptime(date_str, "%Y-%m-%d").date()
    today = date.today()
    return (target - today).days

# Initialize MCP server
server = Server("election-dates")

@server.list_tools()
async def list_tools():
    """List available tools."""
    return [
        Tool(
            name="get_next_election",
            description="Get the next primary and general election dates for a specific state",
            inputSchema={
                "type": "object",
                "properties": {
                    "state_code": {
                        "type": "string",
                        "description": "Two-letter state code (e.g., 'MI', 'CA', 'TX')"
                    }
                },
                "required": ["state_code"]
            }
        ),
        Tool(
            name="get_elections_by_date_range",
            description="Get all elections within a date range",
            inputSchema={
                "type": "object",
                "properties": {
                    "start_date": {
                        "type": "string",
                        "description": "Start date in YYYY-MM-DD format"
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End date in YYYY-MM-DD format"
                    }
                },
                "required": ["start_date", "end_date"]
            }
        ),
        Tool(
            name="get_all_upcoming_elections",
            description="Get all upcoming elections across all states, sorted by date",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="get_election_sources",
            description="Get detailed source citations for a state's election dates",
            inputSchema={
                "type": "object",
                "properties": {
                    "state_code": {
                        "type": "string",
                        "description": "Two-letter state code (e.g., 'MI', 'CA', 'TX')"
                    }
                },
                "required": ["state_code"]
            }
        ),
        # Special Elections Tools
        Tool(
            name="get_special_elections_by_state",
            description="Get all special elections for a specific state",
            inputSchema={
                "type": "object",
                "properties": {
                    "state_code": {
                        "type": "string",
                        "description": "Two-letter state code (e.g., 'TX', 'GA', 'OH')"
                    }
                },
                "required": ["state_code"]
            }
        ),
        Tool(
            name="get_upcoming_special_elections",
            description="Get all upcoming special elections within a specified number of days",
            inputSchema={
                "type": "object",
                "properties": {
                    "days_ahead": {
                        "type": "integer",
                        "description": "Number of days to look ahead (default: 90)"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="get_election_with_specials",
            description="Get regular elections AND special elections combined for a specific state",
            inputSchema={
                "type": "object",
                "properties": {
                    "state_code": {
                        "type": "string",
                        "description": "Two-letter state code (e.g., 'MI', 'CA', 'TX')"
                    }
                },
                "required": ["state_code"]
            }
        ),
        Tool(
            name="get_all_elections_by_date_range",
            description="Get all regular and special elections within a date range",
            inputSchema={
                "type": "object",
                "properties": {
                    "start_date": {
                        "type": "string",
                        "description": "Start date in YYYY-MM-DD format"
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End date in YYYY-MM-DD format"
                    },
                    "include_specials": {
                        "type": "boolean",
                        "description": "Include special elections (default: true)"
                    }
                },
                "required": ["start_date", "end_date"]
            }
        ),
        Tool(
            name="get_special_elections_metadata",
            description="Get metadata about the special elections dataset",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        # EAVS (Election Administration and Voting Survey) Tools
        Tool(
            name="get_eavs_data_for_state",
            description="Get 2024 EAVS election administration statistics for a specific state (registered voters, turnout, mail voting, polling places, poll workers, provisional ballots)",
            inputSchema={
                "type": "object",
                "properties": {
                    "state_code": {
                        "type": "string",
                        "description": "Two-letter state code (e.g., 'MI', 'CA', 'TX')"
                    }
                },
                "required": ["state_code"]
            }
        ),
        Tool(
            name="get_state_eavs_comparison",
            description="Compare EAVS election administration statistics between multiple states",
            inputSchema={
                "type": "object",
                "properties": {
                    "state_codes": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of two-letter state codes to compare (e.g., ['MI', 'CA', 'TX'])"
                    }
                },
                "required": ["state_codes"]
            }
        ),
        Tool(
            name="get_national_eavs_summary",
            description="Get national summary of 2024 EAVS data across all states (total registered voters, ballots cast, mail voting statistics)",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    """Handle tool calls."""
    data = load_election_data()

    if name == "get_next_election":
        state_code = arguments.get("state_code", "").upper()
        state = get_state_by_code(data, state_code)

        if not state:
            return [TextContent(
                type="text",
                text=json.dumps({"error": f"State '{state_code}' not found"}, indent=2)
            )]

        result = {
            "state": state["state_code"],
            "state_name": state["state_name"],
            "next_primary": state["next_primary"]["date"],
            "primary_days_until": days_until(state["next_primary"]["date"]),
            "next_general": state["next_general"]["date"],
            "general_days_until": days_until(state["next_general"]["date"]),
            "confidence_level": state["next_primary"]["confidence"],
            "sources": {
                "statute": state["sources"][0]["reference"] if state["sources"] else None,
                "statute_url": state["sources"][0]["url"] if state["sources"] else None,
                "sos_url": state["sources"][1]["url"] if len(state["sources"]) > 1 else None,
                "last_verified": state["last_updated"]
            }
        }

        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]

    elif name == "get_elections_by_date_range":
        start_date = arguments.get("start_date")
        end_date = arguments.get("end_date")

        try:
            start = datetime.strptime(start_date, "%Y-%m-%d").date()
            end = datetime.strptime(end_date, "%Y-%m-%d").date()
        except ValueError as e:
            return [TextContent(
                type="text",
                text=json.dumps({"error": f"Invalid date format: {e}"}, indent=2)
            )]

        elections = []
        for state in data["states"]:
            primary_date = datetime.strptime(state["next_primary"]["date"], "%Y-%m-%d").date()
            general_date = datetime.strptime(state["next_general"]["date"], "%Y-%m-%d").date()

            if start <= primary_date <= end:
                elections.append({
                    "state": state["state_code"],
                    "state_name": state["state_name"],
                    "date": state["next_primary"]["date"],
                    "type": "primary",
                    "days_until": days_until(state["next_primary"]["date"])
                })

            if start <= general_date <= end:
                elections.append({
                    "state": state["state_code"],
                    "state_name": state["state_name"],
                    "date": state["next_general"]["date"],
                    "type": "general",
                    "days_until": days_until(state["next_general"]["date"])
                })

        # Sort by date
        elections.sort(key=lambda x: x["date"])

        return [TextContent(
            type="text",
            text=json.dumps({
                "date_range": {"start": start_date, "end": end_date},
                "elections_count": len(elections),
                "elections": elections
            }, indent=2)
        )]

    elif name == "get_all_upcoming_elections":
        elections = []
        for state in data["states"]:
            elections.append({
                "state": state["state_code"],
                "state_name": state["state_name"],
                "date": state["next_primary"]["date"],
                "type": "primary",
                "days_until": days_until(state["next_primary"]["date"])
            })
            elections.append({
                "state": state["state_code"],
                "state_name": state["state_name"],
                "date": state["next_general"]["date"],
                "type": "general",
                "days_until": days_until(state["next_general"]["date"])
            })

        # Sort by date
        elections.sort(key=lambda x: x["date"])

        return [TextContent(
            type="text",
            text=json.dumps({
                "total_elections": len(elections),
                "data_updated": data["metadata"]["generated_at"][:10],
                "elections": elections
            }, indent=2)
        )]

    elif name == "get_election_sources":
        state_code = arguments.get("state_code", "").upper()
        state = get_state_by_code(data, state_code)

        if not state:
            return [TextContent(
                type="text",
                text=json.dumps({"error": f"State '{state_code}' not found"}, indent=2)
            )]

        result = {
            "state": state["state_code"],
            "state_name": state["state_name"],
            "primary_election": {
                "date": state["next_primary"]["date"],
                "date_rule": state["next_primary"]["date_rule"],
                "statute_reference": state["next_primary"]["statute_reference"],
                "confidence": state["next_primary"]["confidence"]
            },
            "general_election": {
                "date": state["next_general"]["date"],
                "date_rule": state["next_general"]["date_rule"],
                "statute_reference": state["next_general"]["statute_reference"],
                "confidence": state["next_general"]["confidence"]
            },
            "sources": state["sources"],
            "validation": state["validation"],
            "last_updated": state["last_updated"],
            "notes": state["notes"]
        }

        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]

    # Special Elections Handlers
    elif name == "get_special_elections_by_state":
        state_code = arguments.get("state_code", "").upper()
        special_data = load_special_elections()

        state_specials = [
            e for e in special_data.get("special_elections", [])
            if e["state_code"] == state_code
        ]

        return [TextContent(
            type="text",
            text=json.dumps({
                "state_code": state_code,
                "special_elections_count": len(state_specials),
                "special_elections": state_specials
            }, indent=2)
        )]

    elif name == "get_upcoming_special_elections":
        days_ahead = arguments.get("days_ahead", 90)
        special_data = load_special_elections()
        today = date.today()

        upcoming = []
        for election in special_data.get("special_elections", []):
            next_date = election.get("next_date")
            if next_date:
                election_date = datetime.strptime(next_date, "%Y-%m-%d").date()
                days_diff = (election_date - today).days
                if 0 <= days_diff <= days_ahead:
                    upcoming.append({
                        **election,
                        "days_until": days_diff
                    })

        # Sort by date
        upcoming.sort(key=lambda x: x.get("next_date", ""))

        return [TextContent(
            type="text",
            text=json.dumps({
                "days_ahead": days_ahead,
                "count": len(upcoming),
                "special_elections": upcoming
            }, indent=2)
        )]

    elif name == "get_election_with_specials":
        state_code = arguments.get("state_code", "").upper()
        state = get_state_by_code(data, state_code)
        special_data = load_special_elections()

        if not state:
            return [TextContent(
                type="text",
                text=json.dumps({"error": f"State '{state_code}' not found"}, indent=2)
            )]

        state_specials = [
            e for e in special_data.get("special_elections", [])
            if e["state_code"] == state_code
        ]

        result = {
            "state": state["state_code"],
            "state_name": state["state_name"],
            "regular_elections": {
                "next_primary": {
                    "date": state["next_primary"]["date"],
                    "days_until": days_until(state["next_primary"]["date"])
                },
                "next_general": {
                    "date": state["next_general"]["date"],
                    "days_until": days_until(state["next_general"]["date"])
                }
            },
            "special_elections_count": len(state_specials),
            "special_elections": state_specials
        }

        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]

    elif name == "get_all_elections_by_date_range":
        start_date = arguments.get("start_date")
        end_date = arguments.get("end_date")
        include_specials = arguments.get("include_specials", True)

        try:
            start = datetime.strptime(start_date, "%Y-%m-%d").date()
            end = datetime.strptime(end_date, "%Y-%m-%d").date()
        except ValueError as e:
            return [TextContent(
                type="text",
                text=json.dumps({"error": f"Invalid date format: {e}"}, indent=2)
            )]

        elections = []

        # Regular elections
        for state in data["states"]:
            primary_date = datetime.strptime(state["next_primary"]["date"], "%Y-%m-%d").date()
            general_date = datetime.strptime(state["next_general"]["date"], "%Y-%m-%d").date()

            if start <= primary_date <= end:
                elections.append({
                    "state": state["state_code"],
                    "state_name": state["state_name"],
                    "date": state["next_primary"]["date"],
                    "type": "primary",
                    "category": "regular",
                    "days_until": days_until(state["next_primary"]["date"])
                })

            if start <= general_date <= end:
                elections.append({
                    "state": state["state_code"],
                    "state_name": state["state_name"],
                    "date": state["next_general"]["date"],
                    "type": "general",
                    "category": "regular",
                    "days_until": days_until(state["next_general"]["date"])
                })

        # Special elections
        if include_specials:
            special_data = load_special_elections()
            for election in special_data.get("special_elections", []):
                next_date = election.get("next_date")
                if next_date:
                    election_date = datetime.strptime(next_date, "%Y-%m-%d").date()
                    if start <= election_date <= end:
                        elections.append({
                            "state": election["state_code"],
                            "state_name": election["state_name"],
                            "date": next_date,
                            "type": election["next_date_type"],
                            "category": "special",
                            "office": election["office"],
                            "district": election["district"],
                            "days_until": (election_date - date.today()).days
                        })

        # Sort by date
        elections.sort(key=lambda x: x["date"])

        return [TextContent(
            type="text",
            text=json.dumps({
                "date_range": {"start": start_date, "end": end_date},
                "include_specials": include_specials,
                "elections_count": len(elections),
                "elections": elections
            }, indent=2)
        )]

    elif name == "get_special_elections_metadata":
        special_data = load_special_elections()
        metadata = special_data.get("metadata", {})

        return [TextContent(
            type="text",
            text=json.dumps({
                "metadata": metadata,
                "states_with_specials": list(special_data.get("by_state", {}).keys())
            }, indent=2)
        )]

    # EAVS Tool Handlers
    elif name == "get_eavs_data_for_state":
        state_code = arguments.get("state_code", "").upper()
        eavs_data = load_eavs_data()
        state_eavs = eavs_data.get("states", {}).get(state_code)

        if not state_eavs:
            return [TextContent(
                type="text",
                text=json.dumps({"error": f"EAVS data not available for state '{state_code}'"}, indent=2)
            )]

        return [TextContent(
            type="text",
            text=json.dumps({
                "state_code": state_code,
                "state_name": state_eavs.get("state_name"),
                "jurisdiction_count": state_eavs.get("jurisdiction_count"),
                "voter_registration": state_eavs.get("voter_registration"),
                "turnout": state_eavs.get("turnout"),
                "mail_voting": state_eavs.get("mail_voting"),
                "polling": state_eavs.get("polling"),
                "provisional": state_eavs.get("provisional"),
                "source": eavs_data.get("metadata", {})
            }, indent=2)
        )]

    elif name == "get_state_eavs_comparison":
        state_codes = [s.upper() for s in arguments.get("state_codes", [])]
        eavs_data = load_eavs_data()
        states_data = eavs_data.get("states", {})

        comparison = []
        for code in state_codes:
            state_eavs = states_data.get(code)
            if state_eavs:
                comparison.append({
                    "state_code": code,
                    "state_name": state_eavs.get("state_name"),
                    "registered_voters": state_eavs.get("voter_registration", {}).get("total_registered"),
                    "ballots_cast": state_eavs.get("turnout", {}).get("total_ballots_cast"),
                    "turnout_percentage": state_eavs.get("turnout", {}).get("turnout_percentage"),
                    "polling_places": state_eavs.get("polling", {}).get("polling_places"),
                    "poll_workers": state_eavs.get("polling", {}).get("poll_workers"),
                    "mail_ballots_sent": state_eavs.get("mail_voting", {}).get("ballots_transmitted"),
                    "mail_return_rate": state_eavs.get("mail_voting", {}).get("return_rate"),
                })

        return [TextContent(
            type="text",
            text=json.dumps({
                "states_compared": len(comparison),
                "comparison": comparison
            }, indent=2)
        )]

    elif name == "get_national_eavs_summary":
        eavs_data = load_eavs_data()
        states_data = eavs_data.get("states", {})

        totals = {
            "total_registered": 0,
            "total_active": 0,
            "total_inactive": 0,
            "total_ballots_cast": 0,
            "total_mail_sent": 0,
            "total_mail_returned": 0,
            "total_polling_places": 0,
            "total_poll_workers": 0,
            "states_reporting": 0,
        }

        for code, state_eavs in states_data.items():
            totals["states_reporting"] += 1
            vr = state_eavs.get("voter_registration", {})
            totals["total_registered"] += vr.get("total_registered") or 0
            totals["total_active"] += vr.get("total_active") or 0
            totals["total_inactive"] += vr.get("total_inactive") or 0

            turnout = state_eavs.get("turnout", {})
            totals["total_ballots_cast"] += turnout.get("total_ballots_cast") or 0

            mail = state_eavs.get("mail_voting", {})
            totals["total_mail_sent"] += mail.get("ballots_transmitted") or 0
            totals["total_mail_returned"] += mail.get("ballots_returned") or 0

            polling = state_eavs.get("polling", {})
            totals["total_polling_places"] += polling.get("polling_places") or 0
            totals["total_poll_workers"] += polling.get("poll_workers") or 0

        # Calculate national turnout percentage
        if totals["total_registered"] > 0:
            totals["national_turnout_percentage"] = round(
                totals["total_ballots_cast"] / totals["total_registered"] * 100, 1
            )

        return [TextContent(
            type="text",
            text=json.dumps({
                "national_summary": totals,
                "source": eavs_data.get("metadata", {})
            }, indent=2)
        )]

    else:
        return [TextContent(
            type="text",
            text=json.dumps({"error": f"Unknown tool: {name}"}, indent=2)
        )]

async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
