import calendar
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

    @keyframes enter-soft {
        from { opacity: 0; transform: translateY(9px); }
        to { opacity: 1; transform: translateY(0); }
    }

    @keyframes mark-float {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-2px); }
    }

    @keyframes live-pulse {
        0%, 100% { box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.32); }
        55% { box-shadow: 0 0 0 6px rgba(34, 197, 94, 0); }
    }

    .hero {
        position: relative;
        isolation: isolate;
        overflow: hidden;
        padding: 2.1rem 1.6rem 1.75rem;
        margin-bottom: 1.2rem;
        border: 1px solid rgba(129, 140, 248, 0.22);
        border-radius: 22px;
        background: linear-gradient(135deg, rgba(17, 27, 51, 0.96), rgba(15, 23, 42, 0.90));
        box-shadow: 0 22px 60px rgba(0, 0, 0, 0.24);
        text-align: center;
        animation: enter-soft 560ms cubic-bezier(0.2, 0.7, 0.2, 1) both;
    }

    .hero::before {
        content: "";
        position: absolute;
        z-index: -1;
        inset: 0;
        background:
            radial-gradient(circle at 50% -28%, rgba(99, 102, 241, 0.27), transparent 46%),
            radial-gradient(circle at 12% 100%, rgba(14, 165, 233, 0.10), transparent 34%);
        pointer-events: none;
    }

    .hero-mark {
        display: block;
        width: 50px;
        height: 50px;
        margin: 0 auto 0.72rem;
        filter: drop-shadow(0 8px 18px rgba(99, 102, 241, 0.28));
        animation: mark-float 5s ease-in-out infinite;
    }

    .hero-title {
        color: #f8fafc;
        font-size: clamp(2rem, 4vw, 2.8rem);
        font-weight: 780;
        letter-spacing: -0.045em;
        line-height: 1.08;
        margin: 0;
    }

    .hero-subtitle {
        max-width: 820px;
        margin: 0.72rem auto 0;
        color: #a8b5ca;
        font-size: 1rem;
        line-height: 1.65;
    }

    .live-pill {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 9px;
        max-width: 100%;
        margin: 1.05rem auto 0;
        padding: 0.58rem 0.95rem;
        border-radius: 999px;
        border: 1px solid rgba(34, 197, 94, 0.34);
        background: linear-gradient(135deg, rgba(34, 197, 94, 0.13), rgba(16, 185, 129, 0.08));
        color: #a7f3d0;
        font-size: 0.78rem;
        font-weight: 750;
        letter-spacing: 0.025em;
        box-shadow: 0 8px 24px rgba(16, 185, 129, 0.08);
    }

    .live-dot {
        flex: 0 0 8px;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #34d399;
        animation: live-pulse 2s ease-out infinite;
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
        transition: transform 180ms ease, border-color 180ms ease, box-shadow 180ms ease;
        animation: enter-soft 480ms ease;
    }

    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        border-color: rgba(129, 140, 248, 0.35);
        box-shadow: 0 16px 38px rgba(0, 0, 0, 0.20);
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
        border: 1px solid rgba(148, 163, 184, 0.16);
        border-radius: 16px;
        background: linear-gradient(145deg, rgba(18, 27, 48, 0.86), rgba(15, 23, 42, 0.62));
        margin-bottom: 1rem;
        animation: enter-soft 460ms ease both;
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

    [data-testid="stVegaLiteChart"],
    [data-testid="stArrowVegaLiteChart"] {
        overflow: hidden;
        border: 1px solid rgba(148, 163, 184, 0.14);
        border-radius: 16px;
        background: rgba(12, 18, 33, 0.72);
        box-shadow: 0 14px 36px rgba(0, 0, 0, 0.16);
        animation: enter-soft 500ms ease both;
    }

    [data-testid="stDataFrame"] {
        border: 1px solid rgba(148, 163, 184, 0.14);
        border-radius: 14px;
        overflow: hidden;
        box-shadow: 0 12px 30px rgba(0, 0, 0, 0.14);
    }

    :focus-visible {
        outline: 2px solid rgba(129, 140, 248, 0.9);
        outline-offset: 3px;
    }

    @media (max-width: 640px) {
        .hero {
            padding: 1.55rem 1rem 1.35rem;
        }

        .hero-mark {
            width: 44px;
            height: 44px;
        }

        .hero-subtitle {
            font-size: 0.92rem;
        }
    }

    @media (prefers-reduced-motion: reduce) {
        .hero,
        .hero-mark,
        .live-dot,
        .section-card,
        [data-testid="stMetric"],
        [data-testid="stVegaLiteChart"],
        [data-testid="stArrowVegaLiteChart"] {
            animation: none !important;
        }

        div.stButton > button,
        [data-testid="stMetric"] {
            transition: none !important;
        }
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
        <svg class="hero-mark" viewBox="0 0 56 56" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
            <defs>
                <linearGradient id="hero-chart-gradient" x1="10" y1="46" x2="46" y2="10" gradientUnits="userSpaceOnUse">
                    <stop offset="0" stop-color="#38bdf8"/>
                    <stop offset="1" stop-color="#a78bfa"/>
                </linearGradient>
            </defs>
            <rect x="2.5" y="2.5" width="51" height="51" rx="16" fill="#111b33" stroke="#354466"/>
            <path d="M13 42.5H43" stroke="#64748b" stroke-width="1.5" stroke-linecap="round"/>
            <rect x="14" y="30" width="6.5" height="12.5" rx="2.2" fill="#38bdf8"/>
            <rect x="24.8" y="23" width="6.5" height="19.5" rx="2.2" fill="url(#hero-chart-gradient)"/>
            <rect x="35.5" y="15" width="6.5" height="27.5" rx="2.2" fill="#a78bfa"/>
            <path d="m13.5 27.5 9-6 8 2 12-11" fill="none" stroke="#dbeafe" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <circle cx="42.5" cy="12.5" r="2.4" fill="#dbeafe"/>
        </svg>
        <h1 class="hero-title">Online Retail Intelligence</h1>
        <p class="hero-subtitle">
            Historical Online Retail Sales replayed through Kafka for product, country, anomaly and demand analysis.
        </p>
        <div class="live-pill" role="status">
            <span class="live-dot"></span>
            LIVE STREAMING • Refresh the page to update
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

kpi5, kpi6, kpi7, kpi8, kpi9 = st.columns(5)

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
        "Hourly Revenue Anomalies",
        f"{summary.get('hourly_revenue_anomalies', 0):,}",
    )

