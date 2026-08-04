from __future__ import annotations

import base64
import html
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st
from plotly.colors import sample_colorscale

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


def section_band(kicker: str, title: str, text: str, background: str, foreground: str = "#FFFFFF", kicker_color: str | None = None) -> None:
    """Render a branded chapter divider without changing the section content below it."""
    kicker_style = f"color:{kicker_color}" if kicker_color else "color:inherit"
    st.markdown(
        f'''<section class="section-band" style="background:{background};color:{foreground}">
          <div class="band-kicker" style="{kicker_style}">{html.escape(kicker)}</div>
          <h2>{html.escape(title)}</h2>
          <p>{html.escape(text)}</p>
        </section>''',
        unsafe_allow_html=True,
    )


def chart_heading(title: str, scale: str, description: str) -> None:
    st.markdown(
        f'''<div class="chart-heading">
          <h3>{html.escape(title)}</h3>
          <div class="chart-scale">{html.escape(scale)}</div>
          <p>{html.escape(description)}</p>
        </div>''',
        unsafe_allow_html=True,
    )


def chart_source(source: str) -> None:
    st.markdown(f'<div class="chart-source"><b>Source:</b> {html.escape(source)}</div>', unsafe_allow_html=True)


st.markdown('''<style>
.section-band{margin:4.75rem 0 2rem;padding:clamp(2rem,4vw,3.8rem);border-radius:.45rem;border-top:.45rem solid #F4B544;box-shadow:0 8px 24px rgba(34,38,78,.08)}
.section-band .band-kicker{font-weight:850;letter-spacing:.16em;font-size:.78rem;text-transform:uppercase;opacity:.9;margin-bottom:1.5rem}
.section-band h2{color:inherit!important;font-size:clamp(2rem,4vw,3.5rem)!important;line-height:1.05!important;margin:0 0 1rem!important;max-width:58rem}
.section-band p{color:inherit!important;font-size:clamp(1rem,1.4vw,1.2rem)!important;line-height:1.65!important;max-width:68rem;margin:0!important;opacity:.94}
.chart-heading{margin:1.35rem 0 .4rem}.chart-heading h3{margin:0!important;color:#41444B!important;font-size:clamp(1.15rem,1.7vw,1.55rem)!important;font-weight:800!important}.chart-scale{color:#41444B;font-size:clamp(.98rem,1.3vw,1.15rem);font-weight:800;margin:.2rem 0 .55rem}.chart-heading p{color:#596489;line-height:1.55;max-width:68rem;margin:0}.chart-source{color:#65708F;font-size:.88rem;margin:.3rem 0 1.8rem;padding-top:.65rem;border-top:1px solid #DDE3EC}
.hero .button{background:#22264E!important;color:#FFFFFF!important;border-color:#22264E!important}.hero .button:hover{background:#147B86!important;color:#FFFFFF!important}
.avat-research-overview{margin:3rem 0 2rem}.avat-overview-marker{width:3.75rem;border-top:.25rem solid #147B86;color:#147B86;font-size:.82rem;font-weight:900;padding-top:.65rem;margin-bottom:1.7rem}.avat-research-overview .avat-overview-kicker{color:#EE5C1F;font-size:.78rem;font-weight:850;letter-spacing:.15em;margin-bottom:.65rem}.avat-research-overview h2{color:#22264E!important;font-size:clamp(1.9rem,3vw,3rem)!important;line-height:1.1!important;margin:.2rem 0 .7rem!important}.avat-research-overview>p{color:#596489;max-width:70rem}.avat-overview-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:1.25rem;margin-top:1.5rem}.avat-overview-card{display:flex!important;flex-direction:column!important;align-items:flex-start!important;position:relative!important;min-height:14rem!important;padding:1.7rem!important;background:#F2F4FA!important;border-top:.35rem solid #147B86!important}.avat-card-label{display:block!important;position:static!important;order:1!important;color:#147B86!important;font-size:.78rem!important;font-weight:850!important;letter-spacing:.13em!important}.avat-card-title{display:block!important;position:static!important;order:2!important;color:#22264E!important;font-size:clamp(1.25rem,1.8vw,1.65rem)!important;font-weight:850!important;line-height:1.2!important;margin:.7rem 0 1rem!important;text-align:left!important}.avat-card-description{display:block!important;position:static!important;order:3!important;color:#596489!important;line-height:1.55!important;margin:0 0 2rem!important;text-align:left!important}.avat-card-arrow{position:absolute!important;right:1.3rem!important;bottom:1.1rem!important;color:#22264E!important;font-size:1.4rem!important;font-weight:800!important;text-decoration:none!important}.avat-overview-card:hover{background:#EAF4FA!important;transform:translateY(-2px)}
.avat-consumer-choice-statement{margin:5rem 0;padding:clamp(3.5rem,7vw,7.5rem);background:#EAF1F5}.avat-consumer-choice-statement small{display:block;color:#147B86;font-weight:850;letter-spacing:.15em;margin-bottom:2.5rem}.avat-consumer-choice-statement p{color:#16253F;font-size:clamp(2.4rem,5.4vw,5.4rem);line-height:1.08;letter-spacing:-.045em;max-width:72rem;margin:0}
.st-key-access_metrics [data-testid="stMetric"]{background:#DDF3ED!important;border-top:.35rem solid #63BFA8!important;border-radius:.35rem!important;padding:1.25rem 1.4rem!important;min-height:9rem}.st-key-access_metrics [data-testid="stMetricLabel"]{color:#147B86!important}.st-key-access_metrics [data-testid="stMetricValue"]{color:#22264E!important}
@media(max-width:800px){.avat-overview-grid{grid-template-columns:1fr}.avat-overview-card{min-height:11rem!important}}
</style>''', unsafe_allow_html=True)


