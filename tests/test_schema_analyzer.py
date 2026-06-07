"""
tests/test_schema_analyzer.py
-------------------------------
Unit tests for services/schema_analyzer.py.

Covers:
  - analyze_schema(): response stripped, schema injected into prompt
  - get_table_description(): response stripped, table_name injected into prompt
"""
import pytest
from unittest.mock import MagicMock


# ── Shared helper ─────────────────────────────────────────────────────────────

def _patch_client(mocker, response_text: str):
    """Patches services.schema_analyzer._client to return response_text."""
    mock_response = MagicMock()
    mock_response.text = response_text
    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = mock_response
    mocker.patch("services.schema_analyzer._client", mock_client)
    return mock_client


# ── analyze_schema ────────────────────────────────────────────────────────────

class TestAnalyzeSchema:
    def test_returns_string(self, mocker, sample_schema):
        _patch_client(mocker, "analysis result")
        from services.schema_analyzer import analyze_schema
        assert isinstance(analyze_schema(sample_schema), str)

    def test_strips_response_whitespace(self, mocker, sample_schema):
        _patch_client(mocker, "  AI analysis text.  \n")
        from services.schema_analyzer import analyze_schema
        result = analyze_schema(sample_schema)
        assert result == "AI analysis text."

    def test_injects_schema_into_prompt(self, mocker, sample_schema):
        mock_client = _patch_client(mocker, "analysis")
        from services.schema_analyzer import analyze_schema
        analyze_schema(sample_schema)

        call_args = mock_client.models.generate_content.call_args
        prompt = call_args.kwargs.get("contents") or call_args.args[1]
        assert "fact_sales" in prompt
        assert "dim_customer" in prompt

    def test_prompt_contains_analysis_sections(self, mocker, sample_schema):
        """Prompt should ask for schema overview, fact/dim tables, etc."""
        mock_client = _patch_client(mocker, "analysis")
        from services.schema_analyzer import analyze_schema
        analyze_schema(sample_schema)

        call_args = mock_client.models.generate_content.call_args
        prompt = call_args.kwargs.get("contents") or call_args.args[1]
        assert "Fact Table" in prompt or "fact table" in prompt.lower()
        assert "Dimension" in prompt or "dimension" in prompt.lower()
        assert "Recommendation" in prompt or "recommendation" in prompt.lower()

    def test_calls_generate_content_once(self, mocker, sample_schema):
        mock_client = _patch_client(mocker, "ok")
        from services.schema_analyzer import analyze_schema
        analyze_schema(sample_schema)
        assert mock_client.models.generate_content.call_count == 1

    def test_different_schemas_use_different_prompts(self, mocker):
        prompts_used = []

        def capture_call(**kwargs):
            prompts_used.append(kwargs.get("contents", ""))
            resp = MagicMock()
            resp.text = "result"
            return resp

        mock_client = MagicMock()
        mock_client.models.generate_content.side_effect = capture_call
        mocker.patch("services.schema_analyzer._client", mock_client)

        from services.schema_analyzer import analyze_schema
        analyze_schema("Table: orders | Columns: order_id (int)")
        analyze_schema("Table: invoices | Columns: invoice_id (int)")

        assert prompts_used[0] != prompts_used[1]

    def test_returns_full_response_text(self, mocker, sample_schema):
        long_response = "Line 1\nLine 2\nLine 3"
        _patch_client(mocker, long_response)
        from services.schema_analyzer import analyze_schema
        result = analyze_schema(sample_schema)
        assert "Line 1" in result
        assert "Line 3" in result


# ── get_table_description ─────────────────────────────────────────────────────

class TestGetTableDescription:
    def test_returns_string(self, mocker, sample_schema):
        _patch_client(mocker, "Table description.")
        from services.schema_analyzer import get_table_description
        assert isinstance(get_table_description(sample_schema, "fact_sales"), str)

    def test_strips_response_whitespace(self, mocker, sample_schema):
        _patch_client(mocker, "  Description here.  \n")
        from services.schema_analyzer import get_table_description
        result = get_table_description(sample_schema, "fact_sales")
        assert result == "Description here."

    def test_injects_table_name_into_prompt(self, mocker, sample_schema):
        mock_client = _patch_client(mocker, "desc")
        from services.schema_analyzer import get_table_description
        get_table_description(sample_schema, "dim_customer")

        call_args = mock_client.models.generate_content.call_args
        prompt = call_args.kwargs.get("contents") or call_args.args[1]
        assert "dim_customer" in prompt

    def test_injects_schema_into_prompt(self, mocker, sample_schema):
        mock_client = _patch_client(mocker, "desc")
        from services.schema_analyzer import get_table_description
        get_table_description(sample_schema, "fact_sales")

        call_args = mock_client.models.generate_content.call_args
        prompt = call_args.kwargs.get("contents") or call_args.args[1]
        # Schema content must appear in prompt
        assert "fact_sales" in prompt

    def test_different_tables_produce_different_prompts(self, mocker, sample_schema):
        prompts_used = []

        def capture(**kwargs):
            prompts_used.append(kwargs.get("contents", ""))
            resp = MagicMock()
            resp.text = "result"
            return resp

        mock_client = MagicMock()
        mock_client.models.generate_content.side_effect = capture
        mocker.patch("services.schema_analyzer._client", mock_client)

        from services.schema_analyzer import get_table_description
        get_table_description(sample_schema, "fact_sales")
        get_table_description(sample_schema, "dim_customer")

        assert prompts_used[0] != prompts_used[1]

    @pytest.mark.parametrize("table_name", [
        "fact_sales",
        "dim_customer",
        "dim_product",
        "dim_date",
        "silver.customer",
        "bronze.customer",
    ])
    def test_all_known_tables(self, mocker, sample_schema, table_name):
        mock_client = _patch_client(mocker, f"Description of {table_name}")
        from services.schema_analyzer import get_table_description
        result = get_table_description(sample_schema, table_name)
        assert isinstance(result, str)
        assert len(result) > 0
