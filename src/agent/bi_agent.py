"""
Autonomous Business Intelligence Agent for OmniBI.
Translates Natural Language executive questions into optimized DuckDB SQL,
executes them securely, handles automatic self-correction (self-healing) upon errors,
and generates human-readable business takeaways.
"""

import os
import re
from typing import Any
import pandas as pd
from dotenv import load_dotenv

from src.database.connection import DuckDBManager

load_dotenv()


class AutonomousBIAgent:
    """Agent that bridges conversational business questions and OLAP SQL analytics."""

    def __init__(self, db: DuckDBManager | None = None, api_key: str | None = None):
        self.db = db if db else DuckDBManager()
        self.api_key = api_key or os.getenv("GROQ_API_KEY") or os.getenv("OPENAI_API_KEY")
        self.schema_context = self.db.get_schema_summary()

    def set_api_key(self, api_key: str) -> None:
        """Dynamically updates the active LLM API key."""
        self.api_key = api_key.strip() if api_key else None

    def _sanitize_sql(self, sql_str: str) -> str:
        """Strips markdown code fences and verifies read-only access."""
        cleaned = re.sub(r"```(sql)?", "", sql_str, flags=re.IGNORECASE).strip()
        cleaned = cleaned.rstrip(";")
        
        # Security Guardrail: forbid destructive DDL/DML
        forbidden = ["DROP", "DELETE", "TRUNCATE", "ALTER", "UPDATE", "INSERT"]
        first_token = cleaned.split()[0].upper() if cleaned.split() else ""
        if first_token not in ["SELECT", "WITH"]:
            raise PermissionError(f"Security Policy: Only SELECT queries are permitted. Found: {first_token}")
        
        for kw in forbidden:
            if re.search(r"\b" + kw + r"\b", cleaned, re.IGNORECASE):
                raise PermissionError(f"Security Violation: Destructive keyword '{kw}' detected.")

        return cleaned

    def _build_prompt(self, user_question: str) -> str:
        return f"""You are an elite Staff Data Engineer and Business Intelligence Architect.
Generate an accurate, performant DuckDB SQL query to answer the user's business question.

### DATABASE SCHEMA:
{self.schema_context}

### RULES:
1. Return ONLY the raw SQL query. Do not wrap in markdown quotes if possible, or use standard ```sql code block.
2. Only write read-only SELECT queries.
3. Use proper column aliases for clear business reporting.
4. For date filtering or formatting, use DuckDB functions (e.g., STRFTIME(order_timestamp, '%Y-%m'), DATE_TRUNC('month', order_timestamp)).
5. Join tables on standard foreign keys (e.g., fact_orders.customer_id = dim_customers.customer_id).

User Question: {user_question}
SQL Query:"""

    def _heal_sql(self, user_question: str, broken_sql: str, error_msg: str) -> str:
        """Agentic self-healing: sends execution traceback back to LLM for auto-correction."""
        if not self.api_key:
            return broken_sql
        try:
            from langchain_groq import ChatGroq
            llm = ChatGroq(model_name="llama-3.3-70b-versatile", temperature=0.0, groq_api_key=self.api_key)
            prompt = f"""You previously generated a DuckDB SQL query that failed with an execution error. Fix the query.

### DATABASE SCHEMA:
{self.schema_context}

User Question: {user_question}
Failed Query: {broken_sql}
Error Message: {error_msg}

Return ONLY the corrected raw SQL query:"""
            res = llm.invoke(prompt)
            return self._sanitize_sql(res.content)
        except Exception as e:
            print(f"[Agent Notice] Self-healing failed: {e}")
            return broken_sql

    def generate_sql(self, user_question: str) -> str:
        """Generates SQL using an LLM if API key is configured, or intelligent heuristic matching."""
        # 1. If LLM is available (Groq / LangChain)
        if self.api_key:
            try:
                from langchain_groq import ChatGroq
                llm = ChatGroq(model_name="llama-3.3-70b-versatile", temperature=0.0, groq_api_key=self.api_key)
                prompt = self._build_prompt(user_question)
                response = llm.invoke(prompt)
                return self._sanitize_sql(response.content)
            except Exception as e:
                print(f"[Agent Notice] LLM fallback triggered: {e}")

        # 2. Rule-based heuristic generator for offline demo & zero-cost testing
        q = user_question.lower()
        if "category" in q or "categories" in q or "product sales" in q:
            return """
            SELECT 
                p.category, 
                ROUND(SUM(i.line_total), 2) AS total_revenue,
                ROUND(SUM(i.line_profit), 2) AS total_profit,
                SUM(i.quantity) AS units_sold
            FROM fact_order_items i
            JOIN dim_products p ON i.product_id = p.product_id
            JOIN fact_orders o ON i.order_id = o.order_id
            WHERE o.order_status != 'Cancelled'
            GROUP BY p.category
            ORDER BY total_revenue DESC
            """
        elif "churn" in q or "risk" in q:
            return """
            SELECT 
                segment,
                loyalty_tier,
                COUNT(customer_id) AS total_customers,
                ROUND(AVG(churn_risk_score), 3) AS avg_churn_risk,
                COUNT(CASE WHEN churn_risk_score > 0.65 THEN 1 END) AS critical_risk_count
            FROM dim_customers
            GROUP BY segment, loyalty_tier
            ORDER BY avg_churn_risk DESC
            """
        elif "monthly" in q or "trend" in q or "timeline" in q or "revenue over time" in q:
            return """
            SELECT 
                STRFTIME(order_timestamp, '%Y-%m') AS month,
                ROUND(SUM(total_amount), 2) AS monthly_revenue,
                COUNT(order_id) AS total_orders
            FROM fact_orders
            WHERE order_status != 'Cancelled'
            GROUP BY 1
            ORDER BY 1 ASC
            """
        elif "ticket" in q or "support" in q or "customer service" in q:
            return """
            SELECT 
                issue_category,
                priority,
                COUNT(ticket_id) AS ticket_count,
                ROUND(AVG(resolution_time_hrs), 1) AS avg_resolution_time_hrs,
                ROUND(AVG(satisfaction_score), 2) AS avg_csat
            FROM fact_support_tickets
            GROUP BY issue_category, priority
            ORDER BY ticket_count DESC
            """
        elif "top customer" in q or "vip" in q or "highest spend" in q or "spenders" in q:
            return """
            SELECT 
                c.customer_name,
                c.segment,
                c.region,
                ROUND(SUM(o.total_amount), 2) AS total_spend,
                COUNT(o.order_id) AS total_orders
            FROM fact_orders o
            JOIN dim_customers c ON o.customer_id = c.customer_id
            WHERE o.order_status != 'Cancelled'
            GROUP BY c.customer_name, c.segment, c.region
            ORDER BY total_spend DESC
            LIMIT 10
            """
        else:
            return """
            SELECT 
                order_status,
                channel,
                COUNT(order_id) AS total_orders,
                ROUND(SUM(total_amount), 2) AS total_revenue
            FROM fact_orders
            GROUP BY order_status, channel
            ORDER BY total_revenue DESC
            """

    def ask(self, user_question: str) -> dict[str, Any]:
        """Main conversational entrypoint with automated self-healing retry logic."""
        sql = self.generate_sql(user_question)
        sql_clean = self._sanitize_sql(sql)
        self_healed = False

        try:
            df = self.db.query(sql_clean)
        except Exception as first_err:
            # Attempt self-healing if LLM key is active
            if self.api_key:
                try:
                    sql_clean = self._heal_sql(user_question, sql_clean, str(first_err))
                    df = self.db.query(sql_clean)
                    self_healed = True
                except Exception as second_err:
                    return {
                        "success": False,
                        "question": user_question,
                        "sql": sql_clean,
                        "data": pd.DataFrame(),
                        "row_count": 0,
                        "self_healed": False,
                        "error": f"Initial Error: {first_err} | Correction Error: {second_err}"
                    }
            else:
                return {
                    "success": False,
                    "question": user_question,
                    "sql": sql_clean,
                    "data": pd.DataFrame(),
                    "row_count": 0,
                    "self_healed": False,
                    "error": str(first_err)
                }

        return {
            "success": True,
            "question": user_question,
            "sql": sql_clean,
            "data": df,
            "row_count": len(df),
            "self_healed": self_healed,
            "error": None
        }


if __name__ == "__main__":
    agent = AutonomousBIAgent()
    res = agent.ask("Which customer segment has the highest churn risk?")
    print("Generated SQL:\n", res["sql"])
    print("\nResult Data:\n", res["data"])
