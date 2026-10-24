
import os

from dotenv import load_dotenv
from google import genai
from sqlalchemy import inspect

from database.db import engine

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

if not API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is missing. Set it in your .env file."
    )

client = genai.Client(api_key=API_KEY)


def get_database_schema():
    inspector = inspect(engine)
    schema_parts = []

    for table_name in inspector.get_table_names():
        columns = inspector.get_columns(table_name)

        column_details = [
            f"{column['name']} ({column['type']})"
            for column in columns
        ]

        schema_parts.append(
            f"Table: {table_name}\nColumns: "
            + ", ".join(column_details)
        )

    return "\n\n".join(schema_parts)


def generate_sql(question: str) -> str:
    schema = get_database_schema()

    prompt = f"""
You are a Text-to-SQL assistant for a sales analytics application.

DATABASE SCHEMA:
{schema}

USER QUESTION:
{question}

RULES:
- Generate exactly one SQLite SELECT query.
- Use only tables and columns in the supplied schema.
- Never generate INSERT, UPDATE, DELETE, DROP, ALTER,
  CREATE, PRAGMA, ATTACH, or DETACH statements.
- Do not generate multiple statements.
- Do not invent columns or tables.
- Use order_date for date-based analysis.
- Treat revenue as quantity * unit_price - discount_amount.
- For revenue calculations, include only Completed transactions.
- Exclude records with missing_price = 1, invalid_numeric = 1,
  or invalid_date = 1 when calculating revenue.
- Use the actual column names from the schema.
- Return only SQL, without Markdown fences or explanations.
- If the question cannot be answered from the schema,
  return UNSUPPORTED.
"""

    response = client.interactions.create(
        model=MODEL,
        input=prompt,
    )

    sql = (response.output_text or "").strip()

    # Remove Markdown fences if the model returns them
    if sql.startswith("```"):
        lines = sql.splitlines()
        lines = [
            line for line in lines
            if not line.strip().startswith("```")
        ]
        sql = "\n".join(lines).strip()

    if sql.upper() == "UNSUPPORTED":
        raise ValueError(
            "This question cannot be answered using the sales database."
        )

    return sql
