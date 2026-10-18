"""
Streamlit Web Application for OmniBI.
Interactive Enterprise Dashboard & Conversational AI Business Intelligence Agent.
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
    page_title="OmniBI | Autonomous Decision Platform",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .metric-card {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 16px;
        text-align: center;
    }
    .metric-value {
        font-size: 24px;
        font-weight: 700;
        color: #0f172a;
    }
    .metric-label {
        font-size: 13px;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def get_services():
    db = DuckDBManager()
    kpis = KPIEngine(db)
    agent = AutonomousBIAgent(db)
    return db, kpis, agent


def main():
    db, kpis, agent = get_services()

    # Sidebar
    st.sidebar.title("⚡ OmniBI Platform")
    st.sidebar.caption("Modern OLAP & Autonomous AI Agent")
    st.sidebar.markdown("---")
    
    app_mode = st.sidebar.radio(
        "Navigation",
        ["📊 Executive Dashboard", "🤖 Conversational BI Agent", "🗄️ Data Warehouse Explorer"]
    )

    st.sidebar.markdown("---")
    st.sidebar.info(
        "**Stack:** DuckDB OLAP + PyArrow + LangChain + Plotly + Streamlit\n\n"
        "**Author:** Rejwana Akter Shormi (CIS / BI)"
    )

    if app_mode == "📊 Executive Dashboard":
        render_dashboard(kpis)
    elif app_mode == "🤖 Conversational BI Agent":
        render_agent_interface(agent)
    else:
        render_warehouse_explorer(db)


def render_dashboard(kpis: KPIEngine):
    st.title("📊 Executive Performance & Health Cockpit")
    st.write("Real-time aggregated indicators computed directly from the in-process DuckDB engine.")

    # Executive KPI Metric Cards
    summary = kpis.get_executive_summary()
    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("Total Revenue", f"${summary['total_revenue']:,.2f}")
    col2.metric("Gross Profit Margin", f"{summary['gross_margin_pct']}%")
    col3.metric("Total Orders", f"{summary['total_orders']:,}")
    col4.metric("Avg Order Value", f"${summary['avg_order_value']:,.2f}")
    col5.metric("Avg CSAT Score", f"{summary['avg_csat']} / 5.0")

    st.markdown("---")

    # Time series & Category charts
    c1, c2 = st.columns([6, 4])

    with c1:
        st.subheader("Monthly Revenue & Order Velocity")
        df_monthly = kpis.get_monthly_revenue_trend()
        fig_rev = px.area(
            df_monthly,
            x="year_month",
            y="monthly_revenue",
            title="Revenue Trajectory (2025 - 2026)",
            labels={"year_month": "Month", "monthly_revenue": "Revenue ($)"},
            template="plotly_white",
            color_discrete_sequence=["#2563eb"]
        )
        st.plotly_chart(fig_rev, use_container_width=True)

    with c2:
        st.subheader("Category Revenue & Profit Breakdown")
        df_cat = kpis.get_category_performance()
        fig_cat = px.bar(
            df_cat,
            x="category",
            y="category_revenue",
            color="profit_margin_pct",
            title="Revenue by Category (Color = Margin %)",
            labels={"category_revenue": "Revenue ($)", "category": "Category"},
            template="plotly_white",
            color_continuous_scale="Viridis"
        )
        st.plotly_chart(fig_cat, use_container_width=True)

    # Churn Risk Matrix
    st.subheader("Customer Segment Churn Exposure")
    df_churn = kpis.get_churn_risk_by_segment()
    fig_churn = px.sunburst(
        df_churn,
        path=["segment", "loyalty_tier"],
        values="customer_count",
        color="avg_churn_risk",
        color_continuous_scale="Reds",
        title="Customer Distribution by Segment & Tier (Shaded by Churn Risk)"
    )
    st.plotly_chart(fig_churn, use_container_width=True)


def render_agent_interface(agent: AutonomousBIAgent):
    st.title("🤖 Autonomous BI Decision Agent")
    st.write("Ask business and financial questions in plain natural language. The agent synthesizes optimized SQL and delivers analytical insights.")

    # Suggested Prompts
    st.write("**Suggested Quick Prompts:**")
    quick_col1, quick_col2, quick_col3 = st.columns(3)
    
    selected_prompt = None
    if quick_col1.button("📦 Category Revenue & Margin"):
        selected_prompt = "Show revenue and margin breakdown by product category"
    if quick_col2.button("⚠️ Churn Risk by Customer Segment"):
        selected_prompt = "Which customer segment is most prone to churn risk?"
    if quick_col3.button("📈 Monthly Revenue Trend"):
        selected_prompt = "Show monthly revenue timeline and order volume"

    user_query = st.text_input(
        "Enter your business question:",
        value=selected_prompt or "",
        placeholder="e.g., Which product category generated the highest profit?"
    )

    if st.button("Generate & Execute Analysis", type="primary") or user_query:
        if not user_query:
            st.warning("Please enter a question or click one of the suggested prompts.")
            return

        with st.spinner("Agent is analyzing database schema and generating SQL..."):
            result = agent.ask(user_query)

        if not result["success"]:
            st.error(f"Execution Error: {result['error']}")
            st.code(result["sql"], language="sql")
        else:
            st.success("Query compiled and executed successfully in DuckDB!")
            
            with st.expander("🔍 View Generated SQL Query", expanded=False):
                st.code(result["sql"], language="sql")

            df = result["data"]
            st.dataframe(df, use_container_width=True)

            # Auto-charting if suitable numeric and categorical columns exist
            numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
            text_cols = df.select_dtypes(include=["object"]).columns.tolist()

            if len(text_cols) >= 1 and len(numeric_cols) >= 1:
                st.subheader("📊 Auto-Generated Visualization")
                x_col = text_cols[0]
                y_col = numeric_cols[0]
                fig = px.bar(
                    df,
                    x=x_col,
                    y=y_col,
                    title=f"{y_col.replace('_', ' ').title()} by {x_col.replace('_', ' ').title()}",
                    template="plotly_white",
                    color_discrete_sequence=["#0284c7"]
                )
                st.plotly_chart(fig, use_container_width=True)


def render_warehouse_explorer(db: DuckDBManager):
    st.title("🗄️ OLAP Data Warehouse Explorer")
    st.write("Inspect table schemas, indexing, and raw records stored in the local DuckDB engine.")

    tables = db.get_table_names()
    selected_table = st.selectbox("Select Table to Inspect:", tables)

    if selected_table:
        col1, col2 = st.columns([7, 3])
        with col1:
            st.subheader(f"Data Preview: `{selected_table}` (Top 50 Rows)")
            preview_df = db.query(f"SELECT * FROM {selected_table} LIMIT 50;")
            st.dataframe(preview_df, use_container_width=True)

        with col2:
            st.subheader("Table Schema & Column Types")
            schema_df = db.query(f"DESCRIBE {selected_table};")
            st.dataframe(schema_df, use_container_width=True)


if __name__ == "__main__":
    main()
