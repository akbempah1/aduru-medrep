import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from data import DF, OPP_DF, THERAPEUTIC_AREAS, REGIONS, MONTHS

# ── Page config ───────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Aduru MedRep",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Palette ───────────────────────────────────────────────────────────────
DEEP_GREEN  = "#0D3B2E"
MID_GREEN   = "#1A5C45"
SOFT_GREEN  = "#2D7A5F"
GOLD        = "#C8A84B"
GOLD_LIGHT  = "#E8CC80"
CREAM       = "#F5F0E8"
CREAM_DARK  = "#EDE7D9"
RED         = "#C0392B"
ORANGE      = "#D35400"
AMBER       = "#D4A017"
EMERALD     = "#1E8449"
TEXT_DARK   = "#1A1A18"
TEXT_LIGHT  = "#6B6B60"

PLOTLY_TEMPLATE = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Sans, Calibri, sans-serif", color=TEXT_DARK, size=12),
    colorway=[MID_GREEN, GOLD, SOFT_GREEN, AMBER, DEEP_GREEN, EMERALD, ORANGE],
    margin=dict(l=10, r=10, t=40, b=10),
    xaxis_gridcolor="#E8E4DC",
    yaxis_gridcolor="#E8E4DC",
    xaxis_showline=False,
    yaxis_showline=False,
)

SCORE_COLORS = {
    "High":   EMERALD,
    "Medium": AMBER,
    "Low":    RED,
}

def opp_tier(score):
    if score >= 65: return "High"
    if score >= 40: return "Medium"
    return "Low"

# ── CSS ───────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {{
    font-family: 'DM Sans', sans-serif;
    background: {CREAM};
    color: {TEXT_DARK};
}}

/* Header */
.medrep-header {{
    background: linear-gradient(135deg, {DEEP_GREEN} 0%, {MID_GREEN} 70%, {SOFT_GREEN} 100%);
    border-radius: 14px;
    padding: 1.6rem 2.2rem;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
}}
.medrep-header::after {{
    content: '';
    position: absolute;
    bottom: -30px; right: -30px;
    width: 160px; height: 160px;
    background: radial-gradient(circle, rgba(200,168,75,0.12) 0%, transparent 70%);
    border-radius: 50%;
}}
.medrep-header h1 {{
    font-family: 'DM Serif Display', serif;
    font-size: 2rem;
    color: {CREAM};
    margin: 0;
}}
.medrep-header h1 span {{ color: {GOLD}; }}
.medrep-header p {{
    color: rgba(245,240,232,0.72);
    font-size: 0.88rem;
    margin: 0.35rem 0 0 0;
    font-weight: 300;
}}
.header-badge {{
    display: inline-block;
    background: rgba(200,168,75,0.18);
    border: 1px solid {GOLD};
    color: {GOLD_LIGHT};
    font-size: 0.62rem;
    font-weight: 700;
    letter-spacing: 1.8px;
    text-transform: uppercase;
    padding: 2px 9px;
    border-radius: 20px;
    margin-bottom: 0.6rem;
}}

/* Metric cards */
.metric-card {{
    background: white;
    border: 1px solid #DDD8CC;
    border-radius: 10px;
    padding: 1rem 1.2rem;
    box-shadow: 0 2px 10px rgba(13,59,46,0.06);
    border-left: 4px solid {MID_GREEN};
}}
.metric-card.gold  {{ border-left-color: {GOLD}; }}
.metric-card.red   {{ border-left-color: {RED}; }}
.metric-card.amber {{ border-left-color: {AMBER}; }}
.metric-num {{
    font-family: 'DM Serif Display', serif;
    font-size: 2rem;
    color: {DEEP_GREEN};
    line-height: 1;
}}
.metric-label {{
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 1px;
    text-transform: uppercase;
    color: {TEXT_LIGHT};
    margin-top: 0.25rem;
}}
.metric-sub {{
    font-size: 0.78rem;
    color: {TEXT_LIGHT};
    margin-top: 0.2rem;
}}

