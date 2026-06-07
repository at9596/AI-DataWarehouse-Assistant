"""
tests/test_prompts.py
----------------------
Unit tests for all prompt builder functions in prompts/.
These are pure string-building functions — no mocking required.
"""
import pytest
from prompts.sql_prompt import build_sql_prompt
from prompts.explain_prompt import build_explain_prompt
from prompts.validation_prompt import build_validation_prompt


# ── build_sql_prompt ──────────────────────────────────────────────────────────

class TestBuildSqlPrompt:
    def test_returns_string(self, sample_schema):
        result = build_sql_prompt(sample_schema, "Show top 10 customers")
        assert isinstance(result, str)

    def test_contains_schema(self, sample_schema):
        result = build_sql_prompt(sample_schema, "Show top 10 customers")
        assert "fact_sales" in result
        assert "dim_customer" in result

    def test_contains_question(self, sample_schema):
        question = "What are the top 10 selling products?"
        result = build_sql_prompt(sample_schema, question)
        assert question in result

    def test_no_leading_or_trailing_whitespace(self, sample_schema):
        result = build_sql_prompt(sample_schema, "Any question?")
        assert result == result.strip()

    def test_instructs_no_markdown_fences(self, sample_schema):
        """Prompt must tell Gemini not to return markdown code fences."""
        result = build_sql_prompt(sample_schema, "Any question?")
        assert "no markdown" in result.lower() or "Return ONLY the SQL" in result

    def test_different_questions_produce_different_prompts(self, sample_schema):
        q1 = build_sql_prompt(sample_schema, "Top sales?")
        q2 = build_sql_prompt(sample_schema, "Bottom sales?")
        assert q1 != q2

    def test_different_schemas_produce_different_prompts(self):
        schema_a = "Table: orders | Columns: order_id (int)"
        schema_b = "Table: invoices | Columns: invoice_id (int)"
        r1 = build_sql_prompt(schema_a, "Same question")
        r2 = build_sql_prompt(schema_b, "Same question")
        assert r1 != r2


# ── build_explain_prompt ──────────────────────────────────────────────────────

class TestBuildExplainPrompt:
    def test_returns_string(self, sample_sql):
        result = build_explain_prompt(sample_sql)
        assert isinstance(result, str)

    def test_contains_sql_query(self, sample_sql):
        result = build_explain_prompt(sample_sql)
        # Key tokens from the sample SQL should appear in the prompt
        assert "fact_sales" in result
        assert "dim_customer" in result
        assert "SUM" in result

    def test_no_leading_or_trailing_whitespace(self, sample_sql):
        result = build_explain_prompt(sample_sql)
        assert result == result.strip()

    def test_requests_structured_explanation(self, sample_sql):
        """Prompt should ask for Purpose, breakdown, etc."""
        result = build_explain_prompt(sample_sql)
        assert "Purpose" in result
        assert "breakdown" in result.lower() or "Step" in result

    def test_embeds_sql_in_code_fence(self, sample_sql):
        """The prompt wraps the SQL in a ```sql fence for Gemini context."""
        result = build_explain_prompt(sample_sql)
        assert "```sql" in result

    def test_empty_sql_still_returns_string(self):
        result = build_explain_prompt("")
        assert isinstance(result, str)
        assert len(result) > 0


# ── build_validation_prompt ───────────────────────────────────────────────────

class TestBuildValidationPrompt:
    def test_returns_string(self, sample_etl):
        result = build_validation_prompt(sample_etl)
        assert isinstance(result, str)

    def test_contains_etl_script(self, sample_etl):
        result = build_validation_prompt(sample_etl)
        assert "silver.customer" in result
        assert "bronze.customer" in result

    def test_no_leading_or_trailing_whitespace(self, sample_etl):
        result = build_validation_prompt(sample_etl)
        assert result == result.strip()

    def test_contains_key_check_categories(self, sample_etl):
        """Prompt should mention the major ETL check areas."""
        result = build_validation_prompt(sample_etl)
        assert "NULL" in result or "null" in result.lower()
        assert "error" in result.lower()
        assert "transaction" in result.lower() or "TRY" in result

    def test_embeds_script_in_code_fence(self, sample_etl):
        result = build_validation_prompt(sample_etl)
        assert "```sql" in result

    def test_requests_numbered_findings(self, sample_etl):
        result = build_validation_prompt(sample_etl)
        assert "numbered" in result.lower() or "list" in result.lower()

    def test_severity_levels_mentioned(self, sample_etl):
        """Prompt should instruct Gemini to use severity levels."""
        result = build_validation_prompt(sample_etl)
        assert "Critical" in result or "Severity" in result

    @pytest.mark.parametrize("script", [
        "SELECT * FROM bronze.orders",
        "INSERT INTO gold.summary SELECT COUNT(*) FROM silver.orders",
        "UPDATE dim_customer SET city = NULL WHERE customer_id = 1",
    ])
    def test_various_scripts_injected_correctly(self, script):
        result = build_validation_prompt(script)
        assert script in result
