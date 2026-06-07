# AI Data Warehouse Assistant

An AI-powered Data Warehouse Assistant built with Python, Streamlit, Gemini API, and SQL Server. The application helps data engineers, analysts, and database developers interact with their data warehouse using natural language.

## Features

### Natural Language to SQL

Convert business questions into optimized SQL queries.

**Example:**

```
Show total sales by month for the current year.
```

Generated SQL:

```
SELECT
    YEAR(order_date) AS sales_year,
    MONTH(order_date) AS sales_month,
    SUM(sales_amount) AS total_sales
FROM fact_sales
WHERE YEAR(order_date) = YEAR(GETDATE())
GROUP BY YEAR(order_date), MONTH(order_date)
ORDER BY sales_month;
```

### SQL Query Explanation

Get detailed explanations of generated or existing SQL queries.

### SQL Optimization Suggestions

Analyze query performance and receive recommendations for:

* Indexing
* Query restructuring
* Join optimization
* Aggregation improvements

### ETL Validation

Validate ETL scripts and identify:

* Missing null handling
* Data quality issues
* Naming convention violations
* Potential performance bottlenecks

### Stored Procedure Analysis

Understand complex stored procedures through AI-generated explanations.

### Data Dictionary Generation

Automatically generate documentation for:

* Tables
* Columns
* Relationships
* Business definitions

### Schema Understanding

Explore database schemas and understand table relationships.

### Automated Documentation

Generate technical documentation for data warehouse objects and ETL pipelines.

---

## Architecture

```
+-------------------+
|     Streamlit     |
|       UI          |
+---------+---------+
          |
          v
+-------------------+
|   Gemini API      |
|  Natural Language |
|    Processing     |
+---------+---------+
          |
          v
+-------------------+
| SQL Generator     |
| Query Analyzer    |
| ETL Validator     |
+---------+---------+
          |
          v
+-------------------+
| SQL Server        |
| Data Warehouse    |
+-------------------+
```

---

## Tech Stack

* Python
* Streamlit
* Gemini API
* SQL Server
* PyODBC
* Pandas
* LangChain (Optional)

---

## Project Structure

```
AI-DataWarehouse-Assistant/
│
├── app.py
├── config.py
├── requirements.txt
│
├── database/
│   ├── connection.py
│   └── schema_loader.py
│
├── services/
│   ├── sql_generator.py
│   ├── sql_explainer.py
│   ├── etl_validator.py
│   ├── documentation_generator.py
│   └── schema_analyzer.py
│
├── prompts/
│   ├── sql_prompt.py
│   ├── explain_prompt.py
│   └── validation_prompt.py
│
├── docs/
│   └── screenshots
│
└── README.md
```

---

## Installation

### Clone Repository

```bash
git clone https://github.com/yourusername/AI-DataWarehouse-Assistant.git

cd AI-DataWarehouse-Assistant
```

### Create Virtual Environment

```bash
python -m venv venv
```

Activate:

```bash
source venv/bin/activate
```

Windows:

```bash
venv\Scripts\activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Environment Variables

Create a `.env` file:

```env
GEMINI_API_KEY=your_api_key

DB_SERVER=localhost
DB_DATABASE=DataWarehouse
DB_USERNAME=sa
DB_PASSWORD=your_password
```

---

## Run Application

```bash
streamlit run app.py
```

Application will be available at:

```text
http://localhost:8501
```

---

## Sample Use Cases

### Generate SQL

Input:

```text
Show top 10 customers by revenue.
```

### Explain SQL

Input:

```sql
SELECT customer_id,
       SUM(sales_amount)
FROM fact_sales
GROUP BY customer_id;
```

### Validate ETL

Input:

```sql
INSERT INTO silver.customer
SELECT *
FROM bronze.customer;
```

Output:

```text
Potential Issues:
- Avoid SELECT *
- Explicit column mapping recommended
- Add data quality checks
```

---

## Future Enhancements

* Query execution plans analysis
* Role-based authentication
* Multi-database support
* Snowflake integration
* Azure Synapse integration
* PostgreSQL support
* Export documentation to PDF
* Dashboard analytics
* AI-powered data lineage generation

---

## Skills Demonstrated

* Data Warehousing
* SQL Server
* ETL Development
* Python Development
* Generative AI
* Prompt Engineering
* System Design
* Database Optimization
* Documentation Automation

---

## Resume Highlight

Built an AI-powered Data Warehouse Assistant using Python, Streamlit, Gemini API, and SQL Server that generated SQL queries from natural language, validated ETL pipelines, explained stored procedures, and automated data warehouse documentation.


## 🎯 MVP Sprint Roadmap

This project is being developed incrementally using sprint-based milestones. The goal is to build an AI-powered assistant that helps data engineers interact with a SQL Server Data Warehouse using natural language, automate documentation, and improve ETL development workflows.

* [x] **Sprint 1: Foundation** ~~Completed~~

  * Create GitHub Repository
  * Design Project Architecture
  * Create README Documentation
  * Configure Gemini API
  * Setup SQL Server Connection
  * Create Database Connector
  * Build Streamlit Interface

* [ ] **Sprint 2: Core AI Features**

  * Natural Language to SQL Generation
  * SQL Execution Engine
  * Query Results Viewer
  * SQL Explanation Module

* [ ] **Sprint 3: Data Warehouse Intelligence**

  * Schema Discovery
  * Table Relationship Mapping
  * Data Dictionary Generation
  * Automated Documentation

* [ ] **Sprint 4: ETL Assistant**

  * ETL Validation
  * Data Quality Checks
  * Naming Convention Analysis
  * Performance Recommendations

