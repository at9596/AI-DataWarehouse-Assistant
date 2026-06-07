"""
tests/test_schema_loader.py
-----------------------------
Unit tests for database/schema_loader.py.

Covers:
  - Demo mode: returns correct DataFrame and text format
  - Live mode: delegates to get_connection + pd.read_sql
"""
import pandas as pd
import pytest
from unittest.mock import patch, MagicMock


# ── Helpers ───────────────────────────────────────────────────────────────────

EXPECTED_COLUMNS = {"TABLE_NAME", "COLUMN_NAME", "DATA_TYPE"}

KNOWN_TABLES = [
    "fact_sales",
    "dim_customer",
    "dim_product",
    "dim_date",
    "silver.customer",
    "bronze.customer",
]


# ── Demo Mode: load_schema_df ─────────────────────────────────────────────────

class TestLoadSchemaDfDemoMode:
    """Tests when DEMO_MODE=True — no real DB connection required."""

    def _load(self):
        # Re-import inside method so the patch is active
        with patch("database.schema_loader.DEMO_MODE", True):
            from database.schema_loader import load_schema_df
            return load_schema_df()

    def test_returns_dataframe(self):
        df = self._load()
        assert isinstance(df, pd.DataFrame)

    def test_has_exactly_three_columns(self):
        df = self._load()
        assert set(df.columns) == EXPECTED_COLUMNS

    def test_is_not_empty(self):
        df = self._load()
        assert len(df) > 0

    @pytest.mark.parametrize("table", KNOWN_TABLES)
    def test_contains_expected_table(self, table):
        df = self._load()
        assert table in df["TABLE_NAME"].values, f"Missing table: {table}"

    def test_fact_sales_has_sale_id(self):
        df = self._load()
        fact = df[df["TABLE_NAME"] == "fact_sales"]
        assert "sale_id" in fact["COLUMN_NAME"].values

    def test_data_types_not_empty(self):
        df = self._load()
        assert df["DATA_TYPE"].notna().all()
        assert (df["DATA_TYPE"] != "").all()

    def test_returns_independent_copy(self):
        """Mutating returned DF must not affect the module-level constant."""
        with patch("database.schema_loader.DEMO_MODE", True):
            import database.schema_loader as sl
            df1 = sl.load_schema_df()
            df2 = sl.load_schema_df()
            original_value = df1.iloc[0]["TABLE_NAME"]
            df1.iloc[0, df1.columns.get_loc("TABLE_NAME")] = "MUTATED"
            assert df2.iloc[0]["TABLE_NAME"] == original_value


# ── Demo Mode: load_schema_text ───────────────────────────────────────────────

class TestLoadSchemaTextDemoMode:
    def _load(self):
        with patch("database.schema_loader.DEMO_MODE", True):
            from database.schema_loader import load_schema_text
            return load_schema_text()

    def test_returns_string(self):
        result = self._load()
        assert isinstance(result, str)

    def test_is_not_empty(self):
        result = self._load()
        assert len(result.strip()) > 0

    def test_each_line_starts_with_table(self):
        result = self._load()
        for line in result.strip().splitlines():
            assert line.startswith("Table:"), f"Bad line format: {line!r}"

    def test_each_line_has_pipe_separator(self):
        result = self._load()
        for line in result.strip().splitlines():
            assert "|" in line, f"Missing pipe separator: {line!r}"

    def test_each_line_has_columns_keyword(self):
        result = self._load()
        for line in result.strip().splitlines():
            assert "Columns:" in line, f"Missing 'Columns:': {line!r}"

    def test_contains_column_names(self):
        result = self._load()
        assert "sale_id" in result
        assert "customer_id" in result
        assert "product_name" in result

    def test_contains_data_types(self):
        result = self._load()
        assert "(int)" in result
        assert "(varchar)" in result
        assert "(decimal)" in result

    @pytest.mark.parametrize("table", KNOWN_TABLES)
    def test_table_appears_in_text(self, table):
        result = self._load()
        assert table in result, f"Table '{table}' missing from schema text"

    def test_line_count_matches_table_count(self):
        """One line per table group."""
        with patch("database.schema_loader.DEMO_MODE", True):
            import database.schema_loader as sl
            df = sl.load_schema_df()
            text = sl.load_schema_text()
            unique_tables = df["TABLE_NAME"].nunique()
            assert len(text.strip().splitlines()) == unique_tables


# ── Live Mode: load_schema_df ─────────────────────────────────────────────────

class TestLoadSchemaDfLiveMode:
    """Tests when DEMO_MODE=False — mocks DB and pandas."""

    MOCK_ROWS = [
        ("dbo.fact_orders", "order_id", "int"),
        ("dbo.fact_orders", "amount",   "decimal"),
        ("dbo.dim_product", "product_id", "int"),
    ]

    def _mock_df(self):
        return pd.DataFrame(self.MOCK_ROWS,
                            columns=["TABLE_NAME", "COLUMN_NAME", "DATA_TYPE"])

    def test_calls_get_connection(self, mocker):
        mock_conn = MagicMock()
        mocker.patch("database.schema_loader.DEMO_MODE", False)
        mocker.patch("database.schema_loader.get_connection", return_value=mock_conn)
        mocker.patch("pandas.read_sql", return_value=self._mock_df())

        from database.schema_loader import load_schema_df
        load_schema_df()

        # get_connection must be called exactly once
        from database import schema_loader
        schema_loader.get_connection.assert_called_once()

    def test_returns_dataframe_from_db(self, mocker):
        mock_conn = MagicMock()
        mocker.patch("database.schema_loader.DEMO_MODE", False)
        mocker.patch("database.schema_loader.get_connection", return_value=mock_conn)
        mocker.patch("pandas.read_sql", return_value=self._mock_df())

        from database.schema_loader import load_schema_df
        df = load_schema_df()
        assert isinstance(df, pd.DataFrame)
        assert "dbo.fact_orders" in df["TABLE_NAME"].values

    def test_live_text_uses_db_data(self, mocker):
        mock_conn = MagicMock()
        mocker.patch("database.schema_loader.DEMO_MODE", False)
        mocker.patch("database.schema_loader.get_connection", return_value=mock_conn)
        mocker.patch("pandas.read_sql", return_value=self._mock_df())

        from database.schema_loader import load_schema_text
        text = load_schema_text()
        assert "dbo.fact_orders" in text
        assert "dbo.dim_product" in text
