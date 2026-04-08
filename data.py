"""
Aduru MedRep — Data Layer
Proprietary dispensing network data, Greater Accra, Ghana.
Real data: Madina branch (2025, 12 months, 49,614 pharmaceutical units).
Regional estimates: modelled from live network using population-weighted extrapolation.
"""

import pandas as pd
import numpy as np
import io
from data_embedded import load_embedded, load_branch_data, REAL_STATS as _REAL_STATS

SEED = 2024
rng = np.random.default_rng(SEED)

REGIONS = {
    "Greater Accra":  {"weight": 1.00, "lat": 5.603,  "lon": -0.187, "network": "live"},
    "Ashanti":        {"weight": 0.82, "lat": 6.687,  "lon": -1.624, "network": "modelled"},
    "Western":        {"weight": 0.54, "lat": 5.093,  "lon": -1.744, "network": "modelled"},
    "Eastern":        {"weight": 0.61, "lat": 6.100,  "lon": -0.470, "network": "modelled"},
    "Volta":          {"weight": 0.38, "lat": 7.147,  "lon":  0.444, "network": "modelled"},
    "Northern":       {"weight": 0.29, "lat": 9.401,  "lon": -0.854, "network": "modelled"},
    "Brong-Ahafo":    {"weight": 0.33, "lat": 7.934,  "lon": -1.734, "network": "modelled"},
}

MARKET_BENCHMARK_MULTIPLIER = 1.28


def build_dispensing_data() -> pd.DataFrame:
    return load_embedded()


def compute_opportunity_score(df: pd.DataFrame) -> pd.DataFrame:
    latest  = df[df["month"] == df["month"].max()]
    summary = (
        latest.groupby(["region", "therapeutic_area"])
        .agg(
            total_units=("units_network", "sum"),
            brand_share=("brand_share", "mean"),
            lat=("lat", "first"),
            lon=("lon", "first"),
            network=("network", "first"),
        )
        .reset_index()
    )
    df_sorted = df.sort_values("month")
    recent    = df_sorted[
        df_sorted["month"] >= df_sorted["month"].max() - pd.DateOffset(months=2)
    ]
    prior     = df_sorted[
        (df_sorted["month"] >= df_sorted["month"].max() - pd.DateOffset(months=5)) &
        (df_sorted["month"] <  df_sorted["month"].max() - pd.DateOffset(months=2))
    ]
    rec_vol   = (
        recent.groupby(["region", "therapeutic_area"])["units_network"]
        .sum().reset_index(name="recent_vol")
    )
    prior_vol = (
        prior.groupby(["region", "therapeutic_area"])["units_network"]
        .sum().reset_index(name="prior_vol")
    )
    growth_df = rec_vol.merge(prior_vol, on=["region", "therapeutic_area"])
    growth_df["growth"] = (
        (growth_df["recent_vol"] - growth_df["prior_vol"]) /
        growth_df["prior_vol"].replace(0, 1)
    ).clip(-0.5, 1.5)

    summary = summary.merge(
        growth_df[["region", "therapeutic_area", "growth"]],
        on=["region", "therapeutic_area"], how="left"
    )
    summary["growth"] = summary["growth"].fillna(0)

    for col in ["total_units", "growth"]:
        mn, mx = summary[col].min(), summary[col].max()
        summary[f"{col}_n"] = (summary[col] - mn) / (mx - mn + 1e-9)

    summary["generic_opp"]       = 1 - summary["brand_share"]
    summary["opportunity_score"] = (
        summary["total_units_n"] * 0.40 +
        summary["growth_n"]      * 0.35 +
        summary["generic_opp"]   * 0.25
    ) * 100
    summary["opportunity_score"] = summary["opportunity_score"].round(1)
    summary["opportunity_rank"]  = (
        summary.groupby("therapeutic_area")["opportunity_score"]
        .rank(ascending=False, method="min")
        .astype(int)
    )
    return summary


# Pre-build
DF     = build_dispensing_data()
OPP_DF = compute_opportunity_score(DF)

REAL_STATS = _REAL_STATS

THERAPEUTIC_AREAS = {
    ta: {"drugs": DF[DF["therapeutic_area"] == ta]["drug"].unique().tolist()[:5]}
    for ta in sorted(DF["therapeutic_area"].unique())
}

MONTHS = sorted(DF["month"].unique())
