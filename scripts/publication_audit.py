from pathlib import Path
from datetime import datetime, timedelta

import pandas as pd

BASE = Path("data/processed")
TODAY = datetime.now()
STALE_AFTER_DAYS = 90

issues = []


def load(name):
    path = BASE / name
    if not path.exists():
        issues.append(
            {
                "dataset": name,
                "record": "Entire dataset",
                "issue": "File is missing",
                "severity": "High",
            }
        )
        return pd.DataFrame()

    try:
        return pd.read_csv(path)
    except pd.errors.EmptyDataError:
        issues.append(
            {
                "dataset": name,
                "record": "Entire dataset",
                "issue": "File is empty",
                "severity": "High",
            }
        )
        return pd.DataFrame()


def blank(value):
    return pd.isna(value) or str(value).strip() == ""


def check_date(dataset, record, value):
    if blank(value):
        issues.append(
            {
                "dataset": dataset,
                "record": record,
                "issue": "Missing verification date",
                "severity": "High",
            }
        )
        return

    try:
        date = pd.to_datetime(value)
        if TODAY - date > timedelta(days=STALE_AFTER_DAYS):
            issues.append(
                {
                    "dataset": dataset,
                    "record": record,
                    "issue": f"Verification date is older than {STALE_AFTER_DAYS} days",
                    "severity": "Medium",
                }
            )
    except Exception:
        issues.append(
            {
                "dataset": dataset,
                "record": record,
                "issue": "Verification date is invalid",
                "severity": "High",
            }
        )


policy = load("state_access.csv")

if not policy.empty:
    for _, row in policy.iterrows():
        state = row.get("state", "Unknown state")

        if blank(row.get("source_url")):
            issues.append(
                {
                    "dataset": "state_access.csv",
                    "record": state,
                    "issue": "Missing official source",
                    "severity": "High",
                }
            )

        score = pd.to_numeric(row.get("overall_score"), errors="coerce")

        if pd.isna(score) or not 0 <= score <= 100:
            issues.append(
                {
                    "dataset": "state_access.csv",
                    "record": state,
                    "issue": "Policy score is missing or outside 0–100",
                    "severity": "High",
                }
            )

        check_date(
            "state_access.csv",
            state,
            row.get("last_verified"),
        )

        summary = str(row.get("policy_summary", "")).lower()
        source = str(row.get("source_url", "")).lower()

        proposal_terms = [
            "proposed",
            "pending",
            "considered",
            "introduced",
            "pilot proposal",
        ]

        enacted_terms = [
            "enacted",
            "signed into law",
            "current law",
            "authorizes",
            "permits",
        ]

        if any(term in summary for term in proposal_terms) and any(
            term in summary for term in enacted_terms
        ):
            issues.append(
                {
                    "dataset": "state_access.csv",
                    "record": state,
                    "issue": "Summary may mix proposed and enacted policy language",
                    "severity": "Medium",
                }
            )

        if (
            row.get("driverless_testing_allowed") == 1
            and row.get("commercial_operation_allowed") == 1
            and "testing" in summary
            and "commercial" not in summary
        ):
            issues.append(
                {
                    "dataset": "state_access.csv",
                    "record": state,
                    "issue": "Commercial authorization may be inferred only from testing language",
                    "severity": "High",
                }
            )


safety = load("safety_data.csv")

if not safety.empty:
    for index, row in safety.iterrows():
        metric = row.get("metric", f"Row {index + 1}")

        source_field = (
            row.get("source_url")
            if "source_url" in safety.columns
            else row.get("source")
        )

        if blank(source_field):
            issues.append(
                {
                    "dataset": "safety_data.csv",
                    "record": metric,
                    "issue": "Missing safety source",
                    "severity": "High",
                }
            )

        required_context = [
            "study_period",
            "comparison_group",
            "geography",
        ]

        for column in required_context:
            if column not in safety.columns or blank(row.get(column)):
                issues.append(
                    {
                        "dataset": "safety_data.csv",
                        "record": metric,
                        "issue": f"Missing {column.replace('_', ' ')}",
                        "severity": "High",
                    }
                )

        if "last_verified" in safety.columns:
            check_date(
                "safety_data.csv",
                metric,
                row.get("last_verified"),
            )
        else:
            issues.append(
                {
                    "dataset": "safety_data.csv",
                    "record": metric,
                    "issue": "Missing last_verified column",
                    "severity": "High",
                }
            )


municipal = load("municipal_barriers.csv")

if not municipal.empty:
    for _, row in municipal.iterrows():
        record = f"{row.get('city', 'Unknown')}, {row.get('state', '')}"

        if blank(row.get("source_url")):
            issues.append(
                {
                    "dataset": "municipal_barriers.csv",
                    "record": record,
                    "issue": "Missing official municipal source",
                    "severity": "High",
                }
            )

        check_date(
            "municipal_barriers.csv",
            record,
            row.get("last_verified"),
        )


federal = load("federal_challenges.csv")

if not federal.empty:
    for _, row in federal.iterrows():
        record = f"{row.get('agency', '')}: {row.get('challenge', '')}"

        if blank(row.get("source_url")):
            issues.append(
                {
                    "dataset": "federal_challenges.csv",
                    "record": record,
                    "issue": "Missing official federal source",
                    "severity": "High",
                }
            )

        check_date(
            "federal_challenges.csv",
            record,
            row.get("last_verified"),
        )


audit = pd.DataFrame(
    issues,
    columns=["dataset", "record", "issue", "severity"],
)

output = BASE / "publication_audit.csv"
audit.to_csv(output, index=False)

print()
print("PUBLICATION AUDIT")
print("-----------------")

if audit.empty:
    print("PASS: No automated issues found.")
else:
    print(f"Total issues: {len(audit)}")
    print(f"High priority: {(audit['severity'] == 'High').sum()}")
    print(f"Medium priority: {(audit['severity'] == 'Medium').sum()}")
    print()
    print(audit.to_string(index=False))

print()
print(f"Saved report to {output}")
print()
print("Manual review still required:")
print("- Confirm each source actually supports the dashboard claim")
print("- Confirm bills marked proposed were not later enacted or rejected")
print("- Confirm testing permission is not treated as commercial permission")
