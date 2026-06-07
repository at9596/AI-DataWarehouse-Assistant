"""
tests/test_documentation_generator.py
----------------------------------------
Unit tests for services/documentation_generator.py.

Covers:
  - generate_data_dictionary(): schema injected, response stripped
  - generate_etl_docs(): ETL script injected, response stripped
"""
import pytest
from unittest.mock import MagicMock


# ── Helper ────────────────────────────────────────────────────────────────────

def _patch_client(mocker, response_text: str):
    mock_response = MagicMock()
    mock_response.text = response_text
    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = mock_response
    mocker.patch("services.documentation_generator._client", mock_client)
    return mock_client


# ── generate_data_dictionary ──────────────────────────────────────────────────

class TestGenerateDataDictionary:
    def test_returns_string(self, mocker, sample_schema):
        _patch_client(mocker, "# Data Dictionary\n## Table: fact_sales")
        from services.documentation_generator import generate_data_dictionary
        assert isinstance(generate_data_dictionary(sample_schema), str)

    def test_strips_response_whitespace(self, mocker, sample_schema):
        _patch_client(mocker, "  ## Data Dictionary  \n")
        from services.documentation_generator import generate_data_dictionary
        result = generate_data_dictionary(sample_schema)
        assert result == "## Data Dictionary"

    def test_injects_schema_into_prompt(self, mocker, sample_schema):
        mock_client = _patch_client(mocker, "docs")
        from services.documentation_generator import generate_data_dictionary
        generate_data_dictionary(sample_schema)

        call_args = mock_client.models.generate_content.call_args
        prompt = call_args.kwargs.get("contents") or call_args.args[1]
        assert "fact_sales" in prompt
        assert "dim_customer" in prompt

    def test_prompt_requests_data_dictionary_format(self, mocker, sample_schema):
        mock_client = _patch_client(mocker, "docs")
        from services.documentation_generator import generate_data_dictionary
        generate_data_dictionary(sample_schema)

        call_args = mock_client.models.generate_content.call_args
        prompt = call_args.kwargs.get("contents") or call_args.args[1]
        assert "Data Dictionary" in prompt

    def test_prompt_asks_for_all_tables(self, mocker, sample_schema):
        mock_client = _patch_client(mocker, "docs")
        from services.documentation_generator import generate_data_dictionary
        generate_data_dictionary(sample_schema)

        call_args = mock_client.models.generate_content.call_args
        prompt = call_args.kwargs.get("contents") or call_args.args[1]
        assert "ALL tables" in prompt or "all tables" in prompt.lower()

    def test_generate_content_called_once(self, mocker, sample_schema):
        mock_client = _patch_client(mocker, "docs")
        from services.documentation_generator import generate_data_dictionary
        generate_data_dictionary(sample_schema)
        assert mock_client.models.generate_content.call_count == 1

    def test_returns_full_multiline_response(self, mocker, sample_schema):
        markdown_doc = (
            "## Table: fact_sales\n"
            "| Column | Data Type | Description |\n"
            "|--------|-----------|-------------|\n"
            "| sale_id | int | Primary key |"
        )
        _patch_client(mocker, markdown_doc)
        from services.documentation_generator import generate_data_dictionary
        result = generate_data_dictionary(sample_schema)
        assert "fact_sales" in result
        assert "sale_id" in result

    def test_different_schemas_produce_different_prompts(self, mocker):
        prompts_used = []

        def capture(**kwargs):
            prompts_used.append(kwargs.get("contents", ""))
            resp = MagicMock()
            resp.text = "docs"
            return resp

        mock_client = MagicMock()
        mock_client.models.generate_content.side_effect = capture
        mocker.patch("services.documentation_generator._client", mock_client)

        from services.documentation_generator import generate_data_dictionary
        generate_data_dictionary("Table: orders | Columns: order_id (int)")
        generate_data_dictionary("Table: products | Columns: product_id (int)")

        assert prompts_used[0] != prompts_used[1]


# ── generate_etl_docs ─────────────────────────────────────────────────────────

class TestGenerateEtlDocs:
    def test_returns_string(self, mocker, sample_etl):
        _patch_client(mocker, "## ETL Documentation")
        from services.documentation_generator import generate_etl_docs
        assert isinstance(generate_etl_docs(sample_etl), str)

    def test_strips_response_whitespace(self, mocker, sample_etl):
        _patch_client(mocker, "  ETL docs here.  \n")
        from services.documentation_generator import generate_etl_docs
        result = generate_etl_docs(sample_etl)
        assert result == "ETL docs here."

    def test_injects_etl_script_into_prompt(self, mocker, sample_etl):
        mock_client = _patch_client(mocker, "docs")
        from services.documentation_generator import generate_etl_docs
        generate_etl_docs(sample_etl)

        call_args = mock_client.models.generate_content.call_args
        prompt = call_args.kwargs.get("contents") or call_args.args[1]
        assert "silver.customer" in prompt
        assert "bronze.customer" in prompt

    def test_prompt_requests_source_and_target_tables(self, mocker, sample_etl):
        mock_client = _patch_client(mocker, "docs")
        from services.documentation_generator import generate_etl_docs
        generate_etl_docs(sample_etl)

        call_args = mock_client.models.generate_content.call_args
        prompt = call_args.kwargs.get("contents") or call_args.args[1]
        assert "Source" in prompt
        assert "Target" in prompt

    def test_prompt_requests_purpose_section(self, mocker, sample_etl):
        mock_client = _patch_client(mocker, "docs")
        from services.documentation_generator import generate_etl_docs
        generate_etl_docs(sample_etl)

        call_args = mock_client.models.generate_content.call_args
        prompt = call_args.kwargs.get("contents") or call_args.args[1]
        assert "Purpose" in prompt

    def test_prompt_embeds_script_in_code_fence(self, mocker, sample_etl):
        mock_client = _patch_client(mocker, "docs")
        from services.documentation_generator import generate_etl_docs
        generate_etl_docs(sample_etl)

        call_args = mock_client.models.generate_content.call_args
        prompt = call_args.kwargs.get("contents") or call_args.args[1]
        assert "```sql" in prompt

    def test_generate_content_called_once(self, mocker, sample_etl):
        mock_client = _patch_client(mocker, "docs")
        from services.documentation_generator import generate_etl_docs
        generate_etl_docs(sample_etl)
        assert mock_client.models.generate_content.call_count == 1

    @pytest.mark.parametrize("etl_script", [
        "INSERT INTO silver.sales SELECT * FROM bronze.sales",
        "EXEC sp_load_gold_layer @date = '2024-01-01'",
        (
            "BEGIN TRY\n"
            "    INSERT INTO gold.summary\n"
            "    SELECT date_id, SUM(sales_amount)\n"
            "    FROM silver.sales GROUP BY date_id\n"
            "END TRY\n"
            "BEGIN CATCH\n"
            "    ROLLBACK\n"
            "END CATCH"
        ),
    ])
    def test_various_etl_scripts(self, mocker, etl_script):
        mock_client = _patch_client(mocker, "etl docs")
        from services.documentation_generator import generate_etl_docs
        result = generate_etl_docs(etl_script)

        call_args = mock_client.models.generate_content.call_args
        prompt = call_args.kwargs.get("contents") or call_args.args[1]
        # Script content must appear in the prompt
        first_line = etl_script.splitlines()[0]
        assert first_line in prompt
        assert isinstance(result, str)
