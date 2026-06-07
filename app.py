"""
app.py
------
AI Data Warehouse Assistant — Main Streamlit Application

Features:
  • Natural Language → SQL  (Sprint 2)
  • SQL Explainer           (Sprint 2)
  • Schema Explorer         (Sprint 3)
  • Data Dictionary         (Sprint 3)
  • ETL Validator           (Sprint 4)
  • ETL Documentor          (Sprint 4)
"""

import streamlit as st
import pandas as pd
import time

from config import DEMO_MODE, GEMINI_API_KEY, DB_SERVER, DB_DATABASE
from database.connection import test_connection
from database.schema_loader import load_schema_df, load_schema_text

# ── Services ──────────────────────────────────────────────────────────────────
from services.sql_generator import generate_sql
from services.sql_explainer import explain_sql
from services.schema_analyzer import analyze_schema, get_table_description
from services.documentation_generator import generate_data_dictionary, generate_etl_docs
from services.etl_validator import validate_etl


# ─────────────────────────────────────────────────────────────────────────────
# Page Config
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Data Warehouse Assistant",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ─────────────────────────────────────────────────────────────────────────────
# Custom CSS — Premium dark theme
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* Base */
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    /* App background */
    .stApp { background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%); }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: rgba(15, 12, 41, 0.95) !important;
        border-right: 1px solid rgba(255,255,255,0.08);
    }
    [data-testid="stSidebar"],
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] li,
    [data-testid="stSidebar"] div,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] small {
        color: #e2e8f0 !important;
    }
    /* Sidebar inline code pills (backtick text) */
    [data-testid="stSidebar"] code {
        background: rgba(139, 92, 246, 0.18) !important;
        color: #c4b5fd !important;
        -webkit-text-fill-color: #c4b5fd !important;
        border: 1px solid rgba(139, 92, 246, 0.3) !important;
        border-radius: 6px !important;
        padding: 1px 6px !important;
        font-size: 0.82rem !important;
        font-family: 'Courier New', monospace !important;
    }

    /* Cards */
    .feature-card {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }
    .feature-card:hover {
        border-color: rgba(139, 92, 246, 0.5);
        box-shadow: 0 8px 32px rgba(139, 92, 246, 0.15);
        transform: translateY(-2px);
    }

    /* Hero banner */
    .hero-banner {
        background: linear-gradient(135deg, rgba(139, 92, 246, 0.3) 0%, rgba(59, 130, 246, 0.3) 100%);
        border: 1px solid rgba(139, 92, 246, 0.3);
        border-radius: 20px;
        padding: 2rem;
        text-align: center;
        margin-bottom: 2rem;
    }
    .hero-banner h1 {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #a78bfa, #60a5fa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    .hero-banner p {
        color: #cbd5e1 !important;
        -webkit-text-fill-color: #cbd5e1 !important;
        font-size: 1.1rem;
        margin-top: 0.5rem;
    }

    /* Status badges */
    .badge-success {
        background: rgba(34,197,94,0.2);
        color: #4ade80;
        border: 1px solid rgba(34,197,94,0.3);
        border-radius: 999px;
        padding: 0.25rem 0.75rem;
        font-size: 0.8rem;
        font-weight: 500;
    }
    .badge-demo {
        background: rgba(251,191,36,0.2);
        color: #fbbf24;
        border: 1px solid rgba(251,191,36,0.3);
        border-radius: 999px;
        padding: 0.25rem 0.75rem;
        font-size: 0.8rem;
        font-weight: 500;
    }

    /* SQL code blocks */
    .sql-output {
        background: rgba(0,0,0,0.4);
        border: 1px solid rgba(139, 92, 246, 0.3);
        border-radius: 12px;
        padding: 1rem;
        font-family: 'Courier New', monospace;
        color: #a78bfa;
        white-space: pre-wrap;
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #7c3aed, #3b82f6) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.6rem 2rem !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        transition: all 0.3s ease !important;
        width: 100%;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 24px rgba(124, 58, 237, 0.4) !important;
    }

    /* Input fields — target Streamlit's BaseWeb internals */
    .stTextArea textarea,
    .stTextInput input,
    [data-baseweb="textarea"],
    [data-baseweb="base-input"],
    [data-baseweb="base-input"] input,
    [data-baseweb="base-input"] textarea {
        background: rgba(255,255,255,0.06) !important;
        border: 1px solid rgba(255,255,255,0.12) !important;
        border-radius: 10px !important;
        color: #e2e8f0 !important;
        caret-color: #a78bfa !important;
        -webkit-text-fill-color: #e2e8f0 !important;
    }
    .stTextArea textarea:focus,
    .stTextInput input:focus,
    [data-baseweb="base-input"]:focus-within,
    [data-baseweb="textarea"]:focus-within {
        border-color: rgba(139, 92, 246, 0.6) !important;
        box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.15) !important;
    }
    /* Placeholder text */
    .stTextArea textarea::placeholder,
    .stTextInput input::placeholder,
    [data-baseweb="base-input"] input::placeholder,
    [data-baseweb="base-input"] textarea::placeholder {
        color: rgba(148, 163, 184, 0.55) !important;
        -webkit-text-fill-color: rgba(148, 163, 184, 0.55) !important;
    }

    /* Selectbox / Dropdown */
    .stSelectbox [data-baseweb="select"],
    .stSelectbox [data-baseweb="select"] > div,
    [data-baseweb="select"] input {
        background: rgba(255,255,255,0.06) !important;
        color: #e2e8f0 !important;
        -webkit-text-fill-color: #e2e8f0 !important;
        border-color: rgba(255,255,255,0.12) !important;
    }
    [data-baseweb="popover"],
    [data-baseweb="menu"] {
        background: #1e1b4b !important;
        border: 1px solid rgba(139,92,246,0.3) !important;
    }
    [data-baseweb="option"] {
        color: #e2e8f0 !important;
        background: transparent !important;
    }
    [data-baseweb="option"]:hover {
        background: rgba(139,92,246,0.2) !important;
    }

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(255,255,255,0.03);
        border-radius: 12px;
        padding: 4px;
        gap: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        color: #94a3b8;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(124,58,237,0.4), rgba(59,130,246,0.4)) !important;
        color: #e2e8f0 !important;
    }

    /* Dividers */
    hr { border-color: rgba(255,255,255,0.08); }

    /* ── Spinner / AI Processing indicator ──────────────────────────── */
    /* Streamlit spinner overlay */
    [data-testid="stSpinner"] {
        background: rgba(15, 12, 41, 0.85) !important;
        border: 1px solid rgba(139, 92, 246, 0.4) !important;
        border-radius: 14px !important;
        padding: 1.2rem 1.8rem !important;
        backdrop-filter: blur(8px) !important;
    }
    /* Spinner text */
    [data-testid="stSpinner"] p,
    [data-testid="stSpinner"] span,
    .stSpinner p {
        color: #c4b5fd !important;
        -webkit-text-fill-color: #c4b5fd !important;
        font-size: 1rem !important;
        font-weight: 500 !important;
    }
    /* Spinner SVG/circle animation */
    [data-testid="stSpinner"] svg {
        stroke: #a78bfa !important;
        color: #a78bfa !important;
    }
    /* Pulse animation for AI processing banner */
    @keyframes ai-pulse {
        0%, 100% { opacity: 1; box-shadow: 0 0 0 0 rgba(139,92,246,0.4); }
        50%       { opacity: 0.85; box-shadow: 0 0 0 8px rgba(139,92,246,0); }
    }
    .ai-processing {
        background: linear-gradient(135deg, rgba(124,58,237,0.25), rgba(59,130,246,0.25));
        border: 1px solid rgba(139, 92, 246, 0.5);
        border-radius: 12px;
        padding: 0.9rem 1.4rem;
        color: #c4b5fd !important;
        -webkit-text-fill-color: #c4b5fd !important;
        font-weight: 500;
        font-size: 0.95rem;
        animation: ai-pulse 1.6s ease-in-out infinite;
        text-align: center;
        margin-bottom: 1rem;
    }

    /* Metric cards */
    [data-testid="metric-container"] {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 12px;
        padding: 1rem;
    }
    /* Metric value and label visibility */
    [data-testid="metric-container"] [data-testid="stMetricValue"],
    [data-testid="metric-container"] [data-testid="stMetricValue"] > div,
    [data-testid="stMetricValue"] {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        font-size: 1.8rem !important;
        font-weight: 700 !important;
    }
    [data-testid="metric-container"] [data-testid="stMetricLabel"],
    [data-testid="stMetricLabel"] > div,
    [data-testid="stMetricLabel"] p {
        color: #94a3b8 !important;
        -webkit-text-fill-color: #94a3b8 !important;
        font-size: 0.85rem !important;
        font-weight: 500 !important;
    }
    [data-testid="stMetricDelta"] {
        color: #4ade80 !important;
        -webkit-text-fill-color: #4ade80 !important;
    }

    /* General markdown text in main content */
    .stMarkdown p, .stMarkdown li, .stMarkdown span {
        color: #e2e8f0 !important;
    }
    /* Inline code in main content — use purple pill style */
    .stMarkdown code:not(.stCode code) {
        background: rgba(139, 92, 246, 0.15) !important;
        color: #c4b5fd !important;
        -webkit-text-fill-color: #c4b5fd !important;
        border: 1px solid rgba(139, 92, 246, 0.25) !important;
        border-radius: 5px !important;
        padding: 1px 6px !important;
        font-size: 0.85em !important;
    }

    /* Tab label text */
    .stTabs [data-baseweb="tab"] p,
    .stTabs [data-baseweb="tab"] span {
        color: #94a3b8 !important;
        -webkit-text-fill-color: #94a3b8 !important;
    }
    .stTabs [aria-selected="true"] p,
    .stTabs [aria-selected="true"] span {
        color: #e2e8f0 !important;
        -webkit-text-fill-color: #e2e8f0 !important;
    }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def cached_schema_text():
    return load_schema_text()

