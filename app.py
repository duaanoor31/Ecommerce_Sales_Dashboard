from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


st.set_page_config(
    page_title="Commerce Pulse | Sales Intelligence",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)


ROOT = Path(__file__).resolve().parent
REQUIRED_COLUMNS = [
    "Year",
    "Month",
    "Category",
    "Region",
    "Units_Sold",
    "Revenue",
    "Profit",
    "Customer_Rating",
    "Ad_Spend",
]
NUMERIC_COLUMNS = [
    "Year",
    "Units_Sold",
    "Revenue",
    "Profit",
    "Customer_Rating",
    "Ad_Spend",
]
MONTH_ORDER = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]
MONTH_NUMBERS = {name.casefold(): number for number, name in enumerate(MONTH_ORDER, start=1)}
SEASONS = {
    12: "Winter", 1: "Winter", 2: "Winter",
    3: "Spring", 4: "Spring", 5: "Spring",
    6: "Summer", 7: "Summer", 8: "Summer",
    9: "Autumn", 10: "Autumn", 11: "Autumn",
}

NOTEBOOK_TOTALS = {
    "records": 1000,
    "units": 263337,
    "revenue": 27123544.52,
    "profit": 5494732.66,
    "ad_spend": 2649554.61,
}

# These are the five head and five tail rows preserved in the notebook output.
# The source CSV was not included, so they are shown only as a preview.
NOTEBOOK_PREVIEW = [
    [2020, "April", "Home Decor", "North", 485, 94360.58, 25442.39, 1.5, 174.51],
    [2021, "October", "Fashion", "South", 95, 14081.40, 3457.23, 3.5, 3975.18],
    [2022, "February", "Groceries", "East", 182, 13700.50, 3985.61, 3.4, 1929.31],
    [2020, "April", "Fashion", "South", 419, 81856.23, 20726.68, 2.8, 3706.92],
    [2020, "September", "Beauty Products", "North", 469, 51810.41, 5624.12, 2.9, 2362.07],
    [2023, "January", "Fashion", "West", 38, 5606.14, 1577.25, 3.2, 4788.84],
    [2024, "October", "Groceries", "East", 422, 13513.47, 2667.70, 3.1, 495.29],
    [2021, "January", "Electronics", "North", 85, 14304.92, 2047.38, 2.1, 370.55],
    [2024, "May", "Groceries", "South", 434, 66941.72, 14621.33, 2.5, 2944.75],
    [2021, "October", "Beauty Products", "North", 211, 19643.44, 2722.46, 1.5, 218.01],
]


st.markdown(
    """
    <style>
    :root { --ink: #eaf1ff; --muted: #92a1bb; --mint: #69e0bd; --line: rgba(166,190,226,.13); }
    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
    .stApp { background: radial-gradient(ellipse at 73% -8%, rgba(62,112,184,.23), transparent 34%), #0b1020; color: var(--ink); }
    [data-testid="stHeader"] { background: transparent; }
    [data-testid="stSidebar"] { background: #0d1425; border-right: 1px solid var(--line); }
    [data-testid="stSidebar"] .block-container { padding-top: 1.6rem; }
    h1, h2, h3 { font-family: 'Manrope', sans-serif; letter-spacing: -.035em; }
    h1 { font-size: clamp(2rem, 4vw, 3.1rem) !important; line-height: 1.07 !important; }
    h2 { font-size: 1.35rem !important; }
    [data-testid="stMetric"] { background: linear-gradient(145deg, rgba(23,33,56,.94), rgba(17,25,44,.86)); border: 1px solid var(--line); padding: 17px 19px; border-radius: 16px; min-height: 116px; }
    [data-testid="stMetricLabel"] { color: #9caecb !important; font-size: .81rem !important; }
    [data-testid="stMetricValue"] { color: #f3f7ff !important; font-family: 'Manrope',sans-serif; font-size: 1.65rem !important; }
    [data-testid="stMetricDelta"] { font-size: .78rem !important; }
    .hero-kicker { color: var(--mint); font-size: .72rem; font-weight: 700; text-transform: uppercase; letter-spacing: .19em; margin-bottom: .65rem; }
    .hero-copy { color: #a6b3ca; max-width: 720px; margin-top: -.2rem; line-height: 1.65; }
    .section-kicker { color: #8fa0bd; font-size: .73rem; font-weight: 700; text-transform: uppercase; letter-spacing: .16em; margin: .2rem 0 .55rem; }
    .insight-card { border: 1px solid var(--line); background: linear-gradient(145deg, rgba(22,33,56,.9), rgba(17,24,43,.82)); padding: 17px 19px; border-radius: 15px; height: 100%; }
    .insight-label { color: #90a0ba; font-size: .72rem; font-weight: 700; text-transform: uppercase; letter-spacing: .12em; }
    .insight-value { color: #f0f5ff; font: 700 1.1rem 'Manrope',sans-serif; padding-top: 8px; }
    .insight-detail { color: #a0aec5; font-size: .86rem; line-height: 1.5; padding-top: 5px; }
    div[data-testid="stTabs"] button { color: #a5b2c9; }
    div[data-testid="stTabs"] button[aria-selected="true"] { color: #74e4c4; }
    .small-note { color: #91a0b8; font-size: .83rem; }
    div[data-testid="stAlert"] { border-radius: 13px; }
    </style>
    """,
    unsafe_allow_html=True,
)


