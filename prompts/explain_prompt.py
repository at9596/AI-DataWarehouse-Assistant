"""
prompts/explain_prompt.py
--------------------------
Prompt template for generating a plain-English explanation
of a SQL query, section by section.
"""


def build_explain_prompt(sql: str) -> str:
    return f"""
You are a SQL tutor helping junior data analysts understand complex queries.

Explain the following SQL query in clear, plain English.
Structure your response as:
1. **Purpose** — What does this query do in one sentence?
2. **Step-by-step breakdown** — Explain each clause (SELECT, FROM, WHERE, GROUP BY, etc.)
3. **Key concepts used** — List any SQL features or techniques (CTEs, window functions, joins, etc.)
4. **Potential improvements** — Suggest 1-2 optimization tips if applicable

SQL Query:
```sql
{sql}
```
""".strip()
