"""
services/schema_analyzer.py
-----------------------------
Calls the Gemini API to analyze the database schema and produce:
- Table-by-table descriptions
- Relationship mapping between fact and dimension tables
- Data domain analysis
"""
from google import genai
from config import GEMINI_API_KEY, GEMINI_MODEL

_client = genai.Client(api_key=GEMINI_API_KEY)


def analyze_schema(schema: str) -> str:
    """
    Given the DB schema as text, returns an AI-generated analysis
    of the data warehouse structure.
    """
    prompt = f"""
You are a senior data architect reviewing a data warehouse schema.

Given the following schema:
{schema}

Provide a comprehensive analysis covering:
1. **Schema Overview** — What kind of data does this warehouse store?
2. **Fact Tables** — List each fact table and what business process it captures
3. **Dimension Tables** — List each dimension and what it describes
4. **Key Relationships** — How do fact and dimension tables relate? (Star schema? Snowflake?)
5. **Data Layers** — Identify any Bronze/Silver/Gold layers and their purpose
6. **Recommendations** — Any missing dimensions, indexes, or design improvements?

Be specific and use the actual table and column names from the schema.
""".strip()

    response = _client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
    return response.text.strip()


def get_table_description(schema: str, table_name: str) -> str:
    """Returns an AI-generated description for a specific table."""
    prompt = f"""
You are a data warehouse documentation expert.

Given this database schema:
{schema}

Write a detailed description for the table: **{table_name}**

Include:
- Table purpose and what business entity/process it represents
- Column-by-column description (name, type, purpose)
- Relationships to other tables
- Common use cases (what kind of queries it supports)
""".strip()

    response = _client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
    return response.text.strip()
