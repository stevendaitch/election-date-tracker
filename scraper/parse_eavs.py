#!/usr/bin/env python3
"""
Parse 2024 EAVS (Election Administration and Voting Survey) data
and aggregate by state for the Election Date Tracker.

Data source: https://www.eac.gov/research-and-data/studies-and-reports
"""

import csv
import json
import os
from collections import defaultdict

# Special values in EAVS data
SPECIAL_VALUES = {-88, -99, -77, '-88', '-99', '-77', 'DNA (DATA NOT AVAILABLE)', ''}

def safe_int(val):
    """Safely convert to int, handling special EAVS values"""
    if val in SPECIAL_VALUES or val is None:
        return None
    try:
        num = int(float(val))
        # Negative numbers are special codes
        if num < 0:
            return None
        return num
    except (ValueError, TypeError):
        return None

def aggregate_state_data(rows):
    """Aggregate jurisdiction-level data to state totals

    Column mapping per EAC Report:
    - A1a = Total registered voters (active + inactive combined in some states)
    - A1b = Active registered voters
    - A1c = Inactive registered voters
    - A2a = Same-day registrations
    - D2a = Polling places
    - D7a = Total poll workers
    - F1a = Total ballots cast/counted
    """
    states = defaultdict(lambda: {
        'state_code': None,
        'state_name': None,
        'jurisdiction_count': 0,
        'voter_registration': {
            'total_active': 0,  # A1b per EAC
            'total_inactive': 0,  # A1c per EAC
            'same_day_registrations': 0,
        },
        'registration_transactions': {
            'motor_vehicle': 0,
            'online': 0,
            'by_mail': 0,
            'in_person': 0,
        },
        'mail_voting': {
            'ballots_transmitted': 0,
            'ballots_returned': 0,
            'ballots_rejected': 0,
            'ballots_counted': 0,
        },
        'uocava': {
            'ballots_transmitted': 0,
            'ballots_returned': 0,
            'ballots_counted': 0,
        },
        'polling': {
            'precincts': 0,
            'polling_places': 0,
            'poll_workers': 0,
        },
        'provisional': {
            'ballots_submitted': 0,
            'ballots_counted': 0,
            'ballots_rejected': 0,
        },
        'turnout': {
            'total_ballots_cast': 0,
        },
    })

    for row in rows:
        state_code = row.get('State_Abbr', '').strip()
        if not state_code:
            continue

        state = states[state_code]
        state['state_code'] = state_code
        state['state_name'] = row.get('State_Full', '').strip()
        state['jurisdiction_count'] += 1

        # Voter Registration (Section A) - per EAC Report column mapping
        # A1a = Total registered (some states report combined)
        # A1b = Active registered voters
        # A1c = Inactive registered voters
        val = safe_int(row.get('A1b'))  # A1b = Active per EAC
        if val: state['voter_registration']['total_active'] += val

        val = safe_int(row.get('A1c'))  # A1c = Inactive per EAC
        if val: state['voter_registration']['total_inactive'] += val

        # A2a = Same-day registrations
        val = safe_int(row.get('A2a'))
        if val: state['voter_registration']['same_day_registrations'] += val

        # Registration transactions (A3x columns)
        # A3a = At motor vehicle offices
        # A3b = By mail
        # A3c = At public assistance offices
        # A3d = At other agencies
        # A3e = Registration drives
        # A3f = Online
        val = safe_int(row.get('A3a'))
        if val: state['registration_transactions']['motor_vehicle'] += val

        val = safe_int(row.get('A3b'))
        if val: state['registration_transactions']['by_mail'] += val

        val = safe_int(row.get('A3f'))
        if val: state['registration_transactions']['online'] += val

        # Mail Voting (Section C)
        # C1a = Total mail ballots transmitted
        val = safe_int(row.get('C1a'))
        if val: state['mail_voting']['ballots_transmitted'] += val

        # C2a = Mail ballots returned by voters
        val = safe_int(row.get('C2a'))
        if val: state['mail_voting']['ballots_returned'] += val

        # C3a = Mail ballots rejected
        val = safe_int(row.get('C3a'))
        if val: state['mail_voting']['ballots_rejected'] += val

        # C6a = Mail ballots counted
        val = safe_int(row.get('C6a'))
        if val: state['mail_voting']['ballots_counted'] += val

        # UOCAVA (Section B - Military/Overseas)
        # B3a = UOCAVA ballots transmitted
        val = safe_int(row.get('B3a'))
        if val: state['uocava']['ballots_transmitted'] += val

        # B4a = UOCAVA ballots returned
        val = safe_int(row.get('B4a'))
        if val: state['uocava']['ballots_returned'] += val

        # Polling Operations (Section D)
        # D1a = Number of precincts
        val = safe_int(row.get('D1a'))
        if val: state['polling']['precincts'] += val

        # D2a = Number of physical polling places
        val = safe_int(row.get('D2a'))
        if val: state['polling']['polling_places'] += val

        # D7a = Total poll workers (per EAC Report, not D3a)
        val = safe_int(row.get('D7a'))
        if val: state['polling']['poll_workers'] += val

        # Provisional Voting (Section E)
        # E1a = Provisional ballots submitted
        val = safe_int(row.get('E1a'))
        if val: state['provisional']['ballots_submitted'] += val

        # E2a = Provisional ballots counted in full
        val = safe_int(row.get('E2a'))
        if val: state['provisional']['ballots_counted'] += val

        # Turnout (Section F)
        # F1a = Total ballots cast/counted
        val = safe_int(row.get('F1a'))
        if val: state['turnout']['total_ballots_cast'] += val

    return dict(states)