def read_source(uploaded_file) -> tuple[pd.DataFrame, str]:
    if uploaded_file is not None:
        return pd.read_csv(uploaded_file), "uploaded"

    for candidate in (ROOT / "ecommerce_sales_data.csv", ROOT / "data" / "ecommerce_sales_data.csv"):
        if candidate.exists():
            return pd.read_csv(candidate), "local"

    return pd.DataFrame(NOTEBOOK_PREVIEW, columns=REQUIRED_COLUMNS), "preview"


def prepare_data(raw: pd.DataFrame) -> pd.DataFrame:
    frame = raw.copy()
    frame.columns = [str(col).strip() for col in frame.columns]
    missing = [col for col in REQUIRED_COLUMNS if col not in frame.columns]
    if missing:
        raise ValueError("Missing required columns: " + ", ".join(missing))

    for col in NUMERIC_COLUMNS:
        frame[col] = pd.to_numeric(frame[col], errors="coerce")

    for col in ["Month", "Category", "Region"]:
        frame[col] = frame[col].astype("string").str.strip()

    month_numbers = frame["Month"].str.casefold().map(MONTH_NUMBERS)
    frame["Date"] = pd.to_datetime(
        frame["Year"].astype("Int64").astype("string") + "-" + month_numbers.astype("Int64").astype("string") + "-01",
        errors="coerce",
    )
    frame["Season"] = month_numbers.map(SEASONS)
    frame["Profit_Margin"] = frame["Profit"] / frame["Revenue"].where(frame["Revenue"] != 0)
    frame["Price_Per_Unit"] = frame["Revenue"] / frame["Units_Sold"].where(frame["Units_Sold"] != 0)
    frame["ROAS"] = frame["Revenue"] / frame["Ad_Spend"].where(frame["Ad_Spend"] != 0)
    return frame


def money(value: float, compact: bool = False) -> str:
    if pd.isna(value):
        return "—"
    if compact and abs(value) >= 1_000_000:
        return f"${value / 1_000_000:,.2f}M"
    if compact and abs(value) >= 10_000:
        return f"${value / 1_000:,.1f}K"
    return f"${value:,.2f}"


def rate(value: float, suffix: str = "%") -> str:
    if pd.isna(value):
        return "—"
    return f"{value:.1f}{suffix}"


def chart_style(fig, height: int = 340):
    fig.update_layout(
        height=height,
        margin=dict(l=12, r=12, t=24, b=12),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans, sans-serif", color="#c8d3e7", size=12),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        hoverlabel=dict(bgcolor="#111a2d", bordercolor="#283a5b", font_color="#f1f5ff"),
    )
    fig.update_xaxes(gridcolor="rgba(165,190,225,.09)", zerolinecolor="rgba(165,190,225,.13)")
    fig.update_yaxes(gridcolor="rgba(165,190,225,.09)", zerolinecolor="rgba(165,190,225,.13)")
    return fig


def insight_card(label: str, value: str, detail: str):
    st.markdown(
        f'<div class="insight-card"><div class="insight-label">{label}</div>'
        f'<div class="insight-value">{value}</div><div class="insight-detail">{detail}</div></div>',
        unsafe_allow_html=True,
    )


st.sidebar.markdown('<div class="hero-kicker">COMMERCE PULSE</div>', unsafe_allow_html=True)
st.sidebar.title("Explore your sales")
st.sidebar.caption("Filter every chart and metric in this dashboard.")
uploaded = st.sidebar.file_uploader("Upload the full sales CSV", type=["csv"])

