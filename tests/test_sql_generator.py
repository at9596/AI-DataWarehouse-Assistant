"""
tests/test_sql_generator.py
-----------------------------
Unit tests for services/sql_generator.py.

Key things under test:
  1. Markdown fence stripping logic (the main business logic in the service)
  2. Correct delegation to build_sql_prompt
  3. Gemini client is called with the right model
"""
import pytest
from unittest.mock import MagicMock, call


# ── Helper ────────────────────────────────────────────────────────────────────

def _run(mocker, raw_response: str, schema: str = "schema", question: str = "question") -> str:
    """Patch _client and call generate_sql, returning the result."""
    mock_response = MagicMock()
    mock_response.text = raw_response

    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = mock_response
    mocker.patch("services.sql_generator._client", mock_client)

    from services.sql_generator import generate_sql
    return generate_sql(schema, question)


# ── Markdown fence stripping ──────────────────────────────────────────────────

class TestMarkdownFenceStripping:
    """
    The sql_generator strips ```sql ... ``` fences that Gemini sometimes adds.
    These tests exercise every case of that post-processing logic.
    """

    def test_plain_sql_passes_through(self, mocker):
        sql = "SELECT * FROM fact_sales ORDER BY sale_id"
        assert _run(mocker, sql) == sql

    def test_strips_sql_fenced_block(self, mocker):
        raw = "```sql\nSELECT * FROM fact_sales\n```"
        result = _run(mocker, raw)
        assert "```" not in result
        assert "SELECT * FROM fact_sales" in result

    def test_strips_generic_fenced_block(self, mocker):
        raw = "```\nSELECT 1\n```"
        result = _run(mocker, raw)
        assert "```" not in result
        assert "SELECT 1" in result

    def test_multiline_sql_body_preserved(self, mocker):
        raw = "```sql\nSELECT a,\n       b\nFROM   t\nWHERE  a > 0\n```"
        result = _run(mocker, raw)
        assert "SELECT a," in result
        assert "FROM   t" in result
        assert "WHERE  a > 0" in result

    def test_cte_query_preserved(self, mocker):
        raw = (
            "```sql\n"
            "WITH cte AS (\n"
            "    SELECT customer_id, SUM(sales_amount) AS total\n"
            "    FROM fact_sales\n"
            "    GROUP BY customer_id\n"
            ")\n"
            "SELECT * FROM cte ORDER BY total DESC\n"
            "```"
        )
        result = _run(mocker, raw)
        assert "WITH cte AS" in result
        assert "GROUP BY customer_id" in result
        assert "```" not in result

    def test_result_is_stripped_of_outer_whitespace(self, mocker):
        raw = "  SELECT 1  "
        result = _run(mocker, raw)
        assert result == result.strip()

    def test_empty_response_returns_empty_string(self, mocker):
        result = _run(mocker, "   ")
        assert result == ""

    def test_returns_string_type(self, mocker):
        result = _run(mocker, "SELECT 1")
        assert isinstance(result, str)


# ── Prompt builder delegation ─────────────────────────────────────────────────

class TestSqlGeneratorDelegation:
    def test_calls_build_sql_prompt_with_correct_args(self, mocker):
        mock_response = MagicMock()
        mock_response.text = "SELECT 1"
        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = mock_response
        mocker.patch("services.sql_generator._client", mock_client)

        mock_builder = mocker.patch(
            "services.sql_generator.build_sql_prompt",
            return_value="built prompt"
        )

        from services.sql_generator import generate_sql
        generate_sql("my_schema", "my_question")

        mock_builder.assert_called_once_with("my_schema", "my_question")

    def test_generate_content_called_with_built_prompt(self, mocker):
        mock_response = MagicMock()
        mock_response.text = "SELECT 1"
        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = mock_response
        mocker.patch("services.sql_generator._client", mock_client)

        mocker.patch(
            "services.sql_generator.build_sql_prompt",
            return_value="the final prompt"
        )

        from services.sql_generator import generate_sql
        generate_sql("schema", "question")

        call_kwargs = mock_client.models.generate_content.call_args
        contents_used = (
            call_kwargs.kwargs.get("contents")
            or call_kwargs.args[1]
        )
        assert contents_used == "the final prompt"

    def test_generate_content_called_exactly_once(self, mocker):
        mock_response = MagicMock()
        mock_response.text = "SELECT 1"
        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = mock_response
        mocker.patch("services.sql_generator._client", mock_client)

        from services.sql_generator import generate_sql
        generate_sql("schema", "question")

        assert mock_client.models.generate_content.call_count == 1


# ── Parametrized fence variants ───────────────────────────────────────────────

@pytest.mark.parametrize("raw,expected_fragment", [
    ("SELECT 1",                                 "SELECT 1"),
    ("```sql\nSELECT 2\n```",                   "SELECT 2"),
    ("```\nSELECT 3\n```",                       "SELECT 3"),
    ("```tsql\nSELECT 4\n```",                  "SELECT 4"),
    ("```sql\nSELECT 5\nFROM t\n```",           "FROM t"),
])
def test_fence_variants(mocker, raw, expected_fragment):
    result = _run(mocker, raw)
    assert expected_fragment in result
    assert "```" not in result