@st.cache_data(ttl=300)
def cached_schema_df():
    return load_schema_df()

def check_api_key() -> bool:
    if not GEMINI_API_KEY or GEMINI_API_KEY == "your_gemini_api_key_here":
        st.error("⚠️ **Gemini API Key not set.** Add `GEMINI_API_KEY=your_key` to your `.env` file.")
        st.markdown("👉 Get a free API key at [aistudio.google.com](https://aistudio.google.com)")
        return False
    return True

def spinner_generate(fn, *args, label="🤖 Asking AI..."):
    """Run an AI function with a visible spinner + pulsing banner and timer."""
    start = time.time()
    # Show a styled pulsing banner so the processing state is always visible
    # on the dark theme (native spinner may be hard to see without styling).
    banner = st.empty()
    banner.markdown(
        f'<div class="ai-processing">⚡ {label}</div>',
        unsafe_allow_html=True,
    )
    with st.spinner(label):
        result = fn(*args)
    banner.empty()          # remove banner once done
    elapsed = time.time() - start
    return result, elapsed


# ─────────────────────────────────────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏭 DW Assistant")
    st.markdown("---")

    # Connection status
    ok, msg = test_connection()
    if DEMO_MODE:
        st.markdown('<span class="badge-demo">🎭 Demo Mode</span>', unsafe_allow_html=True)
    else:
        if ok:
            st.markdown('<span class="badge-success">🟢 DB Connected</span>', unsafe_allow_html=True)
        else:
            st.error(msg)

    st.markdown(f"**Database:** `{DB_DATABASE}`" if not DEMO_MODE else "**Database:** `Demo DW`")
    st.markdown("---")

    # Schema quick view
    st.markdown("### 📊 Schema Tables")
    schema_df = cached_schema_df()
    tables = sorted(schema_df["TABLE_NAME"].unique())
    for t in tables:
        col_count = len(schema_df[schema_df["TABLE_NAME"] == t])
        st.markdown(f"• `{t}` — {col_count} cols")

    st.markdown("---")
    st.markdown("**Model:** `gemini-1.5-flash`")
    st.markdown("**Made with** ❤️ Streamlit + Gemini")


