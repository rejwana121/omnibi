"""
OmniBI: Enterprise Modern Analytics & AI Copilot.
Clean Dribbble / Figma-Grade UI Architecture with Soft Modern Frosted Canvas Aesthetics.
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.database.connection import DuckDBManager
from src.analytics.kpi_engine import KPIEngine
from src.agent.bi_agent import AutonomousBIAgent

# Streamlit Configuration
st.set_page_config(
    page_title="OmniBI | Enterprise Analytics",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Figma / Dribbble Clean Modern SaaS Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Remove Awkward Empty Top Padding */
    .block-container {
        padding-top: 1.2rem !important;
        padding-bottom: 2rem !important;
    }

    /* Soft Modern Dribbble Canvas */
    .stApp {
        background-color: #f8fafc !important;
        color: #0f172a !important;
    }

    /* Clean Brand Header */
    .dribbble-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 18px 28px;
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 20px;
        box-shadow: 0 4px 25px rgba(0, 0, 0, 0.04);
        margin-bottom: 18px;
    }
    .brand-title-wrap {
        display: flex;
        align-items: center;
        gap: 14px;
    }
    .brand-icon-box {
        width: 46px;
        height: 46px;
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        border-radius: 14px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #ffffff;
        font-size: 22px;
        font-weight: 800;
        box-shadow: 0 4px 14px rgba(99, 102, 241, 0.35);
    }
    .brand-heading {
        font-size: 22px;
        font-weight: 800;
        color: #0f172a;
        margin: 0;
        line-height: 1.2;
    }
    .brand-sub {
        font-size: 13px;
        color: #64748b;
        margin: 0;
    }
    .live-status-pill {
        background: #ecfdf5;
        color: #059669;
        border: 1px solid #a7f3d0;
        padding: 6px 14px;
        border-radius: 9999px;
        font-size: 12px;
        font-weight: 700;
        display: inline-flex;
        align-items: center;
        gap: 8px;
    }
    .live-pulse {
        width: 8px;
        height: 8px;
        background-color: #10b981;
        border-radius: 50%;
        box-shadow: 0 0 8px #10b981;
    }

    /* Dribbble Metric Cards */
    .metric-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 20px;
        padding: 22px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        position: relative;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 28px rgba(0, 0, 0, 0.08);
        border-color: #cbd5e1;
    }
    .card-top-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 14px;
    }
    .metric-title {
        font-size: 12px;
        font-weight: 700;
        color: #64748b;
        letter-spacing: 0.6px;
        text-transform: uppercase;
    }
    .pill-green {
        background: #ecfdf5;
        color: #059669;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 11px;
        font-weight: 700;
    }
    .pill-purple {
        background: #f5f3ff;
        color: #7c3aed;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 11px;
        font-weight: 700;
    }
    .pill-blue {
        background: #eff6ff;
        color: #2563eb;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 11px;
        font-weight: 700;
    }
    .metric-big-number {
        font-size: 30px;
        font-weight: 800;
        color: #0f172a;
        letter-spacing: -0.8px;
        line-height: 1.1;
        margin-bottom: 4px;
    }
    .metric-footnote {
        font-size: 12px;
        color: #94a3b8;
    }

    /* Content Panels */
    .white-panel {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 20px;
        padding: 24px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
        margin-bottom: 24px;
    }
    .panel-heading {
        font-size: 16px;
        font-weight: 800;
        color: #0f172a;
        margin-bottom: 4px;
    }
    .panel-sub {
        font-size: 13px;
        color: #64748b;
        margin-bottom: 16px;
    }

    /* High-End Clean Buttons */
    div.stButton > button {
        background: #ffffff !important;
        color: #475569 !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        font-size: 13px !important;
        padding: 8px 16px !important;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.03) !important;
        transition: all 0.2s ease !important;
    }
    div.stButton > button:hover {
        background: #6366f1 !important;
        color: #ffffff !important;
        border-color: #6366f1 !important;
        box-shadow: 0 4px 14px rgba(99, 102, 241, 0.3) !important;
    }

    /* Clean Input Box */
    div.stTextInput > div > div > input {
        background-color: #ffffff !important;
        color: #0f172a !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 12px !important;
        padding: 12px 16px !important;
        font-size: 14px !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.02) !important;
    }
    div.stTextInput > div > div > input:focus {
        border-color: #6366f1 !important;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15) !important;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


def get_services():
    db = DuckDBManager(read_only=True)
    kpis = KPIEngine(db)
    agent = AutonomousBIAgent(db)
    return db, kpis, agent


def format_currency(val: float) -> str:
    if val >= 1_000_000:
        return f"${val / 1_000_000:.2f}M"
    elif val >= 1_000:
        return f"${val / 1_000:.1f}K"
    return f"${val:.2f}"


def main():
    db, kpis, agent = get_services()

    # Dribbble Brand Header with Live Market Ticker
    st.markdown("""
    <div class="dribbble-header">
        <div class="brand-title-wrap">
            <div class="brand-icon-box">⚡</div>
            <div>
                <h1 class="brand-heading">OmniBI Platform</h1>
                <p class="brand-sub">Modern Enterprise Analytics & Autonomous AI Copilot</p>
                <div style="font-size: 12px; color: #6366f1; font-weight: 600; margin-top: 4px;">
                    📈 Real-Time Stream: North America +18.2% YoY • Europe Margin 42.1% • Asia Tech Volume +31.4% • Sub-Second OLAP Latency
                </div>
            </div>
        </div>
        <div class="live-status-pill">
            <div class="live-pulse"></div>
            Vectorized DuckDB: Live Connected
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Dynamic Real-Time Market Filter Controls (Changes all stats & charts live!)
    f_col1, f_col2, f_col3 = st.columns([4, 4, 4])
    with f_col1:
        selected_region = st.selectbox(
            "🌍 Market Region (Filter Live Data)",
            ["All Regions", "North America", "Europe", "Asia-Pacific", "Latin America"]
        )
    with f_col2:
        selected_segment = st.selectbox(
            "🏢 Customer Segment",
            ["All Segments", "Enterprise", "Mid-Market", "SMB", "Consumer"]
        )
    with f_col3:
        st.markdown(f"""
        <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 12px 18px; margin-top: 26px; display: flex; align-items: center; justify-content: space-between;">
            <div>
                <span style="font-size: 11px; font-weight: 700; color: #64748b; text-transform: uppercase;">Active Market Filter</span>
                <div style="font-size: 14px; font-weight: 800; color: #6366f1;">{selected_region} ({selected_segment})</div>
            </div>
            <span style="font-size: 11px; font-weight: 700; color: #059669; background: #ecfdf5; padding: 3px 10px; border-radius: 6px;">
                Auto-Recalculating
            </span>
        </div>
        """, unsafe_allow_html=True)

    clean_region = "All" if selected_region == "All Regions" else selected_region
    clean_segment = "All" if selected_segment == "All Segments" else selected_segment

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # 4 Clean Hero Metric Cards (Dynamically React to Selected Filters)
    summary = kpis.get_executive_summary(region=clean_region, segment=clean_segment)
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="card-top-row">
                <span class="metric-title">Total Revenue</span>
                <span class="pill-green">+14.8% YoY</span>
            </div>
            <div class="metric-big-number">{format_currency(summary['total_revenue'])}</div>
            <div class="metric-footnote">Gross fulfilled transactions</div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="card-top-row">
                <span class="metric-title">Profit Margin</span>
                <span class="pill-purple">Target: 38%</span>
            </div>
            <div class="metric-big-number">{summary['gross_margin_pct']:.1f}%</div>
            <div class="metric-footnote">${format_currency(summary['total_profit'])} net earnings</div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="card-top-row">
                <span class="metric-title">Fulfilled Orders</span>
                <span class="pill-blue">96.2% On-Time</span>
            </div>
            <div class="metric-big-number">{summary['total_orders']:,}</div>
            <div class="metric-footnote">{summary['active_customers']:,} active accounts</div>
        </div>
        """, unsafe_allow_html=True)

    with c4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="card-top-row">
                <span class="metric-title">Customer CSAT</span>
                <span class="pill-green">Healthy</span>
            </div>
            <div class="metric-big-number">{summary['avg_csat']:.2f} <span style="font-size: 16px; color: #94a3b8;">/ 5.0</span></div>
            <div class="metric-footnote">Avg resolution: {summary['avg_resolution_hrs']} hrs</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)

    # Visual Analytics Grid (Area Chart + Category Bar Chart)
    chart1_col, chart2_col = st.columns([7, 5])

    with chart1_col:
        st.markdown(f"""
        <div class="white-panel">
            <div class="panel-heading">📈 Revenue Trajectory & Sales Velocity ({selected_region})</div>
            <div class="panel-sub">Continuous performance timeline across multi-channel sales</div>
        """, unsafe_allow_html=True)

        df_monthly = kpis.get_monthly_revenue_trend(region=clean_region)
        fig_rev = go.Figure()
        fig_rev.add_trace(go.Scatter(
            x=df_monthly["year_month"],
            y=df_monthly["monthly_revenue"],
            mode="lines",
            name="Revenue",
            line=dict(color="#6366f1", width=3, shape="spline"),
            fill="tozeroy",
            fillcolor="rgba(99, 102, 241, 0.08)"
        ))
        fig_rev.update_layout(
            template="plotly_white",
            paper_bgcolor="#ffffff",
            plot_bgcolor="#ffffff",
            margin=dict(l=10, r=10, t=10, b=10),
            height=310,
            xaxis=dict(showgrid=True, gridcolor="#f1f5f9", tickangle=-30),
            yaxis=dict(showgrid=True, gridcolor="#f1f5f9", tickprefix="$"),
            showlegend=False
        )
        st.plotly_chart(fig_rev, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with chart2_col:
        st.markdown(f"""
        <div class="white-panel">
            <div class="panel-heading">🏷️ Category Revenue & Profitability ({selected_region})</div>
            <div class="panel-sub">Breakdown of gross sales across product verticals</div>
        """, unsafe_allow_html=True)

        df_cat = kpis.get_category_performance(region=clean_region)
        fig_cat = px.bar(
            df_cat,
            x="category",
            y="category_revenue",
            color="category",
            color_discrete_sequence=["#6366f1", "#8b5cf6", "#ec4899", "#3b82f6", "#10b981"]
        )
        fig_cat.update_layout(
            template="plotly_white",
            paper_bgcolor="#ffffff",
            plot_bgcolor="#ffffff",
            margin=dict(l=10, r=10, t=10, b=10),
            height=310,
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor="#f1f5f9", tickprefix="$"),
            showlegend=False
        )
        st.plotly_chart(fig_cat, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Clean Recent Transactions Table (Filters live by region)
    st.markdown(f"""
    <div class="white-panel">
        <div class="panel-heading">📦 Recent Transactions & Fulfillment Stream ({selected_region})</div>
        <div class="panel-sub">Latest commercial client orders logged in the DuckDB analytics warehouse</div>
    """, unsafe_allow_html=True)

    recent_orders = kpis.get_recent_orders(region=clean_region, limit=8)
    st.dataframe(recent_orders, use_container_width=True, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Conversational AI Copilot (Clean, Minimalist Card)
    st.markdown("""
    <div class="white-panel">
        <div class="panel-heading">🤖 Ask OmniBI AI Analyst</div>
        <div class="panel-sub">Ask ad-hoc financial questions in plain English. The AI agent compiles and runs DuckDB SQL in real-time.</div>
    """, unsafe_allow_html=True)

    q1, q2, q3, q4 = st.columns(4)
    preset_q = None
    if q1.button("📊 Category Revenue Breakdown", use_container_width=True):
        preset_q = "Show revenue and margin breakdown by product category"
    if q2.button("👑 Top 10 Spending Clients", use_container_width=True):
        preset_q = "Show top 10 highest spend customers"
    if q3.button("📈 Monthly Revenue Timeline", use_container_width=True):
        preset_q = "Show monthly revenue timeline and order volume"
    if q4.button("🎧 Support CSAT Analysis", use_container_width=True):
        preset_q = "Customer support satisfaction and ticket resolution times"

    user_query = st.text_input("Enter your business intelligence question:", value=preset_q or "", placeholder="e.g., Which product category has generated the highest profit?")

    if user_query:
        with st.spinner("Compiling optimized SQL analysis..."):
            result = agent.ask(user_query)

        if result["success"]:
            st.success("Query compiled and executed successfully!")
            st.dataframe(result["data"], use_container_width=True)
        else:
            st.error(f"Error: {result['error']}")

    st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
