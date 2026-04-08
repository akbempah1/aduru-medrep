import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from data import DF, OPP_DF, THERAPEUTIC_AREAS, REGIONS, MONTHS, REAL_STATS
from data_embedded import load_branch_data

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
BRANCH_COLORS = {
    "Madina":     MID_GREEN,
    "Ghana Flag": GOLD,
    "Oyarifa":    ORANGE,
}

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

def opp_tier(score):
    if score >= 65: return "High"
    if score >= 40: return "Medium"
    return "Low"

SCORE_COLORS = {"High": EMERALD, "Medium": AMBER, "Low": RED}

# ── CSS ───────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');
html,body,[class*="css"]{{font-family:'DM Sans',sans-serif;background:{CREAM};color:{TEXT_DARK};}}
.medrep-header{{background:linear-gradient(135deg,{DEEP_GREEN} 0%,{MID_GREEN} 70%,{SOFT_GREEN} 100%);
    border-radius:14px;padding:1.6rem 2.2rem;margin-bottom:1.5rem;}}
.medrep-header h1{{font-family:'DM Serif Display',serif;font-size:2rem;color:{CREAM};margin:0;}}
.medrep-header h1 span{{color:{GOLD};}}
.medrep-header p{{color:rgba(245,240,232,0.72);font-size:0.88rem;margin:0.35rem 0 0 0;font-weight:300;}}
.header-badge{{display:inline-block;background:rgba(200,168,75,0.18);border:1px solid {GOLD};
    color:{GOLD_LIGHT};font-size:0.62rem;font-weight:700;letter-spacing:1.8px;text-transform:uppercase;
    padding:2px 9px;border-radius:20px;margin-bottom:0.6rem;}}
.metric-card{{background:white;border:1px solid #DDD8CC;border-radius:10px;padding:1rem 1.2rem;
    box-shadow:0 2px 10px rgba(13,59,46,0.06);border-left:4px solid {MID_GREEN};margin-bottom:0.5rem;}}
.metric-card.gold{{border-left-color:{GOLD};}}
.metric-card.red{{border-left-color:{RED};}}
.metric-card.amber{{border-left-color:{AMBER};}}
.metric-card.emerald{{border-left-color:{EMERALD};}}
.metric-num{{font-family:'DM Serif Display',serif;font-size:2rem;color:{DEEP_GREEN};line-height:1;}}
.metric-label{{font-size:0.72rem;font-weight:600;letter-spacing:1px;text-transform:uppercase;
    color:{TEXT_LIGHT};margin-top:0.25rem;}}
.metric-sub{{font-size:0.78rem;color:{TEXT_LIGHT};margin-top:0.2rem;}}
.section-hdr{{font-family:'DM Serif Display',serif;font-size:1.25rem;color:{DEEP_GREEN};
    margin:1.5rem 0 0.6rem 0;padding-bottom:0.3rem;border-bottom:2px solid {GOLD};display:inline-block;}}
.branch-chip{{display:inline-block;padding:3px 12px;border-radius:20px;font-size:0.78rem;
    font-weight:600;margin:2px 3px;}}