def binary_label(value: object, yes: str, no: str, missing: str = "Not classified") -> str:
    numeric = pd.to_numeric(value, errors="coerce")
    if pd.isna(numeric):
        return missing
    return yes if int(numeric) == 1 else no


states = csv("state_access.csv")
requirements = csv("state_requirements.csv")
rules = csv("scoring_rules.csv")
scope = csv("scope_factors.csv")
markets = csv("market_tracker.csv")
sources = csv("state_sources.csv")
safety = csv("safety_data.csv")

logo = uri(ASSETS / "ccc-logo.png")
hero = uri(ASSETS / "av-dashboard-hero.jpg")

st.markdown(f"""
<nav><img src="{logo}" alt="Consumer Choice Center"><span>Autonomous Vehicle Access Tracker</span>
<div><a href="#index">Index</a><a href="#markets">Consumer access</a><a href="#audit">State explorer</a><a href="#safety">Safety</a><a href="#federal">Federal policy</a><a href="#method">Methodology</a><a href="#recommendations">Recommendations</a></div></nav>
<section class="hero">
  <div><div class="eyebrow">AUTONOMOUS VEHICLE POLICY</div><h1> Autonomous Vehicle Access Tracker</h1>
  <p>The Autonomous Vehicle Access Tracker (AVAT) compares statutory barriers to <b>commercial driverless passenger service</b> across all 50 states and the District of Columbia. A higher index score indicates a more restrictive regulatory framework.</p>
  <a class="button" href="#index">Explore the index →</a></div>
  <div class="hero-image" style="background-image:linear-gradient(90deg,rgba(34,38,78,.12),rgba(34,38,78,.02)),url('{hero}')"></div>
</section>
<div class="definition">
  <p><b>What is consumer access?</b> Consumer access means that a commercial driverless passenger service is available for members of the public to book within a defined geographic market.</p>
  <p><b>What qualifies as driverless passenger service?</b> The automated driving system performs the driving task without an onboard human safety driver. Testing, freight, services requiring an onboard safety driver, and announced future markets are reported separately.</p>
</div>
""", unsafe_allow_html=True)

about_left, about_right = st.columns([0.40, 0.60], gap="large", vertical_alignment="top")
with about_left:
    st.markdown(
        '''<section class="about-title">
          <div class="section-kicker compact">ABOUT THE TRACKER</div>
          <h2>What is the Autonomous Vehicle Access Tracker (AVAT)?</h2>
          <p>A source-linked dashboard of legal restrictions affecting the current market access for Level-4 commercial driverless passenger service across U.S. jurisdictions.</p>
        </section>''',
        unsafe_allow_html=True,
    )
with about_right:
    st.markdown(
        '''<div class="ava-accordion">
          <details>
            <summary>Overview</summary>
            <p>The Autonomous Vehicle Access Tracker (AVAT) covers all 50 states and the District of Columbia. It supports comparison of market-entry conditions, the monitoring and scoring based on structured methodological methods of state-level AV policy reform.</p>
          </details>
          <details>
            <summary>What does the index measure?</summary>
            <p>The index measures legally binding statutory and administrative restrictions affecting commercial driverless passenger service across four categories: market entry, screening and approval, human-operator restrictions, and other operational restrictions.</p>
          </details>
          <details>
            <summary>How is the index calculated?</summary>
            <p>Each documented restriction receives a base score and scope adjustment,where appropriate. Adjusted measures are summed across the four categories and capped at 1. Missing evidence is classified as Unclassified, never as zero.</p>
          </details>
          <details>
            <summary>What is excluded from scoring?</summary>
            <p>Proposed bills, voluntary guidance, operator announcements, observed market availability, unsupported enforcement practices, and safety outcomes do not determine a jurisdiction’s index result.</p>
          </details>
          <details>
            <summary>How does this complement the primer?</summary>
            <p>The primer provides the broader policy view. The dashboard exposes and supports the underlying classifications, calculations, operational market records, coding status, and primary sources.</p>
          </details>
        </div>''',
        unsafe_allow_html=True,
    )

