"""
services/etl_validator.py
--------------------------
Calls Gemini API to review ETL scripts and return structured
findings across data quality, performance, and best-practice checks.
"""
from google import genai
from config import GEMINI_API_KEY, GEMINI_MODEL
from prompts.validation_prompt import build_validation_prompt

_client = genai.Client(api_key=GEMINI_API_KEY)


def validate_etl(etl_script: str) -> str:
    """
    Validates an ETL script and returns a formatted list of findings.
    """
    prompt = build_validation_prompt(etl_script)
    response = _client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
    return response.text.strip()
