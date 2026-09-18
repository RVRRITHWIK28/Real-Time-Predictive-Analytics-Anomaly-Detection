import requests
import streamlit as st
import os
from streamlit_autorefresh import st_autorefresh


API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")


st.set_page_config(
    page_title="Real-Time Retail Intelligence",
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
# AUTO REFRESH
# =========================================================

st_autorefresh(
    interval=5000,
    key="dashboard_refresh",
)


# =========================================================
# SESSION STATE / NAVIGATION
# =========================================================

SECTIONS = {
    "Overview": "📊  Overview",
    "Products": "📦  Products & Stores",
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
        <div class="hero-title">📊 Real-Time Retail Intelligence</div>
        <div class="hero-subtitle">
            Predictive analytics, anomaly detection and business intelligence
            powered by Kafka, MongoDB, FastAPI and machine learning.
        </div>
        <div class="live-pill">
            <span class="live-dot"></span>
            LIVE DATA • Auto-refreshing every 5 seconds
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# COMMON API HELPERS
# =========================================================

def api_get(endpoint, params=None):
    response = requests.get(
        f"{API_URL}{endpoint}",
        params=params,
        timeout=5,
    )
    response.raise_for_status()
    return response.json()


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
        return f"₹{value / 1_000_000_000:.2f}B"

    if abs(value) >= 1_000_000:
        return f"₹{value / 1_000_000:.2f}M"

    if abs(value) >= 1_000:
        return f"₹{value / 1_000:.1f}K"

    return f"₹{round(value):,}"


def format_units(value):
    return f"{round(float(value)):,} units"


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

try:
    summary = api_get("/analytics/summary")
except requests.exceptions.RequestException:
    st.error(
        "Could not connect to the FastAPI server. "
        "Make sure FastAPI is running at http://127.0.0.1:8000."
    )
    st.stop()


# =========================================================
# TOP KPI ROW
# =========================================================

kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.metric(
        "Total Transactions",
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
        "Average Order Value",
        format_currency(summary.get("average_order_value", 0)),
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
        "Stores",
        f"{round(float(summary.get('unique_stores', 0))):,}",
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
            use_container_width=True,
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
        "Monitor revenue and transaction activity across the retail network.",
    )

    try:
        daily_data = api_get("/analytics/daily").get("daily", [])
    except requests.exceptions.RequestException:
        st.error("Could not load daily analytics.")
        daily_data = []

    if daily_data:

        chart1, chart2 = st.columns(2, gap="large")

        with chart1:
            st.subheader("Revenue Trend")

            revenue_data = {
                item["date"]: item["total_revenue"]
                for item in daily_data
            }

            st.line_chart(revenue_data)

        with chart2:
            st.subheader("Transaction Volume")

            transaction_data = {
                item["date"]: item["transaction_count"]
                for item in daily_data
            }

            st.line_chart(transaction_data)

        st.subheader("Daily Business Summary")

        daily_rows = []

        for item in daily_data:
            daily_rows.append(
                {
                    "Date": item.get("date"),
                    "Transactions": item.get("transaction_count", 0),
                    "Revenue": format_currency(
                        item.get("total_revenue", 0)
                    ),
                }
            )

        st.dataframe(
            daily_rows,
            use_container_width=True,
            hide_index=True,
        )

    else:
        st.info("No daily analytics available yet.")


# =========================================================
# PRODUCTS & STORES
# =========================================================

if st.session_state.active_section == "Products":

    show_section_heading(
        "Products & Stores",
        "Retail Performance",
        "Compare product and store performance using transaction-level MongoDB data.",
    )

    try:
        products = api_get("/products/").get("products", [])
    except requests.exceptions.RequestException:
        st.error("Could not load product analytics.")
        products = []

    try:
        stores = api_get("/stores/").get("stores", [])
    except requests.exceptions.RequestException:
        st.error("Could not load store analytics.")
        stores = []

    if products:

        st.subheader("Product Performance")

        product_rows = []

        for product in products:
            product_rows.append(
                {
                    "Product": product.get("product_id"),
                    "Units Sold": round(
                        float(product.get("total_quantity", 0))
                    ),
                    "Revenue": format_currency(
                        product.get("total_revenue", 0)
                    ),
                    "Transactions": round(
                        float(product.get("transaction_count", 0))
                    ),
                }
            )

        st.dataframe(
            product_rows,
            use_container_width=True,
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

        st.subheader("Store Performance")

        store_rows = []

        for store in stores:
            store_rows.append(
                {
                    "Store": store.get("store_id"),
                    "Units Sold": round(
                        float(store.get("total_quantity", 0))
                    ),
                    "Revenue": format_currency(
                        store.get("total_revenue", 0)
                    ),
                    "Transactions": round(
                        float(store.get("transaction_count", 0))
                    ),
                }
            )

        st.dataframe(
            store_rows,
            use_container_width=True,
            hide_index=True,
        )

    else:
        st.info("No store analytics available.")


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
                    "Type": anomaly.get("anomaly_type"),
                    "Entity": anomaly.get("entity_id"),
                    "Severity": anomaly.get("severity"),
                    "Ratio": anomaly.get("ratio"),
                    "Reason": anomaly.get("reason"),
                    "Business Impact": anomaly.get("business_impact"),
                    "Recommendation": anomaly.get("recommendation"),
                }
            )

        st.dataframe(
            anomaly_rows,
            use_container_width=True,
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
        "Explore machine-learning demand predictions generated by the real-time prediction pipeline.",
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
                    "Store": prediction.get("store_id"),
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
            use_container_width=True,
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
                "Select Store",
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
                    "Store",
                    selected_store,
                )

            st.caption(
                f"Prediction date: "
                f"{latest_prediction.get('prediction_date', 'N/A')}  •  "
                f"Model: {latest_prediction.get('model_version', 'N/A')}"
            )

        else:
            st.info(
                "No prediction is available for the selected product and store."
            )

    else:
        st.info("No demand predictions available yet.")


# =========================================================
# FOOTER
# =========================================================

st.markdown(
    """
    <div class="footer">
        Real-Time Retail Intelligence Platform • Kafka • MongoDB • FastAPI • ML
    </div>
    """,
    unsafe_allow_html=True,
)