def calculate_derived_stats(states):
    """Calculate derived statistics like percentages"""
    for state_code, state in states.items():
        vr = state['voter_registration']
        vr['total_registered'] = vr['total_active'] + vr['total_inactive']

        mv = state['mail_voting']
        if mv['ballots_transmitted'] > 0:
            mv['return_rate'] = round(mv['ballots_returned'] / mv['ballots_transmitted'] * 100, 1)
        else:
            mv['return_rate'] = None

        if mv['ballots_returned'] > 0:
            mv['rejection_rate'] = round(mv['ballots_rejected'] / mv['ballots_returned'] * 100, 2)
        else:
            mv['rejection_rate'] = None

        prov = state['provisional']
        if prov['ballots_submitted'] > 0:
            prov['count_rate'] = round(prov['ballots_counted'] / prov['ballots_submitted'] * 100, 1)
        else:
            prov['count_rate'] = None

        # Turnout percentage (if we have registered voters)
        if vr['total_registered'] > 0 and state['turnout']['total_ballots_cast'] > 0:
            state['turnout']['turnout_percentage'] = round(
                state['turnout']['total_ballots_cast'] / vr['total_registered'] * 100, 1
            )
        else:
            state['turnout']['turnout_percentage'] = None

    return states

def format_for_output(states):
    """Format the data for JSON output with metadata"""
    output = {
        'metadata': {
            'source': 'U.S. Election Assistance Commission (EAC)',
            'dataset': '2024 Election Administration and Voting Survey (EAVS)',
            'version': '1.0',
            'url': 'https://www.eac.gov/research-and-data/studies-and-reports',
            'notes': 'Data aggregated from jurisdiction-level reports',
        },
        'states': {}
    }

    for state_code, state in sorted(states.items()):
        # Clean up zeros to None for cleaner display
        def clean_zeros(d):
            if isinstance(d, dict):
                return {k: clean_zeros(v) for k, v in d.items()}
            return d if d != 0 else None

        output['states'][state_code] = clean_zeros(state)

    return output

def main():
    # Input CSV path
    csv_path = r"C:\Users\17027\Downloads\2024_EAVS_for_Public_Release_nolabel_V1_csv\2024_EAVS_for_Public_Release_nolabel_V1\2024_EAVS_for_Public_Release_nolabel_V1.csv"

    # Output paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)

    outputs = [
        os.path.join(script_dir, 'data', 'eavs_state_data.json'),
        os.path.join(project_dir, 'website', 'public', 'eavs_state_data.json'),
        os.path.join(project_dir, 'mcp-server', 'data', 'eavs_state_data.json'),
    ]

    print(f"Reading EAVS data from: {csv_path}")

    # Read CSV
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    print(f"Loaded {len(rows)} jurisdiction records")

    # Aggregate by state
    states = aggregate_state_data(rows)
    print(f"Aggregated data for {len(states)} states/territories")

    # Calculate derived statistics
    states = calculate_derived_stats(states)

    # Format for output
    output = format_for_output(states)

    # Write to all output locations
    for output_path in outputs:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2)
        print(f"Wrote: {output_path}")

    # Print sample
    print("\n--- Sample Data (Michigan) ---")
    mi = output['states'].get('MI', {})
    print(json.dumps(mi, indent=2))

    print("\n--- Summary ---")
    for state_code, state in sorted(output['states'].items()):
        vr = state.get('voter_registration', {})
        total = vr.get('total_registered')
        if total:
            print(f"{state_code}: {total:,} registered voters")

if __name__ == '__main__':
    main()