try:
    raw_data, source_mode = read_source(uploaded)
    data = prepare_data(raw_data)
except Exception as exc:
    st.error(f"Could not read this dataset: {exc}")
    st.stop()

if source_mode == "preview":
    st.sidebar.info("Showing the 10 rows saved in the notebook preview. Place `ecommerce_sales_data.csv` beside `app.py` or upload it to explore all rows.")
elif source_mode == "local":
    st.sidebar.success("Loaded `ecommerce_sales_data.csv` from the project folder.")
else:
    st.sidebar.success("Using the uploaded CSV.")

available_years = sorted(data["Year"].dropna().astype(int).unique().tolist())
available_categories = sorted(data["Category"].dropna().astype(str).unique().tolist())
available_regions = sorted(data["Region"].dropna().astype(str).unique().tolist())

year_values = st.sidebar.multiselect("Year", available_years, default=available_years)
category_values = st.sidebar.multiselect("Category", available_categories, default=available_categories)
region_values = st.sidebar.multiselect("Region", available_regions, default=available_regions)
rating_values = data["Customer_Rating"].dropna()
rating_range = (1.0, 5.0)
if not rating_values.empty:
    low_rating = max(1.0, float(rating_values.min()))
    high_rating = min(5.0, float(rating_values.max()))
    if low_rating < high_rating:
        rating_range = st.sidebar.slider("Customer rating", 1.0, 5.0, (low_rating, high_rating), step=0.1)

filtered = data[
    data["Year"].isin(year_values)
    & data["Category"].astype(str).isin(category_values)
    & data["Region"].astype(str).isin(region_values)
    & data["Customer_Rating"].between(rating_range[0], rating_range[1], inclusive="both")
].copy()

st.markdown('<div class="hero-kicker">SALES INTELLIGENCE · 2020—2024</div>', unsafe_allow_html=True)
st.title("Commerce, at a glance.")
st.markdown(
    "<div class='hero-copy'>A focused view of revenue, profitability, customer sentiment, and advertising efficiency. Use the filters to explore where performance is coming from.</div>",
    unsafe_allow_html=True,
)
st.write("")

if source_mode == "preview":
    st.info(
        "This dashboard currently charts the 10 head and tail rows preserved in the notebook. "
        "The notebook reports full-dataset totals for 1,000 rows; those figures are shown separately below. "
        "Upload the original CSV for complete, filterable breakdowns.",
        icon="ℹ️",
    )
    total_cols = st.columns(4)
    total_cols[0].metric("Notebook records", f"{NOTEBOOK_TOTALS['records']:,}", help="Full row count reported by the notebook")
    total_cols[1].metric("Reported revenue", money(NOTEBOOK_TOTALS["revenue"], compact=True), help="Full-dataset total recorded in the notebook")
    total_cols[2].metric("Reported profit", money(NOTEBOOK_TOTALS["profit"], compact=True), help="Full-dataset total recorded in the notebook")
    total_cols[3].metric("Reported ad spend", money(NOTEBOOK_TOTALS["ad_spend"], compact=True), help="Full-dataset total recorded in the notebook")

if filtered.empty:
    st.warning("No rows match these filters. Widen or clear the selections in the sidebar.")
    st.stop()

revenue = filtered["Revenue"].sum(min_count=1)
profit = filtered["Profit"].sum(min_count=1)
units = filtered["Units_Sold"].sum(min_count=1)
ad_spend = filtered["Ad_Spend"].sum(min_count=1)
margin = profit / revenue * 100 if revenue else float("nan")
roas = revenue / ad_spend if ad_spend else float("nan")
average_rating = filtered["Customer_Rating"].mean()
average_order_value = filtered["Revenue"].mean()

st.markdown('<div class="section-kicker">Selected performance</div>', unsafe_allow_html=True)
kpis = st.columns(6)
kpis[0].metric("Revenue", money(revenue, compact=True))
kpis[1].metric("Profit", money(profit, compact=True))
kpis[2].metric("Profit margin", rate(margin))
kpis[3].metric("Units sold", f"{units:,.0f}" if pd.notna(units) else "—")
kpis[4].metric("ROAS", f"{roas:,.1f}×" if pd.notna(roas) else "—", help="Revenue divided by ad spend")
kpis[5].metric("Avg. rating", f"{average_rating:.2f} / 5" if pd.notna(average_rating) else "—")

