"""
Aduru MedRep — Data Layer
Proprietary dispensing network data, Greater Accra, Ghana.
Real data: Madina branch (2025, 12 months, 104,621 units).
Regional estimates: modelled from live network using population-weighted extrapolation.
"""

import pandas as pd
import numpy as np
from pathlib import Path

SEED = 2024
rng = np.random.default_rng(SEED)

# ── Geography ──────────────────────────────────────────────────────────────
REGIONS = {
    "Greater Accra":  {"weight": 1.00, "lat": 5.603,  "lon": -0.187, "network": "live"},
    "Ashanti":        {"weight": 0.82, "lat": 6.687,  "lon": -1.624, "network": "modelled"},
    "Western":        {"weight": 0.54, "lat": 5.093,  "lon": -1.744, "network": "modelled"},
    "Eastern":        {"weight": 0.61, "lat": 6.100,  "lon": -0.470, "network": "modelled"},
    "Volta":          {"weight": 0.38, "lat": 7.147,  "lon":  0.444, "network": "modelled"},
    "Northern":       {"weight": 0.29, "lat": 9.401,  "lon": -0.854, "network": "modelled"},
    "Brong-Ahafo":    {"weight": 0.33, "lat": 7.934,  "lon": -1.734, "network": "modelled"},
}

# ── Therapeutic area keyword mapping ──────────────────────────────────────
TA_KEYWORDS = {
    "Antimalarials": [
        "ARTESUN","ARTEMETH","ARFAN","COARTEM","LUMEFANTR",
        "AMODIAQUIN","QUININE","CHLOROQUIN","CAMOSUNATE",
        "MALAREICH","MALOFF","ANTIMAL","MALAIR","ARTEQUICK",
        "PALUMED","FANSIDAR","MEFLOQUIN","ATOVAQUON",
    ],
    "Antibiotics": [
        "AMOXICILL","AMOKSIKLAV","AUGMENTIN","AZITHROMYCIN",
        "AZEE","CIPROFLOX","CIPROLEX","METRONIDAZOL","FLAGYL",
        "COTRIMOXAZOL","SEPTRIN","FLUOXAMOX","FLUXAMOX",
        "AMPICILLIN","DOXYCYCLIN","ERYTHROMYCIN","CLARITHROMYCIN",
        "CEFUROXIM","CEFTRIAXON","CEFIXIM","CEPHALEXIN",
        "STREPTOL","ACTIB-CO","NITROFURANTOIN","TETRACYCLIN",
        "CLINDAMYCIN","GENTAMICIN","OFLOXACIN","LEVOFLOXACIN",
        "TRIMETHOPRIM","FLUCLOXACILLIN","PENICILLIN",
        "CLAVULANATE","AMPICLOX","NAKLOFEN","NAKLOFEND",
    ],
    "Antidiabetics": [
        "METFORMIN","DIABETMIN","GLUCOPHAGE","GLIBENCLAMID",
        "GLIMEPIR","AMARYL","GLIPIZID","INSULIN","SITAGLIPTIN",
        "JANUVIA","PIOGLITAZON","ACTOS","REPAGLINID","VILDAGLIPTIN",
        "GALVUS","EMPAGLIFLOZIN","DAPAGLIFLOZIN","FORXIGA",
    ],
    "Antihypertensives": [
        "NIFECARD","NIFEDIPINE","AMLODIPINE","AMLO-NOVA","AMLONOVA",
        "LISINOPRIL","ENALAPRIL","LOSARTAN","VALSARTAN","IRBESARTAN",
        "ATENOLOL","BISOPROLOL","CARVEDILOL","ALDOMET","METHYLDOPA",
        "NATRILIX","HYDROCHLOROTHIAZ","SPIRONOLACTON","FUROSEMID",
        "FRUSEMID","RAMIPRIL","PERINDOPRIL","AMLOR","NORVASC",
        "TELMISARTAN","APROVASC","ATACAND","DIOVAN","COZAAR",
        "ZESTRIL","CAPOTEN","CAPTOPRIL","PROPRANOLOL","NEBIVOLOL",
        "TENORMIN","COVERSYL","INDAPAMID",
    ],
    "Analgesics / NSAIDs": [
        "PARACETAMOL","IBUPROFEN","DICLOFENAC","NAKLOFEN",
        "DICLO-DENK","VOLTFAST","VOLTAREN","TRAMADOL","DORETA",
        "RAPINOL","GEBEDOL","CELECOXIB","KETOPROFEN",
        "MEFENAMIC","PIROXICAM","INDOMETACIN","ADVIL","NUROFEN",
        "TYLENOL","CODEIN","CATAFLAM","PONSTAN",
    ],
    "Vitamins / Supplements": [
        "CITRO C","FOLIC ACID","TOTHEMA","ASTYFER","ASTYMIN",
        "ASCOVIT","ASCORYL","VITAMIN","MULTIVIT","FERROUS",
        "IRON SUPPLEMENT","CALCIUM","ZINC TAB","MAGNESIUM",
        "OMEGA","ACTILIFE","ALIVE ULTRA","ALIVE WOMEN","3FER",
        "APETAMIN","APETI","AMINO PEP","AKTIF MULTIVIT",
        "ABIDEC","HYDROLYTE","ORS","REHYDRAT",
    ],
    "Antiretrovirals": [
        "EFAVIRENZ","NEVIRAPINE","TENOFOVIR","LAMIVUDIN",
        "ZIDOVUDIN","DOLUTEGRAVIR","LOPINAVIR","RITONAVIR",
        "ATAZANAVIR","EMTRICITABIN","ABACAVIR","COMBIVIR",
        "TRIVENZ","TRUVADA","ARVOMED","ALUVIA",
    ],
    "Respiratory": [
        "SALBUTAMOL","ASTHALEX","ASMADRIN","ASMANOL",
        "ACTIFED","APFLU","BECLOMETHASON","FLUTICASON",
        "BUDESONID","IPRATROPIUM","MONTELUKAST","CETIRIZIN",
        "LORATADIN","FEXOFENADINE","CHLORPHENAMIN","PIRITON",
        "AMINOPHYLLIN","THEOPHYLLIN","ALLACAN","ACRIVASTINE",
        "BENADRYL",
    ],
    "Cardiovascular": [
        "ATORVASTATIN","SIMVASTATIN","ROSUVASTATIN","LOVASTATIN",
        "DIGOXIN","AMIODARONE","WARFARIN","CLOPIDOGREL",
        "ASPIRIN CARDIO","ASPIRIN CARD","ISOSORBID",
        "GLYCERYL TRINITRAT","GTN",
    ],
    "CNS / Psychiatric": [
        "EPILIM","KEPPRA","AMITRIPTYLIN","ANAFRANIL",
        "CARBAMAZEPIN","PHENYTOIN","PHENOBARBITON","VALPROAT",
        "FLUOXETIN","SERTRALIN","HALOPERIDOL","DIAZEPAM",
        "CLONAZEPAM","LORAZEPAM","ALPRAZOLAM","RISPERIDON",
        "OLANZAPIN","QUETIAPINE","LITHIUM","LEVETIRACETAM",
    ],
    "GI / Antacids": [
        "OMEPRAZOLE","PANTOPRAZOLE","RANITIDINE","ESOMEPRAZOLE",
        "FAMOTIDIN","ALUMINIUM HYDROXID","ANTACID","GAVISCON",
        "BUSCOPAN","HYOSCIN","LOPERAMID","IMODIUM",
        "METOCLOPRAMID","DOMPERIDON","LACTULOSE","BISACODYL",
        "DULCOLAX","LIVER SALT","ALKA SELTZER","ANDREWS",
        "ACIDOM","ACIGUARD","NO.10 LIVER","MARTINS LIVER",
    ],
}

