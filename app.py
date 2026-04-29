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
SECTORS_PATH = DATA_DIR / "df_sectors.csv"
GASES_PATH = DATA_DIR / "df_gases.csv"
FULL_CLEAN_PATH = DATA_DIR / "df_full_clean.csv"


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="European GHG Emissions Dashboard",
    page_icon="🌍",
    layout="wide"
)


# =========================================================
# DATA LOADING FUNCTIONS
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


@st.cache_data
def load_sectors_data():
    df = pd.read_csv(SECTORS_PATH)

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
        st.error(f"Missing required columns in df_sectors.csv: {missing_columns}")
        st.stop()

    df["year"] = df["year"].astype(int)
    df["emissions_mt"] = pd.to_numeric(df["emissions_mt"], errors="coerce")
    df = df.dropna(subset=["emissions_mt"])
    df = df.sort_values(["country", "year", "sector"]).reset_index(drop=True)

    return df


@st.cache_data
def load_gases_data():
    df = pd.read_csv(GASES_PATH)

    required_columns = {
        "country",
        "country_code",
        "year",
        "sector_level",
        "sector_code",
        "sector",
        "gas",
        "unit",
        "emissions_value"
    }

    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        st.error(f"Missing required columns in df_gases.csv: {missing_columns}")
        st.stop()

    df["year"] = df["year"].astype(int)
    df["emissions_value"] = pd.to_numeric(df["emissions_value"], errors="coerce")
    df = df.dropna(subset=["emissions_value"])
    df = df.sort_values(["country", "year", "gas"]).reset_index(drop=True)

    return df


@st.cache_data
def load_full_clean_data():
    df = pd.read_csv(FULL_CLEAN_PATH)

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
        st.error(f"Missing required columns in df_full_clean.csv: {missing_columns}")
        st.stop()

    df["year"] = df["year"].astype(int)
    df["emissions_mt"] = pd.to_numeric(df["emissions_mt"], errors="coerce")
    df = df.dropna(subset=["emissions_mt"])

    return df


# =========================================================
# LOAD DATA
# =========================================================

df_totals = load_totals_data()
df_sectors = load_sectors_data()
df_gases = load_gases_data()
df_full_clean = load_full_clean_data()

available_years = sorted(df_totals["year"].unique())
all_countries = sorted(df_totals["country"].unique())
all_sectors = sorted(df_sectors["sector"].unique())
all_gases = sorted(df_gases["gas"].unique())

min_year = int(min(available_years))
max_year = int(max(available_years))


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("Dashboard Controls")

st.sidebar.markdown(
    """
    These controls apply mainly to the **Executive Overview** tab.
    Other tabs include their own controls inside each section.
    """
)

selected_year = st.sidebar.selectbox(
    "Select year for overview",
    options=available_years,
    index=len(available_years) - 1
)

top_n = st.sidebar.selectbox(
    "Number of countries to show in overview ranking",
    options=[5, 10, 15, 20],
    index=1
)


# =========================================================
# MAIN HEADER
# =========================================================

st.title("European Greenhouse Gas Emissions Dashboard")

st.markdown(
    """
    This interactive dashboard analyses greenhouse gas emissions across European countries
    from **2000 to 2024** using cleaned European Environment Agency greenhouse-gas data.

    The dashboard is organised into five sections covering overall emissions, country trends,
    sector-level patterns, gas-specific analysis, and the data methodology.
    """
)


# =========================================================
# DASHBOARD TABS
# =========================================================

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "1. Executive Overview",
        "2. Country Trends",
        "3. Sector Analysis",
        "4. Gas Analysis",
        "5. Data & Methodology"
    ]
)


# =========================================================
# TAB 1: EXECUTIVE OVERVIEW
# =========================================================

