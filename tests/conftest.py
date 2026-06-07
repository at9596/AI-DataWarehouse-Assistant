"""
tests/conftest.py
------------------
Shared pytest fixtures available to all test files automatically.
"""
import pytest


# ── Sample data reused across all tests ──────────────────────────────────────

SAMPLE_SCHEMA = (
    "Table: fact_sales | Columns: sale_id (int), customer_id (int), "
    "product_id (int), date_id (int), sales_amount (decimal), quantity (int), discount (decimal)\n"
    "Table: dim_customer | Columns: customer_id (int), first_name (varchar), "
    "last_name (varchar), email (varchar), city (varchar), country (varchar)\n"
    "Table: dim_product | Columns: product_id (int), product_name (varchar), "
    "category (varchar), subcategory (varchar), unit_price (decimal)\n"
    "Table: dim_date | Columns: date_id (int), full_date (date), year (int), "
    "month (int), month_name (varchar), quarter (int), day_of_week (varchar)"
)

SAMPLE_ETL_SCRIPT = """\
INSERT INTO silver.customer
SELECT customer_id, first_name, last_name, email
FROM bronze.customer
"""

SAMPLE_SQL = """\
SELECT
    dc.first_name,
    dc.last_name,
    SUM(fs.sales_amount) AS total_sales
FROM fact_sales fs
JOIN dim_customer dc ON fs.customer_id = dc.customer_id
GROUP BY dc.first_name, dc.last_name
ORDER BY total_sales DESC
"""


@pytest.fixture
def sample_schema() -> str:
    """Multi-table schema string for use in AI prompt tests."""
    return SAMPLE_SCHEMA


@pytest.fixture
def sample_etl() -> str:
    """Simple ETL INSERT script."""
    return SAMPLE_ETL_SCRIPT


@pytest.fixture
def sample_sql() -> str:
    """A realistic T-SQL query for explainer tests."""
    return SAMPLE_SQL


@pytest.fixture
def make_mock_gemini(mocker):
    """
    Factory fixture: returns a helper that patches a service module's _client
    and configures it to return the given response text.

    Usage:
        def test_something(make_mock_gemini):
            mock_client = make_mock_gemini("services.sql_generator", "SELECT 1")
            from services.sql_generator import generate_sql
            result = generate_sql("schema", "question")
    """
    def _factory(module_path: str, response_text: str):
        from unittest.mock import MagicMock
        mock_response = MagicMock()
        mock_response.text = response_text
        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = mock_response
        mocker.patch(f"{module_path}._client", mock_client)
        return mock_client

    return _factory
