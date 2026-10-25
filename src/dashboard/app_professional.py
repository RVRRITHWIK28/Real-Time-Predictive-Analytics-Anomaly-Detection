import calendar
import json
import os
import time
from datetime import datetime, timezone

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st



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
        font-family: Inter, "Segoe UI", sans-serif;
        color: #e2e8f0;
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
        padding-top: 1.15rem;
        padding-bottom: 2.5rem;
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
        padding: 1.45rem 1.5rem 1.2rem;
        margin-bottom: 0.8rem;
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
        font-size: clamp(1.85rem, 3.4vw, 2.45rem);
        font-weight: 780;
        letter-spacing: -0.045em;
        line-height: 1.08;
        margin: 0;
    }

    .hero-subtitle {
        max-width: 820px;
        margin: 0.72rem auto 0;
        color: #a8b5ca;
        font-size: 0.96rem;
        line-height: 1.6;
    }

    .hero-meta {
        margin: 0.5rem auto 0;
        color: #71809a;
        font-size: 0.75rem;
        letter-spacing: 0.02em;
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

    .status-good { border-color: rgba(34, 197, 94, 0.34); color: #a7f3d0; }
    .status-degraded { border-color: rgba(251, 191, 36, 0.38); color: #fde68a; background: rgba(245, 158, 11, 0.09); }
    .status-offline { border-color: rgba(248, 113, 113, 0.4); color: #fecaca; background: rgba(239, 68, 68, 0.09); }
    .status-degraded .live-dot { background: #fbbf24; animation: none; }
    .status-offline .live-dot { background: #f87171; animation: none; }
    .hero-meta span { margin: 0 0.35rem; }

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
        background: rgba(15, 23, 42, 0.74);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.14);
        transition: transform 200ms ease, border-color 200ms ease, box-shadow 200ms ease, background 200ms ease;
        animation: enter-soft 480ms ease;
    }

    div[data-testid="stMetric"]:hover {
        transform: translateY(-3px);
        border-color: rgba(56, 189, 248, 0.42);
        background: rgba(21, 32, 56, 0.92);
        box-shadow: 0 16px 38px rgba(0, 0, 0, 0.24), 0 0 22px rgba(56, 189, 248, 0.10);
    }

    div[data-testid="stMetric"]:hover [data-testid="stMetricValue"] {
        color: #ffffff;
        text-shadow: 0 0 18px rgba(56, 189, 248, 0.22);
    }

    div[data-testid="stMetric"]:hover [data-testid="stMetricLabel"] {
        color: #c4b5fd;
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
    [data-testid="stArrowVegaLiteChart"],
    [data-testid="stPlotlyChart"] {
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
        [data-testid="stArrowVegaLiteChart"],
        [data-testid="stPlotlyChart"] {
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


def check_backend_status():
    """Report API and MongoDB health without relying on cached dashboard data."""
    try:
        response = requests.get(f"{API_URL}/health/detailed", timeout=(2, 3))
        response.raise_for_status()
        health = response.json()
        if health.get("status") == "healthy" and health.get("database") == "connected":
            return "ANALYTICS + DATABASE CONNECTED", "good"
        if health.get("status") == "healthy":
            return "ANALYTICS API CONNECTED", "degraded"
        return "DATABASE UNAVAILABLE", "offline"
    except requests.exceptions.RequestException:
        return "ANALYTICS API DISCONNECTED", "offline"


# =========================================================
# HEADER
# =========================================================

backend_label, backend_tone = check_backend_status()
st.markdown(
    f"""
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
        <div class="live-pill status-{backend_tone}" role="status" aria-live="polite">
            <span class="live-dot"></span>
            {backend_label}
        </div>
        <p class="hero-meta">API and database connectivity are checked directly.</p>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# COMMON API HELPERS
# =========================================================

def api_get(endpoint, params=None, ttl_seconds=20):
    cache_key = (
        f"_api_last_success::{endpoint}::"
        f"{json.dumps(params or {}, sort_keys=True, default=str)}"
    )
    cached_at = st.session_state.get(cache_key + "::updated_at")
    if (
        not st.session_state.get("_force_api_refresh")
        and cache_key in st.session_state
        and cached_at is not None
        and (datetime.now(timezone.utc) - cached_at).total_seconds() <= ttl_seconds
    ):
        if backend_tone != "good":
            st.session_state["_api_using_cached_data"] = True
        return st.session_state[cache_key]
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
            st.session_state[cache_key + "::updated_at"] = datetime.now(timezone.utc)
            st.session_state["_dashboard_last_updated"] = datetime.now(timezone.utc).strftime("%d %b %Y, %H:%M UTC")
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


PLOTLY_CONFIG = {"displayModeBar": False, "responsive": True, "scrollZoom": False}


def style_figure(fig, height=360):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(12,18,33,0.55)",
        font={"family": "Inter, Segoe UI, sans-serif", "color": "#cbd5e1", "size": 12},
        height=height,
        margin={"l": 8, "r": 18, "t": 34, "b": 8},
        hoverlabel={"bgcolor": "#111827", "bordercolor": "#334155", "font": {"color": "#f8fafc"}},
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "xanchor": "left", "x": 0},
    )
    fig.update_xaxes(showgrid=False, zeroline=False, linecolor="rgba(148,163,184,0.18)")
    fig.update_yaxes(showgrid=True, gridcolor="rgba(148,163,184,0.12)", zeroline=False)
    return fig


def show_plotly(fig, height=360):
    st.plotly_chart(style_figure(fig, height), width="stretch", config=PLOTLY_CONFIG)


def reset_overview_filters():
    for key in ("overview_country_filter", "overview_product_filter", "overview_granularity", "overview_date_range"):
        st.session_state.pop(key, None)


def reset_product_filters():
    st.session_state.pop("country_search", None)
    st.session_state.pop("product_search", None)


def reset_anomaly_filters():
    for key in ("anomaly_year_filter", "anomaly_month_filter", "anomaly_day_filter", "anomaly_time_scale_filter", "anomaly_hour_filter", "anomaly_type_filter", "anomaly_page"):
        st.session_state.pop(key, None)


def reset_forecast_filters():
    for key in ("weekly_forecast_country", "weekly_forecast_search", "weekly_forecast_search_input", "weekly_forecast_horizon", "weekly_forecast_week_filter", "weekly_forecast_stock_code", "weekly_forecast_result", "weekly_forecast_request", "weekly_forecast_generated_at"):
        st.session_state.pop(key, None)


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


def request_dashboard_refresh():
    st.session_state["_force_api_refresh"] = True


refresh_columns = st.columns([5, 1])
with refresh_columns[1]:
    st.button(
        "↻ Refresh data",
        key="dashboard_refresh",
        width="stretch",
        on_click=request_dashboard_refresh,
    )
    st.caption(
        f"Last refreshed: {st.session_state.get('_dashboard_last_updated', 'not yet')}"
    )


# =========================================================
# TOP KPI ROW
# =========================================================

kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.metric(
        "🧾 Sale Lines",
        format_compact_number(summary.get("total_transactions", 0)),
        help="Total sale-line records stored in the analytics database."
    )

with kpi2:
    st.metric(
        "📦 Units Sold",
        format_compact_number(summary.get("total_quantity", 0)),
        help="Total positive quantity across stored sale lines."
    )

with kpi3:
    st.metric(
        "💷 Total Revenue",
        format_currency(summary.get("total_revenue", 0)),
        help="Revenue total returned by the analytics API."
    )

with kpi4:
    st.metric(
        "◉ Average Sale Line Value",
        format_currency(
            summary.get(
                "average_sale_line_value",
                summary.get("average_order_value", 0),
            )
        ),
        help="Average revenue per sale line using the API summary calculation.",
    )


# =========================================================
# SECONDARY KPI ROW
# =========================================================

st.markdown("<div style='height: 10px'></div>", unsafe_allow_html=True)

kpi5, kpi6, kpi7, kpi8, kpi9 = st.columns(5)

with kpi5:
    st.metric(
        "🏷️ Products",
        f"{round(float(summary.get('unique_products', 0))):,}",
    )

with kpi6:
    st.metric(
        "🌐 Countries",
        f"{round(float(summary.get('unique_countries', summary.get('unique_stores', 0)))):,}",
    )

with kpi7:
    st.metric(
        "⏱️ Hourly Revenue Anomalies",
        f"{summary.get('hourly_revenue_anomalies', 0):,}",
    )

with kpi8:
    st.metric(
        "🗓️ Daily Revenue Anomalies",
        f"{summary.get('daily_revenue_anomalies', 0):,}",
    )

with kpi9:
    st.metric(
        "🚨 Revenue Anomalies",
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
        "Explore historical revenue and transaction volume using filters that update the underlying analytics query.",
    )

    st.button(
        "Reset overview filters",
        key="reset_overview_filters",
        on_click=reset_overview_filters,
    )

    if not st.session_state.get("_overview_country_options"):
        try:
            country_response = api_get("/stores/").get("stores", [])
            st.session_state["_overview_country_options"] = sorted(
                {
                    str(item.get("store_id") or item.get("country"))
                    for item in country_response
                    if item.get("store_id") or item.get("country")
                }
            )
        except requests.exceptions.RequestException:
            st.session_state["_overview_country_options"] = []

    country_options = ["All countries", *st.session_state.get("_overview_country_options", [])]
    with st.form("overview_scope_filters", border=False):
        filter_columns = st.columns([1.1, 1.25, 0.85, 0.8], gap="medium")
        with filter_columns[0]:
            selected_country = st.selectbox(
                "Country",
                country_options,
                key="overview_country_filter",
            )
        with filter_columns[1]:
            selected_product = st.text_input(
                "StockCode (exact)",
                placeholder="Optional, e.g. 85123A",
                help="Enter one exact StockCode to scope the revenue and volume trends.",
                key="overview_product_filter",
            ).strip()
        with filter_columns[2]:
            selected_granularity = st.selectbox(
                "Time granularity",
                ["Daily", "Weekly", "Monthly"],
                index=2,
                key="overview_granularity",
            )
        with filter_columns[3]:
            st.form_submit_button("Apply filters", type="primary")

    analytics_params = {}
    if selected_country != "All countries":
        analytics_params["country"] = selected_country
    if selected_product:
        analytics_params["product_id"] = selected_product

    try:
        daily_data = api_get(
            "/analytics/daily",
            params=analytics_params or None,
        ).get("daily", [])
    except requests.exceptions.RequestException:
        st.error("Could not load the selected analytics series.")
        daily_data = []

    if daily_data:
        analytics_frame = pd.DataFrame(daily_data)
        analytics_frame["date"] = pd.to_datetime(
            analytics_frame["date"], errors="coerce"
        ).dt.normalize()
        analytics_frame = analytics_frame.dropna(subset=["date"]).sort_values("date")

        if not analytics_frame.empty:
            min_date = analytics_frame["date"].min().date()
            max_date = analytics_frame["date"].max().date()
            saved_range = st.session_state.get("overview_date_range")
            if (
                isinstance(saved_range, (tuple, list))
                and len(saved_range) == 2
                and (
                    saved_range[0] < min_date
                    or saved_range[1] > max_date
                    or saved_range[0] > saved_range[1]
                )
            ):
                st.session_state.pop("overview_date_range", None)

            date_columns = st.columns([1.25, 2.75], gap="medium")
            with date_columns[0]:
                selected_dates = st.date_input(
                    "Date range",
                    value=(min_date, max_date),
                    min_value=min_date,
                    max_value=max_date,
                    key="overview_date_range",
                )
            with date_columns[1]:
                active_scope = []
                if selected_country != "All countries":
                    active_scope.append(selected_country)
                if selected_product:
                    active_scope.append(f"StockCode {selected_product}")
                scope_label = " · ".join(active_scope) if active_scope else "All countries and StockCodes"
                st.caption(
                    f"{scope_label} · {selected_granularity.lower()} view · dates follow the selected data"
                )

            if isinstance(selected_dates, (tuple, list)):
                if len(selected_dates) == 2:
                    range_start, range_end = selected_dates
                elif len(selected_dates) == 1:
                    range_start = range_end = selected_dates[0]
                else:
                    range_start, range_end = min_date, max_date
            else:
                range_start = range_end = selected_dates

            filtered_frame = analytics_frame[
                analytics_frame["date"].dt.date.between(range_start, range_end)
            ].copy()
            period_mode = selected_granularity
            if period_mode == "Weekly":
                filtered_frame["period"] = (
                    filtered_frame["date"].dt.to_period("W-SUN").dt.start_time
                )
            elif period_mode == "Monthly":
                filtered_frame["period"] = (
                    filtered_frame["date"].dt.to_period("M").dt.to_timestamp()
                )
            else:
                filtered_frame["period"] = filtered_frame["date"]

            trend_data = (
                filtered_frame.groupby("period", as_index=False)
                .agg(
                    total_revenue=("total_revenue", "sum"),
                    transaction_count=("transaction_count", "sum"),
                    total_quantity=("total_quantity", "sum"),
                )
                .sort_values("period")
            )

            if not trend_data.empty:
                st.caption(
                    f"{len(filtered_frame):,} daily records · "
                    f"{int(trend_data['transaction_count'].sum()):,} sale lines · "
                    f"{format_currency(trend_data['total_revenue'].sum())} revenue in this view"
                )

                chart_columns = st.columns(2, gap="large")
                with chart_columns[0]:
                    st.subheader(f"{selected_granularity} revenue")
                    revenue_fig = px.area(
                        trend_data,
                        x="period",
                        y="total_revenue",
                        labels={"period": "Period", "total_revenue": "Revenue"},
                    )
                    revenue_fig.update_traces(
                        line={"color": "#38bdf8", "width": 2.5},
                        fillcolor="rgba(56,189,248,0.12)",
                        hovertemplate="%{x|%d %b %Y}<br>Revenue: £%{y:,.2f}<extra></extra>",
                    )
                    revenue_fig.update_yaxes(tickprefix="£", tickformat=",.0f")
                    show_plotly(revenue_fig, 360)

                with chart_columns[1]:
                    st.subheader(f"{selected_granularity} sale line volume")
                    volume_fig = px.bar(
                        trend_data,
                        x="period",
                        y="transaction_count",
                        labels={"period": "Period", "transaction_count": "Sale lines"},
                    )
                    volume_fig.update_traces(
                        marker_color="#8b7cf6",
                        hovertemplate="%{x|%d %b %Y}<br>Sale lines: %{y:,}<extra></extra>",
                    )
                    volume_fig.update_yaxes(tickformat=",.0f")
                    show_plotly(volume_fig, 360)

                export_frame = trend_data.rename(
                    columns={
                        "period": "Period",
                        "total_revenue": "Revenue",
                        "transaction_count": "Sale Lines",
                        "total_quantity": "Units Sold",
                    }
                )
                st.download_button(
                    "Download filtered trend data",
                    data=export_frame.to_csv(index=False).encode("utf-8"),
                    file_name="retail_trends_filtered.csv",
                    mime="text/csv",
                    key="download_overview_trends",
                )

                st.subheader("Period summary")
                summary_rows = [
                    {
                        "Period": item.period.strftime("%d %b %Y"),
                        "Sale Lines": int(item.transaction_count),
                        "Units Sold": int(item.total_quantity),
                        "Revenue": format_currency(item.total_revenue),
                    }
                    for item in trend_data.itertuples(index=False)
                ]
                st.dataframe(
                    summary_rows,
                    hide_index=True,
                    height=360,
                    alt="Filtered revenue, sale-line, and unit totals by selected period",
                )
            else:
                st.info("No analytics records fall inside the selected date range.")
        else:
            st.info("No valid dated analytics records are available.")
    else:
        st.info("No daily analytics available for the selected filters.")


# =========================================================
# PRODUCTS & COUNTRIES
# =========================================================

if st.session_state.active_section == "Products":

    show_section_heading(
        "Products & Countries",
        "Retail Performance",
        "Rank country and product performance by units and revenue, then search the actual stored records.",
    )
    st.button(
        "Clear country and product searches",
        key="reset_product_filters",
        on_click=reset_product_filters,
    )

    try:
        products = api_get("/products/", ttl_seconds=60).get("products", [])
    except requests.exceptions.RequestException:
        st.error("Could not load product analytics.")
        products = []

    try:
        stores = api_get("/stores/", ttl_seconds=60).get("stores", [])
    except requests.exceptions.RequestException:
        st.error("Could not load country analytics.")
        stores = []

    country_search_columns = st.columns(2, gap="medium")
    with country_search_columns[0]:
        country_query = st.text_input(
            "Filter countries",
            placeholder="Search country name",
            key="country_search",
        ).strip().casefold()
    with country_search_columns[1]:
        product_query = st.text_input(
            "Filter products",
            placeholder="Search StockCode or description",
            key="product_search",
        ).strip().casefold()

    if stores:
        country_chart_rows = []
        for store in stores:
            country = str(store.get("store_id") or store.get("country") or "Unknown")
            if country_query and country_query not in country.casefold():
                continue
            country_chart_rows.append(
                {
                    "Country": country,
                    "Units Sold": round(max(float(store.get("total_quantity", 0) or 0), 0.0)),
                    "Revenue": float(store.get("total_revenue", 0) or 0),
                    "Sale Lines": round(float(store.get("transaction_count", 0) or 0)),
                }
            )
        country_chart_frame = pd.DataFrame(country_chart_rows).sort_values(
            "Units Sold", ascending=False
        ) if country_chart_rows else pd.DataFrame()

        st.subheader("Country sales performance")
        if not country_chart_frame.empty:
            country_chart_columns = st.columns(2, gap="large")
            units_countries = (
                country_chart_frame.nlargest(15, "Units Sold")
                .sort_values("Units Sold", ascending=True)
            )
            with country_chart_columns[0]:
                st.markdown("**Top 15 countries · units sold**")
                country_units_fig = px.bar(
                    units_countries,
                    x="Units Sold",
                    y="Country",
                    orientation="h",
                    custom_data=["Revenue", "Sale Lines"],
                    labels={"Units Sold": "Units sold"},
                )
                country_units_fig.update_traces(
                    marker_color="#38bdf8",
                    hovertemplate="%{y}<br>Units sold: %{x:,.0f}<br>Revenue: £%{customdata[0]:,.2f}<br>Sale lines: %{customdata[1]:,.0f}<extra></extra>",
                )
                country_units_fig.update_xaxes(tickformat=",.0f")
                country_units_fig.update_yaxes(showgrid=False)
                show_plotly(country_units_fig, max(360, len(units_countries) * 29))

            revenue_countries = (
                country_chart_frame.nlargest(15, "Revenue")
                .sort_values("Revenue", ascending=True)
            )
            with country_chart_columns[1]:
                st.markdown("**Top 15 countries · revenue**")
                country_revenue_fig = px.bar(
                    revenue_countries,
                    x="Revenue",
                    y="Country",
                    orientation="h",
                    custom_data=["Units Sold", "Sale Lines"],
                    labels={"Revenue": "Revenue"},
                )
                country_revenue_fig.update_traces(
                    marker_color="#8b7cf6",
                    hovertemplate="%{y}<br>Revenue: £%{x:,.2f}<br>Units sold: %{customdata[0]:,.0f}<br>Sale lines: %{customdata[1]:,.0f}<extra></extra>",
                )
                country_revenue_fig.update_xaxes(tickprefix="£", tickformat=",.0f")
                country_revenue_fig.update_yaxes(showgrid=False)
                show_plotly(country_revenue_fig, max(360, len(revenue_countries) * 29))

            st.subheader("Country Performance")
            country_rows = [
                {
                    "Country": row["Country"],
                    "Units Sold": row["Units Sold"],
                    "Revenue": format_currency(row["Revenue"]),
                    "Sale Lines": row["Sale Lines"],
                }
                for row in country_chart_frame.sort_values("Units Sold", ascending=False).to_dict("records")
            ]
            st.caption(f"{len(country_rows):,} countries match the current search.")
            st.dataframe(
                country_rows,
                hide_index=True,
                height=420,
                alt="Country totals sorted by units sold, with revenue and sale-line totals",
            )
            st.download_button(
                "Download filtered country performance",
                data=pd.DataFrame(country_rows).to_csv(index=False).encode("utf-8"),
                file_name="country_performance_filtered.csv",
                mime="text/csv",
                key="download_country_performance",
            )
        else:
            st.info("No countries match the current search.")
    else:
        st.info("No country analytics available.")

    st.markdown("<div style='height: 12px'></div>", unsafe_allow_html=True)

    if products:
        product_chart_rows = []
        for product in products:
            product_code = str(product.get("product_id") or "Unknown")
            description = str(product.get("description") or "").strip()
            if product_query and (
                product_query not in product_code.casefold()
                and product_query not in description.casefold()
            ):
                continue
            product_chart_rows.append(
                {
                    "StockCode": product_code,
                    "Description": description,
                    "Units Sold": round(max(float(product.get("total_quantity", 0) or 0), 0.0)),
                    "Revenue": float(product.get("total_revenue", 0) or 0),
                    "Sale Lines": round(float(product.get("transaction_count", 0) or 0)),
                }
            )

        product_chart_frame = pd.DataFrame(product_chart_rows)
        if not product_chart_frame.empty:
            st.subheader("Product sales performance")
            product_chart_columns = st.columns(2, gap="large")
            top_products_units = (
                product_chart_frame.nlargest(15, "Units Sold")
                .sort_values("Units Sold", ascending=True)
            )
            with product_chart_columns[0]:
                st.markdown("**Top 15 products · units sold**")
                products_units_fig = px.bar(
                    top_products_units,
                    x="Units Sold",
                    y="StockCode",
                    orientation="h",
                    custom_data=["Description", "Revenue", "Sale Lines"],
                    labels={"StockCode": "StockCode", "Units Sold": "Units sold"},
                )
                products_units_fig.update_traces(
                    marker_color="#38bdf8",
                    hovertemplate="%{y}<br>%{customdata[0]}<br>Units sold: %{x:,.0f}<br>Revenue: £%{customdata[1]:,.2f}<br>Sale lines: %{customdata[2]:,.0f}<extra></extra>",
                )
                products_units_fig.update_xaxes(tickformat=",.0f")
                products_units_fig.update_yaxes(showgrid=False)
                show_plotly(products_units_fig, max(360, len(top_products_units) * 29))

            top_products_revenue = (
                product_chart_frame.nlargest(15, "Revenue")
                .sort_values("Revenue", ascending=True)
            )
            with product_chart_columns[1]:
                st.markdown("**Top 15 products · revenue**")
                products_revenue_fig = px.bar(
                    top_products_revenue,
                    x="Revenue",
                    y="StockCode",
                    orientation="h",
                    custom_data=["Description", "Units Sold", "Sale Lines"],
                    labels={"Revenue": "Revenue"},
                )
                products_revenue_fig.update_traces(
                    marker_color="#8b7cf6",
                    hovertemplate="%{y}<br>%{customdata[0]}<br>Revenue: £%{x:,.2f}<br>Units sold: %{customdata[1]:,.0f}<br>Sale lines: %{customdata[2]:,.0f}<extra></extra>",
                )
                products_revenue_fig.update_xaxes(tickprefix="£", tickformat=",.0f")
                products_revenue_fig.update_yaxes(showgrid=False)
                show_plotly(products_revenue_fig, max(360, len(top_products_revenue) * 29))

            st.subheader("Product Performance")
            sorted_product_rows = product_chart_frame.sort_values(
                "Units Sold", ascending=False
            )
            product_rows = [
                {
                    "StockCode": row["StockCode"],
                    "Description": row["Description"],
                    "Units Sold": row["Units Sold"],
                    "Revenue": format_currency(row["Revenue"]),
                    "Sale Lines": row["Sale Lines"],
                }
                for row in sorted_product_rows.to_dict("records")
            ]
            st.caption(f"{len(product_rows):,} products match the current search; sorted by units sold.")
            st.dataframe(
                product_rows,
                hide_index=True,
                height=520,
                alt="Product totals sorted by units sold, with descriptions, revenue, and sale-line totals",
            )
            st.download_button(
                "Download filtered product performance",
                data=pd.DataFrame(product_rows).to_csv(index=False).encode("utf-8"),
                file_name="product_performance_filtered.csv",
                mime="text/csv",
                key="download_product_performance",
            )
        else:
            st.info("No products match the current search.")
    else:
        st.info("No product analytics available.")


# ANOMALIES
# =========================================================

if st.session_state.active_section == "Anomalies":

    show_section_heading(
        "Isolation Forest",
        "Hourly & Daily Revenue Anomalies",
        "Inspect unusual revenue buckets detected by the existing hourly and daily Isolation Forest models.",
    )
    st.caption(
        "Alerts are model review signals, not confirmed incidents. Charts summarize the currently loaded page; the event table is paginated."
    )
    st.button(
        "Reset anomaly filters",
        key="reset_anomaly_filter_button",
        on_click=reset_anomaly_filters,
    )

    st.subheader("Filter alerts by date, interval, and event type")

    if "anomaly_page" not in st.session_state:
        st.session_state["anomaly_page"] = 1

    def reset_anomaly_page():
        st.session_state["anomaly_page"] = 1

    filter_columns = st.columns([0.9, 1, 0.8, 1, 0.9, 1.3], gap="small")

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

    anomaly_type_options = {
        "All event types": None,
        "Hourly revenue spike": "hourly_revenue_spike",
        "Hourly revenue drop": "hourly_revenue_drop",
        "Daily revenue spike": "daily_revenue_spike",
        "Daily revenue drop": "daily_revenue_drop",
    }
    with filter_columns[5]:
        selected_anomaly_type = st.selectbox(
            "Revenue event",
            list(anomaly_type_options),
            key="anomaly_type_filter",
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
    if anomaly_type_options[selected_anomaly_type]:
        filter_params["anomaly_type"] = anomaly_type_options[selected_anomaly_type]

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
        st.metric("⏱️ All-time hourly revenue alerts", hourly_count)
    with a2:
        st.metric("🗓️ All-time daily revenue alerts", daily_count)
    with a3:
        st.metric("🚨 All-time revenue alerts", overall_count)

    st.caption(
        f"{total_count:,} revenue alerts match the selected filters. "
        "Event timestamps are shown in UTC."
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
        anomaly_frame = pd.DataFrame(anomalies)
        time_column = "bucket" if "bucket" in anomaly_frame else "timestamp"
        anomaly_frame["event_time"] = pd.to_datetime(
            anomaly_frame.get(time_column), errors="coerce", utc=True
        )
        anomaly_frame["current_value"] = pd.to_numeric(
            anomaly_frame.get("current_value"), errors="coerce"
        )
        anomaly_frame["severity_label"] = (
            anomaly_frame.get("severity", pd.Series(index=anomaly_frame.index, dtype="object"))
            .fillna("Unspecified")
            .astype(str)
            .str.title()
        )
        anomaly_frame["time_scale_label"] = (
            anomaly_frame.get("time_scale", pd.Series(index=anomaly_frame.index, dtype="object"))
            .fillna("Unknown")
            .astype(str)
            .str.title()
        )
        for optional_column in ("baseline_value", "anomaly_score", "anomaly_type"):
            if optional_column not in anomaly_frame:
                anomaly_frame[optional_column] = None

        st.subheader("Revenue alert activity")
        st.caption(
            f"Showing charts for the {len(anomalies)} events on page {page_number} of {total_pages}."
        )
        valid_events = anomaly_frame.dropna(subset=["event_time", "current_value"])
        if not valid_events.empty:
            anomaly_chart_columns = st.columns([1.65, 1], gap="large")
            with anomaly_chart_columns[0]:
                st.markdown("**Flagged revenue by time**")
                anomaly_fig = px.scatter(
                    valid_events,
                    x="event_time",
                    y="current_value",
                    color="severity_label",
                    symbol="time_scale_label",
                    custom_data=["baseline_value", "anomaly_score", "anomaly_type"],
                    color_discrete_map={
                        "High": "#fb7185",
                        "Medium": "#fbbf24",
                        "Low": "#38bdf8",
                        "Unspecified": "#94a3b8",
                    },
                    labels={
                        "event_time": "Time (UTC)",
                        "current_value": "Observed revenue",
                        "severity_label": "Severity",
                        "time_scale": "Interval",
                    },
                )
                anomaly_fig.update_traces(
                    hovertemplate="%{x|%d %b %Y %H:%M UTC}<br>Observed revenue: £%{y:,.2f}<br>Expected revenue: £%{customdata[0]:,.2f}<br>IF score: %{customdata[1]}<br>Event: %{customdata[2]}<extra></extra>"
                )
                anomaly_fig.update_yaxes(tickprefix="£", tickformat=",.0f")
                show_plotly(anomaly_fig, 400)

            with anomaly_chart_columns[1]:
                st.markdown("**Severity on this page**")
                severity_data = (
                    anomaly_frame["severity_label"]
                    .value_counts()
                    .rename_axis("Severity")
                    .reset_index(name="Alerts")
                )
                severity_fig = px.bar(
                    severity_data,
                    x="Severity",
                    y="Alerts",
                    color="Severity",
                    color_discrete_map={
                        "High": "#fb7185",
                        "Medium": "#fbbf24",
                        "Low": "#38bdf8",
                        "Unspecified": "#94a3b8",
                    },
                )
                severity_fig.update_layout(showlegend=False)
                severity_fig.update_traces(
                    hovertemplate="%{x}<br>Alerts: %{y:,}<extra></extra>"
                )
                severity_fig.update_yaxes(tickformat=",.0f")
                show_plotly(severity_fig, 400)
        else:
            st.info("These events do not include valid timestamps and revenue values for charting.")

        anomaly_rows = [
            {
                "Interval": str(anomaly.get("time_scale", "")).title(),
                "Timestamp (UTC)": anomaly.get("bucket", anomaly.get("timestamp")),
                "Type": str(anomaly.get("anomaly_type", "")).replace("_", " ").title(),
                "Revenue": format_currency(anomaly.get("current_value", 0)),
                "Expected Revenue": format_currency(anomaly.get("baseline_value", 0)),
                "IF Score": anomaly.get("anomaly_score"),
                "Severity": str(anomaly.get("severity") or "Unspecified").title(),
                "Reason": anomaly.get("reason"),
                "Business Impact": anomaly.get("business_impact"),
                "Recommendation": anomaly.get("recommendation"),
            }
            for anomaly in anomalies
        ]
        st.subheader("Revenue Alerts")
        st.dataframe(anomaly_rows, hide_index=True, height=460)
        st.download_button(
            "Download alerts on this page",
            data=pd.DataFrame(anomaly_rows).to_csv(index=False).encode("utf-8"),
            file_name=f"revenue_alerts_page_{page_number}.csv",
            mime="text/csv",
            key="download_anomalies_page",
        )
    elif (
        selected_year != "All years"
        or selected_month is not None
        or selected_day != "All days"
        or selected_time_scale != "All intervals"
        or selected_hour is not None
        or selected_anomaly_type != "All event types"
    ):
        st.info(
            "No revenue alerts match those date, time, and event-type filters. Try widening your selection."
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
    st.button(
        "Reset forecast filters",
        key="reset_forecast_filter_button",
        on_click=reset_forecast_filters,
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
                            ttl_seconds=0,
                        )
                    st.session_state["weekly_forecast_result"] = forecast_response
                    st.session_state["weekly_forecast_request"] = request_key
                    st.session_state["weekly_forecast_generated_at"] = datetime.now(timezone.utc).strftime("%d %b %Y, %H:%M UTC")
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
                st.caption(
                    f"Model: Random Forest Regressor · 200 trees · recursive weekly estimates · "
                    f"generated {st.session_state.get('weekly_forecast_generated_at', 'time unavailable')}"
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
                    st.metric("🔮 Forecast Units", f"{total_units:,}")
                with metric_columns[1]:
                    st.metric("🗓️ Forecast Weeks", len(forecast_rows))
                with metric_columns[2]:
                    st.metric(
                        "📈 Historical Weeks",
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
                    forecast_fig = go.Figure()
                    history_rows = forecast_result.get("history", [])
                    if history_rows:
                        history_frame = pd.DataFrame(history_rows)
                        forecast_fig.add_scatter(
                            x=history_frame["week_start"],
                            y=history_frame["units"],
                            mode="lines",
                            name="Observed units",
                            line={"color": "#38bdf8", "width": 2.2},
                            hovertemplate="%{x}<br>Observed units: %{y:,.0f}<extra></extra>",
                        )
                    if visible_rows:
                        forecast_fig.add_scatter(
                            x=[item.get("week_start") for item in visible_rows],
                            y=[item.get("predicted_units", 0) for item in visible_rows],
                            mode="lines+markers",
                            name="Forecast units",
                            line={"color": "#a78bfa", "width": 2.4, "dash": "dash"},
                            marker={"size": 8, "color": "#a78bfa"},
                            hovertemplate="%{x}<br>Forecast units: %{y:,.0f}<extra></extra>",
                        )
                    forecast_fig.update_xaxes(title="Week starting")
                    forecast_fig.update_yaxes(title="Units", tickformat=",.0f")
                    show_plotly(forecast_fig, 420)

                st.download_button(
                    "Download selected forecast rows",
                    data=pd.DataFrame(table_rows).to_csv(index=False).encode("utf-8"),
                    file_name=f"weekly_forecast_{selected_stock_code}.csv",
                    mime="text/csv",
                    key="download_weekly_forecast",
                )
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

st.session_state["_force_api_refresh"] = False


st.markdown(
    """
    <div class="footer">
        Online Retail Intelligence • Historical Online Retail Sales • Kafka • MongoDB • FastAPI • ML
    </div>
    """,
    unsafe_allow_html=True,
)