st.markdown('''
<section class="avat-research-overview">
  <div class="avat-overview-marker">01</div>
  <div class="avat-overview-kicker">WHY IT MATTERS</div>
  <h2>Access, safety, and regulation across the United States</h2>
  <p>The tracker combines operational market data, reported safety findings, and state and federal policy conditions in one source-linked research interface.</p>
  <div class="avat-overview-grid">
    <div class="avat-overview-card"><div class="avat-card-label">ACCESS</div><div class="avat-card-title">Consumer access</div><div class="avat-card-description">See which operators, markets, and states are currently represented in the dataset.</div><a class="avat-card-arrow" href="#markets">↗</a></div>
    <div class="avat-overview-card"><div class="avat-card-label">EVIDENCE</div><div class="avat-card-title">Safety evidence</div><div class="avat-card-description">Review reported crash-reduction metrics together with their source, geography, and study period.</div><a class="avat-card-arrow" href="#safety">↗</a></div>
    <div class="avat-overview-card"><div class="avat-card-label">REGULATION</div><div class="avat-card-title">Policy conditions</div><div class="avat-card-description">Compare source-linked state and federal regulatory conditions shaping deployment.</div><a class="avat-card-arrow" href="#audit">↗</a></div>
  </div>
</section>
<section class="avat-consumer-choice-statement">
  <small>CONSUMER CHOICE</small>
  <p>Clear rules and credible evidence can help autonomous mobility reach more consumers while maintaining strong safety expectations.</p>
</section>
''', unsafe_allow_html=True)

st.markdown('<div id="index"></div>', unsafe_allow_html=True)
section_band("01 · STATE RESTRICTIVENESS", "What is the geographic coverage of the AV Access Tracker?", "The AV Access Tracker (AVAT) covers all 50 states and the District of Columbia. The map displays each classified state’s regulatory restrictiveness score for commercial driverless passenger service. Scores closer to 0 indicate fewer documented restrictions, while scores closer to 1 indicate a more restrictive or effectively closed framework. The District of Columbia is reported separately and excluded from formal state rankings.", "#22264E", "#FFFFFF", "#EE5C1F")

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

chart_heading("State AV Regulatory Restrictiveness — Geographic distribution", "Index from 0 (least restrictive) to 1 (most restrictive)", "The map compares documented statutory and administrative restrictions affecting commercial driverless passenger service. Mint indicates less restrictive regulation and brick red indicates more restrictive regulation; gray means unclassified, not zero.")

fig = px.choropleth(map_data, locations="state_code", locationmode="USA-states", scope="usa", color="restrictiveness_index",
    range_color=(0,1), color_continuous_scale=["#9BD8C7", "#F4B544", "#E95C1F", "#B9473A"],
    hover_name="state", custom_data=["index_display", "score_status"])
fig.update_traces(hovertemplate="<b>%{hovertext}</b><br>Index: <b>%{customdata[0]}</b><br>Status: %{customdata[1]}<extra></extra>")
fig.update_layout(height=570, margin=dict(l=0,r=0,t=20,b=0), paper_bgcolor="rgba(0,0,0,0)", font_family="Montserrat", dragmode="pan", uirevision="bounded-us-map", hoverlabel=dict(bgcolor="white", bordercolor="#D8DEE8", font=dict(family="Montserrat", size=12, color="#22264E"), align="left"), coloraxis_colorbar=dict(title="Restrictiveness<br>(0–1 index)", tickvals=[0,.25,.5,.75,1], ticktext=["Least restrictive","Lower","Moderate","Higher","Most restrictive"]))
st.plotly_chart(fig, width="stretch", config={"displayModeBar":False, "scrollZoom":True, "doubleClick":"reset"})
st.caption("Drag to reposition the map and use a mouse wheel or trackpad to zoom. Double-click to reset the full U.S. view. Select a jurisdiction in the State Explorer for the complete source-linked record. The District of Columbia is excluded from formal state rankings.")
chart_source("Consumer Choice Center, AV Access Tracker state legal coding and linked official state sources, 2026.")

bar = ranked.sort_values("restrictiveness_index", ascending=False)
chart_heading("State AV Regulatory Restrictiveness", "Index from 0 (least restrictive) to 1 (most restrictive)", "Bars rank classified states by the combined index. The chart measures documented legal restrictiveness; it is not a safety score, service-quality rating, or overall grade.")
fig = px.bar(bar, x="state", y="restrictiveness_index", color="restrictiveness_index", range_color=(0,1),
    color_continuous_scale=["#9BD8C7", "#F4B544", "#E95C1F", "#B9473A"], custom_data=["score_status"])
