"""
prompts/validation_prompt.py
-----------------------------
Prompt template for validating ETL scripts and SQL stored procedures.
Gemini acts as a data quality auditor and returns structured feedback.
"""


def build_validation_prompt(etl_script: str) -> str:
    return f"""
You are a senior ETL developer and data quality engineer.

Review the following ETL script and identify all issues. For each issue found, provide:
- **Issue type** (e.g., Data Quality, Performance, Naming Convention, Error Handling)
- **Severity** (🔴 Critical / 🟠 High / 🟡 Medium / 🟢 Low)
- **Description** of the problem
- **Recommended fix** with example code where applicable

Check specifically for:
1. Use of SELECT * (explicit column mapping is required)
2. Missing NULL handling (ISNULL / COALESCE)
3. Missing data type conversions
4. No error handling (TRY/CATCH blocks)
5. Naming convention violations (snake_case for columns, PascalCase for procs)
6. Missing WHERE clauses on large table reads (full table scans)
7. Missing duplicate handling / deduplication logic
8. No logging or audit trail
9. Missing transaction management (BEGIN TRAN / COMMIT / ROLLBACK)

ETL Script:
```sql
{etl_script}
```

Format your response as a clear, numbered list of findings.
""".strip()