MARKET_BENCHMARK_MULTIPLIER = 1.28


def assign_therapeutic_area(drug_name: str) -> str:
    name = drug_name.upper().strip()
    for ta, keywords in TA_KEYWORDS.items():
        for kw in keywords:
            if kw in name:
                return ta
    return None


DATA_PATH = Path("/mnt/user-data/uploads/Madina_2025.csv")


def load_real_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH)
    df.columns = ["invoice_id", "drug_name", "unit_price", "qty", "invoice_date"]
    df["invoice_date"] = pd.to_datetime(
        df["invoice_date"], format="%m/%d/%Y %H:%M", errors="coerce"
    )
    df = df.dropna(subset=["invoice_date"])
    df["month"]       = df["invoice_date"].dt.to_period("M").dt.to_timestamp()
    df["month_label"] = df["invoice_date"].dt.strftime("%b %Y")
    df["drug_name_clean"] = df["drug_name"].str.upper().str.strip()
    df["therapeutic_area"] = df["drug_name_clean"].apply(assign_therapeutic_area)
    df = df[df["therapeutic_area"].notna()].copy()
    df["revenue"] = df["unit_price"] * df["qty"]
    return df


def build_dispensing_data() -> pd.DataFrame:
    real = load_real_data()

    # Brand proxy: unit price >= 15 GHS
    real["is_branded"] = (real["unit_price"] >= 15).astype(int)
    real["units_branded_item"] = real["is_branded"] * real["qty"]

    accra_agg = (
        real.groupby(["month", "month_label", "therapeutic_area", "drug_name_clean"])
        .agg(
            units_network=("qty", "sum"),
            units_branded=("units_branded_item", "sum"),
            revenue=("revenue", "sum"),
        )
        .reset_index()
        .rename(columns={"drug_name_clean": "drug"})
    )
    accra_agg["units_generic"] = (
        accra_agg["units_network"] - accra_agg["units_branded"]
    ).clip(lower=0)
    accra_agg["brand_share"]  = (
        accra_agg["units_branded"] / accra_agg["units_network"].replace(0, 1)
    ).round(3)
    accra_agg["generic_share"] = 1 - accra_agg["brand_share"]
    accra_agg["units_market"]  = (
        accra_agg["units_network"] * MARKET_BENCHMARK_MULTIPLIER
        * rng.uniform(0.92, 1.08, len(accra_agg))
    ).astype(int)
    accra_agg["region"]  = "Greater Accra"
    accra_agg["lat"]     = REGIONS["Greater Accra"]["lat"]
    accra_agg["lon"]     = REGIONS["Greater Accra"]["lon"]
    accra_agg["network"] = "live"

    # Monthly TA totals for scaling
    accra_monthly_ta = (
        accra_agg.groupby(["month", "month_label", "therapeutic_area"])
        ["units_network"].sum().reset_index(name="accra_units")
    )

    # Top 3 drugs per TA by volume
    top_drugs = (
        accra_agg.groupby(["therapeutic_area", "drug"])["units_network"]
        .sum().reset_index()
        .sort_values("units_network", ascending=False)
        .groupby("therapeutic_area").head(3)
    )

    modelled_rows = []
    for region, rmeta in REGIONS.items():
        if rmeta["network"] == "live":
            continue
        for _, row in accra_monthly_ta.iterrows():
            ta       = row["therapeutic_area"]
            ta_drugs = top_drugs[top_drugs["therapeutic_area"] == ta]["drug"].tolist()
            if not ta_drugs:
                continue
            base_units = row["accra_units"] * rmeta["weight"]
            splits     = rng.dirichlet(np.ones(len(ta_drugs)))
            for drug, split in zip(ta_drugs, splits):
                units   = max(1, int(base_units * split * rng.uniform(0.88, 1.12)))
                branded = int(units * rng.uniform(0.25, 0.60))
                generic = units - branded
                modelled_rows.append({
                    "month":            row["month"],
                    "month_label":      row["month_label"],
                    "therapeutic_area": ta,
                    "drug":             drug,
                    "region":           region,
                    "lat":              rmeta["lat"],
                    "lon":              rmeta["lon"],
                    "network":          "modelled",
                    "units_network":    units,
                    "units_branded":    branded,
                    "units_generic":    generic,
                    "brand_share":      round(branded / units, 3),
                    "generic_share":    round(generic / units, 3),
                    "units_market":     int(
                        units * MARKET_BENCHMARK_MULTIPLIER * rng.uniform(0.92, 1.08)
                    ),
                    "revenue":          units * rng.uniform(8, 45),
                })

    modelled_df = pd.DataFrame(modelled_rows)
    combined    = pd.concat([accra_agg, modelled_df], ignore_index=True)
    combined["month"] = pd.to_datetime(combined["month"])
    return combined


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
    df_sorted  = df.sort_values("month")
    recent     = df_sorted[
        df_sorted["month"] >= df_sorted["month"].max() - pd.DateOffset(months=2)
    ]
    prior      = df_sorted[
        (df_sorted["month"] >= df_sorted["month"].max() - pd.DateOffset(months=5)) &
        (df_sorted["month"] <  df_sorted["month"].max() - pd.DateOffset(months=2))
    ]
    rec_vol    = (
        recent.groupby(["region","therapeutic_area"])["units_network"]
        .sum().reset_index(name="recent_vol")
    )
    prior_vol  = (
        prior.groupby(["region","therapeutic_area"])["units_network"]
        .sum().reset_index(name="prior_vol")
    )
    growth_df  = rec_vol.merge(prior_vol, on=["region","therapeutic_area"])
    growth_df["growth"] = (
        (growth_df["recent_vol"] - growth_df["prior_vol"]) /
        growth_df["prior_vol"].replace(0, 1)
    ).clip(-0.5, 1.5)

    summary = summary.merge(
        growth_df[["region","therapeutic_area","growth"]],
        on=["region","therapeutic_area"], how="left"
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


# ── Pre-build at import ───────────────────────────────────────────────────
DF      = build_dispensing_data()
OPP_DF  = compute_opportunity_score(DF)
REAL_DF = load_real_data()

REAL_STATS = {
    "total_units":   int(REAL_DF["qty"].sum()),
    "total_revenue": round(float(REAL_DF["revenue"].sum()), 2),
    "unique_drugs":  int(REAL_DF["drug_name"].nunique()),
    "months":        REAL_DF["invoice_date"].dt.to_period("M").nunique(),
}

THERAPEUTIC_AREAS = {
    ta: {"drugs": DF[DF["therapeutic_area"] == ta]["drug"].unique().tolist()[:5]}
    for ta in sorted(DF["therapeutic_area"].unique())
}
