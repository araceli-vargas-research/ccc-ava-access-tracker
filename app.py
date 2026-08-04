from __future__ import annotations

import base64
import html
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).parent
DATA = ROOT / "data" / "processed"
ASSETS = ROOT / "assets"

st.set_page_config(page_title="Autonomous Vehicle Access Tracker | CCC", page_icon="🚘", layout="wide", initial_sidebar_state="collapsed")
st.markdown(f"<style>{(ROOT / 'styles.css').read_text()}</style>", unsafe_allow_html=True)


@st.cache_data
def csv(name: str) -> pd.DataFrame:
    return pd.read_csv(DATA / name)


def uri(path: Path) -> str:
    mime = "image/png" if path.suffix.lower() == ".png" else "image/jpeg"
    return f"data:{mime};base64,{base64.b64encode(path.read_bytes()).decode()}"


def section(kicker: str, title: str, text: str) -> None:
    st.markdown(f'<div class="section-kicker">{kicker}</div><h2>{title}</h2><p class="lede">{text}</p>', unsafe_allow_html=True)


states = csv("state_access.csv")
requirements = csv("state_requirements.csv")
rules = csv("scoring_rules.csv")
scope = csv("scope_factors.csv")
markets = csv("market_tracker.csv")
sources = csv("state_sources.csv")

logo = uri(ASSETS / "ccc-logo.png")
hero = uri(ASSETS / "av-dashboard-hero.jpg")

st.markdown(f"""
<nav><img src="{logo}" alt="Consumer Choice Center"><span>Autonomous Vehicle Access Tracker</span>
<div><a href="#index">Index</a><a href="#markets">Commercial access</a><a href="#method">Methodology</a><a href="#audit">Audit</a></div></nav>
<section class="hero">
  <div><div class="eyebrow">AUTONOMOUS VEHICLE POLICY</div><h1> Autonomous Vehicle Access Tracker</h1>
  <p>The Autonomous Vehicle Access Tracker (AVAT) compares statutory barriers to <b>commercial driverless passenger service</b> across all 50 states and the District of Columbia. A higher index score indicates a more restrictive regulatory framework.</p>
  <a class="button" href="#index">Explore the index →</a></div>
  <div class="hero-image" style="background-image:linear-gradient(90deg,rgba(34,38,78,.12),rgba(34,38,78,.02)),url('{hero}')"></div>
</section>
<div class="definition"><b>What is consumer access?</b> Publicly bookable passenger service in which the automated driving system performs the driving task without an onboard human safety driver. Testing, freight, and announced future markets are reported separately.</div>
""", unsafe_allow_html=True)

about_left, about_right = st.columns([0.40, 0.60], gap="large", vertical_alignment="top")
with about_left:
    st.markdown(
        '''<section class="about-title">
          <div class="section-kicker compact">ABOUT THE TRACKER</div>
          <h2>What is the Autonomous Vehicle Access Tracker?</h2>
          <p>A source-linked indicator of legal restrictions affecting commercial driverless passenger service across U.S. jurisdictions.</p>
        </section>''',
        unsafe_allow_html=True,
    )
with about_right:
    st.markdown(
        '''<div class="ava-accordion">
          <details>
            <summary>Overview</summary>
            <p>The Autonomous Vehicle Access Tracker (AVAT) covers all 50 states and the District of Columbia. It supports comparison of market-entry conditions and the monitoring of state-level AV policy reform.</p>
          </details>
          <details>
            <summary>What does the index measure?</summary>
            <p>The index measures legally binding statutory and administrative restrictions affecting commercial driverless passenger service across four categories: market entry, screening and approval, human-operator restrictions, and other operational restrictions.</p>
          </details>
          <details>
            <summary>How is the index calculated?</summary>
            <p>Each documented restriction receives a base score and, where appropriate, a scope adjustment. Adjusted measures are summed across the four categories and capped at 1. Missing evidence is classified as Unclassified, never as zero.</p>
          </details>
          <details>
            <summary>What is excluded from scoring?</summary>
            <p>Proposed bills, voluntary guidance, operator announcements, observed market availability, unsupported enforcement practices, and safety outcomes do not determine a jurisdiction’s index result.</p>
          </details>
          <details>
            <summary>How does this complement the primer?</summary>
            <p>The primer provides the broader policy argument. The dashboard exposes the underlying classifications, calculations, operational market records, coding status, and primary sources.</p>
          </details>
        </div>''',
        unsafe_allow_html=True,
    )

