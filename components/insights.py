"""OECD-inspired finding-and-evidence rows for the dashboard landing page."""

from __future__ import annotations

from collections.abc import Callable

import pandas as pd
import plotly.express as px
import streamlit as st


def _insight_row(
    title: str,
    body: str,
    takeaway: str,
    chart_function: Callable[[], None],
) -> None:
    left, right = st.columns([0.34, 0.66], gap="large")
    with left:
        st.markdown(
            f"""
            <section class="insight-copy">
              <h2>{title}</h2>
              <p>{body}</p>
              <p class="insight-takeaway"><strong>{takeaway}</strong></p>
            </section>
            """,
            unsafe_allow_html=True,
        )
    with right:
        with st.container(border=True):
            chart_function()


def render_key_findings(
    market_df: pd.DataFrame,
    state_df: pd.DataFrame,
    safety_df: pd.DataFrame,
) -> None:
    """Render three concise findings before the detailed research sections."""
    required = {
        "market": {"state", "state_code", "market", "operator", "public_access", "vehicle_use"},
        "state": {"state", "state_code", "overall_score", "research_status", "policy_summary", "source_url"},
        "safety": {"metric", "value", "study_period", "geography", "source_url", "source_type"},
    }
    frames = {"market": market_df, "state": state_df, "safety": safety_df}
    if any(frame.empty or not columns.issubset(frame.columns) for name, columns in required.items() for frame in [frames[name]]):
        st.info("Key findings will appear when the required processed datasets are available.")
        return

    st.markdown('<div id="findings" class="anchor"></div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-number">02</div><div class="section-label">KEY FINDINGS</div>'
        '<h2 class="section-title wide">What the current evidence shows</h2>',
        unsafe_allow_html=True,
    )

    def access_chart() -> None:
        measure = st.selectbox(
            "Measure",
            ["Public robotaxi markets", "All tracked markets", "Operators represented"],
            key="finding_access_measure",
        )
        data = market_df.copy()
        if measure == "Public robotaxi markets":
            data = data[(data["public_access"] == "Yes") & (data["vehicle_use"] == "Robotaxi")]
            chart = data.groupby("state", as_index=False)["market"].nunique().rename(columns={"market": "value"})
            axis_title = "Verified public robotaxi markets"
        elif measure == "All tracked markets":
            chart = data.groupby("state", as_index=False)["market"].nunique().rename(columns={"market": "value"})
            axis_title = "Tracked markets"
        else:
            chart = data.groupby("state", as_index=False)["operator"].nunique().rename(columns={"operator": "value"})
            axis_title = "Operators represented"
        chart = chart.sort_values("value")
        fig = px.bar(chart, x="value", y="state", orientation="h", color_discrete_sequence=["#263552"])
        fig.update_layout(
            title=f"Autonomous vehicle access — {measure}", xaxis_title=axis_title,
            yaxis_title="", showlegend=False, height=430,
            margin=dict(l=10, r=10, t=65, b=25),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        )
        fig.update_xaxes(dtick=1, gridcolor="#E5E9ED", zeroline=False)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    _insight_row(
        "Public AV access remains geographically concentrated",
        "Commercial autonomous-vehicle activity is expanding, but verified public robotaxi access remains concentrated in a relatively small group of markets and states.",
        "Legal authorization is only one stage of delivering meaningful consumer access.",
        access_chart,
    )

    def policy_access_chart() -> None:
        public_states = set(
            market_df.loc[
                (market_df["public_access"] == "Yes") & (market_df["vehicle_use"] == "Robotaxi"),
                "state_code",
            ]
        )
        chart = state_df.copy()
        chart["Consumer access"] = chart["state_code"].map(
            lambda code: "Verified public service" if code in public_states else "No public service verified"
        )
        display_count = st.selectbox("States shown", [15, 25, "All"], key="finding_state_count")
        chart = chart.sort_values("overall_score", ascending=False)
        if display_count != "All":
            chart = chart.head(int(display_count))
        fig = px.bar(
            chart, x="state", y="overall_score", color="Consumer access",
            color_discrete_map={"Verified public service": "#EE8A1D", "No public service verified": "#263552"},
            hover_data={"policy_summary": True, "research_status": True, "source_url": True},
        )
        fig.update_layout(
            title="Regulatory openness and verified consumer access",
            xaxis_title="", yaxis_title="AV regulatory openness score", height=460,
            legend_title_text="", margin=dict(l=10, r=10, t=65, b=80),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        )
        fig.update_xaxes(tickangle=-50)
        fig.update_yaxes(range=[0, 100], gridcolor="#E5E9ED", zeroline=False)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        st.caption("The score measures only the criteria defined in this project. A score of 100 is not a claim of perfect policy.")

    _insight_row(
        "Legal openness does not guarantee consumer availability",
        "Some states align with every regulatory criterion currently measured while still lacking a verified public robotaxi service in the market tracker.",
        "Read the score as regulatory openness, not as complete policy performance or a consumer outcome.",
        policy_access_chart,
    )

    def safety_chart() -> None:
        chart = safety_df.copy()
        chart["value"] = pd.to_numeric(chart["value"], errors="coerce")
        chart = chart.dropna(subset=["value"]).sort_values("value")
        fig = px.bar(
            chart, x="value", y="metric", orientation="h", text="value",
            color_discrete_sequence=["#166B8C"],
            hover_data=["study_period", "geography", "source_type", "source_url"],
        )
        fig.update_traces(texttemplate="%{text:.0f}% fewer", textposition="inside")
        fig.update_layout(
            title="Operator-reported Waymo safety findings", xaxis_title="Percent fewer crashes",
            yaxis_title="", showlegend=False, height=410,
            margin=dict(l=10, r=10, t=65, b=25),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        )
        fig.update_xaxes(range=[0, 100], ticksuffix="%", gridcolor="#E5E9ED", zeroline=False)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        st.caption("All four current observations are Waymo-reported and should not be generalized to every AV system.")

    _insight_row(
        "Reported safety results are promising but narrow",
        "The current evidence table contains four Waymo-reported crash comparisons covering different outcomes, geographies, and study periods.",
        "The results should be presented with their study context and not treated as an industry-wide estimate.",
        safety_chart,
    )

