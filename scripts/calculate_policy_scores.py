"""Build the 51-jurisdiction AVA research and scoring tables."""

from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT))
from src.scoring import CATEGORIES, score_requirements
DATA = ROOT / "data" / "processed"


def make_requirement(row: pd.Series, requirement_id: str, category: str, measure: str,
                     finding: str, base: float, scope: float = 1.0,
                     include: bool = True, note: str = "") -> dict:
    return {
        "requirement_id": requirement_id,
        "state": row.state,
        "state_code": row.state_code,
        "activity": "Commercial driverless passenger service",
        "category": category,
        "measure": measure,
        "legal_finding": finding,
        "base_score": base,
        "scope_band": "Fully" if scope == 1 else "Largely" if scope == .75 else "Fairly",
        "scope_factor": scope,
        "adjusted_score": round(base * scope, 3),
        "include_in_index": include,
        "coding_status": "Provisional - source review required",
        "source_url": row.source_url,
        "last_verified": row.last_verified,
        "coding_note": note,
    }


def main() -> None:
    legacy = pd.read_csv(DATA / "state_access.csv")
    legacy = legacy.drop(columns=[c for c in legacy.columns if c.endswith("_score") or c == "overall_score"])
    dc = pd.DataFrame([{
        "state": "District of Columbia", "state_code": "DC", "commercial_operation_allowed": pd.NA,
        "driverless_testing_allowed": pd.NA, "statewide_rules": pd.NA, "local_rules_allowed": pd.NA,
        "human_operator_required": pd.NA, "special_permit_required": pd.NA, "insurance_minimum": pd.NA,
        "policy_summary": "No source-complete commercial driverless passenger-service classification is included in this release.",
        "source_url": "", "research_status": "Unclassified - evidence review required", "last_verified": "",
        "source_name": "", "source_type": "Missing", "source_status": "Missing source", "region": "South",
    }])
    states = pd.concat([legacy, dc], ignore_index=True)
    states["jurisdiction_type"] = states.state_code.map(lambda x: "Federal district" if x == "DC" else "State")
    states["include_in_state_ranking"] = states.state_code.ne("DC")

    requirements: list[dict] = []
    for row in states.itertuples(index=False):
        s = pd.Series(row._asdict())
        code = s.state_code
        if code == "DC":
            continue
        commercial = int(s.commercial_operation_allowed)
        testing = int(s.driverless_testing_allowed)
        if commercial:
            finding, base = "General commercial pathway identified", 0.0
        elif testing:
            finding, base = "Testing or controlled-pilot pathway only", 0.5
        else:
            finding, base = "No commercial or testing pathway identified in the cited evidence", 1.0
        requirements.append(make_requirement(s, f"{code}-ME-01", CATEGORIES[0], "Commercial market pathway", finding, base))

        if int(s.special_permit_required) and (commercial or testing):
            requirements.append(make_requirement(s, f"{code}-SA-01", CATEGORIES[1], "Separate AV permit or approval", "Separate AV-specific approval recorded", .05))
        if int(s.human_operator_required) and (commercial or testing):
            score = .20 if commercial else .10
            finding = "Onboard human operator recorded for commercial operation" if commercial else "Onboard human operator recorded for testing"
            requirements.append(make_requirement(s, f"{code}-HO-01", CATEGORIES[2], "Onboard human operator", finding, score))
        if int(s.local_rules_allowed):
            requirements.append(make_requirement(s, f"{code}-OO-01", CATEGORIES[3], "Separate local AV rules", "Broad local AV rulemaking authority recorded", .10))
        insurance = pd.to_numeric(s.insurance_minimum, errors="coerce")
        if commercial and pd.notna(insurance) and insurance > 1_000_000:
            requirements.append(make_requirement(
                s, f"{code}-OO-02", CATEGORIES[3], "AV-specific financial responsibility",
                f"Recorded minimum: ${insurance:,.0f}", .05,
                note="Applied only when the recorded amount governs the headline commercial activity; ordinary auto insurance is not scored."
            ))

    req = pd.DataFrame(requirements)
    req.to_csv(DATA / "state_requirements.csv", index=False)
    scores = score_requirements(req)
    states = states.merge(scores, on="state_code", how="left")
    states["score_status"] = states["restrictiveness_index"].map(lambda x: "Provisional" if pd.notna(x) else "Unclassified")
    states["commercial_access_status"] = states["commercial_operation_allowed"].map({1: "Legal pathway identified", 0: "No general pathway identified"}).fillna("Unclassified")
    states.to_csv(DATA / "state_access.csv", index=False)

    rules = [
        ("ME01", CATEGORIES[0], "Commercial operation expressly prohibited or no lawful pathway identified", 1.00),
        ("ME02", CATEGORIES[0], "No commercial pathway; testing only", .50),
        ("ME03", CATEGORIES[0], "Temporary or controlled pilot", .30),
        ("ME04", CATEGORIES[0], "Limited operators, vehicles, or services", .20),
        ("ME05", CATEGORIES[0], "General commercial pathway available", 0.00),
        ("SA01", CATEGORIES[1], "Discretionary approval with unbounded criteria", .15),
        ("SA02", CATEGORIES[1], "Mandatory pilot or testing before deployment", .10),
        ("SA03", CATEGORIES[1], "Separate AV permit", .05),
        ("HO01", CATEGORIES[2], "Onboard operator required for commercial operation", .20),
        ("HO02", CATEGORIES[2], "Onboard operator required for testing", .10),
        ("OO01", CATEGORIES[3], "Broad local authority to impose separate AV rules", .10),
        ("OO02", CATEGORIES[3], "Geographic, route, hour, fleet, or passenger restriction", .05),
        ("OO03", CATEGORIES[3], "AV financial requirement more than 1x but below 5x comparable TNC minimum", .03),
        ("OO04", CATEGORIES[3], "AV financial requirement at least 5x comparable TNC minimum", .05),
    ]
    pd.DataFrame(rules, columns=["rule_id", "category", "condition", "base_score"]).to_csv(DATA / "scoring_rules.csv", index=False)
    pd.DataFrame([
        ("Fully", ">=90%", 1.00), ("Largely", "50% to <90%", .75),
        ("Fairly", "30% to <50%", .50), ("Moderately", "10% to <30%", .25),
        ("Marginally", "5% to <10%", .10), ("Residually", "<5%", .05),
    ], columns=["scope_band", "estimated_share_of_activity", "scope_factor"]).to_csv(DATA / "scope_factors.csv", index=False)
    print(f"Built {len(states)} jurisdictions and {len(req)} scored requirement records.")


if __name__ == "__main__":
    main()
