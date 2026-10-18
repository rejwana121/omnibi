"""
OmniBI Enterprise Decision Platform & Autonomous AI Agent.
Production-grade dark SaaS interface for executive intelligence and modern OLAP analytics.
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

# Page Configuration
st.set_page_config(
    page_title="OmniBI | Enterprise Decision Engine",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom High-End SaaS Dark Theme Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Background & Container */
    .stApp {
        background: radial-gradient(circle at 10% 20%, #0d131f 0%, #070a10 90%);
        color: #f1f5f9;
    }

    /* Top Brand Header */
    .brand-container {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 12px 20px;
        background: rgba(17, 24, 39, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        backdrop-filter: blur(12px);
        margin-bottom: 24px;
    }

    .brand-title {
        font-size: 22px;
        font-weight: 800;
        background: linear-gradient(135deg, #38bdf8 0%, #818cf8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .status-pill {
        background: rgba(16, 185, 129, 0.15);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.3);
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 12px;
        font-weight: 600;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }
    .status-dot {
        width: 8px;
        height: 8px;
        background-color: #34d399;
        border-radius: 50%;
        box-shadow: 0 0 8px #34d399;
    }

    /* KPI Cards */
    .kpi-grid {
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        gap: 16px;
        margin-bottom: 24px;
    }

    .kpi-card {
        background: rgba(15, 23, 42, 0.75);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 18px 20px;
        backdrop-filter: blur(10px);
        transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
        position: relative;
        overflow: hidden;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        border-color: rgba(56, 189, 248, 0.4);
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5), 0 0 15px rgba(56, 189, 248, 0.1);
    }

    .kpi-top {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 10px;
    }

    .kpi-label {
        font-size: 11px;
        font-weight: 700;
        color: #94a3b8;
        letter-spacing: 0.8px;
        text-transform: uppercase;
    }

    .kpi-badge-green {
        font-size: 11px;
        font-weight: 700;
        color: #34d399;
        background: rgba(16, 185, 129, 0.12);
        padding: 2px 8px;
        border-radius: 6px;
    }
    .kpi-badge-blue {
        font-size: 11px;
        font-weight: 700;
        color: #38bdf8;
        background: rgba(56, 189, 248, 0.12);
        padding: 2px 8px;
        border-radius: 6px;
    }

    .kpi-val {
        font-size: 26px;
        font-weight: 800;
        color: #ffffff;
        letter-spacing: -0.5px;
        line-height: 1.1;
        margin-bottom: 4px;
    }

    .kpi-sub {
        font-size: 12px;
        color: #64748b;
    }

    /* Section Panels */
    .panel-card {
        background: rgba(15, 23, 42, 0.75);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 20px;
        backdrop-filter: blur(8px);
        margin-bottom: 24px;
    }

    /* Custom Badges */
    .tag-critical {
        background: rgba(239, 68, 68, 0.2);
        color: #f87171;
        border: 1px solid rgba(239, 68, 68, 0.3);
        padding: 3px 8px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 11px;
    }
    .tag-tier {
        background: rgba(129, 140, 248, 0.15);
        color: #818cf8;
        padding: 3px 8px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 11px;
    }

    /* Hide Streamlit Header Elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


def get_services():
    db = DuckDBManager()
    kpis = KPIEngine(db)
    agent = AutonomousBIAgent(db)
    return db, kpis, agent


def format_currency(val: float) -> str:
    """Formats large financial figures cleanly with suffixes."""
    if val >= 1_000_000:
        return f"${val / 1_000_000:.2f}M"
    elif val >= 1_000:
        return f"${val / 1_000:.1f}K"
    return f"${val:.2f}"


def main():
    db, kpis, agent = get_services()

    # Top Brand Bar
    st.markdown("""
    <div class="brand-container">
        <div class="brand-title">
            <span>⚡ OmniBI Enterprise</span>
            <span style="font-size: 13px; font-weight: 500; color: #64748b; border-left: 1px solid #334155; padding-left: 10px;">
                Modern OLAP Engine & Autonomous Decision Support
            </span>
        </div>
        <div class="status-pill">
            <div class="status-dot"></div>
            DuckDB In-Memory OLAP Cluster: ACTIVE
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar Navigation
    with st.sidebar:
        st.markdown("<h3 style='color: #f8fafc; font-weight: 800;'>Navigation</h3>", unsafe_allow_html=True)
        app_mode = st.radio(
            "Go to",
            ["📊 Executive Cockpit", "🤖 Autonomous AI Agent", "🗄️ OLAP Data Warehouse"],
            label_visibility="collapsed"
        )

        st.markdown("---")
        st.markdown("<h4 style='color: #94a3b8; font-size: 12px; text-transform: uppercase;'>Global Dimension Filters</h4>", unsafe_allow_html=True)
        
        region_filter = st.selectbox(
            "Geographic Region",
            ["All", "North America", "Europe", "Asia-Pacific", "Latin America"]
        )
        segment_filter = st.selectbox(
            "Customer Segment",
            ["All", "Enterprise", "Mid-Market", "SMB", "Consumer"]
        )

        st.markdown("---")
        st.markdown("""
        <div style="background: rgba(30, 41, 59, 0.5); border: 1px solid rgba(255,255,255,0.06); padding: 12px; border-radius: 8px;">
            <div style="font-size: 11px; color: #38bdf8; font-weight: 700; text-transform: uppercase;">Architecture Stack</div>
            <div style="font-size: 12px; color: #cbd5e1; margin-top: 4px;">• DuckDB Vectorized Execution</div>
            <div style="font-size: 12px; color: #cbd5e1;">• PyArrow Columnar Transport</div>
            <div style="font-size: 12px; color: #cbd5e1;">• LangChain Decision Agent</div>
            <div style="font-size: 12px; color: #cbd5e1;">• Plotly Dark Glassmorphism</div>
            <div style="margin-top: 8px; font-size: 11px; color: #64748b; border-top: 1px solid #334155; padding-top: 6px;">
                Built by <b>Rejwana Akter Shormi</b><br>CIS / Business Intelligence
            </div>
        </div>
        """, unsafe_allow_html=True)

    if app_mode == "📊 Executive Cockpit":
        render_dashboard(kpis, region_filter, segment_filter)
    elif app_mode == "🤖 Autonomous AI Agent":
        render_agent_interface(agent)
    else:
        render_warehouse_explorer(db)


