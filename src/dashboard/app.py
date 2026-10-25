import pandas as pd
import requests
import streamlit as st

API_URL = "http://127.0.0.1:8000"


st.set_page_config(
    page_title="Online Retail Analytics",
    page_icon="📊",
    layout="wide",
)

# -----------------------------
# Custom Dashboard Styling
# -----------------------------

st.markdown(
    """
    <style>

    /* Main tab container */
    div[data-baseweb="tab-list"] {
        gap: 12px;
        padding: 10px 12px;
        margin-bottom: 25px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        background: rgba(255, 255, 255, 0.025);
    }

    /* Individual tabs */
    button[data-baseweb="tab"] {
        height: 48px;
        padding: 0 24px;
        border-radius: 10px;
        font-size: 16px;
        font-weight: 600;
        background: transparent;
        border: 1px solid transparent;
        transition: all 0.2s ease;
    }

    /* Tab hover */
    button[data-baseweb="tab"]:hover {
        background: rgba(255, 255, 255, 0.06);
        border-color: rgba(255, 255, 255, 0.10);
    }

    /* Active tab */
    button[data-baseweb="tab"][aria-selected="true"] {
        background: rgba(80, 120, 255, 0.14);
        border: 1px solid rgba(80, 120, 255, 0.35);
        box-shadow: 0 4px 18px rgba(80, 120, 255, 0.12);
    }

    /* Remove default underline */
    div[data-baseweb="tab-highlight"] {
        display: none;
    }

    /* Tab content spacing */
    div[data-baseweb="tab-panel"] {
        padding-top: 10px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)

st.title("📊 Online Retail Analytics")
st.caption("Online Retail II historical replay via Kafka, MongoDB and FastAPI")


def country_language(value):
    if value is None:
        return value
    return (
        str(value)
        .replace("store_quantity", "country_quantity")
        .replace("Store activity", "Country sales activity")
        .replace("store operations", "country market patterns")
        .replace("at the store", "in that country market")
    )


# -----------------------------
# Fetch analytics summary
# -----------------------------

def get_analytics_summary():
    response = requests.get(
        f"{API_URL}/analytics/summary",
        timeout=5,
    )

    response.raise_for_status()

    return response.json()


try:
    summary = get_analytics_summary()

except requests.exceptions.RequestException as error:
    st.error(
        "Could not connect to the FastAPI server. "
        "Make sure FastAPI is running."
    )
    st.stop()


# -----------------------------
# KPI Cards
# -----------------------------

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
    "Sale Lines",
        f"{summary['total_transactions']:,}",
    )

with col2:
    st.metric(
        "Total Quantity",
        f"{summary['total_quantity']:,}",
    )

with col3:
    st.metric(
        "Total Revenue",
        f"£{summary['total_revenue']:,.2f}",
    )

with col4:
    st.metric(
        "Average Sale Line Value",
        f"£{summary.get('average_sale_line_value', summary['average_order_value']):,.2f}",
    )


# -----------------------------
# Additional KPIs
# -----------------------------

st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Unique Products",
        summary["unique_products"],
    )

with col2:
    st.metric(
        "Countries",
        summary.get("unique_countries", summary["unique_stores"]),
    )

with col3:
    st.metric(
        "Detected Anomalies",
        summary["total_anomalies"],
    )

# -----------------------------
# Professional Navigation
# -----------------------------

if "active_section" not in st.session_state:
    st.session_state.active_section = "Overview"


st.markdown(
    """
    <style>

    /* Navigation spacing */
    div[data-testid="stHorizontalBlock"] {
        gap: 18px;
    }

    /* Navigation buttons */
    div.stButton > button {
        width: 100%;
        min-height: 52px;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.10);
        background: rgba(255, 255, 255, 0.04);
        font-size: 16px;
        font-weight: 600;
        transition: all 0.2s ease;
    }

    div.stButton > button:hover {
        border-color: rgba(100, 140, 255, 0.50);
        background: rgba(100, 140, 255, 0.10);
    }

    </style>
    """,
    unsafe_allow_html=True,
)


nav1, nav2, nav3, nav4 = st.columns(
    [1, 1.35, 1, 1],
    gap="large",
)


with nav1:
    if st.button(
        "📊  Overview",
        width="stretch",
    ):
        st.session_state.active_section = "Overview"


with nav2:
    if st.button(
        "📦  Products & Countries",
        width="stretch",
    ):
        st.session_state.active_section = "Products"


with nav3:
    if st.button(
        "🚨  Anomalies",
        width="stretch",
    ):
        st.session_state.active_section = "Anomalies"


with nav4:
    if st.button(
        "🤖  Predictions",
        width="stretch",
    ):
        st.session_state.active_section = "Predictions"


st.divider()

# =========================================================
# OVERVIEW TAB
# =========================================================

if st.session_state.active_section == "Overview":

    # Daily Analytics
    st.header("📈 Monthly revenue trend")

    try:
        daily_response = requests.get(
            f"{API_URL}/analytics/daily",
            timeout=5,
        )
        daily_response.raise_for_status()
        daily_data = daily_response.json()["daily"]

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

        st.line_chart(
            monthly_data.set_index("month")[["total_revenue"]],
            alt="Monthly revenue totals over time",
        )

    st.header("📊 Monthly sale line volume")

    if daily_data:
        st.line_chart(
            monthly_data.set_index("month")[["transaction_count"]],
            alt="Monthly sale line totals over time",
        )


# =========================================================
# PRODUCTS & STORES TAB
# =========================================================

if st.session_state.active_section == "Products":

    # Product Performance
    st.header("📦 Product Performance")

    try:
        product_response = requests.get(
            f"{API_URL}/products/",
            timeout=5,
        )

        product_response.raise_for_status()

        products = product_response.json()["products"]

    except requests.exceptions.RequestException:
        st.error("Could not load product analytics.")
        products = []

    if products:

        st.dataframe(
            products,
            hide_index=True,
        )


    # Country Performance
    st.header("🌍 Country Performance")

    try:
        store_response = requests.get(
            f"{API_URL}/stores/",
            timeout=5,
        )

        store_response.raise_for_status()

        stores = store_response.json()["stores"]

    except requests.exceptions.RequestException:
        st.error("Could not load country analytics.")
        stores = []

    if stores:

        country_rows = [
            {
                "Country": item.get("store_id"),
                "Units Sold": item.get("total_quantity", 0),
                "Revenue (GBP)": f"£{item.get('total_revenue', 0):,.2f}",
                "Sale Lines": item.get("transaction_count", 0),
            }
            for item in stores
        ]
        st.dataframe(
            country_rows,
            hide_index=True,
        )


    # Product Revenue Chart
    st.header("💰 Revenue by Product")

    if products:

        revenue_chart_data = {
            product["product_id"]: product["total_revenue"]
            for product in products
        }

        st.bar_chart(revenue_chart_data)


    # Product Quantity Chart
    st.header("📦 Quantity Sold by Product")

    if products:

        quantity_chart_data = {
            product["product_id"]: product["total_quantity"]
            for product in products
        }

        st.bar_chart(quantity_chart_data)


# =========================================================
# ANOMALIES TAB
# =========================================================

if st.session_state.active_section == "Anomalies":

    st.header("🚨 Recent Anomalies")

    try:

        anomaly_response = requests.get(
            f"{API_URL}/anomalies/",
            params={
                "is_anomaly": True,
                "limit": 20,
            },
            timeout=5,
        )

        anomaly_response.raise_for_status()

        anomalies = anomaly_response.json()["anomalies"]

    except requests.exceptions.RequestException:

        st.error("Could not load anomaly data.")
        anomalies = []


    if anomalies:

        anomaly_rows = []

        for anomaly in anomalies:

            anomaly_rows.append({
                "Timestamp": anomaly.get("timestamp"),
                "Type": country_language(anomaly.get("anomaly_type")),
                "Entity": anomaly.get("entity_id"),
                "Severity": anomaly.get("severity"),
                "Ratio": anomaly.get("ratio"),
                "Reason": anomaly.get("reason"),
                "Business Impact": country_language(anomaly.get("business_impact")),
                "Recommendation": country_language(anomaly.get("recommendation")),
            })

        st.dataframe(
            anomaly_rows,
            hide_index=True,
        )

    else:

        st.success("No anomalies detected.")


# =========================================================
# PREDICTIONS TAB
# =========================================================

if st.session_state.active_section == "Predictions":

    st.header("🤖 Demand Predictions")

    try:

        prediction_response = requests.get(
            f"{API_URL}/predictions/",
            params={
                "limit": 20,
            },
            timeout=5,
        )

        prediction_response.raise_for_status()

        predictions = prediction_response.json()["predictions"]

    except requests.exceptions.RequestException:

        st.error("Could not load demand predictions.")
        predictions = []


    if predictions:

        prediction_rows = []

        for prediction in predictions:

            prediction_rows.append({
                "Product": prediction.get("product_id"),
                "Country": prediction.get("store_id"),
                "Predicted Demand": round(
                    prediction.get("predicted_demand", 0),
                    2,
                ),
                "Prediction Date": prediction.get("prediction_date"),
                "Model Version": prediction.get("model_version"),
                "Created At": prediction.get("created_at"),
            })

        st.dataframe(
            prediction_rows,
            hide_index=True,
        )

    else:

        st.info("No demand predictions available.")


    # Prediction Explorer
    st.header("🎯 Demand Prediction Explorer")

    if predictions:

        product_options = sorted(
            set(
                prediction.get("product_id")
                for prediction in predictions
                if prediction.get("product_id")
            )
        )

        selected_product = st.selectbox(
            "Select Product",
            product_options,
        )


        store_options = sorted(
            set(
                prediction.get("store_id")
                for prediction in predictions
                if prediction.get("product_id") == selected_product
                and prediction.get("store_id")
            )
        )

        selected_store = st.selectbox(
            "Select Country",
            store_options,
        )


        selected_predictions = [
            prediction
            for prediction in predictions
            if prediction.get("product_id") == selected_product
            and prediction.get("store_id") == selected_store
        ]


        if selected_predictions:

            latest_prediction = selected_predictions[0]

            col1, col2, col3 = st.columns(3)

            with col1:

                st.metric(
                    "Predicted Demand",
                    f"{latest_prediction.get('predicted_demand', 0):.2f} units",
                )

            with col2:

                st.metric(
                    "Product",
                    selected_product,
                )

            with col3:

                st.metric(
                    "Country",
                    selected_store,
                )


            st.write(
                f"**Prediction Date:** "
                f"{latest_prediction.get('prediction_date', 'N/A')}"
            )

            st.write(
                f"**Model Version:** "
                f"{latest_prediction.get('model_version', 'N/A')}"
            )

        else:

            st.info(
                "No prediction available for this product and country."
            )

    else:

        st.info("No demand predictions available.")