tab_overview, tab_products, tab_marketing, tab_data = st.tabs(
    ["Overview", "Products & regions", "Marketing & customers", "Data explorer"]
)

with tab_overview:
    st.write("")
    trend_controls = st.columns([1, 1, 2])
    trend_measure = trend_controls[0].selectbox("Trend metric", ["Revenue", "Profit", "Units sold"])
    trend_grain = trend_controls[1].selectbox("Time grouping", ["Monthly", "Yearly"])
    show_cumulative = trend_controls[2].toggle("Show cumulative total", value=False)
    metric_col = {"Revenue": "Revenue", "Profit": "Profit", "Units sold": "Units_Sold"}[trend_measure]
    trend = filtered.dropna(subset=["Date"]).copy()
    if trend_grain == "Yearly":
        trend["Period"] = trend["Date"].dt.to_period("Y").dt.to_timestamp()
    else:
        trend["Period"] = trend["Date"].dt.to_period("M").dt.to_timestamp()
    trend = trend.groupby("Period", as_index=False)[metric_col].sum().sort_values("Period")
    if not trend.empty:
        if show_cumulative:
            trend[metric_col] = trend[metric_col].cumsum()
            series_name = f"Cumulative {trend_measure.lower()}"
        else:
            series_name = trend_measure
        fig = px.area(
            trend, x="Period", y=metric_col, markers=True,
            color_discrete_sequence=["#68dfbd"],
            labels={"Period": "", metric_col: series_name},
        )
        fig.update_traces(line=dict(width=3), fillcolor="rgba(104,223,189,.14)", marker=dict(size=7))
        fig.update_xaxes(tickformat="%b %Y" if trend_grain == "Monthly" else "%Y")
        st.plotly_chart(chart_style(fig, 350), use_container_width=True, config={"displaylogo": False})
    else:
        st.caption("The selected rows do not contain usable year and month values for a trend chart.")

    st.markdown('<div class="section-kicker">What stands out</div>', unsafe_allow_html=True)
    category_summary = filtered.groupby("Category", dropna=False).agg(Revenue=("Revenue", "sum"), Profit=("Profit", "sum"))
    region_summary = filtered.groupby("Region", dropna=False).agg(Revenue=("Revenue", "sum"), Profit=("Profit", "sum"))
    season_summary = filtered.groupby("Season", dropna=True).agg(Revenue=("Revenue", "sum"), Profit=("Profit", "sum"))
    best_category = category_summary["Revenue"].idxmax() if not category_summary.empty else "—"
    best_region = region_summary["Revenue"].idxmax() if not region_summary.empty else "—"
    best_season = season_summary["Profit"].idxmax() if not season_summary.empty else None
    category_share = category_summary.loc[best_category, "Revenue"] / revenue * 100 if revenue and best_category != "—" else float("nan")
    season_label = best_season if best_season else "Not enough data"
    insight_cols = st.columns(3)
    with insight_cols[0]:
        insight_card("Revenue leader", str(best_category), f"{category_share:.1f}% of selected revenue" if pd.notna(category_share) else "No revenue available")
    with insight_cols[1]:
        region_share = region_summary.loc[best_region, "Revenue"] / revenue * 100 if revenue and best_region != "—" else float("nan")
        insight_card("Leading region", str(best_region), f"{region_share:.1f}% of selected revenue" if pd.notna(region_share) else "No revenue available")
    with insight_cols[2]:
        season_detail = money(season_summary.loc[best_season, "Profit"], compact=True) + " profit" if best_season else "Calendar season derived from Month"
        insight_card("Strongest season", str(season_label), season_detail)

    left, right = st.columns([1.15, 0.85])
    with left:
        st.subheader("Category contribution")
        pie_data = filtered.groupby("Category", as_index=False).agg(Revenue=("Revenue", "sum"))
        pie = px.pie(pie_data, names="Category", values="Revenue", hole=0.68, color_discrete_sequence=px.colors.qualitative.Safe)
        pie.update_traces(textposition="inside", textinfo="percent", insidetextfont=dict(color="#f6f8ff"), hovertemplate="%{label}<br>$%{value:,.2f}<br>%{percent}<extra></extra>")
        pie.update_layout(showlegend=True, legend=dict(orientation="h", y=-.1))
        st.plotly_chart(chart_style(pie, 330), use_container_width=True, config={"displaylogo": False})
    with right:
        st.subheader("Profit versus revenue")
        scatter = px.scatter(
            filtered, x="Revenue", y="Profit", color="Category", size="Units_Sold",
            hover_data=["Year", "Month", "Region", "Customer_Rating"],
            color_discrete_sequence=px.colors.qualitative.Safe,
        )
        scatter.update_traces(marker=dict(opacity=.82, line=dict(width=1, color="rgba(255,255,255,.55)")))
        st.plotly_chart(chart_style(scatter, 330), use_container_width=True, config={"displaylogo": False})