def render_dashboard(kpis: KPIEngine, region: str, segment: str):
    summary = kpis.get_executive_summary(region, segment)

    # 5-Column Responsive KPI Cards (No Text Truncation!)
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-top">
                <span class="kpi-label">Total Revenue</span>
                <span class="kpi-badge-green">+14.8%</span>
            </div>
            <div class="kpi-val">{format_currency(summary['total_revenue'])}</div>
            <div class="kpi-sub">Net fulfilled sales</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-top">
                <span class="kpi-label">Gross Margin</span>
                <span class="kpi-badge-green">Target: 38%</span>
            </div>
            <div class="kpi-val">{summary['gross_margin_pct']:.1f}%</div>
            <div class="kpi-sub">${format_currency(summary['total_profit'])} net profit</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-top">
                <span class="kpi-label">Fulfilled Orders</span>
                <span class="kpi-badge-blue">96.2% Delivered</span>
            </div>
            <div class="kpi-val">{summary['total_orders']:,}</div>
            <div class="kpi-sub">{summary['active_customers']:,} active accounts</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-top">
                <span class="kpi-label">Avg Order Value</span>
                <span class="kpi-badge-blue">AOV</span>
            </div>
            <div class="kpi-val">{format_currency(summary['avg_order_value'])}</div>
            <div class="kpi-sub">Basket size index</div>
        </div>
        """, unsafe_allow_html=True)

    with col5:
        csat = summary['avg_csat']
        csat_color = "kpi-badge-green" if csat >= 3.0 else "kpi-badge-blue"
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-top">
                <span class="kpi-label">Support CSAT</span>
                <span class="{csat_color}">Avg Res: {summary['avg_resolution_hrs']}h</span>
            </div>
            <div class="kpi-val">{csat:.2f} <span style="font-size: 16px; color: #64748b;">/ 5.0</span></div>
            <div class="kpi-sub">Customer satisfaction</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)

    # Main Visual Analytics Grid
    c1, c2 = st.columns([6, 4])

    with c1:
        st.markdown("<div style='font-size: 16px; font-weight: 700; color: #f8fafc; margin-bottom: 8px;'>📈 Monthly Revenue Trajectory & Order Volume</div>", unsafe_allow_html=True)
        df_monthly = kpis.get_monthly_revenue_trend()
        
        fig_rev = go.Figure()
        fig_rev.add_trace(go.Scatter(
            x=df_monthly["year_month"],
            y=df_monthly["monthly_revenue"],
            mode="lines",
            name="Revenue ($)",
            line=dict(color="#38bdf8", width=3, shape="spline"),
            fill="tozeroy",
            fillcolor="rgba(56, 189, 248, 0.12)"
        ))
        fig_rev.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(15, 23, 42, 0.5)",
            plot_bgcolor="rgba(0, 0, 0, 0)",
            margin=dict(l=10, r=10, t=25, b=25),
            height=340,
            xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.06)", tickangle=-30),
            yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.06)", tickprefix="$"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_rev, use_container_width=True)

    with c2:
        st.markdown("<div style='font-size: 16px; font-weight: 700; color: #f8fafc; margin-bottom: 8px;'>🏷️ Category Revenue vs. Profit Margin %</div>", unsafe_allow_html=True)
        df_cat = kpis.get_category_performance()
        
        fig_cat = px.bar(
            df_cat,
            x="category",
            y="category_revenue",
            color="profit_margin_pct",
            color_continuous_scale=[[0, "#38bdf8"], [0.5, "#818cf8"], [1, "#34d399"]],
            labels={"category_revenue": "Revenue ($)", "category": "Category", "profit_margin_pct": "Margin %"}
        )
        fig_cat.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(15, 23, 42, 0.5)",
            plot_bgcolor="rgba(0, 0, 0, 0)",
            margin=dict(l=10, r=10, t=25, b=25),
            height=340,
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.06)", tickprefix="$"),
            coloraxis_colorbar=dict(title="Margin %", len=0.8)
        )
        st.plotly_chart(fig_cat, use_container_width=True)

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # Bottom Row: Customer Churn Matrix & Immediate High-Risk Action Table
    b1, b2 = st.columns([5, 5])

    with b1:
        st.markdown("<div style='font-size: 16px; font-weight: 700; color: #f8fafc; margin-bottom: 8px;'>🎯 Customer Churn Exposure by Segment & Tier</div>", unsafe_allow_html=True)
        df_churn = kpis.get_churn_risk_by_segment()
        fig_churn = px.sunburst(
            df_churn,
            path=["segment", "loyalty_tier"],
            values="customer_count",
            color="avg_churn_risk",
            color_continuous_scale=[[0, "#10b981"], [0.5, "#f59e0b"], [1, "#ef4444"]],
            labels={"avg_churn_risk": "Avg Risk Score"}
        )
        fig_churn.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(15, 23, 42, 0.5)",
            margin=dict(l=5, r=5, t=10, b=10),
            height=330
        )
        st.plotly_chart(fig_churn, use_container_width=True)

    with b2:
        st.markdown("<div style='font-size: 16px; font-weight: 700; color: #f8fafc; margin-bottom: 8px;'>🚨 High-Risk Enterprise Accounts (Actionable Recourse)</div>", unsafe_allow_html=True)
        high_risk_df = kpis.get_high_risk_customers(limit=5)

        for _, row in high_risk_df.iterrows():
            st.markdown(f"""
            <div style="background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255,255,255,0.06); padding: 12px 16px; border-radius: 10px; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <div style="font-weight: 700; color: #f1f5f9; font-size: 14px;">{row['customer_name']}</div>
                    <div style="font-size: 12px; color: #64748b;">
                        ID: <span style="color: #94a3b8;">{row['customer_id']}</span> | 
                        Region: <span style="color: #94a3b8;">{row['region']}</span> | 
                        Spend: <span style="color: #38bdf8; font-weight: 600;">${row['total_spend']:,.2f}</span>
                    </div>
                </div>
                <div style="text-align: right;">
                    <span class="tag-critical">Risk: {row['risk_pct']}%</span>
                    <div style="margin-top: 4px;"><span class="tag-tier">{row['loyalty_tier']} Tier</span></div>
                </div>
            </div>
            """, unsafe_allow_html=True)


def render_agent_interface(agent: AutonomousBIAgent):
    st.markdown("""
    <div style="margin-bottom: 20px;">
        <h2 style="color: #f8fafc; font-weight: 800; margin-bottom: 4px;">🤖 Autonomous BI Decision Agent</h2>
        <div style="color: #94a3b8; font-size: 14px;">
            Ask questions in plain English. The agent references schema metadata, generates validated DuckDB SQL, and displays interactive results with zero latency.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Prompt Suggestions in Styled Cards
    st.markdown("<div style='font-size: 13px; font-weight: 700; color: #64748b; margin-bottom: 8px; text-transform: uppercase;'>Suggested Analytical Inquiries</div>", unsafe_allow_html=True)
    q1, q2, q3, q4 = st.columns(4)
    
    preset_query = None
    if q1.button("📊 Revenue by Category", use_container_width=True):
        preset_query = "Show revenue and margin breakdown by product category"
    if q2.button("⚠️ Churn Vulnerability", use_container_width=True):
        preset_query = "Which customer segment is most prone to churn risk?"
    if q3.button("👑 Top 10 Enterprise Spenders", use_container_width=True):
        preset_query = "Show top 10 highest spend customers"
    if q4.button("🎧 Support CSAT & Delays", use_container_width=True):
        preset_query = "Customer support satisfaction and ticket resolution times"

    user_query = st.text_input(
        "Ask a business intelligence question:",
        value=preset_query or "",
        placeholder="e.g., Which product subcategory generated the highest profit?",
        key="agent_input_box"
    )

    if user_query:
        with st.spinner("Compiling optimized DuckDB SQL & executing vector query..."):
            result = agent.ask(user_query)

        if not result["success"]:
            st.error(f"Execution Error: {result['error']}")
            st.code(result["sql"], language="sql")
        else:
            # Query Details
            with st.expander("⚡ Compiled DuckDB SQL Query", expanded=True):
                st.code(result["sql"], language="sql")

            df = result["data"]
            
            res_col1, res_col2 = st.columns([6, 4])
            with res_col1:
                st.markdown(f"<div style='font-size: 14px; font-weight: 700; color: #38bdf8; margin-bottom: 8px;'>Query Results ({len(df)} rows returned)</div>", unsafe_allow_html=True)
                st.dataframe(df, use_container_width=True, height=280)

            with res_col2:
                numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
                text_cols = df.select_dtypes(include=["object"]).columns.tolist()

                if len(text_cols) >= 1 and len(numeric_cols) >= 1:
                    st.markdown("<div style='font-size: 14px; font-weight: 700; color: #38bdf8; margin-bottom: 8px;'>Dynamic Visual Breakdown</div>", unsafe_allow_html=True)
                    x_col = text_cols[0]
                    y_col = numeric_cols[0]
                    fig = px.bar(
                        df.head(10),
                        x=x_col,
                        y=y_col,
                        template="plotly_dark",
                        color_discrete_sequence=["#38bdf8"]
                    )
                    fig.update_layout(
                        paper_bgcolor="rgba(15, 23, 42, 0.5)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        margin=dict(l=10, r=10, t=10, b=10),
                        height=280,
                        xaxis=dict(showgrid=False),
                        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.06)")
                    )
                    st.plotly_chart(fig, use_container_width=True)