# ─────────────────────────────────────────────────────────────────────────────
# Hero Banner
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-banner">
    <h1>🏭 AI Data Warehouse Assistant</h1>
    <p>Natural Language → SQL &nbsp;|&nbsp; ETL Validation &nbsp;|&nbsp; Auto Documentation &nbsp;|&nbsp; Schema Intelligence</p>
</div>
""", unsafe_allow_html=True)

# Quick stats row
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("📋 Tables", len(tables))
with col2:
    st.metric("📐 Columns", len(schema_df))
with col3:
    st.metric("⚡ AI Model", "Gemini 1.5")
with col4:
    st.metric("🎭 Mode", "Demo" if DEMO_MODE else "Live")

st.markdown("---")


# ─────────────────────────────────────────────────────────────────────────────
# Main Tabs
# ─────────────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "💬 SQL Generator",
    "🔍 SQL Explainer",
    "🗺️ Schema Explorer",
    "📖 Data Dictionary",
    "✅ ETL Validator",
    "📝 ETL Docs",
])


# ── TAB 1: SQL Generator ──────────────────────────────────────────────────────
with tab1:
    st.markdown("### 💬 Natural Language → SQL")
    st.markdown("Ask a business question and get a production-ready T-SQL query instantly.")

    # Example questions
    st.markdown("**💡 Try one of these:**")
    examples = [
        "Show total sales by month for the current year",
        "Top 10 customers by revenue",
        "Sales by product category with year-over-year growth",
        "Average order value by country",
        "Which products had declining sales last quarter?",
    ]
    ex_cols = st.columns(3)
    for i, ex in enumerate(examples[:3]):
        with ex_cols[i]:
            if st.button(ex, key=f"ex_{i}"):
                st.session_state["nl_question"] = ex

    question = st.text_area(
        "Your business question",
        value=st.session_state.get("nl_question", ""),
        placeholder="e.g. Show total sales by month for the current year",
        height=100,
        key="nl_question_input",
    )

    if st.button("⚡ Generate SQL", key="gen_sql_btn"):
        if not check_api_key():
            st.stop()
        if not question.strip():
            st.warning("Please enter a question.")
        else:
            schema = cached_schema_text()
            sql, elapsed = spinner_generate(generate_sql, schema, question)

            st.success(f"✅ Generated in {elapsed:.1f}s")
            st.markdown("**Generated Query:**")
            st.code(sql, language="sql")

            # Store for explainer
            st.session_state["last_sql"] = sql

            # Run query if live DB
            if not DEMO_MODE:
                from database.connection import get_connection
                try:
                    conn = get_connection()
                    df_result = pd.read_sql(sql, conn)
                    st.markdown(f"**Results** ({len(df_result)} rows):")
                    st.dataframe(df_result, width='stretch')
                except Exception as e:
                    st.warning(f"Query generated but execution failed: {e}")
            else:
                st.info("🎭 Demo Mode: Connect a real SQL Server to execute queries and see results.")

            # Quick action: explain the generated SQL
            if st.button("🔍 Explain this SQL", key="explain_from_gen"):
                explanation, _ = spinner_generate(explain_sql, sql, label="📖 Explaining...")
                st.markdown("**Explanation:**")
                st.markdown(explanation)


# ── TAB 2: SQL Explainer ─────────────────────────────────────────────────────
with tab2:
    st.markdown("### 🔍 SQL Query Explainer")
    st.markdown("Paste any SQL query to get a plain-English, clause-by-clause explanation.")

    default_sql = st.session_state.get("last_sql", """SELECT
    c.country,
    p.category,
    SUM(s.sales_amount) AS total_sales,
    COUNT(DISTINCT s.customer_id) AS unique_customers