with tab_products:
    st.write("")
    left, right = st.columns([1.15, .85])
    with left:
        rank_metric = st.selectbox("Rank categories by", ["Revenue", "Profit", "Units sold", "Profit margin", "Average price per unit"])
        category_perf = filtered.groupby("Category", as_index=False).agg(
            Revenue=("Revenue", "sum"), Profit=("Profit", "sum"), Units=("Units_Sold", "sum"),
            Average_Price=("Price_Per_Unit", "mean"),
        )
        category_perf["Profit margin"] = category_perf["Profit"] / category_perf["Revenue"].where(category_perf["Revenue"] != 0) * 100
        rank_col = {"Revenue": "Revenue", "Profit": "Profit", "Units sold": "Units", "Profit margin": "Profit margin", "Average price per unit": "Average_Price"}[rank_metric]
        bars = px.bar(category_perf.sort_values(rank_col), x=rank_col, y="Category", orientation="h", color=rank_col,
                      color_continuous_scale=["#285678", "#68dfbd"], labels={rank_col: rank_metric, "Category": ""}, text_auto=".2s")
        bars.update_layout(coloraxis_showscale=False)
        st.plotly_chart(chart_style(bars, 390), use_container_width=True, config={"displaylogo": False})
    with right:
        st.subheader("Category × region")
        heat_data = filtered.pivot_table(index="Category", columns="Region", values="Revenue", aggfunc="sum", fill_value=0)
        if not heat_data.empty:
            heat = px.imshow(heat_data, aspect="auto", color_continuous_scale=[[0, "#17223a"], [.55, "#347a81"], [1, "#72e4c4"]],
                             labels=dict(x="Region", y="Category", color="Revenue"), text_auto=".2s")
            st.plotly_chart(chart_style(heat, 390), use_container_width=True, config={"displaylogo": False})
        else:
            st.caption("No category and region combinations to display.")
    st.subheader("Seasonal performance")
    seasonal = filtered.dropna(subset=["Season"]).groupby("Season", as_index=False).agg(Revenue=("Revenue", "sum"), Profit=("Profit", "sum"))
    if not seasonal.empty:
        seasonal["Season"] = pd.Categorical(seasonal["Season"], ["Winter", "Spring", "Summer", "Autumn"], ordered=True)
        seasonal = seasonal.sort_values("Season")
        season_fig = go.Figure()
        season_fig.add_bar(x=seasonal["Season"], y=seasonal["Revenue"], name="Revenue", marker_color="#5796db")
        season_fig.add_bar(x=seasonal["Season"], y=seasonal["Profit"], name="Profit", marker_color="#68dfbd")
        season_fig.update_layout(barmode="group", yaxis_title="Amount ($)", xaxis_title="")
        st.plotly_chart(chart_style(season_fig, 320), use_container_width=True, config={"displaylogo": False})
    st.subheader("Profit distribution and outliers")
    profit_data = filtered.dropna(subset=["Profit"])
    profit_fig = px.box(profit_data, x="Profit", points="outliers", color_discrete_sequence=["#68dfbd"],
                        labels={"Profit": "Profit per record ($)"})
    st.plotly_chart(chart_style(profit_fig, 260), use_container_width=True, config={"displaylogo": False})

