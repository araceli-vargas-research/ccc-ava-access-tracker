"""Transparent OECD-style restrictiveness calculations for the AVA tracker."""

from __future__ import annotations

import pandas as pd

CATEGORIES = [
    "Market-entry restrictions",
    "Screening and approval",
    "Human-operator restrictions",
    "Other operational restrictions",
]


def score_requirements(requirements: pd.DataFrame) -> pd.DataFrame:
    """Return one 0-1 index per jurisdiction; unclassified evidence stays null."""
    coded = requirements.loc[requirements["include_in_index"].eq(True)].copy()
    coded["adjusted_score"] = coded["base_score"] * coded["scope_factor"]
    category = (
        coded.groupby(["state_code", "category"], as_index=False)["adjusted_score"].sum()
        .pivot(index="state_code", columns="category", values="adjusted_score")
        .fillna(0.0)
    )
    for name in CATEGORIES:
        if name not in category:
            category[name] = 0.0
    category["restrictiveness_index"] = category[CATEGORIES].sum(axis=1).clip(upper=1.0)
    return category.reset_index()
