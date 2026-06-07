"""
services/sql_explainer.py
--------------------------
Calls the Gemini API to explain a SQL query in plain English,
broken down clause by clause.
"""
from google import genai
from config import GEMINI_API_KEY, GEMINI_MODEL
from prompts.explain_prompt import build_explain_prompt

_client = genai.Client(api_key=GEMINI_API_KEY)


def explain_sql(sql: str) -> str:
    """
    Returns a structured plain-English explanation of the given SQL query.
    """
    prompt = build_explain_prompt(sql)
    response = _client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
    return response.text.strip()
