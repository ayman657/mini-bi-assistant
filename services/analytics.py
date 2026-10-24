
from pathlib import Path
import sqlite3

from database.db import DB_PATH
from services.sql_validator import validate_sql


def execute_query(sql: str) -> dict:
    # Validate before execution.
    safe_sql = validate_sql(sql)

    # Open SQLite in read-only mode.
    db_uri = Path(DB_PATH).resolve().as_uri() + "?mode=ro"

    with sqlite3.connect(db_uri, uri=True, timeout=5) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(safe_sql)
        columns = [item[0] for item in cursor.description or []]
        rows = [dict(row) for row in cursor.fetchmany(500)]

    return {
        "columns": columns,
        "rows": rows,
        "row_count": len(rows)
    }