fig.update_traces(hovertemplate="<b>%{x}</b><br>Index: <b>%{y:.2f}</b><br>Status: %{customdata[0]}<extra></extra>")
fig.update_layout(height=480, showlegend=False, coloraxis_showscale=False, xaxis_title="", yaxis_title="Restrictiveness index", yaxis_range=[0,1], margin=dict(l=10,r=10,t=25,b=100), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="white", font_family="Montserrat", hoverlabel=dict(bgcolor="white", bordercolor="#D8DEE8", font=dict(family="Montserrat", size=12, color="#22264E"), align="left"))
fig.update_xaxes(tickangle=-55); fig.update_yaxes(gridcolor="#E7ECF4")
st.plotly_chart(fig, width="stretch", config={"displayModeBar":False})
chart_source("Consumer Choice Center, AV Access Tracker state legal coding and linked official state sources, 2026.")

with st.expander("View component analysis by jurisdiction"):
    category_cols = ["Market-entry restrictions", "Screening and approval", "Human-operator restrictions", "Other operational restrictions"]
    display = view[["state","state_code","jurisdiction_type","restrictiveness_index","score_status",*category_cols,"policy_summary","source_url"]].sort_values("restrictiveness_index", ascending=False, na_position="last")
    st.dataframe(display, hide_index=True, width="stretch", column_config={"restrictiveness_index":st.column_config.NumberColumn("Index",format="%.2f"),"source_url":st.column_config.LinkColumn("Primary source")})

st.markdown('<div id="markets"></div>', unsafe_allow_html=True)
section_band("02 · CONSUMER ACCESS", "Public AV access remains geographically concentrated", "Commercial autonomous-vehicle activity is expanding, but verified public robotaxi access remains concentrated in a relatively small group of markets and states. Track where autonomous passenger and freight services are publically reported across the United States. Operational market records are reported separately from legal restrictiveness.", "#22264E", "#FFFFFF", "#EE5C1F")

public = markets[(markets.public_access.eq("Yes")) & (markets.service_status.eq("Commercial"))].copy()
with st.container(key="access_metrics"):
    m1,m2,m3,m4 = st.columns(4)
    m1.metric("Markets shown", markets.market.nunique())
    m2.metric("Operators", markets.operator.nunique())
    m3.metric("States represented", markets.state.nunique())
    m4.metric("Publicly accessible", public.market.nunique())

operator_totals = (markets.groupby("operator", as_index=False)["market"].nunique().rename(columns={"market":"markets"}).sort_values("markets", ascending=True))
state_totals = (markets.groupby(["state", "state_code"], as_index=False)["market"].nunique().rename(columns={"market":"markets"}))
access_left, access_right = st.columns([1, 1.25], gap="large")
with access_left:
    chart_heading("Markets currently recorded for each operator", "Number of unique markets in the research dataset", "The bars summarize the tracker’s current market coverage. They do not measure fleet size, rides, revenue, ridership, or market share.")
    operator_fig = px.bar(operator_totals, x="markets", y="operator", orientation="h", color="operator", text="markets", color_discrete_sequence=["#EE5C1F", "#22264E", "#63BFA8", "#F4B544"])
    operator_fig.update_traces(hovertemplate="<b>%{y}</b><br>Markets recorded: %{x}<extra></extra>", textposition="outside")
    operator_fig.update_layout(height=380, showlegend=False, xaxis_title="Unique markets in dataset", yaxis_title="", margin=dict(l=5,r=35,t=10,b=45), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="white", font_family="Montserrat")
    operator_fig.update_xaxes(dtick=1, gridcolor="#E7ECF4")
    st.plotly_chart(operator_fig, width="stretch", config={"displayModeBar":False})
    chart_source("Consumer Choice Center, AV Access Tracker market records and linked operator sources, 2026.")
with access_right:
    chart_heading("Consumer Access Snapshot", "Unique recorded markets by state", "Darker states contain more distinct passenger or freight markets in the tracker. Legal authorization alone does not count as an operating market.")
    access_fig = px.choropleth(state_totals, locations="state_code", locationmode="USA-states", scope="usa", color="markets", hover_name="state", color_continuous_scale=["#DDF3ED", "#63BFA8", "#147B86", "#22264E"], custom_data=["markets"])
    access_fig.update_traces(hovertemplate="<b>%{hovertext}</b><br>Markets recorded: %{customdata[0]}<extra></extra>")
    access_fig.update_layout(height=380, margin=dict(l=0,r=0,t=10,b=0), paper_bgcolor="rgba(0,0,0,0)", font_family="Montserrat", dragmode="pan", coloraxis_colorbar=dict(title="Markets"))
    st.plotly_chart(access_fig, width="stretch", config={"displayModeBar":False, "scrollZoom":True, "doubleClick":"reset"})
    chart_source("Consumer Choice Center, AV Access Tracker market records and linked operator sources, 2026.")

