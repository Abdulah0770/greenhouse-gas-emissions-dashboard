
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# =========================================================
# PROJECT PATHS
# =========================================================

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
TOTALS_PATH = DATA_DIR / "df_totals.csv"


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="European GHG Emissions Dashboard",
    page_icon="🌍",
    layout="wide"
)


# =========================================================
# LOAD DATA
# =========================================================

@st.cache_data
def load_totals_data():
    df = pd.read_csv(TOTALS_PATH)

    required_columns = {
        "country",
        "country_code",
        "year",
        "sector_level",
        "sector_code",
        "sector",
        "gas",
        "unit",
        "emissions_mt"
    }

    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        st.error(f"Missing required columns in df_totals.csv: {missing_columns}")
        st.stop()

    df["year"] = df["year"].astype(int)
    df["emissions_mt"] = pd.to_numeric(df["emissions_mt"], errors="coerce")
    df = df.dropna(subset=["emissions_mt"])
    df = df.sort_values(["country", "year"]).reset_index(drop=True)

    return df


df_totals = load_totals_data()


# =========================================================
# SIDEBAR CONTROLS
# =========================================================

st.sidebar.title("Dashboard Controls")

st.sidebar.markdown(
    """
    Use these controls to explore total greenhouse gas emissions
    by selected year and country ranking size.
    """
)

available_years = sorted(df_totals["year"].unique())

selected_year = st.sidebar.selectbox(
    "Select year",
    options=available_years,
    index=len(available_years) - 1
)

top_n = st.sidebar.selectbox(
    "Number of countries to show",
    options=[5, 10, 15, 20],
    index=1
)


# =========================================================
# MAIN DASHBOARD HEADER
# =========================================================

st.title("European Greenhouse Gas Emissions Dashboard")

st.markdown(
    """
    This Streamlit dashboard analyses greenhouse gas emissions across European countries
    from **2000 to 2024**. This first section provides an executive overview using
    country-level total emissions.

    **Dataset used:** `df_totals.csv`  
    **Measurement unit:** Mt CO2 eq.
    """
)

st.divider()


# =========================================================
# TAB 1 / SECTION 1: EXECUTIVE OVERVIEW
# =========================================================

st.header("Executive Overview")

st.markdown(
    """
    This section gives a high-level summary of total greenhouse gas emissions.
    It is designed to help users quickly understand the overall emissions trend,
    the highest and lowest emitting countries, and country rankings for a selected year.
    """
)

# ---------------------------------------------------------
# FILTER DATA FOR SELECTED YEAR
# ---------------------------------------------------------

df_selected_year = df_totals[df_totals["year"] == selected_year].copy()

if df_selected_year.empty:
    st.error("No data available for the selected year.")
    st.stop()

# ---------------------------------------------------------
# KPI CALCULATIONS
# ---------------------------------------------------------

selected_year_total = df_selected_year["emissions_mt"].sum()

base_year = df_totals["year"].min()
df_base_year = df_totals[df_totals["year"] == base_year].copy()
base_year_total = df_base_year["emissions_mt"].sum()

if base_year_total != 0:
    change_since_base = ((selected_year_total - base_year_total) / base_year_total) * 100
else:
    change_since_base = 0

highest_row = df_selected_year.loc[df_selected_year["emissions_mt"].idxmax()]
lowest_row = df_selected_year.loc[df_selected_year["emissions_mt"].idxmin()]

highest_country = highest_row["country"]
highest_value = highest_row["emissions_mt"]

lowest_country = lowest_row["country"]
lowest_value = lowest_row["emissions_mt"]

number_of_countries = df_selected_year["country"].nunique()


# ---------------------------------------------------------
# KPI CARDS
# ---------------------------------------------------------

st.subheader("Headline Indicators")

kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

kpi1.metric(
    label="Selected Year",
    value=str(selected_year)
)

