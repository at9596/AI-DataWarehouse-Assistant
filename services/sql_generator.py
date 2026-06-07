"""
services/sql_generator.py
--------------------------
Calls the Gemini API to convert a natural language question
into an optimized T-SQL query using the database schema as context.
"""
from google import genai
from config import GEMINI_API_KEY, GEMINI_MODEL
from prompts.sql_prompt import build_sql_prompt

_client = genai.Client()


def generate_sql(schema: str, question: str) -> str:
    """
    Given the DB schema (as text) and a natural language question,
    returns a T-SQL query string.
    """
    prompt = build_sql_prompt(schema, question)
    # response = _client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
    response = _client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
    sql = response.text.strip()

    # Strip markdown code fences if Gemini wraps the output
    if sql.startswith("```"):
        lines = sql.splitlines()
        sql = "\n".join(
            line for line in lines
            if not line.strip().startswith("```")
        ).strip()

    return sql