def render_warehouse_explorer(db: DuckDBManager):
    st.markdown("""
    <div style="margin-bottom: 20px;">
        <h2 style="color: #f8fafc; font-weight: 800; margin-bottom: 4px;">🗄️ OLAP Data Warehouse Explorer</h2>
        <div style="color: #94a3b8; font-size: 14px;">
            Examine in-process columnar tables, metadata definitions, and indexing directly from the underlying DuckDB engine.
        </div>
    </div>
    """, unsafe_allow_html=True)

    tables = db.get_table_names()
    selected_table = st.selectbox("Select Table to Inspect:", tables)

    if selected_table:
        col1, col2 = st.columns([7, 3])
        with col1:
            st.markdown(f"<div style='font-size: 14px; font-weight: 700; color: #38bdf8; margin-bottom: 8px;'>Table Records: {selected_table} (Top 100 Sample Rows)</div>", unsafe_allow_html=True)
            preview_df = db.query(f"SELECT * FROM {selected_table} LIMIT 100;")
            st.dataframe(preview_df, use_container_width=True, height=450)

        with col2:
            st.markdown(f"<div style='font-size: 14px; font-weight: 700; color: #38bdf8; margin-bottom: 8px;'>Column Attributes & Data Types</div>", unsafe_allow_html=True)
            schema_df = db.query(f"DESCRIBE {selected_table};")
            st.dataframe(schema_df, use_container_width=True, height=450)


if __name__ == "__main__":
    main()