with tab1:

    st.header("Executive Overview")

    st.markdown(
        """
        This section provides a high-level summary of total greenhouse gas emissions.
        It is designed to help users quickly understand the overall emissions trend,
        the highest and lowest emitting countries, and the country ranking for a selected year.

        **Dataset used:** `df_totals.csv`  
        **Unit:** Mt CO2 eq.
        """
    )

    df_selected_year = df_totals[df_totals["year"] == selected_year].copy()

    if df_selected_year.empty:
        st.error("No data available for the selected year.")
        st.stop()

    selected_year_total = df_selected_year["emissions_mt"].sum()

    base_year = min_year
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
        value=highest_country
    )
    kpi3.caption(f"{highest_value:,.2f} Mt CO2 eq.")

    kpi4.metric(
        label="Lowest Emitter",
        value=lowest_country
    )
    kpi4.caption(f"{lowest_value:,.2f} Mt CO2 eq.")

    kpi5.metric(
        label=f"Change Since {base_year}",
        value=f"{change_since_base:.2f}%"
    )

    st.caption(f"Number of countries included in selected year: {number_of_countries}")

    st.divider()

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

    st.subheader(f"Full Country Emissions Ranking for {selected_year}")

    df_table = df_ranking.copy()
    df_table["Rank"] = df_table.index + 1

    if selected_year_total != 0:
        df_table["Share of Selected-Year Total (%)"] = (
            df_table["emissions_mt"] / selected_year_total
        ) * 100
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


# =========================================================
# TAB 2: COUNTRY TRENDS
# =========================================================