st.markdown('<div id="index"></div>', unsafe_allow_html=True)
section("01 · STATE RESTRICTIVENESS", "What is the geographic coverage of the AV Access Tracker?", "The AV Access Tracker (AVAT) covers all 50 states and the District of Columbia. The map displays each classified state’s regulatory restrictiveness score for commercial driverless passenger service. Scores closer to 0 indicate fewer documented restrictions, while scores closer to 1 indicate a more restrictive or effectively closed framework. The District of Columbia is reported separately and excluded from formal state rankings.")

ranked = states.loc[states.include_in_state_ranking.eq(True) & states.restrictiveness_index.notna()].copy()
unclassified = states.restrictiveness_index.isna().sum()
c1, c2, c3, c4 = st.columns(4)
c1.metric("Jurisdictions covered", "51", "50 states + D.C.")
c2.metric("States classified", f"{len(ranked)}", "provisional legal coding")
c3.metric("Median restriction", f"{ranked.restrictiveness_index.median():.2f}", "0 least · 1 most")
c4.metric("Unclassified", f"{unclassified}", "never treated as zero")

region = st.multiselect("Region", sorted(states.region.dropna().unique()), default=sorted(states.region.dropna().unique()))
view = states[states.region.isin(region)].copy()
map_data = view[view.state_code.ne("DC") & view.restrictiveness_index.notna()].copy()
map_data["index_display"] = map_data.restrictiveness_index.map(lambda x: f"{x:.2f}")

if "map_projection_scale" not in st.session_state:
    st.session_state.map_projection_scale = 1.0

zoom_out, zoom_reset, zoom_in, zoom_note = st.columns([0.12, 0.12, 0.12, 0.64], vertical_alignment="center")
if zoom_out.button("− Zoom", key="map_zoom_out", use_container_width=True):
    st.session_state.map_projection_scale = max(1.0, round(st.session_state.map_projection_scale - 0.1, 1))
if zoom_reset.button("Reset", key="map_zoom_reset", use_container_width=True):
    st.session_state.map_projection_scale = 1.0
if zoom_in.button("+ Zoom", key="map_zoom_in", use_container_width=True):
    st.session_state.map_projection_scale = min(1.5, round(st.session_state.map_projection_scale + 0.1, 1))
zoom_note.caption(f"Map zoom: {st.session_state.map_projection_scale:.1f}× · Limited to 1.0–1.5×")

fig = px.choropleth(map_data, locations="state_code", locationmode="USA-states", scope="usa", color="restrictiveness_index",
    range_color=(0,1), color_continuous_scale=["#9BD8C7", "#F4B544", "#E95C1F", "#B9473A"],
    hover_name="state", custom_data=["index_display", "commercial_access_status", "policy_summary", "score_status"])
fig.update_traces(hovertemplate="<b>%{hovertext}</b><br><br>Restrictiveness index: <b>%{customdata[0]}</b><br>Commercial pathway: %{customdata[1]}<br>Status: %{customdata[3]}<br><br>%{customdata[2]}<extra></extra>")
fig.update_geos(projection_scale=st.session_state.map_projection_scale)
fig.update_layout(height=570, margin=dict(l=0,r=0,t=20,b=0), paper_bgcolor="rgba(0,0,0,0)", font_family="Montserrat", dragmode=False, uirevision="bounded-us-map", coloraxis_colorbar=dict(title="Restriction<br>0–1", tickvals=[0,.25,.5,.75,1]))
st.plotly_chart(fig, width="stretch", config={"displayModeBar":False, "scrollZoom":False, "doubleClick":False})
st.caption("District of Columbia is included in the research table but excluded from formal state rankings. Hover text shows the legal classification and source-based summary.")

bar = ranked.sort_values("restrictiveness_index", ascending=False)
fig = px.bar(bar, x="state", y="restrictiveness_index", color="restrictiveness_index", range_color=(0,1),
    color_continuous_scale=["#9BD8C7", "#F4B544", "#E95C1F", "#B9473A"], custom_data=["policy_summary","source_url","score_status"])
