import json
import os
import time

import pandas as pd
import requests
import streamlit as st
from streamlit_autorefresh import st_autorefresh



API_URL = os.getenv("API_URL", "http://127.0.0.1:8000").strip().rstrip("/")


st.set_page_config(
    page_title="Online Retail Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# =========================================================
# PROFESSIONAL STYLING
# =========================================================

st.markdown(
    """
    <style>

    /* ---------- Global ---------- */

    .stApp {
        background:
            radial-gradient(circle at 15% 10%, rgba(99, 102, 241, 0.10), transparent 28%),
            radial-gradient(circle at 85% 5%, rgba(14, 165, 233, 0.08), transparent 24%),
            #0b1020;
    }

    [data-testid="stHeader"] {
        background: rgba(11, 16, 32, 0.82);
    }

    .block-container {
        max-width: 1500px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    h1, h2, h3 {
        letter-spacing: -0.02em;
    }

    /* ---------- Header ---------- */

    .hero {
        padding: 1.4rem 1.6rem;
        margin-bottom: 1.2rem;
        border: 1px solid rgba(148, 163, 184, 0.16);
        border-radius: 20px;
        background: rgba(15, 23, 42, 0.72);
        box-shadow: 0 18px 50px rgba(0, 0, 0, 0.20);
    }

    .hero-title {
        font-size: 2rem;
        font-weight: 750;
        margin-bottom: 0.25rem;
    }

    .hero-subtitle {
        color: #94a3b8;
        font-size: 0.98rem;
    }

    .live-pill {
        display: inline-flex;
        align-items: center;
        gap: 7px;
        padding: 6px 11px;
        border-radius: 999px;
        border: 1px solid rgba(34, 197, 94, 0.30);
        background: rgba(34, 197, 94, 0.10);
        color: #86efac;
        font-size: 0.78rem;
        font-weight: 700;
        margin-top: 0.8rem;
    }

    .live-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #22c55e;
        box-shadow: 0 0 10px rgba(34, 197, 94, 0.8);
    }

    /* ---------- Navigation ---------- */

    .nav-label {
        color: #64748b;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        margin-bottom: 0.45rem;
    }

    div.stButton > button {
        min-height: 48px;
        border-radius: 12px;
        border: 1px solid rgba(148, 163, 184, 0.16);
        background: rgba(30, 41, 59, 0.58);
        color: #cbd5e1;
        font-weight: 650;
        transition: all 0.18s ease;
    }

    div.stButton > button:hover {
        border-color: rgba(129, 140, 248, 0.55);
        background: rgba(79, 70, 229, 0.12);
        color: #ffffff;
        transform: translateY(-1px);
    }

    /* ---------- KPI Cards ---------- */

    div[data-testid="stMetric"] {
        padding: 1rem 1.05rem;
        border: 1px solid rgba(148, 163, 184, 0.14);
        border-radius: 16px;
        background: rgba(15, 23, 42, 0.70);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.12);
    }

    div[data-testid="stMetricLabel"] {
        color: #94a3b8;
    }

    div[data-testid="stMetricValue"] {
        font-size: 1.55rem;
    }

    /* ---------- Section cards ---------- */

    .section-card {
        padding: 1rem 1.1rem;
        border: 1px solid rgba(148, 163, 184, 0.13);
        border-radius: 16px;
        background: rgba(15, 23, 42, 0.55);
        margin-bottom: 1rem;
    }

    .section-kicker {
        color: #818cf8;
        font-size: 0.72rem;
        font-weight: 750;
        letter-spacing: 0.11em;
        text-transform: uppercase;
    }

    .section-title {
        font-size: 1.15rem;
        font-weight: 700;
        margin-top: 0.15rem;
        margin-bottom: 0.2rem;
    }

    .section-description {
        color: #94a3b8;
        font-size: 0.86rem;
    }

    /* ---------- Tables ---------- */

    [data-testid="stDataFrame"] {
        border: 1px solid rgba(148, 163, 184, 0.12);
        border-radius: 14px;
        overflow: hidden;
    }

    /* ---------- Status / footer ---------- */

    .footer {
        text-align: center;
        color: #64748b;
        font-size: 0.75rem;
        padding-top: 1.5rem;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# SESSION STATE / NAVIGATION
# =========================================================

SECTIONS = {
    "Overview": "📊  Overview",
    "Products": "📦  Products & Countries",
    "Anomalies": "🚨  Anomalies",
    "Predictions": "🤖  Predictions",
}


if "active_section" not in st.session_state:
    st.session_state.active_section = "Overview"


def change_section(section):
    st.session_state.active_section = section


# =========================================================
# HEADER
# =========================================================

st.markdown(
    """
    <div class="hero">
        <div class="hero-title">📊 Online Retail Intelligence</div>
        <div class="hero-subtitle">
            Historical Online Retail II sales replayed through Kafka for
            product, country, anomaly and demand analysis.
        </div>
        <div class="live-pill">
            <span class="live-dot"></span>
            HISTORICAL REPLAY • Refresh the page to update
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# COMMON API HELPERS
# =========================================================

def api_get(endpoint, params=None):
    cache_key = (
        f"_api_last_success::{endpoint}::"
        f"{json.dumps(params or {}, sort_keys=True, default=str)}"
    )
    last_error = None

    for attempt in range(3):
        try:
            response = requests.get(
                f"{API_URL}{endpoint}",
                params=params,
                timeout=(3, 30),
            )
            response.raise_for_status()
            data = response.json()
            st.session_state[cache_key] = data
            return data
        except requests.exceptions.ConnectionError as error:
            last_error = error
            if attempt < 2:
                time.sleep(0.25 * (2 ** attempt))
        except requests.exceptions.Timeout as error:
            last_error = error
            break
        except requests.exceptions.HTTPError as error:
            status_code = error.response.status_code if error.response else 0
            if status_code < 500:
                raise
            last_error = error
            if attempt < 2:
                time.sleep(0.25 * (2 ** attempt))

    if cache_key in st.session_state:
        st.session_state["_api_using_cached_data"] = True
        return st.session_state[cache_key]

    if last_error is not None:
        raise last_error

    raise requests.exceptions.ConnectionError(
        f"Analytics API is unavailable at {API_URL}."
    )


def format_compact_number(value):
    value = float(value)

    if abs(value) >= 1_000_000_000:
        return f"{value / 1_000_000_000:.2f}B"

    if abs(value) >= 1_000_000:
        return f"{value / 1_000_000:.2f}M"

    if abs(value) >= 1_000:
        return f"{value / 1_000:.1f}K"

    return f"{round(value):,}"


def format_currency(value):
    value = float(value)

    if abs(value) >= 1_000_000_000:
        return f"£{value / 1_000_000_000:.2f}B"

    if abs(value) >= 1_000_000:
        return f"£{value / 1_000_000:.2f}M"

    if abs(value) >= 1_000:
        return f"£{value / 1_000:.1f}K"

    return f"£{round(value):,}"


def format_units(value):
    return f"{round(float(value)):,} units"


def country_language(value):
    """Translate legacy store labels for Online Retail II's country grouping."""
    if value is None:
        return value
    return (
        str(value)
        .replace("store_quantity", "country_quantity")
        .replace("Store activity", "Country sales activity")
        .replace("store operations", "country market patterns")
        .replace("at the store", "in that country market")
    )


def show_section_heading(kicker, title, description):
    st.markdown(
        f"""
        <div class="section-card">
            <div class="section-kicker">{kicker}</div>
            <div class="section-title">{title}</div>
            <div class="section-description">{description}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# FETCH SUMMARY
# =========================================================

st.session_state["_api_using_cached_data"] = False

try:
    summary = api_get("/analytics/summary")
except requests.exceptions.RequestException:
    st.info(
        f"Analytics API at {API_URL} is temporarily unavailable. "
        "The dashboard will try again automatically."
    )
    st.stop()


# =========================================================
# TOP KPI ROW
# =========================================================

kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.metric(
        "Sale Lines",
        format_compact_number(summary.get("total_transactions", 0)),
    )

with kpi2:
    st.metric(
        "Units Sold",
        format_compact_number(summary.get("total_quantity", 0)),
    )

with kpi3:
    st.metric(
        "Total Revenue",
        format_currency(summary.get("total_revenue", 0)),
    )

with kpi4:
    st.metric(
        "Average Sale Line Value",
        format_currency(
            summary.get(
                "average_sale_line_value",
                summary.get("average_order_value", 0),
            )
        ),
    )


# =========================================================
# SECONDARY KPI ROW
# =========================================================

st.markdown("<div style='height: 10px'></div>", unsafe_allow_html=True)

kpi5, kpi6, kpi7 = st.columns(3)

with kpi5:
    st.metric(
        "Products",
        f"{round(float(summary.get('unique_products', 0))):,}",
    )

with kpi6:
    st.metric(
        "Countries",
        f"{round(float(summary.get('unique_countries', summary.get('unique_stores', 0)))):,}",
    )

with kpi7:
    st.metric(
        "Detected Anomalies",
        f"{summary.get('total_anomalies', 0):,}",
    )


# =========================================================
# NAVIGATION
# =========================================================

st.markdown("<div style='height: 18px'></div>", unsafe_allow_html=True)

st.markdown(
    '<div class="nav-label">Workspace</div>',
    unsafe_allow_html=True,
)

nav1, nav2, nav3, nav4 = st.columns(
    [1, 1.35, 1, 1],
    gap="medium",
)

nav_columns = [
    (nav1, "Overview"),
    (nav2, "Products"),
    (nav3, "Anomalies"),
    (nav4, "Predictions"),
]

for column, section in nav_columns:
    with column:
        button_type = (
            "primary"
            if st.session_state.active_section == section
            else "secondary"
        )

        st.button(
            SECTIONS[section],
            key=f"nav_{section.lower()}",
            width="stretch",
            type=button_type,
            on_click=change_section,
            args=(section,),
        )


st.divider()


# =========================================================
# OVERVIEW
# =========================================================

if st.session_state.active_section == "Overview":

    show_section_heading(
        "Overview",
        "Business Performance",
        "Review historical sales lines, revenue and activity over the dataset period.",
    )

    try:
        daily_data = api_get("/analytics/daily").get("daily", [])
    except requests.exceptions.RequestException:
        st.error("Could not load daily analytics.")
        daily_data = []

    if daily_data:
        analytics_frame = pd.DataFrame(daily_data)
        analytics_frame["month"] = (
            pd.to_datetime(analytics_frame["date"], errors="coerce")
            .dt.to_period("M")
            .dt.to_timestamp()
        )
        monthly_data = (
            analytics_frame.dropna(subset=["month"])
            .groupby("month", as_index=False)
            .agg(
                total_revenue=("total_revenue", "sum"),
                transaction_count=("transaction_count", "sum"),
            )
            .sort_values("month")
        )

        chart1, chart2 = st.columns(2, gap="large")

        with chart1:
            st.subheader("Monthly revenue trend")
            st.line_chart(
                monthly_data.set_index("month")[["total_revenue"]],
                alt="Monthly revenue totals over time",
            )

        with chart2:
            st.subheader("Monthly sale line volume")
            st.line_chart(
                monthly_data.set_index("month")[["transaction_count"]],
                alt="Monthly sale line totals over time",
            )

        st.subheader("Monthly business summary")
        monthly_rows = [
            {
                "Month": item.month.strftime("%b %Y"),
                "Sale Lines": int(item.transaction_count),
                "Revenue": format_currency(item.total_revenue),
            }
            for item in monthly_data.itertuples(index=False)
        ]
        st.dataframe(
            monthly_rows,
            hide_index=True,
            alt="Monthly Online Retail II revenue and sale line totals",
        )

    else:
        st.info("No daily analytics available yet.")


# =========================================================
# PRODUCTS & COUNTRIES
# =========================================================

if st.session_state.active_section == "Products":

    show_section_heading(
        "Products & Countries",
        "Retail Performance",
        "Compare StockCode performance and country markets using the imported sales lines.",
    )

    try:
        products = api_get("/products/").get("products", [])
    except requests.exceptions.RequestException:
        st.error("Could not load product analytics.")
        products = []

    try:
        stores = api_get("/stores/").get("stores", [])
    except requests.exceptions.RequestException:
        st.error("Could not load country analytics.")
        stores = []

    if products:

        st.subheader("Product Performance")

        product_rows = []

        for product in products:
            product_rows.append(
                {
                    "Product": product.get("product_id"),
                    "Description": product.get("description"),
                    "Units Sold": round(
                        float(product.get("total_quantity", 0))
                    ),
                    "Revenue": format_currency(
                        product.get("total_revenue", 0)
                    ),
                    "Sale Lines": round(
                        float(product.get("transaction_count", 0))
                    ),
                }
            )

        st.dataframe(
            product_rows,
            hide_index=True,
        )

        chart1, chart2 = st.columns(2, gap="large")

        with chart1:
            st.subheader("Revenue by Product")

            revenue_chart_data = {
                product["product_id"]: product["total_revenue"]
                for product in products
            }

            st.bar_chart(revenue_chart_data)

        with chart2:
            st.subheader("Units Sold by Product")

            quantity_chart_data = {
                product["product_id"]: product["total_quantity"]
                for product in products
            }

            st.bar_chart(quantity_chart_data)

    else:
        st.info("No product analytics available.")

    st.markdown("<div style='height: 12px'></div>", unsafe_allow_html=True)

    if stores:

        st.subheader("Country Performance")

        store_rows = []

        for store in stores:
            store_rows.append(
                {
                    "Country": store.get("store_id"),
                    "Units Sold": round(
                        float(store.get("total_quantity", 0))
                    ),
                    "Revenue": format_currency(
                        store.get("total_revenue", 0)
                    ),
                    "Sale Lines": round(
                        float(store.get("transaction_count", 0))
                    ),
                }
            )

        st.dataframe(
            store_rows,
            hide_index=True,
        )

    else:
        st.info("No country analytics available.")


# =========================================================
# ANOMALIES
# =========================================================

if st.session_state.active_section == "Anomalies":

    show_section_heading(
        "Anomaly Detection",
        "Detected Business Anomalies",
        "Review unusual revenue and quantity patterns identified by the streaming analytics pipeline.",
    )

    try:
        anomalies = api_get(
            "/anomalies/",
            params={
                "is_anomaly": True,
                "limit": 20,
            },
        ).get("anomalies", [])

    except requests.exceptions.RequestException:
        st.error("Could not load anomaly data.")
        anomalies = []

    if anomalies:

        high_count = sum(
            1
            for anomaly in anomalies
            if str(anomaly.get("severity", "")).upper() == "HIGH"
        )

        medium_count = sum(
            1
            for anomaly in anomalies
            if str(anomaly.get("severity", "")).upper() == "MEDIUM"
        )

        low_count = sum(
            1
            for anomaly in anomalies
            if str(anomaly.get("severity", "")).upper() == "LOW"
        )

        a1, a2, a3 = st.columns(3)

        with a1:
            st.metric("High Severity", high_count)

        with a2:
            st.metric("Medium Severity", medium_count)

        with a3:
            st.metric("Low Severity", low_count)

        st.subheader("Recent Anomalies")

        anomaly_rows = []

        for anomaly in anomalies:
            anomaly_rows.append(
                {
                    "Timestamp": anomaly.get("timestamp"),
                    "Type": country_language(anomaly.get("anomaly_type")),
                    "Entity": anomaly.get("entity_id"),
                    "Severity": anomaly.get("severity"),
                    "Ratio": anomaly.get("ratio"),
                    "Reason": anomaly.get("reason"),
                    "Business Impact": country_language(anomaly.get("business_impact")),
                    "Recommendation": country_language(anomaly.get("recommendation")),
                }
            )

        st.dataframe(
            anomaly_rows,
            hide_index=True,
        )

    else:
        st.success("No anomalies detected.")


# =========================================================
# PREDICTIONS
# =========================================================

if st.session_state.active_section == "Predictions":

    show_section_heading(
        "Predictive Analytics",
        "Demand Forecasting",
        "Explore machine-learning forecasts generated from the historical sales replay.",
    )

    try:
        predictions = api_get(
            "/predictions/",
            params={
                "limit": 20,
            },
        ).get("predictions", [])

    except requests.exceptions.RequestException:
        st.error("Could not load demand predictions.")
        predictions = []

    if predictions:

        prediction_values = [
            float(item.get("predicted_demand", 0))
            for item in predictions
        ]

        p1, p2, p3 = st.columns(3)

        with p1:
            st.metric(
                "Latest Prediction",
                f"{round(prediction_values[0]):,} units",
            )

        with p2:
            st.metric(
                "Predictions Loaded",
                len(predictions),
            )

        with p3:
            st.metric(
                "Average Predicted Demand",
                f"{round(sum(prediction_values) / len(prediction_values)):,} units",
            )

        st.subheader("Recent Predictions")

        prediction_rows = []

        for prediction in predictions:
            prediction_rows.append(
                {
                    "Product": prediction.get("product_id"),
                    "Country": prediction.get("store_id"),
                    "Predicted Demand": round(
                        float(prediction.get("predicted_demand", 0))
                    ),
                    "Prediction Date": prediction.get("prediction_date"),
                    "Model Version": prediction.get("model_version"),
                    "Created At": prediction.get("created_at"),
                }
            )

        st.dataframe(
            prediction_rows,
            hide_index=True,
        )

        st.markdown("<div style='height: 12px'></div>", unsafe_allow_html=True)

        st.subheader("Prediction Explorer")

        explorer1, explorer2 = st.columns(2, gap="large")

        product_options = sorted(
            {
                prediction.get("product_id")
                for prediction in predictions
                if prediction.get("product_id")
            }
        )

        with explorer1:
            selected_product = st.selectbox(
                "Select Product",
                product_options,
                key="prediction_product",
            )

        store_options = sorted(
            {
                prediction.get("store_id")
                for prediction in predictions
                if prediction.get("product_id") == selected_product
                and prediction.get("store_id")
            }
        )

        with explorer2:
            selected_store = st.selectbox(
                "Select Country",
                store_options,
                key="prediction_store",
            )

        selected_predictions = [
            prediction
            for prediction in predictions
            if prediction.get("product_id") == selected_product
            and prediction.get("store_id") == selected_store
        ]

        if selected_predictions:

            latest_prediction = selected_predictions[0]

            e1, e2, e3 = st.columns(3)

            with e1:
                st.metric(
                    "Predicted Demand",
                    f"{round(float(latest_prediction.get('predicted_demand', 0))):,} units",
                )

            with e2:
                st.metric(
                    "Product",
                    selected_product,
                )

            with e3:
                st.metric(
                    "Country",
                    selected_store,
                )

            st.caption(
                f"Prediction date: "
                f"{latest_prediction.get('prediction_date', 'N/A')}  •  "
                f"Model: {latest_prediction.get('model_version', 'N/A')}"
            )

        else:
            st.info(
                "No prediction is available for the selected product and country."
            )

    else:
        st.info("No demand predictions available yet.")


if st.session_state.get("_api_using_cached_data"):
    st.caption(
        "Showing the latest available data while the analytics API reconnects."
    )


# =========================================================
# FOOTER
# =========================================================

st.markdown(
    """
    <div class="footer">
        Online Retail II Historical Replay • Kafka • MongoDB • FastAPI • ML
    </div>
    """,
    unsafe_allow_html=True,
)