with tab2:

    st.header("Country Trends and Comparison")

    st.markdown(
        """
        This section compares emissions trends between selected countries over a chosen
        time period. It focuses on country-level change rather than the combined total
        shown in the Executive Overview.

        **Dataset used:** `df_totals.csv`  
        **Unit:** Mt CO2 eq.
        """
    )

    default_countries = [
        country for country in ["Germany", "France", "Italy", "Türkiye", "Poland"]
        if country in all_countries
    ]

    selected_countries = st.multiselect(
        "Select countries to compare",
        options=all_countries,
        default=default_countries
    )

    selected_year_range = st.slider(
        "Select year range for comparison",
        min_value=min_year,
        max_value=max_year,
        value=(min_year, max_year),
        step=1
    )

    start_year, end_year = selected_year_range

    if not selected_countries:
        st.warning("Please select at least one country to display the comparison.")
    else:
        df_country_filtered = df_totals[
            (df_totals["country"].isin(selected_countries)) &
            (df_totals["year"] >= start_year) &
            (df_totals["year"] <= end_year)
        ].copy()

        st.subheader("Selected Countries Emissions Trend")

        fig_country_trend = px.line(
            df_country_filtered,
            x="year",
            y="emissions_mt",
            color="country",
            markers=True,
            title=f"Greenhouse Gas Emissions Trend by Country, {start_year}–{end_year}",
            labels={
                "year": "Year",
                "emissions_mt": "Emissions (Mt CO2 eq.)",
                "country": "Country"
            }
        )

        fig_country_trend.update_layout(
            height=500,
            hovermode="x unified",
            margin=dict(l=20, r=20, t=60, b=20)
        )

        st.plotly_chart(fig_country_trend, use_container_width=True)

        st.divider()

        st.subheader(f"Percentage Change by Selected Country, {start_year}–{end_year}")

        df_start = (
            df_totals[df_totals["year"] == start_year]
            [["country", "emissions_mt"]]
            .rename(columns={"emissions_mt": "Start Emissions"})
        )

        df_end = (
            df_totals[df_totals["year"] == end_year]
            [["country", "emissions_mt"]]
            .rename(columns={"emissions_mt": "End Emissions"})
        )

        df_change = pd.merge(df_start, df_end, on="country", how="inner")
        df_change = df_change[df_change["country"].isin(selected_countries)].copy()

        df_change["Absolute Change"] = (
            df_change["End Emissions"] - df_change["Start Emissions"]
        )

        df_change["Percentage Change (%)"] = df_change.apply(
            lambda row: (
                (row["Absolute Change"] / row["Start Emissions"]) * 100
                if row["Start Emissions"] != 0
                else 0
            ),
            axis=1
        )

        df_change = df_change.sort_values("Percentage Change (%)").reset_index(drop=True)

        df_change_display = df_change.rename(columns={"country": "Country"})

        st.dataframe(
            df_change_display.style.format(
                {
                    "Start Emissions": "{:,.2f}",
                    "End Emissions": "{:,.2f}",
                    "Absolute Change": "{:,.2f}",
                    "Percentage Change (%)": "{:.2f}"
                }
            ),
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        st.subheader(f"Largest Emissions Reductions and Increases, {start_year}–{end_year}")

        df_all_start = (
            df_totals[df_totals["year"] == start_year]
            [["country", "emissions_mt"]]
            .rename(columns={"emissions_mt": "Start Emissions"})
        )

        df_all_end = (
            df_totals[df_totals["year"] == end_year]
            [["country", "emissions_mt"]]
            .rename(columns={"emissions_mt": "End Emissions"})
        )

        df_all_change = pd.merge(df_all_start, df_all_end, on="country", how="inner")

        df_all_change["Absolute Change"] = (
            df_all_change["End Emissions"] - df_all_change["Start Emissions"]
        )

        df_all_change["Percentage Change (%)"] = df_all_change.apply(
            lambda row: (
                (row["Absolute Change"] / row["Start Emissions"]) * 100
                if row["Start Emissions"] != 0
                else 0
            ),
            axis=1
        )

        df_all_change = df_all_change.sort_values("Percentage Change (%)").reset_index(drop=True)

        reducers = df_all_change.head(5).copy()
        increasers = df_all_change.tail(5).sort_values("Percentage Change (%)", ascending=False).copy()

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Top 5 percentage reductions**")
            reducers_display = reducers.rename(columns={"country": "Country"})
            st.dataframe(
                reducers_display.style.format(
                    {
                        "Start Emissions": "{:,.2f}",
                        "End Emissions": "{:,.2f}",
                        "Absolute Change": "{:,.2f}",
                        "Percentage Change (%)": "{:.2f}"
                    }
                ),
                use_container_width=True,
                hide_index=True
            )

        with col2:
            st.markdown("**Top 5 percentage increases**")
            increasers_display = increasers.rename(columns={"country": "Country"})
            st.dataframe(
                increasers_display.style.format(
                    {
                        "Start Emissions": "{:,.2f}",
                        "End Emissions": "{:,.2f}",
                        "Absolute Change": "{:,.2f}",
                        "Percentage Change (%)": "{:.2f}"
                    }
                ),
                use_container_width=True,
                hide_index=True
            )


# =========================================================
# TAB 3: SECTOR ANALYSIS
# =========================================================

with tab3:

    st.header("Sector Analysis")

    st.markdown(
        """
        This section analyses greenhouse gas emissions by top-level sector.
        It helps users understand which sectors contribute most to emissions
        and how sector-level emissions change over time.

        **Dataset used:** `df_sectors.csv`  
        **Unit:** Mt CO2 eq.
        """
    )

    sector_country = st.selectbox(
        "Select country for sector analysis",
        options=all_countries,
        index=all_countries.index("Germany") if "Germany" in all_countries else 0
    )

    sector_year = st.selectbox(
        "Select year for sector breakdown",
        options=available_years,
        index=len(available_years) - 1
    )

    include_other_sector = st.checkbox(
        "Include 'Other' sector",
        value=True
    )

    sector_options = all_sectors.copy()

    if not include_other_sector and "Other" in sector_options:
        sector_options = [sector for sector in sector_options if sector != "Other"]

    selected_sectors = st.multiselect(
        "Select sectors for trend chart",
        options=sector_options,
        default=sector_options
    )

    df_sector_country_year = df_sectors[
        (df_sectors["country"] == sector_country) &
        (df_sectors["year"] == sector_year)
    ].copy()

    if not include_other_sector:
        df_sector_country_year = df_sector_country_year[
            df_sector_country_year["sector"] != "Other"
        ].copy()

    # Apply selected sector filter to the sector breakdown chart
    if selected_sectors:
        df_sector_country_year = df_sector_country_year[
            df_sector_country_year["sector"].isin(selected_sectors)
        ].copy()
    else:
        st.warning("Please select at least one sector to display the sector breakdown.")

    df_sector_country_year = df_sector_country_year.sort_values(
        "emissions_mt",
        ascending=False
    )

    st.subheader(f"Sector Breakdown for {sector_country} in {sector_year}")

    fig_sector_bar = px.bar(
        df_sector_country_year,
        x="sector",
        y="emissions_mt",
        title=f"Greenhouse Gas Emissions by Sector: {sector_country}, {sector_year}",
        labels={
            "sector": "Sector",
            "emissions_mt": "Emissions (Mt CO2 eq.)"
        },
        text="emissions_mt"
    )

    fig_sector_bar.update_traces(
        texttemplate="%{text:.2f}",
        textposition="outside"
    )

    fig_sector_bar.update_layout(
        height=500,
        xaxis_tickangle=-30,
        margin=dict(l=20, r=20, t=60, b=120)
    )

    st.plotly_chart(fig_sector_bar, use_container_width=True)

    st.caption(
        "Note: Land Use (LULUCF) can be negative because it may represent net removals or absorption."
    )

    st.divider()

    if not selected_sectors:
        st.warning("Please select at least one sector.")
    else:
        df_sector_trend = df_sectors[
            (df_sectors["country"] == sector_country) &
            (df_sectors["sector"].isin(selected_sectors))
        ].copy()

        fig_sector_trend = px.line(
            df_sector_trend,
            x="year",
            y="emissions_mt",
            color="sector",
            markers=True,
            title=f"Sector Emissions Trend: {sector_country}, {min_year}–{max_year}",
            labels={
                "year": "Year",
                "emissions_mt": "Emissions (Mt CO2 eq.)",
                "sector": "Sector"
            }
        )

        fig_sector_trend.update_layout(
            height=500,
            hovermode="x unified",
            margin=dict(l=20, r=20, t=60, b=20)
        )

        st.plotly_chart(fig_sector_trend, use_container_width=True)

    st.divider()

    st.subheader(f"Country Ranking for Selected Sector in {sector_year}")

    ranking_sector = st.selectbox(
        "Select sector for country ranking",
        options=sector_options,
        index=sector_options.index("Energy") if "Energy" in sector_options else 0
    )

    df_sector_ranking = df_sectors[
        (df_sectors["sector"] == ranking_sector) &
        (df_sectors["year"] == sector_year)
    ].copy()

    df_sector_ranking = df_sector_ranking.sort_values(
        "emissions_mt",
        ascending=False
    ).head(10)

    fig_sector_ranking = px.bar(
        df_sector_ranking,
        x="emissions_mt",
        y="country",
        orientation="h",
        title=f"Top 10 Countries for {ranking_sector} Emissions in {sector_year}",
        labels={
            "country": "Country",
            "emissions_mt": "Emissions (Mt CO2 eq.)"
        },
        text="emissions_mt"
    )

    fig_sector_ranking.update_traces(
        texttemplate="%{text:.2f}",
        textposition="outside"
    )

    fig_sector_ranking.update_layout(
        yaxis={"categoryorder": "total ascending"},
        height=500,
        margin=dict(l=20, r=20, t=60, b=20)
    )

    st.plotly_chart(fig_sector_ranking, use_container_width=True)


# =========================================================
# TAB 4: GAS ANALYSIS
# =========================================================

with tab4:

    st.header("Gas Analysis")

    st.markdown(
        """
        This section analyses individual greenhouse gases. Users select one gas at a time
        to avoid misleading comparisons because the gas-level dataset contains mixed units.

        **Dataset used:** `df_gases.csv`
        """
    )

    selected_gas = st.selectbox(
        "Select greenhouse gas",
        options=all_gases,
        index=all_gases.index("CO2") if "CO2" in all_gases else 0
    )

    df_selected_gas_all = df_gases[df_gases["gas"] == selected_gas].copy()

    gas_units = sorted(df_selected_gas_all["unit"].unique().tolist())
    selected_gas_unit = gas_units[0] if gas_units else "Unknown unit"

    st.info(
        f"""
        Selected gas: **{selected_gas}**  
        Unit for selected gas: **{selected_gas_unit}**

        This section analyses one gas at a time. It does not combine all gases because
        CO2, CH4 and N2O are measured in Gg, while fluorinated gases are measured in Mt CO2 eq.
        """
    )

    gas_countries_default = [
        country for country in ["Germany", "France", "Italy", "Türkiye", "Poland"]
        if country in all_countries
    ]

    selected_gas_countries = st.multiselect(
        "Select countries for gas trend",
        options=all_countries,
        default=gas_countries_default
    )

    gas_year_range = st.slider(
        "Select year range for gas trend",
        min_value=min_year,
        max_value=max_year,
        value=(min_year, max_year),
        step=1,
        key="gas_year_range"
    )
        gas_start_year, gas_end_year = gas_year_range


    if not selected_gas_countries:
        st.warning("Please select at least one country for the gas trend chart.")
    else:
        df_gas_trend = df_gases[
            (df_gases["gas"] == selected_gas) &
            (df_gases["country"].isin(selected_gas_countries)) &
            (df_gases["year"] >= gas_start_year) &
            (df_gases["year"] <= gas_end_year)
        ].copy()

        st.subheader(f"{selected_gas} Trend by Selected Country")

        fig_gas_trend = px.line(
            df_gas_trend,
            x="year",
            y="emissions_value",
            color="country",
            markers=True,
            title=f"{selected_gas} Trend by Country, {gas_start_year}–{gas_end_year}",
            labels={
                "year": "Year",
                "emissions_value": f"{selected_gas} emissions ({selected_gas_unit})",
                "country": "Country"
            }
        )

        fig_gas_trend.update_layout(
            height=500,
            hovermode="x unified",
            margin=dict(l=20, r=20, t=60, b=20)
        )

        st.plotly_chart(fig_gas_trend, use_container_width=True)

    st.divider()

    selected_gas_ranking_year = st.selectbox(
        "Select year for gas country ranking",
        options=available_years,
        index=len(available_years) - 1,
        key="gas_ranking_year"
    )

    st.subheader(f"Top Countries for {selected_gas} in {selected_gas_ranking_year}")
    df_gas_ranking = df_gases[
        (df_gases["gas"] == selected_gas) &
        (df_gases["year"] == selected_gas_ranking_year)
    ].copy()

    df_gas_ranking = df_gas_ranking.sort_values(
        "emissions_value",
        ascending=False
    ).reset_index(drop=True)

    df_gas_top = df_gas_ranking.head(10)

    fig_gas_ranking = px.bar(
        df_gas_top,
        x="emissions_value",
        y="country",
        orientation="h",
        title=f"Top 10 Countries for {selected_gas} in {selected_gas_ranking_year}",
        labels={
            "country": "Country",
            "emissions_value": f"{selected_gas} emissions ({selected_gas_unit})"
        },
        text="emissions_value"
    )

    fig_gas_ranking.update_traces(
        texttemplate="%{text:.2f}",
        textposition="outside"
    )

    fig_gas_ranking.update_layout(
        yaxis={"categoryorder": "total ascending"},
        height=500,
        margin=dict(l=20, r=20, t=60, b=20)
    )

    st.plotly_chart(fig_gas_ranking, use_container_width=True)

    df_gas_table = df_gas_ranking.copy()
    df_gas_table["Rank"] = df_gas_table.index + 1

    df_gas_table = df_gas_table[
        [
            "Rank",
            "country",
            "country_code",
            "year",
            "gas",
            "unit",
            "emissions_value"
        ]
    ]

    df_gas_table = df_gas_table.rename(
        columns={
            "country": "Country",
            "country_code": "Country Code",
            "year": "Year",
            "gas": "Gas",
            "unit": "Unit",
            "emissions_value": "Emissions Value"
        }
    )

    st.dataframe(
        df_gas_table.style.format(
            {
                "Emissions Value": "{:,.2f}"
            }
        ),
        use_container_width=True,
        hide_index=True
    )


# =========================================================
# TAB 5: DATA AND METHODOLOGY
# =========================================================

with tab5:

    st.header("Data and Methodology")

    st.markdown(
        """
        This section explains the datasets used in the dashboard, the cleaned file structure,
        and key limitations that users should understand when interpreting the visualisations.
        """
    )

    st.subheader("Dataset Source and Scope")

    st.markdown(
        """
        The dashboard uses cleaned greenhouse-gas emissions data derived from the
        European Environment Agency dataset selected for this coursework.

        The dashboard focuses on:
        - European countries included in the cleaned dataset
        - Years **2000 to 2024**
        - Total greenhouse gas emissions
        - Top-level sector emissions
        - Individual greenhouse gases
        """
    )

    st.divider()

    st.subheader("Cleaned Files Used")

    file_summary = pd.DataFrame(
        [
            {
                "File": "df_totals.csv",
                "Purpose": "Country-level total greenhouse gas emissions over time",
                "Rows": len(df_totals),
                "Columns": len(df_totals.columns),
                "Countries": df_totals["country"].nunique(),
                "Year Range": f"{df_totals['year'].min()}–{df_totals['year'].max()}",
                "Main Value Column": "emissions_mt",
                "Unit Notes": "Mt CO2 eq."
            },
            {
                "File": "df_sectors.csv",
                "Purpose": "Top-level sector emissions by country and year",
                "Rows": len(df_sectors),
                "Columns": len(df_sectors.columns),
                "Countries": df_sectors["country"].nunique(),
                "Year Range": f"{df_sectors['year'].min()}–{df_sectors['year'].max()}",
                "Main Value Column": "emissions_mt",
                "Unit Notes": "Mt CO2 eq."
            },
            {
                "File": "df_gases.csv",
                "Purpose": "Individual greenhouse gas values by country and year",
                "Rows": len(df_gases),
                "Columns": len(df_gases.columns),
                "Countries": df_gases["country"].nunique(),
                "Year Range": f"{df_gases['year'].min()}–{df_gases['year'].max()}",
                "Main Value Column": "emissions_value",
                "Unit Notes": "Mixed units; use selected gas unit"
            },
            {
                "File": "df_full_clean.csv",
                "Purpose": "Full cleaned master dataset retained as reference",
                "Rows": len(df_full_clean),
                "Columns": len(df_full_clean.columns),
                "Countries": df_full_clean["country"].nunique(),
                "Year Range": f"{df_full_clean['year'].min()}–{df_full_clean['year'].max()}",
                "Main Value Column": "emissions_mt",
                "Unit Notes": "Contains mixed units depending on row"
            }
        ]
    )

    st.dataframe(file_summary, use_container_width=True, hide_index=True)

    st.divider()

    st.subheader("Data Quality Checks")

    quality_summary = pd.DataFrame(
        [
            {
                "File": "df_totals.csv",
                "Missing Values in Main Value Column": int(df_totals["emissions_mt"].isna().sum()),
                "Duplicate Rows": int(df_totals.duplicated().sum())
            },
            {
                "File": "df_sectors.csv",
                "Missing Values in Main Value Column": int(df_sectors["emissions_mt"].isna().sum()),
                "Duplicate Rows": int(df_sectors.duplicated().sum())
            },
            {
                "File": "df_gases.csv",
                "Missing Values in Main Value Column": int(df_gases["emissions_value"].isna().sum()),
                "Duplicate Rows": int(df_gases.duplicated().sum())
            },
            {
                "File": "df_full_clean.csv",
                "Missing Values in Main Value Column": int(df_full_clean["emissions_mt"].isna().sum()),
                "Duplicate Rows": int(df_full_clean.duplicated().sum())
            }
        ]
    )

    st.dataframe(quality_summary, use_container_width=True, hide_index=True)

    st.divider()

    st.subheader("Main Cleaning and Preparation Steps")

    st.markdown(
        """
        The cleaned files were prepared from the original downloaded emissions dataset.
        The main preparation steps were:

        1. Removed unnecessary metadata columns.
        2. Standardised column names.
        3. Filtered the dataset to the period **2000–2024**.
        4. Removed aggregate rows that could cause double counting.
        5. Created a country-level total emissions file for overview and country analysis.
        6. Created a top-level sector file for sector analysis.
        7. Created a gas-level file for individual gas analysis.
        8. Preserved the full cleaned master file for reference.
        """
    )

    st.divider()

    st.subheader("Important Limitations")

    st.warning(
        """
        Gas-level analysis must be interpreted carefully because `df_gases.csv`
        contains mixed units. CO2, CH4 and N2O are measured in Gg, while HFCs,
        PFCs, SF6 and NF3 are measured in Mt CO2 eq. For this reason, the Gas Analysis
        tab analyses one gas at a time and clearly displays the selected gas unit.
        """
    )

    st.info(
        """
        Land Use (LULUCF) values in the sector dataset can be negative. This is not
        treated as an error because negative values may represent net removals or
        absorption.
        """
    )

    st.markdown(
        """
        This dashboard is descriptive rather than predictive. It is designed to help
        users explore historical emissions patterns, not to forecast future emissions.
        """
    )
