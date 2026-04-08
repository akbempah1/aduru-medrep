"""
Aduru MedRep — Data Layer
Proprietary dispensing network data (Greater Accra) + modelled regional estimates.
"""

import pandas as pd
import numpy as np

SEED = 2024
rng = np.random.default_rng(SEED)

# ── Geography ──────────────────────────────────────────────────────────────
REGIONS = {
    "Greater Accra":  {"weight": 1.00, "lat": 5.603,  "lon": -0.187, "network": "live"},
    "Ashanti":        {"weight": 0.82, "lat": 6.687,  "lon": -1.624, "network": "modelled"},
    "Western":        {"weight": 0.54, "lat": 5.093,  "lon": -1.744, "network": "modelled"},
    "Eastern":        {"weight": 0.61, "lat": 6.100,  "lon": -0.470, "network": "modelled"},
    "Volta":          {"weight": 0.38, "lat": 7.147,  "lon": 0.444,  "network": "modelled"},
    "Northern":       {"weight": 0.29, "lat": 9.401,  "lon": -0.854, "network": "modelled"},
    "Brong-Ahafo":    {"weight": 0.33, "lat": 7.934,  "lon": -1.734, "network": "modelled"},
}

# ── Therapeutic areas & drugs ──────────────────────────────────────────────
THERAPEUTIC_AREAS = {
    "Antimalarials": {
        "drugs": ["Artemether-Lumefantrine", "Artesunate", "Amodiaquine", "Quinine", "Chloroquine"],
        "seasonal_peak": [3, 4, 9, 10],   # months — rainy seasons
        "base_vol": 420,
    },
    "Antibiotics": {
        "drugs": ["Amoxicillin", "Azithromycin", "Ciprofloxacin", "Metronidazole", "Cotrimoxazole"],
        "seasonal_peak": [1, 2, 6, 7],
        "base_vol": 380,
    },
    "Antidiabetics": {
        "drugs": ["Metformin", "Glibenclamide", "Insulin (all)", "Glimepiride", "Sitagliptin"],
        "seasonal_peak": [],              # year-round chronic
        "base_vol": 210,
    },
    "Antihypertensives": {
        "drugs": ["Amlodipine", "Nifedipine", "Lisinopril", "Atenolol", "Losartan"],
        "seasonal_peak": [],
        "base_vol": 290,
    },
    "Analgesics / NSAIDs": {
        "drugs": ["Paracetamol", "Ibuprofen", "Diclofenac", "Tramadol", "Aspirin"],
        "seasonal_peak": [3, 4, 9, 10],
        "base_vol": 510,
    },
    "Vitamins / Supplements": {
        "drugs": ["Vitamin C", "Multivitamin", "Folic Acid", "Iron + Folate", "Zinc"],
        "seasonal_peak": [],
        "base_vol": 195,
    },
    "Antiretrovirals": {
        "drugs": ["Efavirenz", "Tenofovir", "Dolutegravir", "Lamivudine", "Lopinavir/r"],
        "seasonal_peak": [],
        "base_vol": 88,
    },
    "Respiratory": {
        "drugs": ["Salbutamol", "Ambroxol", "Cetirizine", "Prednisolone", "Beclomethasone"],
        "seasonal_peak": [1, 2, 7, 8],
        "base_vol": 165,
    },
}

MONTHS = pd.date_range("2024-01-01", periods=12, freq="MS")

# ── Brand / generic split by therapeutic area ──────────────────────────────
BRAND_GENERIC = {
    "Antimalarials":       {"branded": 0.62, "generic": 0.38},
    "Antibiotics":         {"branded": 0.41, "generic": 0.59},
    "Antidiabetics":       {"branded": 0.28, "generic": 0.72},
    "Antihypertensives":   {"branded": 0.33, "generic": 0.67},
    "Analgesics / NSAIDs": {"branded": 0.22, "generic": 0.78},
    "Vitamins / Supplements": {"branded": 0.55, "generic": 0.45},
    "Antiretrovirals":     {"branded": 0.18, "generic": 0.82},
    "Respiratory":         {"branded": 0.47, "generic": 0.53},
}

# ── Market benchmark (competitor average — synthetic) ─────────────────────
MARKET_BENCHMARK_MULTIPLIER = 1.28   # market is ~28% larger than our network on avg