with kpi8:
    st.metric(
        "Daily Revenue Anomalies",
        f"{summary.get('daily_revenue_anomalies', 0):,}",
    )

with kpi9:
    st.metric(
        "Revenue Anomalies",
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
        "Compare country totals and top-selling products by units sold.",
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

    if stores:
        sorted_stores = sorted(
            stores,
            key=lambda item: float(item.get("total_quantity", 0) or 0),
            reverse=True,
        )
        country_rows = []

        for store in sorted_stores:
            country_rows.append(
                {
                    "Country": str(store.get("store_id") or "Unknown"),
                    "Units Sold": round(
                        max(float(store.get("total_quantity", 0) or 0), 0.0)
                    ),
                    "Revenue": format_currency(store.get("total_revenue", 0)),
                    "Sale Lines": round(
                        float(store.get("transaction_count", 0) or 0)
                    ),
                }
            )

        top_country_chart_rows = [
            {
                "Country": row["Country"],
                "Units Sold": row["Units Sold"],
            }
            for row in country_rows[:15]
        ]

        st.subheader("Top 15 Countries by Units Sold")
        if top_country_chart_rows:
            st.bar_chart(
                pd.DataFrame(top_country_chart_rows),
                x="Country",
                y="Units Sold",
                horizontal=True,
                sort="-Units Sold",
                height=560,
                alt="Top 15 countries ranked by units sold",
            )
        else:
            st.info("No country sales are available to compare.")

        st.subheader("Country Performance")
        st.dataframe(
            country_rows,
            hide_index=True,
            alt="Country totals sorted by units sold, with revenue and sale-line totals",
        )
    else:
        st.info("No country analytics available.")

    st.markdown("<div style='height: 12px'></div>", unsafe_allow_html=True)

    if products:
        sorted_products = sorted(
            products,
            key=lambda item: float(item.get("total_quantity", 0) or 0),
            reverse=True,
        )
        product_rows = []
        top_product_chart_rows = []

        for product in sorted_products:
            product_code = str(product.get("product_id") or "Unknown")
            description = str(product.get("description") or "").strip()
            units_sold = max(
                float(product.get("total_quantity", 0) or 0),
                0.0,
            )
            product_rows.append(
                {
                    "Product": product_code,
                    "Description": description,
                    "Units Sold": round(units_sold),
                    "Revenue": format_currency(product.get("total_revenue", 0)),
                    "Sale Lines": round(
                        float(product.get("transaction_count", 0) or 0)
                    ),
                }
            )

            if len(top_product_chart_rows) < 15:
                chart_label = (
                    f"{product_code} — {description}"
                    if description
                    else product_code
                )
                top_product_chart_rows.append(
                    {
                        "Product": chart_label,
                        "Units Sold": round(units_sold),
                    }
                )

        st.subheader("Top 15 Products by Units Sold")
        if top_product_chart_rows:
            st.bar_chart(
                pd.DataFrame(top_product_chart_rows),
                x="Product",
                y="Units Sold",
                horizontal=True,
                sort="-Units Sold",
                height=620,
                alt="Top 15 products ranked by units sold",
            )
        else:
            st.info("No product sales are available to compare.")

        st.subheader("Product Performance")
        st.dataframe(
            product_rows,
            hide_index=True,
            alt="Product totals sorted by units sold, with descriptions, revenue, and sale-line totals",
        )
    else:
        st.info("No product analytics available.")


# ANOMALIES
# =========================================================

if st.session_state.active_section == "Anomalies":

    show_section_heading(
        "Isolation Forest",
        "Hourly & Daily Revenue Anomalies",
        "Separate models flag unusual sale revenue at hourly and daily intervals.",
    )
    st.caption(
        "Each row is a revenue bucket flagged by Isolation Forest. "
        "The configured contamination rate controls how rare a point must be; "
        "alerts are review signals, not confirmed incidents."
    )

    st.subheader("Filter anomalies by date and time")
    st.caption(
        "Choose a year, month, day, and UTC hour to locate matching revenue alerts."
    )

    if "anomaly_page" not in st.session_state:
        st.session_state["anomaly_page"] = 1

    def reset_anomaly_page():
        st.session_state["anomaly_page"] = 1

    filter_columns = st.columns(5, gap="small")

    with filter_columns[0]:
        selected_year = st.selectbox(
            "Calendar year",
            ["All years", 2009, 2010, 2011],
            key="anomaly_year_filter",
            on_change=reset_anomaly_page,
        )

    month_options = ["All months", *calendar.month_name[1:]]
    with filter_columns[1]:
        selected_month_label = st.selectbox(
            "Month",
            month_options,
            key="anomaly_month_filter",
            on_change=reset_anomaly_page,
        )
    selected_month = (
        month_options.index(selected_month_label)
        if selected_month_label != "All months"
        else None
    )

    if selected_month is None:
        day_options = ["All days"]
    else:
        years_to_check = (
            [2009, 2010, 2011] if selected_year == "All years" else [selected_year]
        )
        latest_valid_day = max(
            calendar.monthrange(candidate_year, selected_month)[1]
            for candidate_year in years_to_check
        )
        day_options = ["All days", *range(1, latest_valid_day + 1)]

    day_key = "anomaly_day_filter"
    if st.session_state.get(day_key) not in day_options:
        st.session_state[day_key] = "All days"
    with filter_columns[2]:
        selected_day = st.selectbox(
            "Day",
            day_options,
            disabled=selected_month is None,
            key=day_key,
            on_change=reset_anomaly_page,
        )

    with filter_columns[3]:
        selected_time_scale = st.selectbox(
            "Alert interval",
            ["All intervals", "Hourly", "Daily"],
            key="anomaly_time_scale_filter",
            on_change=reset_anomaly_page,
        )

    hour_key = "anomaly_hour_filter"
    if selected_time_scale == "Daily" and st.session_state.get(hour_key) is not None:
        st.session_state[hour_key] = None
    with filter_columns[4]:
        selected_hour = st.selectbox(
            "Hour (UTC)",
            [None, *range(24)],
            format_func=lambda value: (
                "All hours" if value is None else f"{value:02d}:00"
            ),
            disabled=selected_time_scale == "Daily",
            key=hour_key,
            on_change=reset_anomaly_page,
        )

    filter_params = {"is_anomaly": True, "limit": 100}
    if selected_year != "All years":
        filter_params["year"] = selected_year
    if selected_month is not None:
        filter_params["month"] = selected_month
    if selected_day != "All days":
        filter_params["day"] = selected_day
    if selected_time_scale != "All intervals":
        filter_params["time_scale"] = selected_time_scale.lower()
    if selected_hour is not None:
        filter_params["hour"] = selected_hour
        filter_params["time_scale"] = "hourly"

    page_number = max(1, int(st.session_state.get("anomaly_page", 1)))
    anomaly_load_failed = False
    try:
        anomaly_response = api_get(
            "/anomalies/",
            params={**filter_params, "offset": (page_number - 1) * 100},
        )
        anomalies = anomaly_response.get("anomalies", [])
        total_count = int(
            anomaly_response.get(
                "total_count",
                anomaly_response.get("count", len(anomalies)),
            )
        )
        total_pages = max(1, (total_count + 99) // 100)

        if page_number > total_pages:
            page_number = total_pages
            st.session_state["anomaly_page"] = page_number
            anomaly_response = api_get(
                "/anomalies/",
                params={**filter_params, "offset": (page_number - 1) * 100},
            )
            anomalies = anomaly_response.get("anomalies", [])
            total_count = int(
                anomaly_response.get(
                    "total_count",
                    anomaly_response.get("count", len(anomalies)),
                )
            )
            total_pages = max(1, (total_count + 99) // 100)
    except requests.exceptions.RequestException:
        st.error("Could not load revenue anomaly data.")
        anomalies = []
        total_count = 0
        total_pages = 1
        anomaly_load_failed = True

    hourly_count = int(summary.get("hourly_revenue_anomalies", 0))
    daily_count = int(summary.get("daily_revenue_anomalies", 0))
    overall_count = int(summary.get("total_anomalies", 0))

    a1, a2, a3 = st.columns(3)
    with a1:
        st.metric("All-Time Hourly Revenue Alerts", hourly_count)
    with a2:
        st.metric("All-Time Daily Revenue Alerts", daily_count)
    with a3:
        st.metric("All-Time Revenue Alerts", overall_count)

    st.caption(
        f"{total_count:,} revenue alerts match the selected filters. "
        "Results are ordered newest first; timestamps use UTC."
    )

    if total_pages > 1:
        st.selectbox(
            "Results page",
            list(range(1, total_pages + 1)),
            format_func=lambda page: f"Page {page} of {total_pages}",
            key="anomaly_page",
        )

    if anomaly_load_failed:
        st.info(
            "The matching alert list is unavailable right now. Please try again shortly."
        )
    elif anomalies:
        st.subheader("Revenue Alerts")
        anomaly_rows = [
            {
                "Time Scale": str(anomaly.get("time_scale", "")).title(),
                "Timestamp (UTC)": anomaly.get("timestamp"),
                "Type": str(anomaly.get("anomaly_type", ""))
                .replace("_", " ")
                .title(),
                "Revenue": format_currency(anomaly.get("current_value", 0)),
                "Expected Revenue": format_currency(
                    anomaly.get("baseline_value", 0)
                ),
                "IF Score": anomaly.get("anomaly_score"),
                "Severity": anomaly.get("severity"),
                "Reason": anomaly.get("reason"),
                "Business Impact": anomaly.get("business_impact"),
                "Recommendation": anomaly.get("recommendation"),
            }
            for anomaly in anomalies
        ]
        st.dataframe(
            anomaly_rows,
            hide_index=True,
        )
    elif (
        selected_year != "All years"
        or selected_month is not None
        or selected_day != "All days"
        or selected_time_scale != "All intervals"
        or selected_hour is not None
    ):
        st.info(
            "No revenue alerts match those date and time filters. "
            "Try widening your selection."
        )
    else:
        st.info(
            "No hourly or daily revenue outliers have been recorded yet. "
            "The models need at least 14 days of hourly history and 60 days of daily history."
        )

# =========================================================
# PREDICTIONS
# =========================================================

if st.session_state.active_section == "Predictions":

    show_section_heading(
        "Predictive Analytics",
        "Weekly StockCode Demand Forecast",
        "Estimate how many units of a selected StockCode a country may need in each upcoming dataset week.",
    )

    if "weekly_forecast_countries" not in st.session_state:
        try:
            country_options_response = api_get("/predictions/weekly/options")
            st.session_state["weekly_forecast_countries"] = (
                country_options_response.get("countries", [])
            )
        except requests.exceptions.RequestException:
            st.error("Could not load the countries. Check the analytics API connection.")
    country_options = st.session_state.get("weekly_forecast_countries", [])

    if country_options:
        filter_columns = st.columns([1, 1.4, 1])
        with filter_columns[0]:
            selected_country = st.selectbox(
                "Country",
                country_options,
                key="weekly_forecast_country",
            )
        previous_country = st.session_state.get("weekly_forecast_last_country")
        if previous_country != selected_country:
            st.session_state["weekly_forecast_search"] = ""
            st.session_state["weekly_forecast_search_input"] = ""
            st.session_state["weekly_forecast_stock_options_key"] = None
            st.session_state["weekly_forecast_last_country"] = selected_country
        with filter_columns[1]:
            with st.form("weekly_stock_code_search_form"):
                search_input = st.text_input(
                    "Search StockCode or description",
                    key="weekly_forecast_search_input",
                    placeholder="Type a StockCode or product description",
                )
                apply_search = st.form_submit_button("Find StockCodes")
        if apply_search:
            st.session_state["weekly_forecast_search"] = search_input.strip()
        stock_code_search = st.session_state.get("weekly_forecast_search", "")
        with filter_columns[2]:
            horizon_weeks = st.slider(
                "Forecast horizon (weeks)",
                min_value=1,
                max_value=13,
                value=13,
                help="Choose 1–13 weekly forecasts (up to approximately 3 months).",
                key="weekly_forecast_horizon",
            )

        options_key = (selected_country, stock_code_search)
        if st.session_state.get("weekly_forecast_stock_options_key") != options_key:
            try:
                stock_options_response = api_get(
                    "/predictions/weekly/options",
                    params={
                        "country": selected_country,
                        "search": stock_code_search or None,
                        "limit": 50,
                    },
                )
                st.session_state["weekly_forecast_stock_options"] = (
                    stock_options_response.get("stock_codes", [])
                )
                st.session_state["weekly_forecast_stock_options_key"] = options_key
            except requests.exceptions.RequestException:
                st.error("Could not load StockCodes for the selected country.")
        stock_codes = st.session_state.get("weekly_forecast_stock_options", [])
        if st.session_state.get("weekly_forecast_stock_options_key") != options_key:
            stock_codes = []

        if stock_codes:
            stock_by_code = {
                item["stock_code"]: item
                for item in stock_codes
                if item.get("stock_code")
            }
            code_options = list(stock_by_code)
            if (
                st.session_state.get("weekly_forecast_stock_code")
                not in code_options
            ):
                st.session_state["weekly_forecast_stock_code"] = code_options[0]
            selected_stock_code = st.selectbox(
                "StockCode",
                code_options,
                format_func=lambda code: (
                    f"{code} — {stock_by_code[code].get('description') or 'Description unavailable'}"
                ),
                key="weekly_forecast_stock_code",
            )

            selected_stock = stock_by_code[selected_stock_code]
            st.caption(
                f"{selected_stock.get('sale_lines', 0):,} historical sale lines · "
                f"{selected_stock.get('units_sold', 0):,} units sold in {selected_country}"
            )

            request_key = {
                "country": selected_country,
                "stock_code": selected_stock_code,
                "weeks": horizon_weeks,
            }
            if st.button("Generate weekly forecast", type="primary"):
                st.session_state.pop("weekly_forecast_result", None)
                st.session_state.pop("weekly_forecast_request", None)
                try:
                    with st.spinner(
                        "Training the Random Forest model on this product's weekly sales..."
                    ):
                        forecast_response = api_get(
                            "/predictions/weekly-forecast",
                            params=request_key,
                        )
                    st.session_state["weekly_forecast_result"] = forecast_response
                    st.session_state["weekly_forecast_request"] = request_key
                except requests.exceptions.HTTPError as error:
                    detail = "Forecast could not be generated."
                    try:
                        detail = error.response.json().get("detail", detail)
                    except (AttributeError, ValueError):
                        pass
                    st.error(str(detail))
                except requests.exceptions.RequestException:
                    st.error("Could not reach the analytics API to generate the forecast.")

            forecast_result = st.session_state.get("weekly_forecast_result")
            forecast_request = st.session_state.get("weekly_forecast_request")
            if forecast_result and forecast_request == request_key:
                st.success(
                    f"Random Forest forecast ready for {selected_stock_code} in {selected_country}."
                )
                latest_week = forecast_result.get("last_observed_week", "unknown")
                st.caption(
                    f"Weekly history: {forecast_result.get('history_start_week')} "
                    f"through {latest_week}. The first forecast week starts immediately "
                    "after that final historical week."
                )

                forecast_rows = forecast_result.get("forecast", [])
                total_units = sum(
                    int(item.get("predicted_units", 0))
                    for item in forecast_rows
                )
                metric_columns = st.columns(3)
                with metric_columns[0]:
                    st.metric("Forecast Units", f"{total_units:,}")
                with metric_columns[1]:
                    st.metric("Forecast Weeks", len(forecast_rows))
                with metric_columns[2]:
                    st.metric(
                        "Historical Weeks",
                        f"{forecast_result.get('history_weeks', 0):,}",
                    )

                week_options = ["All weeks", *range(1, len(forecast_rows) + 1)]
                if (
                    st.session_state.get("weekly_forecast_week_filter")
                    not in week_options
                ):
                    st.session_state["weekly_forecast_week_filter"] = "All weeks"
                selected_week = st.selectbox(
                    "Filter by forecast week",
                    week_options,
                    format_func=lambda week: (
                        week if isinstance(week, str) else f"Week {week}"
                    ),
                    key="weekly_forecast_week_filter",
                )
                visible_rows = forecast_rows
                if selected_week != "All weeks":
                    visible_rows = [
                        item
                        for item in forecast_rows
                        if item.get("week_number") == selected_week
                    ]

                table_rows = [
                    {
                        "Forecast Week": f"Week {item['week_number']}",
                        "Week Starts": item.get("week_start"),
                        "Week Ends": item.get("week_end"),
                        "Predicted Units Required": item.get("predicted_units", 0),
                    }
                    for item in visible_rows
                ]
                st.dataframe(
                    pd.DataFrame(table_rows),
                    hide_index=True,
                    use_container_width=True,
                )
                if visible_rows:
                    chart_data = pd.DataFrame(
                        [
                            {
                                "Week starting": item.get("week_start"),
                                "Predicted units": item.get("predicted_units", 0),
                            }
                            for item in visible_rows
                        ]
                    ).set_index("Week starting")
                    st.line_chart(chart_data)
                st.caption(
                    "The model is trained separately for the selected country and "
                    "StockCode. Future weeks are predicted recursively, so each "
                    "later estimate also uses earlier forecast estimates."
                )
        elif stock_code_search.strip():
            st.info(
                "No StockCodes in this country match that search. Try another code "
                "or part of the product description."
            )
        else:
            st.info(
                "No StockCodes with positive historical sales were found for this country."
            )
    else:
        st.info("No countries with positive historical sales are available.")


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


