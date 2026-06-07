"""
tests/test_etl_validator.py
-----------------------------
Unit tests for services/etl_validator.py.

Covers:
  - validate_etl(): response stripped, prompt builder called correctly
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
    mocker.patch("services.etl_validator._client", mock_client)
    return mock_client


# ── validate_etl ──────────────────────────────────────────────────────────────

class TestValidateEtl:
    def test_returns_string(self, mocker, sample_etl):
        _patch_client(mocker, "1. Finding: missing error handling.")
        from services.etl_validator import validate_etl
        assert isinstance(validate_etl(sample_etl), str)

    def test_strips_response_whitespace(self, mocker, sample_etl):
        _patch_client(mocker, "   ⚠️ Critical: no TRY/CATCH.   \n")
        from services.etl_validator import validate_etl
        result = validate_etl(sample_etl)
        assert result == "⚠️ Critical: no TRY/CATCH."

    def test_calls_build_validation_prompt(self, mocker, sample_etl):
        _patch_client(mocker, "findings")
        mock_builder = mocker.patch(
            "services.etl_validator.build_validation_prompt",
            return_value="mocked validation prompt"
        )
        from services.etl_validator import validate_etl
        validate_etl(sample_etl)
        mock_builder.assert_called_once_with(sample_etl)

    def test_passes_built_prompt_to_gemini(self, mocker, sample_etl):
        mock_client = _patch_client(mocker, "findings")
        mocker.patch(
            "services.etl_validator.build_validation_prompt",
            return_value="the validation prompt"
        )
        from services.etl_validator import validate_etl
        validate_etl(sample_etl)

        call_args = mock_client.models.generate_content.call_args
        contents = call_args.kwargs.get("contents") or call_args.args[1]
        assert contents == "the validation prompt"

    def test_generate_content_called_once(self, mocker, sample_etl):
        mock_client = _patch_client(mocker, "findings")
        from services.etl_validator import validate_etl
        validate_etl(sample_etl)
        assert mock_client.models.generate_content.call_count == 1

    def test_returns_full_multiline_response(self, mocker, sample_etl):
        findings = "1. Missing TRY/CATCH\n2. SELECT * used\n3. No NULL handling"
        _patch_client(mocker, findings)
        from services.etl_validator import validate_etl
        result = validate_etl(sample_etl)
        assert "Missing TRY/CATCH" in result
        assert "SELECT * used" in result
        assert "No NULL handling" in result

    @pytest.mark.parametrize("etl_script", [
        "INSERT INTO silver.orders SELECT * FROM bronze.orders",
        "UPDATE gold.summary SET total = 0 WHERE date_id = 1",
        "DELETE FROM bronze.temp WHERE created_date < '2024-01-01'",
        (
            "BEGIN TRAN\n"
            "INSERT INTO silver.customer SELECT customer_id FROM bronze.customer\n"
            "COMMIT"
        ),
    ])
    def test_various_etl_scripts(self, mocker, etl_script):
        mock_builder = mocker.patch(
            "services.etl_validator.build_validation_prompt",
            return_value="prompt"
        )
        _patch_client(mocker, "some findings")
        from services.etl_validator import validate_etl
        result = validate_etl(etl_script)

        # Builder must be called with the exact script passed in
        mock_builder.assert_called_once_with(etl_script)
        assert isinstance(result, str)
