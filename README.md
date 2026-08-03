# CCC Autonomous Vehicle Access Tracker

This Streamlit research interface complements the CCC autonomous-vehicle primer. It compares statutory restrictions affecting **commercial driverless passenger service** across the 50 U.S. states and the District of Columbia.

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 -m streamlit run app.py
```

## Index interpretation

- `0.00` = least restrictive legal conditions under the published framework.
- `1.00` = effectively closed or most restrictive under the published framework.
- Blank / `Unclassified` = evidence is incomplete; it is never treated as zero.

The index is adapted from the measure-level structure of the OECD FDI Regulatory Restrictiveness Index. CCC's AV coding and results are independent and do not represent OECD findings.

The State Explorer lists all 51 jurisdictions as clickable score buttons. Selecting one opens a source-linked policy summary, component breakdown, and requirement-level audit record.

`adjusted_score = base_score × scope_factor`

The jurisdiction index is the sum of adjusted restrictions, capped at 1.00.

## Data files

- `state_access.csv`: 51-jurisdiction output table.
- `state_requirements.csv`: one row per coded legal restriction.
- `scoring_rules.csv`: public codebook of base scores.
- `scope_factors.csv`: public scope-adjustment table.
- `market_tracker.csv`: observed operator and market activity, separate from legal scoring.
- `state_sources.csv`: jurisdiction source directory.

Rebuild outputs with:

```bash
python3 scripts/calculate_policy_scores.py
```

## Research caution

The current classifications are provisional and require a second legal review before publication. The index measures regulatory restrictiveness, not safety performance, service quality, or overall policy merit. District of Columbia is included for comparison but excluded from formal state rankings.