st.caption("Bar height represents unique markets in this dataset, not ridership, fleet size, revenue, or market share. Operator totals describe dashboard research coverage and do not indicate vehicles or rides.")
with st.expander("View active AV market records and sources"):
    st.dataframe(markets, hide_index=True, width="stretch", column_config={"source_url":st.column_config.LinkColumn("Source")})

state_explorer_slot = st.container()

st.markdown('<div id="safety"></div>', unsafe_allow_html=True)
section_band("04 · SAFETY SNAPSHOT", "Reported safety evidence", "Reported crash reductions compared with human-driver benchmarks in comparable operating areas and driving exposure. Operator-reported findings are presented with their study period, geography, and source and are not used in state scores.", "#22264E", "#FFFFFF", "#EE5C1F")
safety_plot = safety.copy()
safety_plot["value"] = pd.to_numeric(safety_plot["value"], errors="coerce")
safety_plot = safety_plot.dropna(subset=["value"]).sort_values("value")
chart_heading("Reported crash reductions relative to human-driver benchmarks", "Percent fewer reported crashes in comparable operating areas and exposure", "Each bar reproduces the direction and magnitude recorded in the underlying study. Results are source-, period-, geography-, and comparison-group specific and should not be generalized to every autonomous system.")
safety_metrics_ordered = safety_plot.sort_values("value", ascending=False)["metric"].astype(str).tolist()
safety_palette = ["#22264E", "#174A6B", "#4A78A8", "#9DC3D3", "#B8D2DF", "#D8E8EF"]
safety_color_map = {metric: safety_palette[index % len(safety_palette)] for index, metric in enumerate(safety_metrics_ordered)}
safety_fig = px.bar(
    safety_plot,
    x="value",
    y="metric",
    orientation="h",
    color="metric",
    color_discrete_map=safety_color_map,
    category_orders={"metric": safety_plot["metric"].astype(str).tolist()},
    text="value",
    custom_data=["source", "study_period", "geography"],
)
safety_fig.update_traces(texttemplate="%{x:.0f}% fewer", textposition="inside", hovertemplate="<b>%{y}</b><br>%{x:.0f}% fewer<br>Source: %{customdata[0]}<br>Period: %{customdata[1]}<br>Geography: %{customdata[2]}<extra></extra>")
for trace in safety_fig.data:
    trace.textfont.color = "#FFFFFF" if safety_color_map.get(str(trace.name)) in {"#22264E", "#174A6B", "#4A78A8"} else "#22264E"
safety_fig.update_layout(height=390, showlegend=False, xaxis_title="Reported reduction relative to benchmark", yaxis_title="", xaxis_range=[0,100], margin=dict(l=10,r=20,t=15,b=45), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="white", font_family="Montserrat", bargap=.18)
safety_fig.update_xaxes(ticksuffix="%", gridcolor="#E7ECF4")
st.plotly_chart(safety_fig, width="stretch", config={"displayModeBar":False})
chart_source("Consumer Choice Center compilation of the linked operator and research studies shown below, 2026.")
with st.expander("View safety study details and source links"):
    st.dataframe(safety, hide_index=True, width="stretch", column_config={"source_url":st.column_config.LinkColumn("Source")})

st.markdown('<div id="federal"></div>', unsafe_allow_html=True)
section_band("05 · FEDERAL POLICY", "Key federal bottlenecks", "Federal standards and institutions shape vehicle design, exemptions, freight, transit, infrastructure, and communications. These records are research and advocacy materials reported separately from state restrictiveness scores.", "#22264E", "#FFFFFF", "#EE5C1F")
st.markdown('''<style>
.federal-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:1rem;margin:1rem 0 2rem}.federal-card{padding:1.2rem;border-top:.32rem solid #EE5C1F;background:#F2F4FA;border-radius:.8rem;min-height:11rem}.federal-card h4{color:#22264E;margin:.2rem 0 .55rem}.federal-card p{color:#596489;font-size:.92rem;line-height:1.5}@media(max-width:900px){.federal-grid{grid-template-columns:repeat(2,1fr)}}
</style>
<div class="federal-grid">
<div class="federal-card"><h4>Outdated vehicle standards</h4><p>Some federal standards were written for conventional vehicles with steering wheels, pedals, mirrors, and human drivers.</p></div>
<div class="federal-card"><h4>Limited exemption pathway</h4><p>Purpose-built autonomous vehicles may need temporary exemptions while permanent safety standards are updated.</p></div>
<div class="federal-card"><h4>Fragmented authority</h4><p>Passenger vehicles, freight, infrastructure, transit, and communications fall under different federal institutions.</p></div>
<div class="federal-card"><h4>No unified national framework</h4><p>Federal rules, agency guidance, state laws, and testing programs do not yet operate as one consistent framework.</p></div>
</div>''', unsafe_allow_html=True)

