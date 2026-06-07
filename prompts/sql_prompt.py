"""
prompts/sql_prompt.py
---------------------
Prompt template for converting a natural language question
into an optimized T-SQL query using the database schema as context.
"""


def build_sql_prompt(schema: str, question: str) -> str:
    return f"""
You are a senior SQL Server data warehouse developer with 10+ years of experience in T-SQL.

Given the following database schema:
{schema}

Write an optimized T-SQL query that answers this business question:
"{question}"

Rules:
- Use proper table aliases
- Always qualify column names with table aliases
- Use CTEs instead of nested subqueries where possible
- Add ORDER BY for readability
- Return ONLY the SQL query — no explanation, no markdown fences
""".strip()
