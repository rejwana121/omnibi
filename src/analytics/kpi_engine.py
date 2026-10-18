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

    def get_executive_summary(self, region: str = "All", segment: str = "All", *args, **kwargs) -> dict:
        """Computes top-level business health indicators with optional filters."""
        where_clauses = ["o.order_status NOT IN ('Cancelled', 'Returned')"]
        cust_where = []
        
        if region != "All":
            where_clauses.append(f"c.region = '{region}'")
            cust_where.append(f"region = '{region}'")
        if segment != "All":
            where_clauses.append(f"c.segment = '{segment}'")
            cust_where.append(f"segment = '{segment}'")

        order_where_str = " AND ".join(where_clauses)
        cust_where_str = f"WHERE {' AND '.join(cust_where)}" if cust_where else ""

        sql = f"""
        SELECT 
            COUNT(DISTINCT o.order_id) as total_orders,
            COALESCE(SUM(o.total_amount), 0) as total_revenue,
            COALESCE(AVG(o.total_amount), 0) as avg_order_value,
            COALESCE(SUM(i.line_profit), 0) as total_profit,
            COALESCE((SUM(i.line_profit) / NULLIF(SUM(i.line_total), 0)) * 100, 0) as gross_margin_pct
        FROM fact_orders o
        JOIN fact_order_items i ON o.order_id = i.order_id
        JOIN dim_customers c ON o.customer_id = c.customer_id
        WHERE {order_where_str};
        """
        df = self.db.query(sql)
        row = df.iloc[0].to_dict()

        # Customer & ticket metrics
        cust_sql = f"""
        SELECT 
            COUNT(DISTINCT customer_id) as active_customers,
            COALESCE(AVG(churn_risk_score), 0) as avg_churn_risk
        FROM dim_customers {cust_where_str};
        """
        cust_row = self.db.query(cust_sql).iloc[0].to_dict()
        row.update(cust_row)

        ticket_sql = """
        SELECT 
            COALESCE(AVG(resolution_time_hrs), 0) as avg_resolution_hrs,
            COALESCE(AVG(satisfaction_score), 0) as avg_csat
        FROM fact_support_tickets;
        """
        ticket_row = self.db.query(ticket_sql).iloc[0].to_dict()
        row.update(ticket_row)

        # Clean numerical types
        row["total_orders"] = int(row.get("total_orders", 0))
        row["active_customers"] = int(row.get("active_customers", 0))
        return row

    def get_high_risk_customers(self, limit: int = 6) -> pd.DataFrame:
        """Returns top customers at immediate risk of churning with commercial value."""
        sql = f"""
        SELECT 
            c.customer_id,
            c.customer_name,
            c.segment,
            c.region,
            c.loyalty_tier,
            ROUND(c.churn_risk_score * 100, 1) as risk_pct,
            ROUND(COALESCE(SUM(o.total_amount), 0), 2) as total_spend
        FROM dim_customers c
        LEFT JOIN fact_orders o ON c.customer_id = o.customer_id
        GROUP BY c.customer_id, c.customer_name, c.segment, c.region, c.loyalty_tier, c.churn_risk_score
        ORDER BY c.churn_risk_score DESC, total_spend DESC
        LIMIT {limit};
        """
        return self.db.query(sql)

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

    def get_recent_orders(self, limit: int = 8) -> pd.DataFrame:
        """Returns clean recent transaction records for display."""
        sql = f"""
        SELECT 
            o.order_id,
            c.customer_name,
            c.region,
            STRFTIME(o.order_timestamp, '%Y-%m-%d') as order_date,
            o.channel,
            ROUND(o.total_amount, 2) as amount,
            o.order_status
        FROM fact_orders o
        JOIN dim_customers c ON o.customer_id = c.customer_id
        ORDER BY o.order_timestamp DESC
        LIMIT {limit};
        """
        return self.db.query(sql)


if __name__ == "__main__":
    kpis = KPIEngine()
    print("Executive Summary:", kpis.get_executive_summary())