fig.update_traces(hovertemplate="<b>%{x}</b><br>Restrictiveness: <b>%{y:.2f}</b><br>Status: %{customdata[2]}<br><br>%{customdata[0]}<extra></extra>")
fig.update_layout(height=480, showlegend=False, coloraxis_showscale=False, xaxis_title="", yaxis_title="Restrictiveness index", yaxis_range=[0,1], margin=dict(l=10,r=10,t=25,b=100), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="white", font_family="Montserrat")
fig.update_xaxes(tickangle=-55); fig.update_yaxes(gridcolor="#E7ECF4")
st.plotly_chart(fig, width="stretch", config={"displayModeBar":False})

with st.expander("View component analysis by jurisdiction"):
    category_cols = ["Market-entry restrictions", "Screening and approval", "Human-operator restrictions", "Other operational restrictions"]
    display = view[["state","state_code","jurisdiction_type","restrictiveness_index","score_status",*category_cols,"policy_summary","source_url"]].sort_values("restrictiveness_index", ascending=False, na_position="last")
    st.dataframe(display, hide_index=True, width="stretch", column_config={"restrictiveness_index":st.column_config.NumberColumn("Index",format="%.2f"),"source_url":st.column_config.LinkColumn("Primary source")})

st.markdown('<div id="markets"></div>', unsafe_allow_html=True)
section("02 · COMMERCIAL ACCESS", "Observed service is separate from legal openness", "The market tracker reports operational activity. A permissive law does not establish that residents can book a driverless ride, and an operator announcement is not counted as current public access.")
public = markets[(markets.vehicle_use.eq("Robotaxi")) & (markets.public_access.eq("Yes")) & (markets.service_status.eq("Commercial"))].copy()
m1,m2,m3 = st.columns(3)
m1.metric("Verified public markets", public.market.nunique())
m2.metric("States represented", public.state.nunique())
m3.metric("Operators represented", public.operator.nunique())
st.dataframe(markets, hide_index=True, width="stretch", column_config={"source_url":st.column_config.LinkColumn("Source")})

st.markdown('<div id="method"></div>', unsafe_allow_html=True)
section("03 · METHODOLOGY", "Transparent measure-level scoring", "The structure is adapted from the OECD FDI Regulatory Restrictiveness Index: observed legal restrictions receive a base score, are adjusted for their scope, and are summed to a maximum of 1.00. CCC’s AV classifications and results are independent and do not represent OECD findings.")
st.markdown("### Formula")
st.latex(r"AVA_j = \min\left(1,\ \sum_i b_i \times s_i\right)")
st.markdown("Where $b_i$ is the published base score for restriction $i$ and $s_i$ is the activity-scope factor. Missing evidence produces **Unclassified**, never 0.")

left,right = st.columns([1.35,1])
with left:
    st.markdown("### Scoring framework")
    st.dataframe(rules, hide_index=True, width="stretch", column_config={"base_score":st.column_config.NumberColumn("Base score",format="%.3f")})
with right:
    st.markdown("### Scope factors")
    st.dataframe(scope, hide_index=True, width="stretch", column_config={"scope_factor":st.column_config.NumberColumn("Factor",format="%.2f")})

st.markdown("### What is and is not scored")
a,b = st.columns(2)
with a:
    st.markdown("**Included**\n- Enacted restrictions governing commercial driverless passenger service\n- AV-specific approvals and human-operator mandates\n- Local operating restrictions where legally authorized\n- AV financial requirements above comparable rideshare requirements")
with b:
    st.markdown("**Memorandum items only**\n- Proposed bills and advisory councils\n- Ordinary registration and traffic rules\n- Company announcements and voluntary guidance\n- Testing-only insurance when scoring commercial service")

st.markdown('<div id="audit"></div>', unsafe_allow_html=True)
section("04 · STATE EXPLORER", "Every jurisdiction at a glance", "Select any state or the District of Columbia to open its source-linked policy summary and component analysis. Scores run from 0.00 (least restrictive) to 1.00 (most restrictive); missing evidence remains unclassified.")

