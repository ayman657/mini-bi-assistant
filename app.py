
import requests
import streamlit as st
import pandas as pd

API_URL = "http://127.0.0.1:8000/api/ask"

# ---------- Page configuration ----------
st.set_page_config(
    page_title="Sales Assistant",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------- Custom styling ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

.stApp {
    background: #f7f8fc;
    font-family: 'Inter', sans-serif;
    color: #202a3b;
}

.block-container {
    max-width: 1050px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

header[data-testid="stHeader"] {
    background: transparent;
}

h1, h2, h3 {
    color: #182338 !important;
    letter-spacing: -0.5px;
}

p, label {
    color: #657188;
}

.intro {
    padding: 28px 30px;
    background: white;
    border: 1px solid #e6eaf1;
    border-radius: 20px;
    margin-bottom: 25px;
}

.intro-tag {
    color: #5369e8;
    font-weight: 700;
    font-size: 12px;
    letter-spacing: 1.5px;
    text-transform: uppercase;
}

.intro-title {
    font-size: clamp(28px, 4vw, 38px);
    font-weight: 700;
    line-height: 1.25;
    color: #182338;
    margin: 10px 0;
}

.intro-description {
    font-size: 15px;
    line-height: 1.7;
    color: #68758b;
    max-width: 650px;
}

div[data-testid="stVerticalBlockBorderWrapper"] {
    background: white;
    border: 1px solid #e6eaf1 !important;
    border-radius: 16px !important;
}

div.stButton > button {
    min-height: 44px;
    border-radius: 11px;
    border: 1px solid #e1e6ef;
    background: white;
    color: #35435c;
    font-weight: 500;
    transition: all 0.18s ease;
}

div.stButton > button:hover {
    border-color: #aab5ff;
    background: #f1f3ff;
    color: #4659d5;
    transform: translateY(-1px);
}

div.stButton > button[kind="primary"] {
    background: #dcefe7;
    color: #245b48;
    border: 1px solid #c6e3d7;
    font-weight: 600;
    transition: all 0.2s ease;
}

div.stButton > button[kind="primary"]:hover {
    background: #c8e5d8;
    color: #194b3a;
    border-color: #a9d5c3;
    transform: translateY(-1px);
}
.stTextArea textarea {
    background: white !important;
    border: 1px solid #dce2ed !important;
    border-radius: 12px !important;
    color: #202a3b !important;
    font-size: 15px !important;
    padding: 14px !important;
}

.stTextArea textarea:focus {
    border-color: #7586f3 !important;
    box-shadow: 0 0 0 2px #e8ebff !important;
}

div[data-testid="stMetric"] {
    background: #f8f9ff;
    border: 1px solid #e7eaff;
    border-radius: 13px;
    padding: 16px;
}

div[data-testid="stMetricLabel"] {
    color: #68758b;
}

div[data-testid="stMetricValue"] {
    color: #465bd7;
}

[data-testid="stDataFrame"] {
    border: 1px solid #e6eaf1;
    border-radius: 12px;
    overflow: hidden;
}

hr {
    border-color: #e6eaf1 !important;
}

.footer {
    text-align: center;
    color: #98a1b2;
    font-size: 12px;
    padding-top: 25px;
}
</style>
""", unsafe_allow_html=True)


# ---------- Header ----------
st.markdown("""
<div class="intro">
    <div class="intro-tag">Sales analytics</div>
    <div class="intro-title">Ask your sales data anything.</div>
    <div class="intro-description">
        Explore revenue, products, regions and monthly trends
        using simple questions. Every result comes from your sales database.
    </div>
</div>
""", unsafe_allow_html=True)


# ---------- Suggested questions ----------
st.subheader("Try asking")

examples = [
    ("💰", "Total revenue", "What is the total revenue?"),
    ("🏆", "Top product", "Which product generated the highest revenue?"),
    ("📈", "Monthly trend", "What is the monthly revenue trend?"),
    ("🌍", "Best region", "Which region generated the highest sales?"),
    (
        "🔄",
        "Compare months",
        "How did revenue change between March and April 2026?",
    ),
]

if "question" not in st.session_state:
    st.session_state.question = ""

for start in range(0, len(examples), 3):
    cols = st.columns(3)

    for j, (emoji, title, prompt) in enumerate(
        examples[start:start + 3]
    ):
        with cols[j]:
            if st.button(
                f"{emoji}  {title}",
                key=f"sample_{start}_{j}",
                use_container_width=True,
            ):
                st.session_state.question = prompt


# ---------- Question input ----------
st.markdown("")

with st.container(border=True):
    st.subheader("Your question")

    question = st.text_area(
        "Ask a question about your sales",
        key="question",
        placeholder="For example, which region had the highest revenue?",
        height=100,
        label_visibility="collapsed",
    )

    col1, col2 = st.columns([1, 4])

    with col1:
        analyze = st.button(
            "Analyze →",
            type="primary",
            use_container_width=True,
        )

    with col2:
        st.caption(
            "Results are calculated from your database, not invented by AI."
        )


# ---------- Process the question ----------
if analyze:
    if not question.strip():
        st.warning("Please enter a question first.")

    else:
        try:
            with st.spinner("Working on your answer..."):
                response = requests.post(
                    API_URL,
                    json={"question": question.strip()},
                    timeout=90,
                )

            if response.ok:
                result = response.json()
                rows = result.get("rows", [])
                columns = result.get("columns", [])

                st.markdown("---")
                st.subheader("Your results")
                st.caption(result.get("question", question))

                # Summary metrics
                metric1, metric2 = st.columns(2)

                metric1.metric(
                    "Rows returned",
                    result.get("row_count", len(rows)),
                )

                metric2.metric(
                    "Columns",
                    len(columns),
                )

                if rows:
                    df = pd.DataFrame(rows, columns=columns)

                    st.markdown("### Supporting data")

                    st.dataframe(
                        df,
                        use_container_width=True,
                        hide_index=True,
                    )

                    # Create a chart only when suitable columns exist.
                    numeric_columns = df.select_dtypes(
                        include="number"
                    ).columns.tolist()

                    category_columns = [
                        column
                        for column in df.columns
                        if column not in numeric_columns
                    ]

                    if (
                        numeric_columns
                        and category_columns
                        and len(df) > 1
                    ):
                        with st.container(border=True):
                            st.subheader("Visual summary")

                            chart_data = df.set_index(
                                category_columns[0]
                            )[[numeric_columns[0]]]

                            st.bar_chart(chart_data)

                    # Download results
                    st.download_button(
                        label="Download results (CSV)",
                        data=df.to_csv(index=False).encode("utf-8"),
                        file_name="sales_results.csv",
                        mime="text/csv",
                    )

                else:
                    st.info(
                        "The query completed but returned no records."
                    )

                # Show generated SQL
                with st.expander("See generated SQL"):
                    st.code(
                        result.get("sql", ""),
                        language="sql",
                    )

            else:
                try:
                    error_message = response.json().get(
                        "detail",
                        response.text,
                    )
                except ValueError:
                    error_message = response.text

                st.error(
                    f"Could not complete the request: {error_message}"
                )

        except requests.exceptions.ConnectionError:
            st.error(
                "Cannot connect to the backend. Start FastAPI in another "
                "terminal using: uvicorn main:app --reload"
            )

        except requests.exceptions.Timeout:
            st.error(
                "The request took too long. The backend or AI service "
                "did not respond in time. Please try again."
            )

        except Exception as exc:
            st.error(f"Something went wrong: {exc}")


# ---------- Footer ----------
st.markdown("---")

st.markdown("""
<div class="footer">
    Built with Python · Streamlit · FastAPI · Gemini · SQLite
</div>
""", unsafe_allow_html=True)
