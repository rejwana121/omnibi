"""
KPI Engine for OmniBI.
Pre-computes and caches core executive metrics, margin analytics,
and churn indicators directly from DuckDB.
"""

import pandas as pd
from src.database.connection import DuckDBManager


class KPIEngine:
    def __init__(self, db: DuckDBManager | None = None):
        self.db = db if db else DuckDBManager()

    def get_executive_summary(self) -> dict:
        """Computes top-level business health indicators."""
        sql = """
        SELECT 
            COUNT(DISTINCT o.order_id) as total_orders,
            ROUND(SUM(o.total_amount), 2) as total_revenue,
            ROUND(AVG(o.total_amount), 2) as avg_order_value,
            ROUND(SUM(i.line_profit), 2) as total_profit,
            ROUND((SUM(i.line_profit) / NULLIF(SUM(i.line_total), 0)) * 100, 2) as gross_margin_pct
        FROM fact_orders o
        JOIN fact_order_items i ON o.order_id = i.order_id
        WHERE o.order_status NOT IN ('Cancelled', 'Returned');
        """
        df = self.db.query(sql)
        row = df.iloc[0].to_dict()

        # Customer & ticket metrics
        cust_sql = """
        SELECT 
            COUNT(DISTINCT customer_id) as active_customers,
            ROUND(AVG(churn_risk_score), 3) as avg_churn_risk
        FROM dim_customers;
        """
        cust_row = self.db.query(cust_sql).iloc[0].to_dict()
        row.update(cust_row)

        ticket_sql = """
        SELECT 
            ROUND(AVG(resolution_time_hrs), 1) as avg_resolution_hrs,
            ROUND(AVG(satisfaction_score), 2) as avg_csat
        FROM fact_support_tickets;
        """
        ticket_row = self.db.query(ticket_sql).iloc[0].to_dict()
        row.update(ticket_row)

        return row

    def get_monthly_revenue_trend(self) -> pd.DataFrame:
        """Returns monthly revenue and order volume for time-series charts."""
        sql = """
        SELECT 
            STRFTIME(order_timestamp, '%Y-%m') as year_month,
            ROUND(SUM(total_amount), 2) as monthly_revenue,
            COUNT(order_id) as order_count
        FROM fact_orders
        WHERE order_status != 'Cancelled'
        GROUP BY 1
        ORDER BY 1 ASC;
        """
        return self.db.query(sql)

    def get_category_performance(self) -> pd.DataFrame:
        """Returns breakdown of sales, profit, and margins across product categories."""
        sql = """
        SELECT 
            p.category,
            ROUND(SUM(i.line_total), 2) as category_revenue,
            ROUND(SUM(i.line_profit), 2) as category_profit,
            ROUND((SUM(i.line_profit) / SUM(i.line_total)) * 100, 1) as profit_margin_pct,
            SUM(i.quantity) as units_sold
        FROM fact_order_items i
        JOIN dim_products p ON i.product_id = p.product_id
        JOIN fact_orders o ON i.order_id = o.order_id
        WHERE o.order_status != 'Cancelled'
        GROUP BY p.category
        ORDER BY category_revenue DESC;
        """
        return self.db.query(sql)

    def get_churn_risk_by_segment(self) -> pd.DataFrame:
        """Returns customer churn exposure by business tier."""
        sql = """
        SELECT 
            segment,
            loyalty_tier,
            COUNT(customer_id) as customer_count,
            ROUND(AVG(churn_risk_score), 2) as avg_churn_risk,
            COUNT(CASE WHEN churn_risk_score > 0.65 THEN 1 END) as high_risk_count
        FROM dim_customers
        GROUP BY segment, loyalty_tier
        ORDER BY avg_churn_risk DESC;
        """
        return self.db.query(sql)


if __name__ == "__main__":
    kpis = KPIEngine()
    print("Executive Summary:", kpis.get_executive_summary())