kpi2.metric(
    label="Total Emissions",
    value=f"{selected_year_total:,.2f} Mt"
)

kpi3.metric(
    label="Highest Emitter",
    value=highest_country,
    delta=f"{highest_value:,.2f} Mt"
)

kpi4.metric(
    label="Lowest Emitter",
    value=lowest_country,
    delta=f"{lowest_value:,.2f} Mt"
)

kpi5.metric(
    label=f"Change Since {base_year}",
    value=f"{change_since_base:.2f}%"
)

st.caption(f"Number of countries included in selected year: {number_of_countries}")

st.divider()


# ---------------------------------------------------------
# OVERALL EMISSIONS TREND
# ---------------------------------------------------------

st.subheader("Total Emissions Trend Across All Included Countries")

df_total_by_year = (
    df_totals
    .groupby("year", as_index=False)["emissions_mt"]
    .sum()
    .sort_values("year")
)

fig_trend = px.line(
    df_total_by_year,
    x="year",
    y="emissions_mt",
    markers=True,
    title="Total Greenhouse Gas Emissions Across Included Countries, 2000–2024",
    labels={
        "year": "Year",
        "emissions_mt": "Total emissions (Mt CO2 eq.)"
    }
)

fig_trend.update_layout(
    height=450,
    hovermode="x unified",
    margin=dict(l=20, r=20, t=60, b=20)
)

st.plotly_chart(fig_trend, use_container_width=True)

st.markdown(
    f"""
    From **{base_year}** to **{selected_year}**, total emissions across the included
    countries changed by **{change_since_base:.2f}%**.
    """
)

st.divider()


# ---------------------------------------------------------
# TOP EMITTING COUNTRIES BAR CHART
# ---------------------------------------------------------

st.subheader(f"Top {top_n} Emitting Countries in {selected_year}")

df_ranking = (
    df_selected_year
    .sort_values("emissions_mt", ascending=False)
    .reset_index(drop=True)
)

df_top = df_ranking.head(top_n).copy()

fig_top = px.bar(
    df_top,
    x="emissions_mt",
    y="country",
    orientation="h",
    title=f"Top {top_n} Countries by Greenhouse Gas Emissions in {selected_year}",
    labels={
        "country": "Country",
        "emissions_mt": "Emissions (Mt CO2 eq.)"
    },
    text="emissions_mt"
)

fig_top.update_traces(
    texttemplate="%{text:.2f}",
    textposition="outside"
)

fig_top.update_layout(
    yaxis={"categoryorder": "total ascending"},
    height=500,
    margin=dict(l=20, r=20, t=60, b=20)
)

st.plotly_chart(fig_top, use_container_width=True)

st.divider()


# ---------------------------------------------------------
# RANKING TABLE
# ---------------------------------------------------------

st.subheader(f"Full Country Emissions Ranking for {selected_year}")

df_table = df_ranking.copy()
df_table["Rank"] = df_table.index + 1

if selected_year_total != 0:
    df_table["Share of Selected-Year Total (%)"] = (df_table["emissions_mt"] / selected_year_total) * 100
else:
    df_table["Share of Selected-Year Total (%)"] = 0

df_table = df_table[
    [
        "Rank",
        "country",
        "country_code",
        "year",
        "emissions_mt",
        "Share of Selected-Year Total (%)"
    ]
]

df_table = df_table.rename(
    columns={
        "country": "Country",
        "country_code": "Country Code",
        "year": "Year",
        "emissions_mt": "Emissions (Mt CO2 eq.)"
    }
)

st.dataframe(
    df_table.style.format(
        {
            "Emissions (Mt CO2 eq.)": "{:,.2f}",
            "Share of Selected-Year Total (%)": "{:.2f}"
        }
    ),
    use_container_width=True,
    hide_index=True
)

st.info(
    """
    This section uses `df_totals.csv`, which contains country-level total greenhouse gas
    emissions by year. Values are measured in Mt CO2 eq.
    """
)