st.markdown('<div id="method"></div>', unsafe_allow_html=True)
section_band("06 · METHODOLOGY", "Transparent measure-level scoring", "The structure is adapted from the OECD FDI Regulatory Restrictiveness Index: observed legal restrictions receive a base score, are adjusted for their scope, and are summed to a maximum of 1.00. CCC’s AV classifications and results are independent and do not represent OECD findings.", "#22264E", "#FFFFFF", "#EE5C1F")
st.markdown('''<style>
.st-key-formula_panel, .st-key-included_panel, .st-key-memo_panel {
    border-radius: 1rem;
    padding: 1.15rem 1.25rem;
}
.st-key-formula_panel { background: #F2F4FA; border-left: .38rem solid #22264E; }
.st-key-included_panel { background: #F0FAF7; border-left: .35rem solid #63BFA8; }
.st-key-memo_panel { background: #FFF7EE; border-left: .35rem solid #F4B544; }
.method-label { color:#111111; font-weight:800; letter-spacing:.08em; font-size:.78rem; }
</style>''', unsafe_allow_html=True)
with st.container(key="formula_panel"):
    st.markdown('<div class="method-label">INDEX CONSTRUCTION</div><h3>Formula</h3>', unsafe_allow_html=True)
    st.latex(r"AVA_j = \min\left(1,\ \sum_i b_i \times s_i\right)")
    st.markdown("Where $b_i$ is the published base score for restriction $i$ and $s_i$ is the activity-scope factor. Missing evidence produces **Unclassified**, never 0.")

st.markdown("### Technical scoring tables")
st.write("The **scoring framework** assigns a published base value to each documented restriction. **Scope factors** adjust that value according to how broadly the measure applies to the relevant commercial activity.")
with st.expander("View scoring framework and scope factors"):
    left,right = st.columns([1.35,1])
    with left:
        st.markdown("#### Scoring framework")
        st.caption("Base scores assigned to documented legal conditions in each policy category.")
        st.dataframe(rules, hide_index=True, width="stretch", column_config={"base_score":st.column_config.NumberColumn("Base score",format="%.3f")})
    with right:
        st.markdown("#### Scope factors")
        st.caption("Multipliers reflecting the estimated share of relevant activity affected by a restriction.")
        st.dataframe(scope, hide_index=True, width="stretch", column_config={"scope_factor":st.column_config.NumberColumn("Factor",format="%.2f")})
    chart_source("Consumer Choice Center AVAT scoring framework, adapted from OECD composite-indicator and FDI restrictiveness methods, 2026.")

st.markdown("### What is and is not scored")
a,b = st.columns(2)
with a:
    with st.container(key="included_panel"):
        st.markdown("**Included in the index**\n- Enacted restrictions governing commercial driverless passenger service\n- AV-specific approvals and human-operator mandates\n- Local operating restrictions where legally authorized\n- AV financial requirements above comparable rideshare requirements")
with b:
    with st.container(key="memo_panel"):
        st.markdown("**Memorandum items only**\n- Proposed bills and advisory councils\n- Ordinary registration and traffic rules\n- Company announcements and voluntary guidance\n- Testing-only insurance when scoring commercial service")

state_explorer_slot.__enter__()
st.markdown('<div id="audit"></div>', unsafe_allow_html=True)
section_band("03 · STATE EXPLORER", "Where autonomous vehicle services are operating today", "Some states align with every regulatory criterion currently measured while still lacking a verified public robotaxi service in the market tracker. Filter by operator, state, or service status to see which markets are currently included in the tracker. Scores run from 0.00 (least restrictive) to 1.00 (most restrictive); missing evidence remains unclassified.", "#22264E", "#FFFFFF", "#EE5C1F")

if "selected_jurisdiction" not in st.session_state:
    st.session_state.selected_jurisdiction = None

button_states = states.sort_values("state").reset_index(drop=True)
map_colors = ["#9BD8C7", "#F4B544", "#E95C1F", "#B9473A"]
map_colorscale = [[0.0, map_colors[0]], [1 / 3, map_colors[1]], [2 / 3, map_colors[2]], [1.0, map_colors[3]]]
state_button_styles = []
for _, jurisdiction in button_states.iterrows():
    code = html.escape(str(jurisdiction.state_code))
    score = pd.to_numeric(jurisdiction.restrictiveness_index, errors="coerce")
    if pd.isna(score):
        background = "#E7ECF4"
        foreground = "#343A4F"
    else:
        background = sample_colorscale(map_colorscale, [float(score)])[0]
        foreground = "#FFFFFF" if float(score) >= 0.56 else "#22264E"
    selected_border = "#22264E" if st.session_state.selected_jurisdiction == jurisdiction.state else background
    selected_shadow = "0 0 0 3px rgba(34,38,78,.18)" if st.session_state.selected_jurisdiction == jurisdiction.state else "none"
    state_button_styles.append(
        f"""
        .st-key-jurisdiction_{code} button {{
            min-height: 4.1rem !important;
            background: {background} !important;
            border: 2px solid {selected_border} !important;
            color: {foreground} !important;
            box-shadow: {selected_shadow} !important;
            font-weight: 800 !important;
        }}
        .st-key-jurisdiction_{code} button p {{
            color: {foreground} !important;
            font-size: 1.02rem !important;
            font-weight: 800 !important;
        }}
        .st-key-jurisdiction_{code} button:hover {{
            filter: brightness(.96);
            transform: translateY(-1px);
        }}
        """
    )

