"""
tests/test_sql_explainer.py
-----------------------------
Unit tests for services/sql_explainer.py.

Covers:
  - explain_sql(): response stripped, prompt builder called correctly
  - Gemini client called exactly once per invocation
"""
import pytest
from unittest.mock import MagicMock


# ── Helper ────────────────────────────────────────────────────────────────────

def _patch_client(mocker, response_text: str):
    mock_response = MagicMock()
    mock_response.text = response_text
    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = mock_response
    mocker.patch("services.sql_explainer._client", mock_client)
    return mock_client


# ── explain_sql ───────────────────────────────────────────────────────────────

class TestExplainSql:
    def test_returns_string(self, mocker, sample_sql):
        _patch_client(mocker, "This query retrieves top customers.")
        from services.sql_explainer import explain_sql
        assert isinstance(explain_sql(sample_sql), str)

    def test_strips_response_whitespace(self, mocker, sample_sql):
        _patch_client(mocker, "  Explanation text.  \n")
        from services.sql_explainer import explain_sql
        result = explain_sql(sample_sql)
        assert result == "Explanation text."

    def test_calls_build_explain_prompt(self, mocker, sample_sql):
        _patch_client(mocker, "explanation")
        mock_builder = mocker.patch(
            "services.sql_explainer.build_explain_prompt",
            return_value="mocked explain prompt"
        )
        from services.sql_explainer import explain_sql
        explain_sql(sample_sql)
        mock_builder.assert_called_once_with(sample_sql)

    def test_passes_built_prompt_to_gemini(self, mocker, sample_sql):
        mock_client = _patch_client(mocker, "explanation")
        mocker.patch(
            "services.sql_explainer.build_explain_prompt",
            return_value="the explain prompt"
        )
        from services.sql_explainer import explain_sql
        explain_sql(sample_sql)

        call_args = mock_client.models.generate_content.call_args
        contents = call_args.kwargs.get("contents") or call_args.args[1]
        assert contents == "the explain prompt"

    def test_generate_content_called_once(self, mocker, sample_sql):
        mock_client = _patch_client(mocker, "explanation")
        from services.sql_explainer import explain_sql
        explain_sql(sample_sql)
        assert mock_client.models.generate_content.call_count == 1

    def test_returns_full_structured_response(self, mocker, sample_sql):
        structured = (
            "**Purpose:** Retrieves top customers by sales.\n"
            "**Step-by-step:** 1. JOINs fact_sales with dim_customer\n"
            "**Key concepts:** JOIN, GROUP BY, ORDER BY"
        )
        _patch_client(mocker, structured)
        from services.sql_explainer import explain_sql
        result = explain_sql(sample_sql)
        assert "Purpose" in result
        assert "Step-by-step" in result
        assert "Key concepts" in result

    @pytest.mark.parametrize("sql", [
        "SELECT 1",
        "SELECT COUNT(*) FROM fact_sales",
        "SELECT * FROM dim_customer WHERE country = 'USA'",
        (
            "WITH ranked AS (\n"
            "    SELECT customer_id, ROW_NUMBER() OVER (ORDER BY sales_amount DESC) AS rn\n"
            "    FROM fact_sales\n"
            ")\n"
            "SELECT * FROM ranked WHERE rn <= 10"
        ),
    ])
    def test_various_sql_queries(self, mocker, sql):
        mock_builder = mocker.patch(
            "services.sql_explainer.build_explain_prompt",
            return_value="prompt"
        )
        _patch_client(mocker, "explanation")
        from services.sql_explainer import explain_sql
        result = explain_sql(sql)

        mock_builder.assert_called_once_with(sql)
        assert isinstance(result, str)