FROM fact_sales s
JOIN dim_customer c ON s.customer_id = c.customer_id
JOIN dim_product  p ON s.product_id  = p.product_id
GROUP BY c.country, p.category
ORDER BY total_sales DESC;""")

    sql_input = st.text_area(
        "SQL Query to explain",
        value=default_sql,
        height=200,
        key="explain_sql_input",
    )

    if st.button("📖 Explain Query", key="explain_btn"):
        if not check_api_key():
            st.stop()
        if not sql_input.strip():
            st.warning("Please enter a SQL query.")
        else:
            explanation, elapsed = spinner_generate(explain_sql, sql_input, label="📖 Generating explanation...")
            st.success(f"✅ Done in {elapsed:.1f}s")
            st.markdown("---")
            st.markdown(explanation)


# ── TAB 3: Schema Explorer ───────────────────────────────────────────────────
with tab3:
    st.markdown("### 🗺️ Schema Explorer")

    sub1, sub2 = st.tabs(["📋 Schema Table", "🤖 AI Analysis"])

    with sub1:
        st.markdown("**Full Schema — All Tables & Columns**")
        schema_df_view = cached_schema_df()
        st.dataframe(schema_df_view, width='stretch', height=500)

        # Per-table drill-down
        st.markdown("---")
        st.markdown("**🔎 Drill into a specific table**")
        selected_table = st.selectbox("Select a table", tables, key="schema_table_select")
        filtered = schema_df_view[schema_df_view["TABLE_NAME"] == selected_table]
        st.dataframe(filtered.reset_index(drop=True), width='stretch')

    with sub2:
        st.markdown("**AI-powered schema analysis — understand your data warehouse architecture**")
        col_full, col_table = st.columns(2)

        with col_full:
            if st.button("🏗️ Analyze Full Schema", key="analyze_schema_btn"):
                if not check_api_key():
                    st.stop()
                schema = cached_schema_text()
                analysis, elapsed = spinner_generate(analyze_schema, schema, label="🤖 Analyzing schema...")
                st.success(f"✅ Done in {elapsed:.1f}s")
                st.markdown(analysis)

        with col_table:
            table_for_desc = st.selectbox("Select table for AI description", tables, key="desc_table_select")
            if st.button("📄 Describe This Table", key="desc_table_btn"):
                if not check_api_key():
                    st.stop()
                schema = cached_schema_text()
                desc, elapsed = spinner_generate(
                    get_table_description, schema, table_for_desc,
                    label=f"🤖 Describing {table_for_desc}..."
                )
                st.success(f"✅ Done in {elapsed:.1f}s")
                st.markdown(desc)


# ── TAB 4: Data Dictionary ───────────────────────────────────────────────────
with tab4:
    st.markdown("### 📖 Auto-Generated Data Dictionary")
    st.markdown(
        "Click below to generate a complete, AI-written data dictionary "
        "for your entire data warehouse schema."
    )

    st.info(
        "⏱️ This may take 20–40 seconds as it documents every table and column. "
        "You can copy the output and save it as `docs/data_dictionary.md`."
    )

    if st.button("📖 Generate Full Data Dictionary", key="gen_dict_btn"):
        if not check_api_key():
            st.stop()
        schema = cached_schema_text()
        dictionary, elapsed = spinner_generate(
            generate_data_dictionary, schema, label="📖 Building data dictionary..."
        )
        st.success(f"✅ Generated in {elapsed:.1f}s")
        st.markdown("---")
        st.markdown(dictionary)

        # Download button
        st.download_button(
            label="⬇️ Download as Markdown",
            data=dictionary,
            file_name="data_dictionary.md",
            mime="text/markdown",
        )


# ── TAB 5: ETL Validator ─────────────────────────────────────────────────────
with tab5:
    st.markdown("### ✅ ETL Script Validator")
    st.markdown("Paste your ETL script or stored procedure — AI will audit it for issues.")

    demo_etl = """-- Example ETL: Bronze → Silver Customer load
