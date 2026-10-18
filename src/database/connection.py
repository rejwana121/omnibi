import os
from pathlib import Path
import duckdb
import pandas as pd

DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "omnibi.duckdb"
SCHEMA_SQL_PATH = Path(__file__).resolve().parent / "schema.sql"

class DuckDBManager:
    """Manages the lifecycle and queries for the OmniBI DuckDB database."""

    def __init__(self, db_path: str | Path | None = None, read_only: bool = True):
        self.db_path = str(db_path) if db_path else str(DEFAULT_DB_PATH)
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        if not os.path.exists(self.db_path):
            self.conn = duckdb.connect(database=self.db_path, read_only=False)
            self.init_schema()
        else:
            self.conn = duckdb.connect(database=self.db_path, read_only=read_only)

    def init_schema(self) -> None:
        """Executes the DDL schema if tables do not exist."""
        if SCHEMA_SQL_PATH.exists():
            with open(SCHEMA_SQL_PATH, "r", encoding="utf-8") as f:
                ddl = f.read()
            self.conn.execute(ddl)

    def query(self, sql: str) -> pd.DataFrame:
        """Executes a SQL query and returns results as a pandas DataFrame."""
        return self.conn.execute(sql).df()

    def execute(self, sql: str, params: list | tuple | None = None) -> None:
        """Executes a SQL statement without returning data."""
        if params:
            self.conn.execute(sql, params)
        else:
            self.conn.execute(sql)

    def get_table_names(self) -> list[str]:
        """Returns all user-defined table names in the database."""
        res = self.conn.execute("SHOW TABLES;").fetchall()
        return [r[0] for r in res]

    def get_schema_summary(self) -> str:
        """Generates a compact summary of tables and column definitions for LLM context."""
        summary = []
        tables = self.get_table_names()
        for t in tables:
            cols = self.conn.execute(f"DESCRIBE {t};").fetchall()
            col_strs = [f"{c[0]} ({c[1]})" for c in cols]
            summary.append(f"Table '{t}':\n  Columns: " + ", ".join(col_strs))
        return "\n\n".join(summary)

    def close(self) -> None:
        """Closes the active database connection."""
        self.conn.close()


if __name__ == "__main__":
    db = DuckDBManager()
    print("Database initialized successfully at:", db.db_path)
    print("Tables:", db.get_table_names())
    db.close()