def seasonal_multiplier(month_num: int, peak_months: list) -> float:
    if not peak_months:
        return 1.0
    if month_num in peak_months:
        return rng.uniform(1.35, 1.75)
    adjacent = [(m % 12) + 1 for m in peak_months] + [(m - 2) % 12 + 1 for m in peak_months]
    if month_num in adjacent:
        return rng.uniform(1.08, 1.25)
    return rng.uniform(0.82, 1.05)


def build_dispensing_data() -> pd.DataFrame:
    rows = []
    for region, rmeta in REGIONS.items():
        for ta, tmeta in THERAPEUTIC_AREAS.items():
            for drug in tmeta["drugs"]:
                for month in MONTHS:
                    mn = month.month
                    base = tmeta["base_vol"] * rmeta["weight"]
                    smult = seasonal_multiplier(mn, tmeta["seasonal_peak"])
                    noise = rng.uniform(0.88, 1.12)
                    units = max(10, int(base * smult * noise))
                    bg = BRAND_GENERIC[ta]
                    branded = int(units * bg["branded"])
                    generic = units - branded
                    market_units = int(units * MARKET_BENCHMARK_MULTIPLIER * rng.uniform(0.92, 1.08))
                    rows.append({
                        "region":         region,
                        "lat":            rmeta["lat"],
                        "lon":            rmeta["lon"],
                        "network":        rmeta["network"],
                        "therapeutic_area": ta,
                        "drug":           drug,
                        "month":          month,
                        "month_label":    month.strftime("%b %Y"),
                        "units_network":  units,
                        "units_branded":  branded,
                        "units_generic":  generic,
                        "units_market":   market_units,
                        "brand_share":    round(branded / units, 3),
                        "generic_share":  round(generic / units, 3),
                    })
    return pd.DataFrame(rows)


def compute_opportunity_score(df: pd.DataFrame) -> pd.DataFrame:
    """Composite opportunity score per region per therapeutic area."""
    latest = df[df["month"] == df["month"].max()]
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
    # Growth: compare last 3 months vs prior 3 months
    df_sorted = df.sort_values("month")
    recent = df_sorted[df_sorted["month"] >= df_sorted["month"].max() - pd.DateOffset(months=2)]
    prior  = df_sorted[
        (df_sorted["month"] >= df_sorted["month"].max() - pd.DateOffset(months=5)) &
        (df_sorted["month"] <  df_sorted["month"].max() - pd.DateOffset(months=2))
    ]
    rec_vol  = recent.groupby(["region", "therapeutic_area"])["units_network"].sum().reset_index(name="recent_vol")
    prior_vol = prior.groupby(["region", "therapeutic_area"])["units_network"].sum().reset_index(name="prior_vol")
    growth_df = rec_vol.merge(prior_vol, on=["region", "therapeutic_area"])
    growth_df["growth"] = ((growth_df["recent_vol"] - growth_df["prior_vol"]) /
                           growth_df["prior_vol"].replace(0, 1)).clip(-0.5, 1.5)

    summary = summary.merge(growth_df[["region", "therapeutic_area", "growth"]],
                            on=["region", "therapeutic_area"], how="left")
    summary["growth"] = summary["growth"].fillna(0)

    # Normalise components 0–1
    for col in ["total_units", "growth"]:
        mn, mx = summary[col].min(), summary[col].max()
        summary[f"{col}_n"] = (summary[col] - mn) / (mx - mn + 1e-9)

    # Generic share is opportunity (high generic = harder for branded reps)
    summary["generic_opp"] = 1 - summary["brand_share"]

    # Composite
    summary["opportunity_score"] = (
        summary["total_units_n"] * 0.40 +
        summary["growth_n"]      * 0.35 +
        summary["generic_opp"]   * 0.25
    ) * 100

    summary["opportunity_score"] = summary["opportunity_score"].round(1)
    summary["opportunity_rank"]  = summary.groupby("therapeutic_area")["opportunity_score"].rank(
        ascending=False, method="min"
    ).astype(int)

    return summary


# Pre-build at import
DF      = build_dispensing_data()
OPP_DF  = compute_opportunity_score(DF)
