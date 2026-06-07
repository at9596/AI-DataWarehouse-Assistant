"""
database/schema_loader.py
--------------------------
Loads the database schema (tables + columns) from SQL Server.
In DEMO_MODE, returns a realistic sample data warehouse schema.
"""
from __future__ import annotations
import pandas as pd
from config import DEMO_MODE
from database.connection import get_connection


# ── Demo schema used when DEMO_MODE=true ─────────────────────────────────────
DEMO_SCHEMA_DF = pd.DataFrame([
    # fact_sales
    ("fact_sales",     "sale_id",       "int"),
    ("fact_sales",     "customer_id",   "int"),
    ("fact_sales",     "product_id",    "int"),
    ("fact_sales",     "date_id",       "int"),
    ("fact_sales",     "sales_amount",  "decimal"),
    ("fact_sales",     "quantity",      "int"),
    ("fact_sales",     "discount",      "decimal"),
    # dim_customer
    ("dim_customer",   "customer_id",   "int"),
    ("dim_customer",   "first_name",    "varchar"),
    ("dim_customer",   "last_name",     "varchar"),
    ("dim_customer",   "email",         "varchar"),
    ("dim_customer",   "city",          "varchar"),
    ("dim_customer",   "country",       "varchar"),
    # dim_product
    ("dim_product",    "product_id",    "int"),
    ("dim_product",    "product_name",  "varchar"),
    ("dim_product",    "category",      "varchar"),
    ("dim_product",    "subcategory",   "varchar"),
    ("dim_product",    "unit_price",    "decimal"),
    # dim_date
    ("dim_date",       "date_id",       "int"),
    ("dim_date",       "full_date",     "date"),
    ("dim_date",       "year",          "int"),
    ("dim_date",       "month",         "int"),
    ("dim_date",       "month_name",    "varchar"),
    ("dim_date",       "quarter",       "int"),
    ("dim_date",       "day_of_week",   "varchar"),
    # silver.customer (ETL layer)
    ("silver.customer","customer_id",   "int"),
    ("silver.customer","first_name",    "varchar"),
    ("silver.customer","last_name",     "varchar"),
    ("silver.customer","email",         "varchar"),
    ("silver.customer","phone",         "varchar"),
    ("silver.customer","created_date",  "datetime"),
    # bronze.customer (raw layer)
    ("bronze.customer","customer_id",   "int"),
    ("bronze.customer","first_name",    "nvarchar"),
    ("bronze.customer","last_name",     "nvarchar"),
    ("bronze.customer","email",         "nvarchar"),
    ("bronze.customer","phone",         "nvarchar"),
    ("bronze.customer","created_date",  "nvarchar"),
], columns=["TABLE_NAME", "COLUMN_NAME", "DATA_TYPE"])


def load_schema_df() -> pd.DataFrame:
    """Returns schema as a DataFrame: TABLE_NAME, COLUMN_NAME, DATA_TYPE."""
    if DEMO_MODE:
        return DEMO_SCHEMA_DF.copy()

    conn = get_connection()
    query = """
        SELECT TABLE_SCHEMA + '.' + TABLE_NAME AS TABLE_NAME,
               COLUMN_NAME,
               DATA_TYPE
        FROM   INFORMATION_SCHEMA.COLUMNS
        ORDER  BY TABLE_NAME, ORDINAL_POSITION
    """
    return pd.read_sql(query, conn)


def load_schema_text() -> str:
    """
    Returns schema as a formatted text string for injecting into AI prompts.
    Example line:  Table: fact_sales | Columns: sale_id (int), sales_amount (decimal)
    """
    df = load_schema_df()
    lines = []
    for table, group in df.groupby("TABLE_NAME"):
        cols = ", ".join(
            f"{row.COLUMN_NAME} ({row.DATA_TYPE})"
            for _, row in group.iterrows()
        )
        lines.append(f"Table: {table} | Columns: {cols}")
    return "\n".join(lines)