INSERT INTO silver.customer
SELECT *
FROM bronze.customer
WHERE created_date > '2024-01-01'"""

    etl_script = st.text_area(
        "ETL Script / Stored Procedure",
        value=demo_etl,
        height=250,
        key="etl_validate_input",
        placeholder="Paste your T-SQL ETL script here...",
    )

    severity_filter = st.multiselect(
        "Filter by severity",
        ["🔴 Critical", "🟠 High", "🟡 Medium", "🟢 Low"],
        default=["🔴 Critical", "🟠 High", "🟡 Medium", "🟢 Low"],
    )

    if st.button("🔍 Validate ETL Script", key="validate_etl_btn"):
        if not check_api_key():
            st.stop()
        if not etl_script.strip():
            st.warning("Please paste an ETL script.")
        else:
            findings, elapsed = spinner_generate(validate_etl, etl_script, label="🔍 Auditing ETL script...")
            st.success(f"✅ Audit complete in {elapsed:.1f}s")
            st.markdown("---")
            st.markdown("### 📋 Audit Findings")
            st.markdown(findings)


# ── TAB 6: ETL Docs ──────────────────────────────────────────────────────────
with tab6:
    st.markdown("### 📝 ETL Documentation Generator")
    st.markdown("Automatically generate technical documentation for any ETL script or stored procedure.")

    etl_for_docs = st.text_area(
        "ETL Script / Stored Procedure to Document",
        height=250,
        key="etl_docs_input",
        placeholder="Paste your T-SQL ETL script or stored procedure here...",
    )

    if st.button("📝 Generate Documentation", key="gen_etl_docs_btn"):
        if not check_api_key():
            st.stop()
        if not etl_for_docs.strip():
            st.warning("Please paste an ETL script.")
        else:
            docs, elapsed = spinner_generate(
                generate_etl_docs, etl_for_docs, label="📝 Generating documentation..."
            )
            st.success(f"✅ Generated in {elapsed:.1f}s")
            st.markdown("---")
            st.markdown(docs)

            st.download_button(
                label="⬇️ Download as Markdown",
                data=docs,
                file_name="etl_documentation.md",
                mime="text/markdown",
            )
