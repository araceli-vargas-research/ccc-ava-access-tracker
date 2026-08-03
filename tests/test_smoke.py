from pathlib import Path

import pandas as pd

ROOT = Path(__file__).parents[1]
DATA = ROOT / "data" / "processed"


def test_required_files_exist():
    for name in ["state_access.csv", "state_requirements.csv", "scoring_rules.csv", "scope_factors.csv", "market_tracker.csv"]:
        assert (DATA / name).exists()


def test_51_jurisdictions_and_dc_rules():
    states = pd.read_csv(DATA / "state_access.csv")
    assert len(states) == 51
    assert states.state_code.nunique() == 51
    dc = states.loc[states.state_code.eq("DC")].iloc[0]
    assert dc.jurisdiction_type == "Federal district"
    assert not bool(dc.include_in_state_ranking)


def test_index_range_and_unclassified_not_zero():
    states = pd.read_csv(DATA / "state_access.csv")
    classified = states.restrictiveness_index.dropna()
    assert classified.between(0, 1).all()
    assert states.loc[states.score_status.eq("Unclassified"), "restrictiveness_index"].isna().all()


def test_requirement_math_and_sources():
    req = pd.read_csv(DATA / "state_requirements.csv")
    expected = (req.base_score * req.scope_factor).round(3)
    assert expected.equals(req.adjusted_score.round(3))
    assert req.loc[req.include_in_index, "source_url"].fillna("").str.startswith("http").all()


def test_no_legacy_100_point_scores():
    states = pd.read_csv(DATA / "state_access.csv")
    forbidden = {"overall_score", "commercial_score", "testing_score", "insurance_score"}
    assert forbidden.isdisjoint(states.columns)
