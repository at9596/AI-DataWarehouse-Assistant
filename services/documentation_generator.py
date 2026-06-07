"""
services/documentation_generator.py
--------------------------------------
Calls Gemini API to auto-generate data warehouse documentation:
- Full Data Dictionary (all tables + columns)
- ETL Pipeline documentation
- Business glossary
"""
from google import genai
from config import GEMINI_API_KEY, GEMINI_MODEL

_client = genai.Client(api_key=GEMINI_API_KEY)


def generate_data_dictionary(schema: str) -> str:
    """
    Generates a complete data dictionary for the warehouse schema.
    Returns markdown-formatted documentation.
    """
    prompt = f"""
You are a data governance expert creating official data warehouse documentation.

Given the following database schema:
{schema}

Generate a complete **Data Dictionary** in markdown format. Include:

For each table:
## Table: <table_name>
| Column | Data Type | Description | Example Values | Nullable |
|--------|-----------|-------------|----------------|----------|
| ...    | ...       | ...         | ...            | Yes/No   |

**Business Definition:** One sentence on what this table represents.
**Primary Key:** Which column(s) uniquely identify a row?
**Common Joins:** Which tables does this join to most often?

Generate the dictionary for ALL tables in the schema.
""".strip()

    response = _client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
    return response.text.strip()


def generate_etl_docs(etl_script: str) -> str:
    """
    Generates human-readable documentation for an ETL script or stored procedure.
    """
    prompt = f"""
You are a senior ETL developer writing technical documentation.

Document the following ETL script in a clear, structured format:

```sql
{etl_script}
```

Include:
1. **Purpose** — What does this ETL job do?
2. **Source Tables** — What tables does it read from?
3. **Target Tables** — What tables does it write to?
4. **Transformation Logic** — What business rules or transformations are applied?
5. **Dependencies** — What must run before this job?
6. **Schedule** — Recommend a run frequency (daily, hourly, etc.)
7. **Error Handling** — Is there error handling? What should be added?
""".strip()

    response = _client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
    return response.text.strip()
