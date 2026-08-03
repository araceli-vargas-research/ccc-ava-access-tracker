from pathlib import Path
import pandas as pd

OUTPUT = Path("data/processed/state_access.csv")

STATE_LIST = [
    ("Alabama","AL"),("Alaska","AK"),("Arizona","AZ"),("Arkansas","AR"),
    ("California","CA"),("Colorado","CO"),("Connecticut","CT"),("Delaware","DE"),
    ("Florida","FL"),("Georgia","GA"),("Hawaii","HI"),("Idaho","ID"),
    ("Illinois","IL"),("Indiana","IN"),("Iowa","IA"),("Kansas","KS"),
    ("Kentucky","KY"),("Louisiana","LA"),("Maine","ME"),("Maryland","MD"),
    ("Massachusetts","MA"),("Michigan","MI"),("Minnesota","MN"),("Mississippi","MS"),
    ("Missouri","MO"),("Montana","MT"),("Nebraska","NE"),("Nevada","NV"),
    ("New Hampshire","NH"),("New Jersey","NJ"),("New Mexico","NM"),("New York","NY"),
    ("North Carolina","NC"),("North Dakota","ND"),("Ohio","OH"),("Oklahoma","OK"),
    ("Oregon","OR"),("Pennsylvania","PA"),("Rhode Island","RI"),
    ("South Carolina","SC"),("South Dakota","SD"),("Tennessee","TN"),("Texas","TX"),
    ("Utah","UT"),("Vermont","VT"),("Virginia","VA"),("Washington","WA"),
    ("West Virginia","WV"),("Wisconsin","WI"),("Wyoming","WY")
]

verified_updates = {
    "AZ": {
        "commercial_operation_allowed": 1,
        "driverless_testing_allowed": 1,
        "statewide_rules": 1,
        "local_rules_allowed": 0,
        "human_operator_required": 0,
        "special_permit_required": 1,
        "insurance_minimum": 0,
        "overall_score": 90,
        "policy_summary": "Statewide framework supports testing and commercial operation.",
        "research_status": "Preliminary review",
        "last_verified": "2026-07-20",
    },
    "TX": {
        "commercial_operation_allowed": 1,
        "driverless_testing_allowed": 1,
        "statewide_rules": 1,
        "local_rules_allowed": 0,
        "human_operator_required": 0,
        "special_permit_required": 0,
        "insurance_minimum": 0,
        "overall_score": 90,
        "policy_summary": "Uniform statewide rules limit separate municipal AV regulation.",
        "research_status": "Preliminary review",
        "last_verified": "2026-07-20",
    },
    "CA": {
        "commercial_operation_allowed": 1,
        "driverless_testing_allowed": 1,
        "statewide_rules": 0,
        "local_rules_allowed": 1,
        "human_operator_required": 0,
        "special_permit_required": 1,
        "insurance_minimum": 5000000,
        "overall_score": 60,
        "policy_summary": "Commercial deployment is allowed through a more complex permit system.",
        "research_status": "Preliminary review",
        "last_verified": "2026-07-20",
    },
    "NV": {
        "commercial_operation_allowed": 1,
        "driverless_testing_allowed": 1,
        "statewide_rules": 1,
        "local_rules_allowed": 0,
        "human_operator_required": 0,
        "special_permit_required": 0,
        "insurance_minimum": 0,
        "overall_score": 85,
        "policy_summary": "State law broadly permits automated vehicle operation.",
        "research_status": "Preliminary review",
        "last_verified": "2026-07-20",
    },
    "FL": {
        "commercial_operation_allowed": 1,
        "driverless_testing_allowed": 1,
        "statewide_rules": 1,
        "local_rules_allowed": 0,
        "human_operator_required": 0,
        "special_permit_required": 0,
        "insurance_minimum": 0,
        "overall_score": 85,
        "policy_summary": "Fully autonomous operation is permitted under statewide rules.",
        "research_status": "Preliminary review",
        "last_verified": "2026-07-20",
    },
}

rows = []

for state, state_code in STATE_LIST:
    row = {
        "state": state,
        "state_code": state_code,
        "commercial_operation_allowed": 0,
        "driverless_testing_allowed": 0,
        "statewide_rules": 0,
        "local_rules_allowed": 0,
        "human_operator_required": 0,
        "special_permit_required": 0,
        "insurance_minimum": 0,
        "overall_score": 0,
        "policy_summary": "Research pending.",
        "source_url": "",
        "research_status": "Not reviewed",
        "last_verified": "",
    }

    if state_code in verified_updates:
        row.update(verified_updates[state_code])

    rows.append(row)

df = pd.DataFrame(rows)
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(OUTPUT, index=False)

print(f"Saved {len(df)} states to {OUTPUT}")
print(f"Reviewed states: {(df['research_status'] != 'Not reviewed').sum()}")