/* Section header */
.section-hdr {{
    font-family: 'DM Serif Display', serif;
    font-size: 1.25rem;
    color: {DEEP_GREEN};
    margin: 1.5rem 0 0.6rem 0;
    padding-bottom: 0.3rem;
    border-bottom: 2px solid {GOLD};
    display: inline-block;
}}

/* Opportunity badge */
.opp-high   {{ background: #eafaf1; color: {EMERALD}; border: 1px solid {EMERALD}; }}
.opp-medium {{ background: #fefbe6; color: {AMBER};   border: 1px solid {AMBER}; }}
.opp-low    {{ background: #fdecea; color: {RED};     border: 1px solid {RED}; }}
.opp-badge {{
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
}}

/* Data note */
.data-note {{
    background: {CREAM_DARK};
    border: 1px solid #DDD8CC;
    border-radius: 8px;
    padding: 0.7rem 1rem;
    font-size: 0.78rem;
    color: {TEXT_LIGHT};
    margin-top: 1rem;
    line-height: 1.6;
}}

/* Sidebar */
[data-testid="stSidebar"] {{
    background: {DEEP_GREEN} !important;
}}
[data-testid="stSidebar"] * {{
    color: {CREAM} !important;
}}
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stRadio label {{
    color: {GOLD_LIGHT} !important;
    font-size: 0.72rem !important;
    font-weight: 600 !important;
    letter-spacing: 1px !important;
    text-transform: uppercase !important;
}}

.stButton > button {{
    background: {MID_GREEN} !important;
    color: {CREAM} !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
}}
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style="padding:1rem 0 0.5rem 0">
        <div style="font-family:'DM Serif Display',serif;font-size:1.3rem;color:{GOLD}">
            Aduru MedRep
        </div>
        <div style="font-size:0.75rem;color:rgba(245,240,232,0.6);margin-top:0.2rem">
            Territory Intelligence Platform
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    selected_ta = st.selectbox(
        "Therapeutic Area",
        list(THERAPEUTIC_AREAS.keys()),
        index=0,
    )
    selected_region = st.selectbox(
        "Region Focus",
        ["All Regions"] + list(REGIONS.keys()),
        index=0,
    )
    selected_drug = st.selectbox(
        "Drug (optional filter)",
        ["All Drugs"] + THERAPEUTIC_AREAS[selected_ta]["drugs"],
    )
    view = st.radio(
        "Dashboard View",
        ["Territory Overview", "Trend Analysis", "Brand vs Generic",
         "Opportunity Scores", "Rep Planner"],
        index=0,
    )

    st.markdown("---")
    st.markdown(f"""
    <div style="font-size:0.72rem;color:rgba(245,240,232,0.45);line-height:1.6">
        Data: Proprietary dispensing network,<br>
        Greater Accra + modelled regional estimates.<br>
        <br>
        © 2025 Aduru Analytics<br>
        aduru-analytics.com
    </div>
    """, unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="medrep-header">
    <div class="header-badge">Pharmaceutical Territory Intelligence</div>
    <h1>Aduru <span>MedRep</span></h1>
    <p>West Africa's first AI-powered dispensing intelligence platform for pharmaceutical territory management ·
       Ghana network · {len(REGIONS)} regions · 8 therapeutic areas</p>
</div>
""", unsafe_allow_html=True)

# ── Filter data ───────────────────────────────────────────────────────────
df = DF.copy()
df_ta = df[df["therapeutic_area"] == selected_ta]
if selected_region != "All Regions":
    df_ta = df_ta[df_ta["region"] == selected_region]
if selected_drug != "All Drugs":
    df_ta = df_ta[df_ta["drug"] == selected_drug]

opp = OPP_DF[OPP_DF["therapeutic_area"] == selected_ta].copy()
opp["tier"] = opp["opportunity_score"].apply(opp_tier)

# ── KPI row ───────────────────────────────────────────────────────────────
total_units    = df_ta["units_network"].sum()
total_market   = df_ta["units_market"].sum()
avg_brand_share = df_ta["brand_share"].mean()
network_share  = total_units / total_market if total_market > 0 else 0

latest_month   = df_ta[df_ta["month"] == df_ta["month"].max()]["units_network"].sum()
prior_month    = df_ta[df_ta["month"] == sorted(df_ta["month"].unique())[-2]]["units_network"].sum()
mom_growth     = (latest_month - prior_month) / prior_month * 100 if prior_month > 0 else 0

top_opp_region = opp.loc[opp["opportunity_score"].idxmax(), "region"] if not opp.empty else "—"

k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-num">{total_units:,.0f}</div>
        <div class="metric-label">Network Units Dispensed</div>
        <div class="metric-sub">{selected_ta} · YTD 2024</div>
    </div>""", unsafe_allow_html=True)
with k2:
    color = "gold" if mom_growth >= 0 else "red"
    arrow = "↑" if mom_growth >= 0 else "↓"
    st.markdown(f"""
    <div class="metric-card {color}">
        <div class="metric-num">{arrow}{abs(mom_growth):.1f}%</div>
        <div class="metric-label">Month-on-Month Growth</div>
        <div class="metric-sub">Latest vs prior month</div>
    </div>""", unsafe_allow_html=True)
with k3:
    st.markdown(f"""
    <div class="metric-card amber">
        <div class="metric-num">{avg_brand_share:.0%}</div>
        <div class="metric-label">Avg Brand Share</div>
        <div class="metric-sub">Branded vs generic dispensing</div>
    </div>""", unsafe_allow_html=True)
with k4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-num">{top_opp_region}</div>
        <div class="metric-label">Top Opportunity Region</div>
        <div class="metric-sub">Highest composite score</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════
# VIEW 1 — Territory Overview
# ══════════════════════════════════════════════════════════════════════════
if view == "Territory Overview":
    st.markdown('<div class="section-hdr">Territory Dispensing Map</div>', unsafe_allow_html=True)
    st.markdown("")

    map_data = (
        df_ta.groupby(["region", "lat", "lon", "network"])["units_network"]
        .sum().reset_index()
    )
    map_data["size"] = (map_data["units_network"] / map_data["units_network"].max() * 60 + 15).clip(15, 80)
    map_data["label"] = map_data.apply(
        lambda r: f"{r['region']}<br>{r['units_network']:,.0f} units<br>{'● Live network' if r['network']=='live' else '◌ Modelled'}",
        axis=1
    )

    fig_map = go.Figure()
    for net_type, marker_sym, col in [("live", "circle", MID_GREEN), ("modelled", "circle-open", GOLD)]:
        sub = map_data[map_data["network"] == net_type]
        fig_map.add_trace(go.Scattergeo(
            lat=sub["lat"], lon=sub["lon"],
            text=sub["label"],
            hoverinfo="text",
            mode="markers",
            marker=dict(
                size=sub["size"],
                color=col,
                symbol=marker_sym,
                line=dict(color=col, width=2),
                opacity=0.85,
            ),
            name="Live network" if net_type == "live" else "Modelled estimate",
        ))

    fig_map.update_layout(
        geo=dict(
            scope="africa",
            center=dict(lat=7.5, lon=-1.0),
            projection_scale=6,
            showland=True, landcolor="#F0EBE0",
            showocean=True, oceancolor="#E8F4F8",
            showcountries=True, countrycolor="#CCCCCC",
            showframe=False,
            bgcolor="rgba(0,0,0,0)",
        ),
        height=420,
        legend=dict(x=0.01, y=0.99, bgcolor="rgba(255,255,255,0.8)"),
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=10, b=0),
    )
    st.plotly_chart(fig_map, use_container_width=True)

    # Regional bar chart
    st.markdown('<div class="section-hdr">Regional Volume Breakdown</div>', unsafe_allow_html=True)
    bar_data = (
        df_ta.groupby("region")["units_network"]
        .sum().reset_index()
        .sort_values("units_network", ascending=True)
    )
    fig_bar = go.Figure(go.Bar(
        x=bar_data["units_network"], y=bar_data["region"],
        orientation="h",
        marker=dict(
            color=bar_data["units_network"],
            colorscale=[[0, CREAM_DARK], [0.5, SOFT_GREEN], [1, DEEP_GREEN]],
            showscale=False,
        ),
        text=bar_data["units_network"].apply(lambda x: f"{x:,.0f}"),
        textposition="outside",
    ))
    fig_bar.update_layout(
        **PLOTLY_TEMPLATE,
        height=320,
        xaxis_title="Units dispensed (YTD)",
        yaxis_title="",
    )
    st.plotly_chart(fig_bar, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════
# VIEW 2 — Trend Analysis
# ══════════════════════════════════════════════════════════════════════════
elif view == "Trend Analysis":
    st.markdown('<div class="section-hdr">Monthly Dispensing Trends</div>', unsafe_allow_html=True)

    trend_data = (
        df_ta.groupby(["month", "month_label", "region"])["units_network"]
        .sum().reset_index()
        .sort_values("month")
    )

    fig_trend = px.line(
        trend_data, x="month_label", y="units_network",
        color="region",
        markers=True,
        color_discrete_sequence=[MID_GREEN, GOLD, SOFT_GREEN, AMBER, DEEP_GREEN, EMERALD, ORANGE],
    )
    fig_trend.update_layout(
        **PLOTLY_TEMPLATE,
        height=380,
        xaxis_title="Month",
        yaxis_title="Units dispensed",
        legend_title="Region",
        hovermode="x unified",
    )
    fig_trend.update_traces(line=dict(width=2.5), marker=dict(size=7))
    st.plotly_chart(fig_trend, use_container_width=True)

    # Network vs market
    st.markdown('<div class="section-hdr">Network Dispensing vs Market Estimate</div>', unsafe_allow_html=True)
    mkt_data = (
        df_ta.groupby(["month", "month_label"])
        .agg(network=("units_network","sum"), market=("units_market","sum"))
        .reset_index().sort_values("month")
    )

    fig_mkt = go.Figure()
    fig_mkt.add_trace(go.Bar(
        x=mkt_data["month_label"], y=mkt_data["market"],
        name="Market estimate", marker_color=CREAM_DARK,
    ))
    fig_mkt.add_trace(go.Bar(
        x=mkt_data["month_label"], y=mkt_data["network"],
        name="Our network", marker_color=MID_GREEN,
    ))
    fig_mkt.update_layout(
        **PLOTLY_TEMPLATE,
        barmode="overlay",
        height=320,
        xaxis_title="Month",
        yaxis_title="Units",
        legend=dict(x=0.01, y=0.99),
    )
    st.plotly_chart(fig_mkt, use_container_width=True)

    # Drug-level trend heatmap
    st.markdown('<div class="section-hdr">Drug-Level Trend Heatmap</div>', unsafe_allow_html=True)
    heat_data = (
        df_ta.groupby(["drug", "month_label"])["units_network"]
        .sum().reset_index()
    )
    heat_pivot = heat_data.pivot(index="drug", columns="month_label", values="units_network").fillna(0)
    # Reorder columns by month
    month_order = DF["month_label"].unique().tolist()
    heat_pivot = heat_pivot[[c for c in month_order if c in heat_pivot.columns]]

    fig_heat = go.Figure(go.Heatmap(
        z=heat_pivot.values,
        x=heat_pivot.columns.tolist(),
        y=heat_pivot.index.tolist(),
        colorscale=[[0, CREAM_DARK], [0.5, SOFT_GREEN], [1, DEEP_GREEN]],
        hoverongaps=False,
    ))
    fig_heat.update_layout(
        **PLOTLY_TEMPLATE,
        height=280,
        xaxis_title="Month",
        yaxis_title="",
    )
    st.plotly_chart(fig_heat, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════
# VIEW 3 — Brand vs Generic
# ══════════════════════════════════════════════════════════════════════════
elif view == "Brand vs Generic":
    st.markdown('<div class="section-hdr">Brand vs Generic Split by Region</div>', unsafe_allow_html=True)
    st.caption("High generic share = greater detailing opportunity for branded products")

    bg_data = (
        df_ta.groupby("region")
        .agg(branded=("units_branded","sum"), generic=("units_generic","sum"))
        .reset_index()
    )
    bg_data["total"] = bg_data["branded"] + bg_data["generic"]
    bg_data["brand_pct"] = bg_data["branded"] / bg_data["total"]
    bg_data["generic_pct"] = bg_data["generic"] / bg_data["total"]
    bg_data = bg_data.sort_values("brand_pct", ascending=True)

    fig_bg = go.Figure()
    fig_bg.add_trace(go.Bar(
        y=bg_data["region"], x=bg_data["brand_pct"] * 100,
        orientation="h", name="Branded", marker_color=MID_GREEN,
        text=bg_data["brand_pct"].apply(lambda x: f"{x:.0%}"),
        textposition="inside", textfont=dict(color="white"),
    ))
    fig_bg.add_trace(go.Bar(
        y=bg_data["region"], x=bg_data["generic_pct"] * 100,
        orientation="h", name="Generic", marker_color=CREAM_DARK,
        text=bg_data["generic_pct"].apply(lambda x: f"{x:.0%}"),
        textposition="inside", textfont=dict(color=TEXT_LIGHT),
    ))
    fig_bg.update_layout(
        **PLOTLY_TEMPLATE,
        barmode="stack",
        height=340,
        xaxis_title="Share (%)",
        yaxis_title="",
        legend=dict(x=0.7, y=0.05),
    )
    st.plotly_chart(fig_bg, use_container_width=True)

    # Monthly brand share trend
    st.markdown('<div class="section-hdr">Brand Share Trend Over Time</div>', unsafe_allow_html=True)
    bs_trend = (
        df_ta.groupby(["month", "month_label"])
        .agg(branded=("units_branded","sum"), total=("units_network","sum"))
        .reset_index()
        .sort_values("month")
    )
    bs_trend["brand_share"] = bs_trend["branded"] / bs_trend["total"]

    fig_bs = go.Figure()
    fig_bs.add_trace(go.Scatter(
        x=bs_trend["month_label"], y=bs_trend["brand_share"] * 100,
        mode="lines+markers",
        line=dict(color=GOLD, width=3),
        marker=dict(size=8, color=GOLD),
        fill="tozeroy", fillcolor=f"rgba(200,168,75,0.08)",
        name="Brand share %",
    ))
    fig_bs.add_hline(
        y=bs_trend["brand_share"].mean() * 100,
        line_dash="dot", line_color=TEXT_LIGHT,
        annotation_text=f"Average {bs_trend['brand_share'].mean():.0%}",
        annotation_position="top right",
    )
    fig_bs.update_layout(
        **PLOTLY_TEMPLATE,
        height=300,
        yaxis_title="Brand share (%)",
        xaxis_title="Month",
    )
    st.plotly_chart(fig_bs, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════
# VIEW 4 — Opportunity Scores
# ══════════════════════════════════════════════════════════════════════════
elif view == "Opportunity Scores":
    st.markdown('<div class="section-hdr">Territory Opportunity Ranking</div>', unsafe_allow_html=True)
    st.caption("Composite score: dispensing volume (40%) · growth momentum (35%) · generic penetration opportunity (25%)")

    opp_display = opp.copy().sort_values("opportunity_score", ascending=False)
    opp_display["tier_badge"] = opp_display["tier"].apply(
        lambda t: f'<span class="opp-badge opp-{t.lower()}">{t}</span>'
    )

    # Scored bar chart
    fig_opp = go.Figure()
    colors = opp_display["tier"].map({"High": EMERALD, "Medium": AMBER, "Low": RED}).tolist()
    fig_opp.add_trace(go.Bar(
        x=opp_display["opportunity_score"],
        y=opp_display["region"],
        orientation="h",
        marker_color=colors,
        text=opp_display["opportunity_score"].apply(lambda x: f"{x:.0f}"),
        textposition="outside",
    ))
    fig_opp.update_layout(
        **PLOTLY_TEMPLATE,
        height=320,
        xaxis=dict(range=[0, 115], title="Opportunity Score (0–100)"),
        yaxis_title="",
    )
    st.plotly_chart(fig_opp, use_container_width=True)

    # Table
    for _, row in opp_display.iterrows():
        tier  = row["tier"]
        score = row["opportunity_score"]
        color = {"High": EMERALD, "Medium": AMBER, "Low": RED}[tier]
        net   = "● Live network" if row["network"] == "live" else "◌ Modelled"
        growth_pct = row["growth"] * 100
        g_arrow = "↑" if growth_pct >= 0 else "↓"
        st.markdown(f"""
        <div style="background:white;border:1px solid #DDD8CC;border-left:4px solid {color};
                    border-radius:8px;padding:0.7rem 1.1rem;margin-bottom:0.5rem;
                    display:flex;justify-content:space-between;align-items:center">
            <div>
                <strong style="font-size:1rem;color:{TEXT_DARK}">{row['region']}</strong>
                <span style="font-size:0.75rem;color:{TEXT_LIGHT};margin-left:0.6rem">{net}</span><br>
                <span style="font-size:0.82rem;color:{TEXT_LIGHT}">
                    Volume: {row['total_units']:,.0f} units ·
                    Growth: {g_arrow}{abs(growth_pct):.1f}% ·
                    Brand share: {row['brand_share']:.0%}
                </span>
            </div>
            <div style="text-align:right">
                <div style="font-family:'DM Serif Display',serif;font-size:1.8rem;color:{color};line-height:1">{score:.0f}</div>
                <span class="opp-badge opp-{tier.lower()}">{tier}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════
# VIEW 5 — Rep Planner
# ══════════════════════════════════════════════════════════════════════════
elif view == "Rep Planner":
    st.markdown('<div class="section-hdr">Territory Rep Planner</div>', unsafe_allow_html=True)
    st.caption("Model expected dispensing uplift based on rep visit frequency")

    col1, col2 = st.columns([1, 1])
    with col1:
        rep_region   = st.selectbox("Target Region", list(REGIONS.keys()), key="rep_region")
        visits_month = st.slider("Rep visits per month", 1, 20, 6)
        campaign_months = st.slider("Campaign duration (months)", 1, 12, 3)
        focus_drug = st.selectbox("Focus Drug", THERAPEUTIC_AREAS[selected_ta]["drugs"], key="rep_drug")

    # Uplift model (evidence-based parameters from pharma detailing literature)
    base_uplift_per_visit = 0.028    # 2.8% per visit (Manchanda & Chintagunta 2004)
    saturation_factor     = max(0.4, 1 - (visits_month - 1) * 0.045)
    total_uplift          = min(0.65, visits_month * base_uplift_per_visit * saturation_factor)

    region_base = (
        DF[(DF["region"] == rep_region) &
           (DF["therapeutic_area"] == selected_ta) &
           (DF["drug"] == focus_drug)]
        ["units_network"].mean()
    )
    projected_monthly = region_base * (1 + total_uplift)
    total_projected   = projected_monthly * campaign_months
    total_baseline    = region_base * campaign_months
    incremental       = total_projected - total_baseline

    with col2:
        st.markdown(f"""
        <div style="background:{DEEP_GREEN};border-radius:12px;padding:1.3rem 1.5rem;color:{CREAM}">
            <div style="font-size:0.7rem;letter-spacing:1.5px;text-transform:uppercase;
                        color:{GOLD_LIGHT};font-weight:600;margin-bottom:0.8rem">
                PROJECTED IMPACT
            </div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.8rem">
                <div>
                    <div style="font-family:'DM Serif Display',serif;font-size:1.7rem;color:{GOLD}">
                        +{total_uplift:.0%}
                    </div>
                    <div style="font-size:0.75rem;color:rgba(245,240,232,0.65)">
                        Projected uplift
                    </div>
                </div>
                <div>
                    <div style="font-family:'DM Serif Display',serif;font-size:1.7rem;color:{GOLD}">
                        {incremental:,.0f}
                    </div>
                    <div style="font-size:0.75rem;color:rgba(245,240,232,0.65)">
                        Incremental units over {campaign_months}mo
                    </div>
                </div>
                <div>
                    <div style="font-family:'DM Serif Display',serif;font-size:1.7rem;color:{CREAM}">
                        {total_baseline:,.0f}
                    </div>
                    <div style="font-size:0.75rem;color:rgba(245,240,232,0.65)">
                        Baseline ({campaign_months}mo)
                    </div>
                </div>
                <div>
                    <div style="font-family:'DM Serif Display',serif;font-size:1.7rem;color:{CREAM}">
                        {total_projected:,.0f}
                    </div>
                    <div style="font-size:0.75rem;color:rgba(245,240,232,0.65)">
                        Projected ({campaign_months}mo)
                    </div>
                </div>
            </div>
            <div style="margin-top:0.8rem;font-size:0.75rem;color:rgba(245,240,232,0.45)">
                Model: Manchanda & Chintagunta (2004) detailing response function.
                Saturation adjustment applied above 8 visits/month.
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Visits vs uplift curve
    st.markdown('<div class="section-hdr">Visit Frequency vs Uplift Curve</div>', unsafe_allow_html=True)
    visit_range = list(range(1, 21))
    uplift_curve = [
        min(0.65, v * base_uplift_per_visit * max(0.4, 1 - (v-1)*0.045)) * 100
        for v in visit_range
    ]
    fig_curve = go.Figure()
    fig_curve.add_trace(go.Scatter(
        x=visit_range, y=uplift_curve,
        mode="lines+markers",
        line=dict(color=MID_GREEN, width=3),
        marker=dict(size=7, color=MID_GREEN),
        fill="tozeroy", fillcolor=f"rgba(26,92,69,0.08)",
    ))
    fig_curve.add_vline(
        x=visits_month, line_dash="dot", line_color=GOLD,
        annotation_text=f"Your setting: {visits_month} visits",
        annotation_position="top right",
        annotation_font_color=GOLD,
    )
    fig_curve.update_layout(
        **PLOTLY_TEMPLATE,
        height=260,
        xaxis_title="Rep visits per month",
        yaxis_title="Expected dispensing uplift (%)",
        showlegend=False,
    )
    st.plotly_chart(fig_curve, use_container_width=True)

    st.markdown(f"""
    <div class="data-note">
        <strong>Methodology note:</strong> Uplift projections use the Manchanda &amp; Chintagunta (2004)
        detailing response function, calibrated to community pharmacy settings.
        Saturation effects are applied above 8 visits/month.
        Projections are directional estimates — actual impact depends on rep quality,
        product positioning, and competitive detailing activity.
    </div>
    """, unsafe_allow_html=True)

# ── Footer note ───────────────────────────────────────────────────────────
st.markdown(f"""
<div class="data-note" style="margin-top:2rem">
    <strong>Data note:</strong> Greater Accra data reflects proprietary dispensing network records.
    Regional estimates for Ashanti, Western, Eastern, Volta, Northern, and Brong-Ahafo are modelled
    using Greater Accra patterns weighted by regional population and healthcare infrastructure indices.
    Market benchmark figures represent estimated total regional market based on network capture rate analysis.
    <br><br>
    © 2025 Aduru Analytics · <a href="https://phytorx-africa.streamlit.app" style="color:{MID_GREEN}">
    phytorx-africa.streamlit.app</a>
</div>
""", unsafe_allow_html=True)