st.markdown(
    "<style>" + "".join(state_button_styles) + """
    .state-detail-top > div:first-child > span {
        display: inline-block;
        font-size: clamp(1.6rem, 2.2vw, 2rem) !important;
        font-weight: 900 !important;
        letter-spacing: .08em;
        margin-bottom: .5rem;
    }
    .state-detail-top > div:first-child > h3 {
        font-size: clamp(3rem, 5vw, 4.75rem) !important;
        line-height: 1 !important;
        letter-spacing: -.035em !important;
        font-family: Montserrat, sans-serif !important;
        font-weight: 850 !important;
        margin: 0 !important;
    }
    .state-detail .state-tags span {
        font-size: 1rem !important;
        padding: .55rem .9rem !important;
    }
    .state-detail > p {
        font-size: clamp(1.1rem, 1.5vw, 1.3rem) !important;
        line-height: 1.65 !important;
    }
    .state-detail > a {
        font-size: 1.12rem !important;
        font-weight: 800 !important;
    }
    .state-detail .state-score small {
        font-size: .9rem !important;
    }
    </style>""",
    unsafe_allow_html=True,
)

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
    summary = str(state_row.policy_summary)
    status = html.escape(str(state_row.score_status))
    st.markdown('''<style>
    .st-key-state_profile{padding:clamp(1.5rem,3vw,2.75rem)!important;background:#EAF4FA!important;border-left:.55rem solid #147B86!important;border-radius:.8rem!important}
    .st-key-state_profile h1{font-family:Montserrat,sans-serif!important;font-size:clamp(3.5rem,6vw,5.75rem)!important;line-height:.95!important;letter-spacing:-.045em!important;font-weight:900!important;color:#22264E!important;margin:.2rem 0 1rem!important}
    .st-key-state_profile h3{font-size:1.65rem!important;letter-spacing:.12em!important;color:#147B86!important;margin:0!important}
    .st-key-state_profile p{font-size:clamp(1.1rem,1.5vw,1.3rem)!important;line-height:1.65!important;color:#4E5D7D!important}
    </style>''', unsafe_allow_html=True)
    with st.container(key="state_profile", border=True):
        profile_left, profile_right = st.columns([1.4, .6], vertical_alignment="top")
        with profile_left:
            st.markdown(f"### {html.escape(str(state_row.state_code))}")
            st.title(selected)
        with profile_right:
            st.metric("Restrictiveness index", score_label)
        st.markdown(f"**{pathway}** &nbsp; · &nbsp; **{status}** &nbsp; · &nbsp; **{html.escape(str(state_row.jurisdiction_type))}**", unsafe_allow_html=True)
        st.write(summary)
        if isinstance(state_row.source_url, str) and state_row.source_url.startswith("http"):
            st.link_button("Open primary source ↗", state_row.source_url)
    st.markdown("#### Policy conditions")
    commercial_label = binary_label(state_row.commercial_operation_allowed, "Allowed", "No pathway")
    testing_label = binary_label(state_row.driverless_testing_allowed, "Allowed", "Not identified")
    operator_label = binary_label(state_row.human_operator_required, "Required", "Not required")
    permit_label = binary_label(state_row.special_permit_required, "Required", "Not required")
    local_rule_label = binary_label(state_row.local_rules_allowed, "Allowed", "Limited / pre-empted")
    statewide_label = binary_label(state_row.statewide_rules, "Yes", "No comprehensive framework")
    insurance_value = pd.to_numeric(state_row.insurance_minimum, errors="coerce")
    insurance_label = "None recorded" if pd.isna(insurance_value) or insurance_value == 0 else f"${insurance_value:,.0f}"
    st.markdown(
        f'''<div class="state-extra-grid">
          <div><small>COMMERCIAL OPERATION</small><b>{commercial_label}</b></div>
          <div><small>DRIVERLESS TESTING</small><b>{testing_label}</b></div>
          <div><small>HUMAN OPERATOR</small><b>{operator_label}</b></div>
          <div><small>SPECIAL PERMIT</small><b>{permit_label}</b></div>
          <div><small>STATEWIDE FRAMEWORK</small><b>{statewide_label}</b></div>
          <div><small>SEPARATE LOCAL AV RULES</small><b>{local_rule_label}</b></div>
          <div><small>INSURANCE MINIMUM</small><b>{insurance_label}</b></div>
          <div><small>RESEARCH STATUS</small><b>{html.escape(str(state_row.research_status))}</b></div>
          <div><small>REGION</small><b>{html.escape(str(state_row.region))}</b></div>
          <div><small>LAST VERIFIED</small><b>{html.escape(str(state_row.last_verified))}</b></div>
        </div>
        <style>
        .state-extra-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:.8rem;margin:1rem 0 1.5rem}}
        .state-extra-grid>div{{padding:1rem;background:#F2F4FA;border-top:.25rem solid #63BFA8;border-radius:.55rem}}
        .state-extra-grid small{{display:block;color:#6A7395;font-size:.72rem;font-weight:800;letter-spacing:.08em;margin-bottom:.35rem}}
        .state-extra-grid b{{color:#22264E;font-size:1.05rem;line-height:1.25}}@media(max-width:800px){{.state-extra-grid{{grid-template-columns:1fr 1fr}}}}
        </style>''',
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
state_explorer_slot.__exit__(None, None, None)

st.markdown('<div id="recommendations"></div>', unsafe_allow_html=True)
st.markdown('''<style>
.st-key-recommendations_panel{margin:4rem 0 3rem;padding:clamp(1.5rem,3.5vw,3rem);border:none;border-top:.45rem solid #F4B544;border-radius:.45rem;background:#22264E;box-shadow:0 10px 26px rgba(34,38,78,.14)}
.rec-kicker{color:#EE5C1F;font-weight:850;letter-spacing:.11em;font-size:.82rem;margin-bottom:1.7rem}.rec-title{color:#FFFFFF;font-size:clamp(2.4rem,5vw,4.5rem);font-weight:850;line-height:1;margin-bottom:1.4rem}.rec-copy{color:#FFFFFF!important;font-size:1.05rem;line-height:1.65;margin:0 0 1.2rem}.rec-note{background:#EAF4FA;color:#147B86;padding:1rem 1.1rem;border-radius:.65rem;font-weight:650;line-height:1.55}
.st-key-rec_1,.st-key-rec_2,.st-key-rec_3,.st-key-rec_4{padding:.85rem 1rem!important;margin-bottom:.65rem;box-shadow:0 5px 14px rgba(34,38,78,.06)}
.st-key-rec_1,.st-key-rec_2,.st-key-rec_3,.st-key-rec_4{background:#FFF7F1!important;border-left:.42rem solid #EE5C1F!important}
</style>''', unsafe_allow_html=True)
with st.container(key="recommendations_panel"):
    rec_intro, rec_list = st.columns([0.85, 1.35], gap="large", vertical_alignment="top")
    with rec_intro:
        st.markdown('''<div class="rec-kicker">07 · POLICY RECOMMENDATIONS</div>
        <div class="rec-title">What should change?</div>
        <p class="rec-copy">States and federal agencies can expand consumer access by making approval pathways clear, proportionate, and predictable while retaining generally applicable safety rules.</p>
        <div class="rec-note">These are Consumer Choice Center recommendations drawn from the accompanying primer. They are separate from the legal index and do not affect any jurisdiction’s score.</div>''', unsafe_allow_html=True)
    with rec_list:
        recommendations = [
            ("Modernize federal vehicle standards", "Update design rules and exemption pathways so purpose-built driverless vehicles can be evaluated at commercially meaningful scale."),
            ("Create clear statewide commercial pathways", "Use uniform state rules for deployment and avoid duplicative local permits, fees, and operating approvals."),
            ("Use evidence-building regulatory sandboxes", "Allow controlled deployment with defined reporting, review periods, and an explicit route from pilot operation to commercial service."),
            ("Keep insurance, liability, and fees technology-neutral", "Apply requirements proportionate to comparable passenger services and avoid AV-specific costs unsupported by documented risk."),
        ]
        for number, (title, description) in enumerate(recommendations, start=1):
            with st.container(key=f"rec_{number}", border=True):
                st.markdown(f"### {number}. {title}")
                st.write(description)

st.markdown("""
<div class="method-note"><b>Method sources</b><br>
OECD (2024), <i>OECD FDI Regulatory Restrictiveness Index: Methodology and policy applications</i>.<br>
OECD & European Commission, Joint Research Centre (2008), <i>Handbook on Constructing Composite Indicators: Methodology and User Guide</i>.<br><br>
The dashboard complements the autonomous-vehicle primer; it is not a reproduction of any operator dashboard and does not assess vehicle safety performance.
</div><footer>CONSUMER CHOICE CENTER <span>Autonomous Vehicle Access Tracker · Research release</span></footer>
""", unsafe_allow_html=True)