if "selected_jurisdiction" not in st.session_state:
    st.session_state.selected_jurisdiction = None

button_states = states.sort_values("state").reset_index(drop=True)
for start in range(0, len(button_states), 6):
    row_columns = st.columns(6, gap="small")
    for column, (_, jurisdiction) in zip(row_columns, button_states.iloc[start:start + 6].iterrows()):
        score_label = "N/A" if pd.isna(jurisdiction.restrictiveness_index) else f"{jurisdiction.restrictiveness_index:.2f}"
        is_selected = st.session_state.selected_jurisdiction == jurisdiction.state
        if column.button(
            f"{jurisdiction.state_code}  ·  {score_label}",
            key=f"jurisdiction_{jurisdiction.state_code}",
            type="primary" if is_selected else "secondary",
            width="stretch",
            help=f"Open {jurisdiction.state}'s policy record",
        ):
            st.session_state.selected_jurisdiction = jurisdiction.state
            st.rerun()

st.markdown('<div class="score-key"><span><b>0.00</b> least restrictive</span><span><b>1.00</b> most restrictive</span><span><b>N/A</b> unclassified</span></div>', unsafe_allow_html=True)

selected = st.session_state.selected_jurisdiction
if selected is None:
    st.markdown('<div class="state-empty">Select a jurisdiction above to view its full policy record.</div>', unsafe_allow_html=True)
else:
    state_row = states.loc[states.state.eq(selected)].iloc[0]
    score_label = "Unclassified" if pd.isna(state_row.restrictiveness_index) else f"{state_row.restrictiveness_index:.2f}"
    pathway = html.escape(str(state_row.commercial_access_status))
    summary = html.escape(str(state_row.policy_summary))
    status = html.escape(str(state_row.score_status))
    source_link = ""
    if isinstance(state_row.source_url, str) and state_row.source_url.startswith("http"):
        source_link = f'<a href="{html.escape(state_row.source_url)}" target="_blank">Open primary source ↗</a>'
    st.markdown(
        f'''<section class="state-detail">
          <div class="state-detail-top"><div><span>{html.escape(str(state_row.state_code))}</span><h3>{html.escape(selected)}</h3></div><div class="state-score"><small>RESTRICTIVENESS</small>{score_label}</div></div>
          <div class="state-tags"><span>{pathway}</span><span>{status}</span><span>{html.escape(str(state_row.jurisdiction_type))}</span></div>
          <p>{summary}</p>{source_link}
        </section>''',
        unsafe_allow_html=True,
    )
    category_cols = ["Market-entry restrictions", "Screening and approval", "Human-operator restrictions", "Other operational restrictions"]
    components = pd.DataFrame({
        "Component": category_cols,
        "Score": [state_row.get(category, pd.NA) for category in category_cols],
    })
    components["Score"] = pd.to_numeric(components["Score"], errors="coerce")
    st.markdown("#### Component breakdown")
    st.dataframe(components, hide_index=True, width="stretch", column_config={"Score": st.column_config.ProgressColumn("Restriction", min_value=0, max_value=1, format="%.2f")})
    detail = requirements[requirements.state.eq(selected)][["category","measure","legal_finding","base_score","scope_factor","adjusted_score","coding_status","source_url"]]
    st.markdown("#### Requirement-level record")
    if detail.empty:
        st.info("No scored requirement is published because the jurisdiction is unclassified.")
    else:
        st.dataframe(detail, hide_index=True, width="stretch", column_config={"source_url":st.column_config.LinkColumn("Source")})

st.markdown("""
<div class="method-note"><b>Method sources</b><br>
OECD (2024), <i>OECD FDI Regulatory Restrictiveness Index: Methodology and policy applications</i>.<br>
OECD & European Commission, Joint Research Centre (2008), <i>Handbook on Constructing Composite Indicators: Methodology and User Guide</i>.<br><br>
The dashboard complements the autonomous-vehicle primer; it is not a reproduction of any operator dashboard and does not assess vehicle safety performance.
</div><footer>CONSUMER CHOICE CENTER <span>Autonomous Vehicle Access Tracker · Research release</span></footer>
""", unsafe_allow_html=True)