.branch-madina{{background:#e8f4ee;color:{MID_GREEN};border:1px solid {MID_GREEN};}}
.branch-flag{{background:#fdf5e3;color:#8a6f00;border:1px solid {GOLD};}}
.branch-oyarifa{{background:#fdf0e9;color:{ORANGE};border:1px solid {ORANGE};}}
.opp-high{{background:#eafaf1;color:{EMERALD};border:1px solid {EMERALD};}}
.opp-medium{{background:#fefbe6;color:{AMBER};border:1px solid {AMBER};}}
.opp-low{{background:#fdecea;color:{RED};border:1px solid {RED};}}
.opp-badge{{display:inline-block;padding:2px 10px;border-radius:20px;font-size:0.75rem;font-weight:600;}}
.data-note{{background:{CREAM_DARK};border:1px solid #DDD8CC;border-radius:8px;
    padding:0.7rem 1rem;font-size:0.78rem;color:{TEXT_LIGHT};margin-top:1rem;line-height:1.6;}}
.insight-box{{background:{DEEP_GREEN};border-radius:10px;padding:1rem 1.3rem;margin-bottom:0.8rem;}}
.insight-box .title{{font-size:0.7rem;font-weight:700;letter-spacing:1.5px;
    text-transform:uppercase;color:{GOLD_LIGHT};margin-bottom:0.4rem;}}
.insight-box .body{{font-size:0.9rem;color:{CREAM};line-height:1.5;}}
[data-testid="stSidebar"]{{background:{DEEP_GREEN}!important;}}
[data-testid="stSidebar"] *{{color:{CREAM}!important;}}
[data-testid="stSidebar"] .stSelectbox label,[data-testid="stSidebar"] .stRadio label{{
    color:{GOLD_LIGHT}!important;font-size:0.72rem!important;font-weight:600!important;
    letter-spacing:1px!important;text-transform:uppercase!important;}}
.stButton>button{{background:{MID_GREEN}!important;color:{CREAM}!important;
    border:none!important;border-radius:8px!important;font-weight:600!important;}}
div[data-testid="stExpander"]{{border:1px solid #DDD8CC!important;border-radius:8px!important;}}
</style>
""", unsafe_allow_html=True)

# ── Load branch data ──────────────────────────────────────────────────────
BRANCH_DF = load_branch_data()

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

    selected_ta = st.selectbox("Therapeutic Area", list(THERAPEUTIC_AREAS.keys()), index=1)
    selected_region = st.selectbox("Region Focus", ["All Regions"] + list(REGIONS.keys()), index=0)
    selected_drug = st.selectbox(
        "Drug Filter",
        ["All Drugs"] + THERAPEUTIC_AREAS[selected_ta]["drugs"],
    )
    view = st.radio(
        "Dashboard View",
        ["🗺 Territory Overview", "📈 Trend Analysis", "💊 Brand vs Generic",
         "🏆 Opportunity Scores", "🏪 Branch Comparison", "🧑‍💼 Rep Planner"],
        index=0,
    )
    st.markdown("---")
    st.markdown(f"""
    <div style="font-size:0.72rem;color:rgba(245,240,232,0.45);line-height:1.7">
        <strong style="color:rgba(245,240,232,0.7)">Network:</strong><br>
        Madina · Ghana Flag · Oyarifa<br>
        Greater Accra, Ghana<br><br>
        <strong style="color:rgba(245,240,232,0.7)">Data:</strong><br>
        {REAL_STATS['total_units']:,} units · 12 months<br>
        GHS {REAL_STATS['total_revenue']:,.0f} revenue<br><br>
        © 2025 Aduru Analytics
    </div>
    """, unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="medrep-header">
    <div class="header-badge">Pharmaceutical Territory Intelligence · Ghana</div>
    <h1>Aduru <span>MedRep</span></h1>
    <p>
        West Africa's first AI-powered dispensing intelligence for pharmaceutical territory management ·
        3-branch live network · Greater Accra ·
        {REAL_STATS['total_units']:,} real dispensing units ·
        {len(REGIONS)} regions modelled
    </p>
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

bdf = BRANCH_DF[BRANCH_DF["therapeutic_area"] == selected_ta].copy()

# ── KPIs ─────────────────────────────────────────────────────────────────
total_units      = df_ta["units_network"].sum()
total_market     = df_ta["units_market"].sum()
avg_brand_share  = df_ta["brand_share"].mean()
network_share    = total_units / total_market if total_market > 0 else 0
months_sorted    = sorted(df_ta["month"].unique())
latest_units     = df_ta[df_ta["month"] == months_sorted[-1]]["units_network"].sum()
prior_units      = df_ta[df_ta["month"] == months_sorted[-2]]["units_network"].sum() if len(months_sorted) > 1 else latest_units
mom_growth       = (latest_units - prior_units) / prior_units * 100 if prior_units > 0 else 0
top_opp_region   = opp.loc[opp["opportunity_score"].idxmax(), "region"] if not opp.empty else "—"
top_drug         = (
    df_ta[df_ta["network"] == "live"].groupby("drug")["units_network"]
    .sum().idxmax() if not df_ta[df_ta["network"] == "live"].empty else "—"
)

k1, k2, k3, k4, k5 = st.columns(5)
metrics = [
    (k1, f"{total_units:,.0f}", "Network Units", f"{selected_ta} · YTD 2025", ""),
    (k2, f"{'↑' if mom_growth>=0 else '↓'}{abs(mom_growth):.1f}%", "MoM Growth",
     "Latest vs prior month", "gold" if mom_growth >= 0 else "red"),
    (k3, f"{avg_brand_share:.0%}", "Avg Brand Share", "Branded vs generic", "amber"),
    (k4, top_opp_region, "Top Opportunity", "Highest composite score", "emerald"),
    (k5, top_drug[:22] + "…" if len(str(top_drug)) > 22 else str(top_drug),
     "Top Drug (Accra)", "By units dispensed", ""),
]
for col, num, label, sub, color in metrics:
    with col:
        st.markdown(f"""
        <div class="metric-card {color}">
            <div class="metric-num">{num}</div>
            <div class="metric-label">{label}</div>
            <div class="metric-sub">{sub}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════
# VIEW 1 — Territory Overview
# ══════════════════════════════════════════════════════════════════════════
if view == "🗺 Territory Overview":
    st.markdown('<div class="section-hdr">Territory Dispensing Map</div>', unsafe_allow_html=True)
    st.markdown("")

    map_data = (
        df_ta.groupby(["region", "lat", "lon", "network"])["units_network"]
        .sum().reset_index()
    )
    map_data["size"]  = (map_data["units_network"] / map_data["units_network"].max() * 60 + 15).clip(15, 80)
    map_data["label"] = map_data.apply(
        lambda r: f"{r['region']}<br>{r['units_network']:,.0f} units<br>"
                  f"{'● Live network (3 branches)' if r['network']=='live' else '◌ Modelled estimate'}",
        axis=1,
    )
    fig_map = go.Figure()
    for net_type, sym, col in [("live", "circle", MID_GREEN), ("modelled", "circle-open", GOLD)]:
        sub = map_data[map_data["network"] == net_type]
        fig_map.add_trace(go.Scattergeo(
            lat=sub["lat"], lon=sub["lon"],
            text=sub["label"], hoverinfo="text", mode="markers",
            marker=dict(size=sub["size"], color=col, symbol=sym,
                        line=dict(color=col, width=2), opacity=0.85),
            name="Live network (3 branches)" if net_type == "live" else "Modelled estimate",
        ))
    fig_map.update_layout(
        geo=dict(
            scope="africa", center=dict(lat=7.5, lon=-1.0), projection_scale=6,
            showland=True, landcolor="#F0EBE0",
            showocean=True, oceancolor="#E8F4F8",
            showcountries=True, countrycolor="#CCCCCC", showframe=False,
            bgcolor="rgba(0,0,0,0)",
        ),
        height=420,
        legend=dict(x=0.01, y=0.99, bgcolor="rgba(255,255,255,0.85)"),
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=10, b=0),
    )
    st.plotly_chart(fig_map, use_container_width=True)

    col_bar, col_pie = st.columns([3, 2])
    with col_bar:
        st.markdown('<div class="section-hdr">Regional Volume Breakdown</div>', unsafe_allow_html=True)
        bar_data = (
            df_ta.groupby("region")["units_network"].sum().reset_index()
            .sort_values("units_network", ascending=True)
        )
        fig_bar = go.Figure(go.Bar(
            x=bar_data["units_network"], y=bar_data["region"], orientation="h",
            marker=dict(
                color=bar_data["units_network"],
                colorscale=[[0, CREAM_DARK], [0.5, SOFT_GREEN], [1, DEEP_GREEN]],
                showscale=False,
            ),
            text=bar_data["units_network"].apply(lambda x: f"{x:,.0f}"),
            textposition="outside",
        ))
        fig_bar.update_layout(**PLOTLY_TEMPLATE, height=300,
                              xaxis_title="Units dispensed", yaxis_title="")
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_pie:
        st.markdown('<div class="section-hdr">Network vs Market</div>', unsafe_allow_html=True)
        net_total = df_ta["units_network"].sum()
        mkt_total = df_ta["units_market"].sum()
        gap       = max(0, mkt_total - net_total)
        fig_pie = go.Figure(go.Pie(
            labels=["Our Network", "Market Gap"],
            values=[net_total, gap],
            hole=0.55,
            marker=dict(colors=[MID_GREEN, CREAM_DARK]),
            textinfo="label+percent",
            textfont=dict(size=11),
        ))
        fig_pie.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", margin=dict(l=0,r=0,t=10,b=0),
            showlegend=False, height=300,
            annotations=[dict(
                text=f"{net_total/mkt_total:.0%}<br>capture",
                x=0.5, y=0.5, font_size=14, showarrow=False, font_color=DEEP_GREEN,
            )],
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    # Auto insights
    st.markdown('<div class="section-hdr">Network Insights</div>', unsafe_allow_html=True)
    top_region = bar_data.iloc[-1]
    low_region = bar_data.iloc[0]
    brand_gap  = df_ta.groupby("region")["brand_share"].mean()
    max_brand_region = brand_gap.idxmax()
    st.markdown(f"""
    <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:0.8rem;margin-top:0.5rem">
        <div class="insight-box">
            <div class="title">Highest Volume Region</div>
            <div class="body"><strong>{top_region['region']}</strong> leads with
            {top_region['units_network']:,.0f} units in {selected_ta}</div>
        </div>
        <div class="insight-box">
            <div class="title">Underserved Region</div>
            <div class="body"><strong>{low_region['region']}</strong> shows lowest volume —
            potential expansion opportunity</div>
        </div>
        <div class="insight-box">
            <div class="title">Highest Brand Penetration</div>
            <div class="body"><strong>{max_brand_region}</strong> has strongest brand share
            ({brand_gap[max_brand_region]:.0%}) — defend this territory</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════
# VIEW 2 — Trend Analysis
# ══════════════════════════════════════════════════════════════════════════
elif view == "📈 Trend Analysis":
    st.markdown('<div class="section-hdr">Monthly Dispensing Trends by Region</div>', unsafe_allow_html=True)
    trend_data = (
        df_ta.groupby(["month", "month_label", "region"])["units_network"]
        .sum().reset_index().sort_values("month")
    )
    fig_trend = px.line(
        trend_data, x="month_label", y="units_network", color="region",
        markers=True,
        color_discrete_sequence=[MID_GREEN, GOLD, SOFT_GREEN, AMBER, DEEP_GREEN, EMERALD, ORANGE],
    )
    fig_trend.update_layout(**PLOTLY_TEMPLATE, height=380,
                             xaxis_title="Month", yaxis_title="Units dispensed",
                             legend_title="Region", hovermode="x unified")
    fig_trend.update_traces(line=dict(width=2.5), marker=dict(size=7))
    st.plotly_chart(fig_trend, use_container_width=True)

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown('<div class="section-hdr">Network vs Market Estimate</div>', unsafe_allow_html=True)
        mkt_data = (
            df_ta.groupby(["month", "month_label"])
            .agg(network=("units_network","sum"), market=("units_market","sum"))
            .reset_index().sort_values("month")
        )
        fig_mkt = go.Figure()
        fig_mkt.add_trace(go.Bar(x=mkt_data["month_label"], y=mkt_data["market"],
                                 name="Market estimate", marker_color=CREAM_DARK))
        fig_mkt.add_trace(go.Bar(x=mkt_data["month_label"], y=mkt_data["network"],
                                 name="Our network", marker_color=MID_GREEN))
        fig_mkt.update_layout(**PLOTLY_TEMPLATE, barmode="overlay", height=300,
                               xaxis_title="Month", yaxis_title="Units",
                               legend=dict(x=0.01, y=0.99))
        st.plotly_chart(fig_mkt, use_container_width=True)

    with col_b:
        st.markdown('<div class="section-hdr">Drug Heatmap</div>', unsafe_allow_html=True)
        heat_data = (
            df_ta[df_ta["network"] == "live"]
            .groupby(["drug", "month_label"])["units_network"].sum().reset_index()
        )
        if not heat_data.empty:
            heat_pivot = heat_data.pivot(index="drug", columns="month_label", values="units_network").fillna(0)
            month_order = [m for m in df_ta["month_label"].unique() if m in heat_pivot.columns]
            heat_pivot  = heat_pivot[[c for c in month_order if c in heat_pivot.columns]]
            # Show top 12 drugs only
            top12 = heat_pivot.sum(axis=1).nlargest(12).index
            heat_pivot = heat_pivot.loc[top12]
            fig_heat = go.Figure(go.Heatmap(
                z=heat_pivot.values, x=heat_pivot.columns.tolist(), y=heat_pivot.index.tolist(),
                colorscale=[[0, CREAM_DARK],[0.5, SOFT_GREEN],[1, DEEP_GREEN]],
            ))
            fig_heat.update_layout(**PLOTLY_TEMPLATE, height=300,
                                    xaxis_title="Month", yaxis_title="")
            st.plotly_chart(fig_heat, use_container_width=True)

    # Seasonal pattern
    st.markdown('<div class="section-hdr">Seasonal Pattern (Accra live network)</div>',
                unsafe_allow_html=True)
    seasonal = (
        df_ta[df_ta["network"] == "live"]
        .groupby("month_label")["units_network"].sum().reset_index()
    )
    seasonal["month_num"] = pd.to_datetime(seasonal["month_label"], format="%b %Y").dt.month
    seasonal = seasonal.sort_values("month_num")
    avg = seasonal["units_network"].mean()
    seasonal["above_avg"] = seasonal["units_network"] >= avg
    fig_sea = go.Figure()
    fig_sea.add_hline(y=avg, line_dash="dot", line_color=TEXT_LIGHT,
                      annotation_text=f"Average {avg:,.0f}", annotation_position="top right")
    for _, row in seasonal.iterrows():
        fig_sea.add_trace(go.Bar(
            x=[row["month_label"]], y=[row["units_network"]],
            marker_color=MID_GREEN if row["above_avg"] else CREAM_DARK,
            showlegend=False,
        ))
    fig_sea.update_layout(**PLOTLY_TEMPLATE, height=260,
                           xaxis_title="", yaxis_title="Units")
    st.plotly_chart(fig_sea, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════
# VIEW 3 — Brand vs Generic
# ══════════════════════════════════════════════════════════════════════════
elif view == "💊 Brand vs Generic":
    st.markdown('<div class="section-hdr">Brand vs Generic Split by Region</div>', unsafe_allow_html=True)
    st.caption("High generic share = greater detailing opportunity for branded products")

    bg_data = (
        df_ta.groupby("region")
        .agg(branded=("units_branded","sum"), generic=("units_generic","sum"))
        .reset_index()
    )
    bg_data["total"]       = bg_data["branded"] + bg_data["generic"]
    bg_data["brand_pct"]   = bg_data["branded"]  / bg_data["total"]
    bg_data["generic_pct"] = bg_data["generic"] / bg_data["total"]
    bg_data = bg_data.sort_values("brand_pct", ascending=True)

    fig_bg = go.Figure()
    fig_bg.add_trace(go.Bar(
        y=bg_data["region"], x=bg_data["brand_pct"]*100, orientation="h",
        name="Branded", marker_color=MID_GREEN,
        text=bg_data["brand_pct"].apply(lambda x: f"{x:.0%}"),
        textposition="inside", textfont=dict(color="white"),
    ))
    fig_bg.add_trace(go.Bar(
        y=bg_data["region"], x=bg_data["generic_pct"]*100, orientation="h",
        name="Generic", marker_color=CREAM_DARK,
        text=bg_data["generic_pct"].apply(lambda x: f"{x:.0%}"),
        textposition="inside", textfont=dict(color=TEXT_LIGHT),
    ))
    fig_bg.update_layout(**PLOTLY_TEMPLATE, barmode="stack", height=320,
                          xaxis_title="Share (%)", yaxis_title="",
                          legend=dict(x=0.7, y=0.05))
    st.plotly_chart(fig_bg, use_container_width=True)

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown('<div class="section-hdr">Brand Share Trend</div>', unsafe_allow_html=True)
        bs_trend = (
            df_ta[df_ta["network"] == "live"]
            .groupby(["month","month_label"])
            .agg(branded=("units_branded","sum"), total=("units_network","sum"))
            .reset_index().sort_values("month")
        )
        bs_trend["brand_share"] = bs_trend["branded"] / bs_trend["total"]
        avg_bs = bs_trend["brand_share"].mean()
        fig_bs = go.Figure()
        fig_bs.add_trace(go.Scatter(
            x=bs_trend["month_label"], y=bs_trend["brand_share"]*100,
            mode="lines+markers",
            line=dict(color=GOLD, width=3), marker=dict(size=8, color=GOLD),
            fill="tozeroy", fillcolor="rgba(200,168,75,0.08)",
        ))
        fig_bs.add_hline(y=avg_bs*100, line_dash="dot", line_color=TEXT_LIGHT,
                         annotation_text=f"Avg {avg_bs:.0%}",
                         annotation_position="top right")
        fig_bs.update_layout(**PLOTLY_TEMPLATE, height=280,
                              yaxis_title="Brand share (%)", xaxis_title="")
        st.plotly_chart(fig_bs, use_container_width=True)

    with col_b:
        st.markdown('<div class="section-hdr">Top Branded Drugs (Accra)</div>', unsafe_allow_html=True)
        top_branded = (
            df_ta[df_ta["network"] == "live"]
            .groupby("drug")["units_branded"].sum().reset_index()
            .sort_values("units_branded", ascending=True).tail(10)
        )
        fig_tb = go.Figure(go.Bar(
            x=top_branded["units_branded"], y=top_branded["drug"],
            orientation="h", marker_color=GOLD,
            text=top_branded["units_branded"].apply(lambda x: f"{x:,.0f}"),
            textposition="outside",
        ))
        fig_tb.update_layout(**PLOTLY_TEMPLATE, height=280,
                              xaxis_title="Branded units", yaxis_title="")
        st.plotly_chart(fig_tb, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════
# VIEW 4 — Opportunity Scores
# ══════════════════════════════════════════════════════════════════════════
elif view == "🏆 Opportunity Scores":
    st.markdown('<div class="section-hdr">Territory Opportunity Ranking</div>', unsafe_allow_html=True)
    st.caption("Composite score: dispensing volume (40%) · growth momentum (35%) · generic penetration opportunity (25%)")

    opp_display = opp.sort_values("opportunity_score", ascending=False)
    colors = opp_display["tier"].map({"High": EMERALD, "Medium": AMBER, "Low": RED}).tolist()

    col_chart, col_table = st.columns([1, 1])
    with col_chart:
        fig_opp = go.Figure()
        fig_opp.add_trace(go.Bar(
            x=opp_display["opportunity_score"],
            y=opp_display["region"],
            orientation="h",
            marker_color=colors,
            text=opp_display["opportunity_score"].apply(lambda x: f"{x:.0f}"),
            textposition="outside",
        ))
        fig_opp.update_layout(**PLOTLY_TEMPLATE, height=340,
                               xaxis=dict(range=[0,115], title="Opportunity Score (0–100)"),
                               yaxis_title="")
        st.plotly_chart(fig_opp, use_container_width=True)

    with col_table:
        for _, row in opp_display.iterrows():
            tier    = row["tier"]
            color   = SCORE_COLORS[tier]
            net     = "● Live" if row["network"] == "live" else "◌ Modelled"
            growth  = row["growth"] * 100
            g_arrow = "↑" if growth >= 0 else "↓"
            st.markdown(f"""
            <div style="background:white;border:1px solid #DDD8CC;border-left:4px solid {color};
                        border-radius:8px;padding:0.65rem 1rem;margin-bottom:0.45rem;
                        display:flex;justify-content:space-between;align-items:center">
                <div>
                    <strong style="font-size:0.95rem;color:{TEXT_DARK}">{row['region']}</strong>
                    <span style="font-size:0.72rem;color:{TEXT_LIGHT};margin-left:0.5rem">{net}</span><br>
                    <span style="font-size:0.8rem;color:{TEXT_LIGHT}">
                        {row['total_units']:,.0f} units ·
                        {g_arrow}{abs(growth):.1f}% growth ·
                        {row['brand_share']:.0%} branded
                    </span>
                </div>
                <div style="text-align:right">
                    <div style="font-family:'DM Serif Display',serif;font-size:1.7rem;
                                color:{color};line-height:1">{row['opportunity_score']:.0f}</div>
                    <span class="opp-badge opp-{tier.lower()}">{tier}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # Bubble chart — all TAs at once
    st.markdown('<div class="section-hdr">Opportunity Landscape — All Therapeutic Areas</div>',
                unsafe_allow_html=True)
    all_opp = OPP_DF[OPP_DF["network"] == "live"].copy()
    all_opp["tier"] = all_opp["opportunity_score"].apply(opp_tier)
    fig_bub = px.scatter(
        all_opp, x="opportunity_score", y="total_units",
        size="opportunity_score", color="therapeutic_area",
        hover_name="therapeutic_area",
        labels={"opportunity_score":"Opportunity Score","total_units":"Units Dispensed"},
        color_discrete_sequence=[MID_GREEN,GOLD,SOFT_GREEN,AMBER,DEEP_GREEN,EMERALD,ORANGE,RED],
        size_max=30,
    )
    fig_bub.update_layout(**PLOTLY_TEMPLATE, height=320,
                           xaxis_title="Opportunity Score", yaxis_title="Units Dispensed")
    st.plotly_chart(fig_bub, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════
# VIEW 5 — Branch Comparison (NEW)
# ══════════════════════════════════════════════════════════════════════════
elif view == "🏪 Branch Comparison":
    st.markdown('<div class="section-hdr">Branch Performance Comparison</div>',
                unsafe_allow_html=True)
    st.markdown("""
    <div style="margin-bottom:1rem">
        <span class="branch-chip branch-madina">● Madina</span>
        <span class="branch-chip branch-flag">● Ghana Flag</span>
        <span class="branch-chip branch-oyarifa">● Oyarifa</span>
        <span style="font-size:0.8rem;color:#6B6B60;margin-left:0.5rem">
            Live dispensing data · Greater Accra network
        </span>
    </div>
    """, unsafe_allow_html=True)

    # Branch KPI cards
    b1, b2, b3 = st.columns(3)
    branch_totals = (
        bdf.groupby("branch")
        .agg(units=("units_network","sum"), revenue=("revenue","sum"),
             brand_share=("brand_share","mean"))
        .reset_index()
    )
    cols_map = {"Madina": b1, "Ghana Flag": b2, "Oyarifa": b3}
    color_map = {"Madina": "", "Ghana Flag": "gold", "Oyarifa": "amber"}
    for _, row in branch_totals.iterrows():
        with cols_map.get(row["branch"], b1):
            st.markdown(f"""
            <div class="metric-card {color_map.get(row['branch'],'')}">
                <div class="metric-num">{row['units']:,.0f}</div>
                <div class="metric-label">{row['branch']}</div>
                <div class="metric-sub">
                    GHS {row['revenue']:,.0f} revenue ·
                    {row['brand_share']:.0%} branded
                </div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Monthly trend by branch
    col_trend, col_share = st.columns([3, 2])
    with col_trend:
        st.markdown('<div class="section-hdr">Monthly Volume by Branch</div>',
                    unsafe_allow_html=True)
        branch_monthly = (
            bdf.groupby(["month","month_label","branch"])["units_network"]
            .sum().reset_index().sort_values("month")
        )
        fig_bt = go.Figure()
        for branch, color in BRANCH_COLORS.items():
            sub = branch_monthly[branch_monthly["branch"] == branch]
            fig_bt.add_trace(go.Scatter(
                x=sub["month_label"], y=sub["units_network"],
                name=branch, mode="lines+markers",
                line=dict(color=color, width=2.5),
                marker=dict(size=7, color=color),
            ))
        fig_bt.update_layout(**PLOTLY_TEMPLATE, height=300,
                              xaxis_title="", yaxis_title="Units dispensed",
                              hovermode="x unified", legend_title="Branch")
        st.plotly_chart(fig_bt, use_container_width=True)

    with col_share:
        st.markdown('<div class="section-hdr">Network Share by Branch</div>',
                    unsafe_allow_html=True)
        branch_share = branch_totals.copy()
        branch_share["share"] = branch_share["units"] / branch_share["units"].sum()
        fig_bs2 = go.Figure(go.Pie(
            labels=branch_share["branch"],
            values=branch_share["units"],
            hole=0.5,
            marker=dict(colors=[MID_GREEN, GOLD, ORANGE]),
            textinfo="label+percent",
            textfont=dict(size=11),
        ))
        fig_bs2.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", margin=dict(l=0,r=0,t=10,b=0),
            showlegend=False, height=300,
        )
        st.plotly_chart(fig_bs2, use_container_width=True)

    # TA breakdown by branch
    st.markdown('<div class="section-hdr">Therapeutic Area Mix by Branch</div>',
                unsafe_allow_html=True)
    ta_branch = (
        bdf.groupby(["branch","therapeutic_area"])["units_network"]
        .sum().reset_index()
    )
    fig_ta_b = px.bar(
        ta_branch, x="therapeutic_area", y="units_network", color="branch",
        barmode="group",
        color_discrete_map=BRANCH_COLORS,
        labels={"units_network":"Units","therapeutic_area":"Therapeutic Area","branch":"Branch"},
    )
    fig_ta_b.update_layout(**PLOTLY_TEMPLATE, height=340,
                            xaxis_title="", yaxis_title="Units dispensed",
                            legend_title="Branch",
                            xaxis_tickangle=-30)
    st.plotly_chart(fig_ta_b, use_container_width=True)

    # Brand share by branch
    col_bg1, col_bg2 = st.columns(2)
    with col_bg1:
        st.markdown('<div class="section-hdr">Brand Share by Branch</div>',
                    unsafe_allow_html=True)
        bs_branch = branch_totals.copy()
        bs_branch["generic_share"] = 1 - bs_branch["brand_share"]
        fig_bsb = go.Figure()
        for branch, color in BRANCH_COLORS.items():
            row = bs_branch[bs_branch["branch"] == branch]
            if row.empty: continue
            fig_bsb.add_trace(go.Bar(
                name=branch,
                x=[branch],
                y=[float(row["brand_share"].iloc[0]) * 100],
                marker_color=color,
                text=[f"{float(row['brand_share'].iloc[0]):.0%}"],
                textposition="outside",
            ))
        fig_bsb.update_layout(**PLOTLY_TEMPLATE, height=280,
                               yaxis=dict(range=[0, 100], title="Brand share (%)"),
                               xaxis_title="", showlegend=False,
                               yaxis_gridcolor="#E8E4DC")
        st.plotly_chart(fig_bsb, use_container_width=True)

    with col_bg2:
        st.markdown('<div class="section-hdr">Top Drug per Branch</div>',
                    unsafe_allow_html=True)
        for branch in ["Madina", "Ghana Flag", "Oyarifa"]:
            sub = bdf[bdf["branch"] == branch]
            if sub.empty: continue
            top = sub.groupby("drug")["units_network"].sum().idxmax()
            vol = sub.groupby("drug")["units_network"].sum().max()
            color = BRANCH_COLORS[branch]
            st.markdown(f"""
            <div style="background:white;border:1px solid #DDD8CC;border-left:4px solid {color};
                        border-radius:8px;padding:0.65rem 1rem;margin-bottom:0.5rem">
                <strong style="color:{color}">{branch}</strong><br>
                <span style="font-size:0.95rem;color:{TEXT_DARK}">{top}</span><br>
                <span style="font-size:0.78rem;color:{TEXT_LIGHT}">{vol:,.0f} units dispensed YTD</span>
            </div>
            """, unsafe_allow_html=True)

    # Growth ranking
    st.markdown('<div class="section-hdr">Month-on-Month Growth by Branch</div>',
                unsafe_allow_html=True)
    bm = branch_monthly.copy()
    bm_sorted = bm.sort_values("month")
    bm_latest = bm_sorted.groupby("branch").tail(1).rename(columns={"units_network":"latest"})
    bm_prior  = bm_sorted.groupby("branch").nth(-2).rename(columns={"units_network":"prior"})
    growth_br = bm_latest[["branch","latest"]].merge(
        bm_prior[["branch","prior"]], on="branch"
    )
    growth_br["growth_pct"] = (
        (growth_br["latest"] - growth_br["prior"]) / growth_br["prior"] * 100
    ).round(1)
    fig_gbr = go.Figure(go.Bar(
        x=growth_br["branch"],
        y=growth_br["growth_pct"],
        marker_color=[MID_GREEN if g>=0 else RED for g in growth_br["growth_pct"]],
        text=growth_br["growth_pct"].apply(lambda x: f"{'↑' if x>=0 else '↓'}{abs(x):.1f}%"),
        textposition="outside",
    ))
    fig_gbr.add_hline(y=0, line_color=TEXT_LIGHT, line_width=1)
    fig_gbr.update_layout(**PLOTLY_TEMPLATE, height=240,
                           xaxis_title="", yaxis_title="MoM Growth (%)",
                           showlegend=False)
    st.plotly_chart(fig_gbr, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════
# VIEW 6 — Rep Planner
# ══════════════════════════════════════════════════════════════════════════
elif view == "🧑‍💼 Rep Planner":
    st.markdown('<div class="section-hdr">Territory Rep Planner</div>', unsafe_allow_html=True)
    st.caption("Model expected dispensing uplift based on rep visit frequency")

    col1, col2 = st.columns([1, 1])
    with col1:
        rep_region      = st.selectbox("Target Region", list(REGIONS.keys()), key="rep_region")
        visits_month    = st.slider("Rep visits per month", 1, 20, 6)
        campaign_months = st.slider("Campaign duration (months)", 1, 12, 3)
        focus_drug      = st.selectbox(
            "Focus Drug",
            THERAPEUTIC_AREAS[selected_ta]["drugs"],
            key="rep_drug",
        )

    base_uplift_per_visit = 0.028
    saturation_factor     = max(0.4, 1 - (visits_month - 1) * 0.045)
    total_uplift          = min(0.65, visits_month * base_uplift_per_visit * saturation_factor)

    region_data = DF[
        (DF["region"] == rep_region) &
        (DF["therapeutic_area"] == selected_ta) &
        (DF["drug"] == focus_drug)
    ]
    region_base     = region_data["units_network"].mean() if not region_data.empty else 50
    proj_monthly    = region_base * (1 + total_uplift)
    total_proj      = proj_monthly * campaign_months
    total_base      = region_base * campaign_months
    incremental     = total_proj - total_base

    with col2:
        st.markdown(f"""
        <div style="background:{DEEP_GREEN};border-radius:12px;padding:1.3rem 1.5rem;color:{CREAM}">
            <div style="font-size:0.7rem;letter-spacing:1.5px;text-transform:uppercase;
                        color:{GOLD_LIGHT};font-weight:600;margin-bottom:0.8rem">PROJECTED IMPACT</div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.8rem">
                <div>
                    <div style="font-family:'DM Serif Display',serif;font-size:1.7rem;color:{GOLD}">
                        +{total_uplift:.0%}
                    </div>
                    <div style="font-size:0.75rem;color:rgba(245,240,232,0.65)">Projected uplift</div>
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
                        {total_base:,.0f}
                    </div>
                    <div style="font-size:0.75rem;color:rgba(245,240,232,0.65)">
                        Baseline ({campaign_months}mo)
                    </div>
                </div>
                <div>
                    <div style="font-family:'DM Serif Display',serif;font-size:1.7rem;color:{CREAM}">
                        {total_proj:,.0f}
                    </div>
                    <div style="font-size:0.75rem;color:rgba(245,240,232,0.65)">
                        Projected ({campaign_months}mo)
                    </div>
                </div>
            </div>
            <div style="margin-top:0.8rem;font-size:0.72rem;color:rgba(245,240,232,0.4)">
                Manchanda & Chintagunta (2004) detailing response function.
                Saturation adjustment applied above 8 visits/month.
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="section-hdr">Visit Frequency vs Uplift Curve</div>',
                unsafe_allow_html=True)
    vrange = list(range(1, 21))
    ucurve = [
        min(0.65, v * base_uplift_per_visit * max(0.4, 1-(v-1)*0.045)) * 100
        for v in vrange
    ]
    fig_curve = go.Figure()
    fig_curve.add_trace(go.Scatter(
        x=vrange, y=ucurve, mode="lines+markers",
        line=dict(color=MID_GREEN, width=3), marker=dict(size=7, color=MID_GREEN),
        fill="tozeroy", fillcolor="rgba(26,92,69,0.08)",
    ))
    fig_curve.add_vline(x=visits_month, line_dash="dot", line_color=GOLD,
                        annotation_text=f"Your setting: {visits_month} visits",
                        annotation_position="top right",
                        annotation_font_color=GOLD)
    fig_curve.update_layout(**PLOTLY_TEMPLATE, height=260,
                             xaxis_title="Rep visits per month",
                             yaxis_title="Expected uplift (%)", showlegend=False)
    st.plotly_chart(fig_curve, use_container_width=True)

    # Optimal territory ranking for this rep
    st.markdown('<div class="section-hdr">Recommended Territory Priority</div>',
                unsafe_allow_html=True)
    st.caption("Regions ranked by ROI — highest volume × highest generic penetration × lowest current brand share")
    ta_opp = OPP_DF[OPP_DF["therapeutic_area"] == selected_ta].sort_values(
        "opportunity_score", ascending=False
    ).reset_index(drop=True)
    for i, row in ta_opp.iterrows():
        tier  = opp_tier(row["opportunity_score"])
        color = SCORE_COLORS[tier]
        net   = "● Live" if row["network"] == "live" else "◌ Modelled"
        st.markdown(f"""
        <div style="background:white;border:1px solid #DDD8CC;border-left:4px solid {color};
                    border-radius:8px;padding:0.6rem 1rem;margin-bottom:0.4rem;
                    display:flex;justify-content:space-between;align-items:center">
            <div>
                <strong>#{i+1} {row['region']}</strong>
                <span style="font-size:0.72rem;color:{TEXT_LIGHT};margin-left:0.5rem">{net}</span><br>
                <span style="font-size:0.78rem;color:{TEXT_LIGHT}">
                    {row['total_units']:,.0f} units ·
                    {row['brand_share']:.0%} branded ·
                    {row['generic_opp']:.0%} generic opportunity
                </span>
            </div>
            <div style="font-family:'DM Serif Display',serif;font-size:1.5rem;color:{color}">
                {row['opportunity_score']:.0f}
            </div>
        </div>
        """, unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="data-note" style="margin-top:2rem">
    <strong>Data note:</strong> Greater Accra figures reflect real dispensing data from a
    3-branch proprietary pharmacy network (2025, 12 months, {REAL_STATS['total_units']:,} units).
    Regional estimates for Ashanti, Western, Eastern, Volta, Northern, and Brong-Ahafo are modelled
    using Greater Accra patterns weighted by regional population and healthcare infrastructure indices.
    Market benchmark figures represent estimated total regional market based on network capture rate analysis.
    Brand/generic classification uses unit price as proxy (branded ≥ GHS 15).
    <br><br>
    © 2025 Aduru Analytics · aduru-analytics.com
</div>
""", unsafe_allow_html=True)
