"""
State SOS website configuration for election date scraping.
Each state has different page structures, so we define custom extraction logic.
"""

# 2026 Election dates (verified from NCSL and official sources)
KNOWN_2026_DATES = {
    "AL": {"primary": "2026-05-19", "general": "2026-11-03"},
    "AK": {"primary": "2026-08-18", "general": "2026-11-03"},
    "AZ": {"primary": "2026-08-04", "general": "2026-11-03"},
    "AR": {"primary": "2026-03-03", "general": "2026-11-03"},
    "CA": {"primary": "2026-06-02", "general": "2026-11-03"},
    "CO": {"primary": "2026-06-30", "general": "2026-11-03"},
    "CT": {"primary": "2026-08-11", "general": "2026-11-03"},
    "DE": {"primary": "2026-09-15", "general": "2026-11-03"},
    "FL": {"primary": "2026-08-18", "general": "2026-11-03"},
    "GA": {"primary": "2026-05-19", "general": "2026-11-03"},
    "HI": {"primary": "2026-08-08", "general": "2026-11-03"},
    "ID": {"primary": "2026-05-19", "general": "2026-11-03"},
    "IL": {"primary": "2026-03-17", "general": "2026-11-03"},
    "IN": {"primary": "2026-05-05", "general": "2026-11-03"},
    "IA": {"primary": "2026-06-02", "general": "2026-11-03"},
    "KS": {"primary": "2026-08-04", "general": "2026-11-03"},
    "KY": {"primary": "2026-05-19", "general": "2026-11-03"},
    "LA": {"primary": "2026-05-16", "general": "2026-11-03"},
    "ME": {"primary": "2026-06-09", "general": "2026-11-03"},
    "MD": {"primary": "2026-06-23", "general": "2026-11-03"},
    "MA": {"primary": "2026-09-01", "general": "2026-11-03"},
    "MI": {"primary": "2026-08-04", "general": "2026-11-03"},
    "MN": {"primary": "2026-08-11", "general": "2026-11-03"},
    "MS": {"primary": "2026-03-10", "general": "2026-11-03"},
    "MO": {"primary": "2026-08-04", "general": "2026-11-03"},
    "MT": {"primary": "2026-06-02", "general": "2026-11-03"},
    "NE": {"primary": "2026-05-12", "general": "2026-11-03"},
    "NV": {"primary": "2026-06-09", "general": "2026-11-03"},
    "NH": {"primary": "2026-09-08", "general": "2026-11-03"},
    "NJ": {"primary": "2026-06-02", "general": "2026-11-03"},
    "NM": {"primary": "2026-06-02", "general": "2026-11-03"},
    "NY": {"primary": "2026-06-23", "general": "2026-11-03"},
    "NC": {"primary": "2026-03-03", "general": "2026-11-03"},
    "ND": {"primary": "2026-06-09", "general": "2026-11-03"},
    "OH": {"primary": "2026-05-05", "general": "2026-11-03"},
    "OK": {"primary": "2026-06-16", "general": "2026-11-03"},
    "OR": {"primary": "2026-05-19", "general": "2026-11-03"},
    "PA": {"primary": "2026-05-19", "general": "2026-11-03"},
    "RI": {"primary": "2026-09-08", "general": "2026-11-03"},
    "SC": {"primary": "2026-06-09", "general": "2026-11-03"},
    "SD": {"primary": "2026-06-02", "general": "2026-11-03"},
    "TN": {"primary": "2026-08-06", "general": "2026-11-03"},
    "TX": {"primary": "2026-03-03", "general": "2026-11-03"},
    "UT": {"primary": "2026-06-23", "general": "2026-11-03"},
    "VT": {"primary": "2026-08-11", "general": "2026-11-03"},
    "VA": {"primary": "2026-06-16", "general": "2026-11-03"},
    "WA": {"primary": "2026-08-04", "general": "2026-11-03"},
    "WV": {"primary": "2026-05-12", "general": "2026-11-03"},
    "WI": {"primary": "2026-08-11", "general": "2026-11-03"},
    "WY": {"primary": "2026-08-18", "general": "2026-11-03"},
}

# All 50 state codes
ALL_STATES = [
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
    "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
    "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY",
]

# State code to full name mapping
STATE_NAMES = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas",
    "CA": "California", "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware",
    "FL": "Florida", "GA": "Georgia", "HI": "Hawaii", "ID": "Idaho",
    "IL": "Illinois", "IN": "Indiana", "IA": "Iowa", "KS": "Kansas",
    "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland",
    "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi",
    "MO": "Missouri", "MT": "Montana", "NE": "Nebraska", "NV": "Nevada",
    "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico", "NY": "New York",
    "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma",
    "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina",
    "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas", "UT": "Utah",
    "VT": "Vermont", "VA": "Virginia", "WA": "Washington", "WV": "West Virginia",
    "WI": "Wisconsin", "WY": "Wyoming",
}
