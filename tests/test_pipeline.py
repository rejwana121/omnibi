"""
OmniBI Automated Integration & Quality Assurance Test Suite.
Tests database integrity, KPI calculations, and AI agent guardrails.
"""

import pytest
from src.database.connection import DuckDBManager
from src.analytics.kpi_engine import KPIEngine
from src.analytics.report_generator import ExecutiveReportGenerator
from src.agent.bi_agent import AutonomousBIAgent


@pytest.fixture(scope="module")
def db():
    manager = DuckDBManager(read_only=True)
    yield manager
    manager.close()


@pytest.fixture(scope="module")
def kpis(db):
    return KPIEngine(db)


@pytest.fixture(scope="module")
def agent(db):
    return AutonomousBIAgent(db)


def test_database_tables_exist(db):
    """Verifies that all 5 required star-schema tables exist."""
    tables = db.get_table_names()
    expected = ["dim_customers", "dim_products", "fact_orders", "fact_order_items", "fact_support_tickets"]
    for t in expected:
        assert t in tables, f"Expected table '{t}' was not found in database."


def test_kpi_engine_values(kpis):
    """Verifies executive summary produces realistic non-zero metrics."""
    summary = kpis.get_executive_summary()
    assert summary["total_orders"] > 0
    assert summary["total_revenue"] > 100000.0
    assert summary["gross_margin_pct"] > 0.0
    assert summary["active_customers"] > 0


def test_report_generator(kpis):
    """Verifies executive report generator creates valid non-empty markdown."""
    rep_gen = ExecutiveReportGenerator(kpis)
    brief = rep_gen.generate_markdown_brief()
    assert "# ⚡ OmniBI Executive Intelligence Briefing" in brief
    assert "High-Priority Enterprise Retention Targets" in brief


def test_agent_guardrail_blocks_drop(agent):
    """Ensures security guardrails reject destructive DDL commands."""
    with pytest.raises(PermissionError):
        agent._sanitize_sql("DROP TABLE dim_customers;")


def test_agent_guardrail_blocks_delete(agent):
    """Ensures security guardrails reject destructive DELETE commands."""
    with pytest.raises(PermissionError):
        agent._sanitize_sql("DELETE FROM fact_orders WHERE total_amount > 0;")


def test_agent_valid_query_execution(agent):
    """Verifies valid heuristic query compiles and returns data."""
    res = agent.ask("Show revenue by category")
    assert res["success"] is True
    assert res["row_count"] > 0
    assert "total_revenue" in res["data"].columns