with tab_marketing:
    st.write("")
    left, right = st.columns([1.2, .8])
    with left:
        st.subheader("Advertising spend and revenue")
        ad_data = filtered.dropna(subset=["Ad_Spend", "Revenue"])
        ad_fig = px.scatter(ad_data, x="Ad_Spend", y="Revenue", color="Category", size="Profit", size_max=28,
                            hover_data=["Region", "Month", "Year", "ROAS"], color_discrete_sequence=px.colors.qualitative.Safe,
                            labels={"Ad_Spend": "Ad spend ($)", "Revenue": "Revenue ($)"})
        ad_fig.update_traces(marker=dict(opacity=.8, line=dict(width=1, color="rgba(255,255,255,.5)")))
        st.plotly_chart(chart_style(ad_fig, 365), use_container_width=True, config={"displaylogo": False})
    with right:
        st.subheader("Return on ad spend")
        roas_data = filtered.dropna(subset=["ROAS"])
        if not roas_data.empty:
            log_roas = st.checkbox("Logarithmic scale", value=True, key="roas_log_scale")
            roas_fig = px.box(roas_data, x="Category", y="ROAS", color="Category", points="all", color_discrete_sequence=px.colors.qualitative.Safe)
            roas_fig.update_layout(showlegend=False)
            roas_fig.update_yaxes(title="Revenue / ad spend (×)")
            if log_roas:
                roas_fig.update_yaxes(type="log")
            st.plotly_chart(chart_style(roas_fig, 365), use_container_width=True, config={"displaylogo": False})
        else:
            st.caption("ROAS needs positive ad spend values.")
    st.subheader("Customer ratings")
    rating_summary = filtered.groupby("Category", as_index=False).agg(Avg_Rating=("Customer_Rating", "mean"), Records=("Customer_Rating", "count"))
    ratings_fig = px.bar(rating_summary.sort_values("Avg_Rating"), x="Avg_Rating", y="Category", orientation="h", color="Avg_Rating",
                         color_continuous_scale=[[0, "#dd8e72"], [.55, "#e7c36d"], [1, "#68dfbd"]], text="Avg_Rating",
                         labels={"Avg_Rating": "Average customer rating (out of 5)", "Category": ""}, hover_data=["Records"])
    ratings_fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")
    ratings_fig.update_xaxes(range=[0, 5])
    ratings_fig.update_layout(coloraxis_showscale=False)
    st.plotly_chart(chart_style(ratings_fig, 330), use_container_width=True, config={"displaylogo": False})
    st.caption("ROAS is calculated as revenue divided by advertising spend. A very high value can occur when ad spend is near zero, so use the point-level detail when interpreting outliers.")

with tab_data:
    st.write("")
    st.subheader("Filtered records")
    st.caption(f"{len(filtered):,} of {len(data):,} loaded rows match the current filters.")
    visible_columns = REQUIRED_COLUMNS + ["Date", "Season", "Profit_Margin", "Price_Per_Unit", "ROAS"]
    st.dataframe(filtered[visible_columns], use_container_width=True, hide_index=True)
    csv_bytes = filtered[visible_columns].to_csv(index=False).encode("utf-8")
    st.download_button("Download filtered rows", data=csv_bytes, file_name="commerce_pulse_filtered.csv", mime="text/csv")

    st.write("")
    left, right = st.columns(2)
    with left:
        st.subheader("Missing values")
        missing_counts = data[REQUIRED_COLUMNS].isna().sum().rename("Missing values").to_frame()
        st.dataframe(missing_counts, use_container_width=True)
    with right:
        st.subheader("Dataset checks")
        quality = pd.DataFrame(
            {"Check": ["Loaded rows", "Duplicate rows", "Unparseable dates", "Rows with negative revenue"],
             "Result": [len(data), int(data.duplicated(subset=REQUIRED_COLUMNS).sum()), int(data["Date"].isna().sum()), int((data["Revenue"] < 0).sum())]}
        )
        st.dataframe(quality, hide_index=True, use_container_width=True)

    if source_mode == "preview":
        st.markdown('<div class="section-kicker">Notebook full-dataset reference</div>', unsafe_allow_html=True)
        st.caption("The notebook recorded these totals for 1,000 rows. The raw file is needed for complete category, region, monthly, and row-level analysis.")
        refs = st.columns(4)
        refs[0].metric("Units sold", f"{NOTEBOOK_TOTALS['units']:,}")
        refs[1].metric("Revenue", money(NOTEBOOK_TOTALS["revenue"]))
        refs[2].metric("Profit", money(NOTEBOOK_TOTALS["profit"]))
        refs[3].metric("Ad spend", money(NOTEBOOK_TOTALS["ad_spend"]))
        notebook_margin = NOTEBOOK_TOTALS["profit"] / NOTEBOOK_TOTALS["revenue"] * 100
        notebook_roas = NOTEBOOK_TOTALS["revenue"] / NOTEBOOK_TOTALS["ad_spend"]
        st.caption(f"Derived from the notebook's full-dataset totals: {notebook_margin:.1f}% aggregate profit margin · {notebook_roas:.2f}× aggregate ROAS. The notebook also reports no missing values and zero duplicate rows.")

