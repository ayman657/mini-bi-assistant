
import sqlglot
from sqlglot import exp


def validate_sql(sql: str) -> str:
    try:
        statements = sqlglot.parse(sql, read="sqlite")
    except Exception as exc:
        raise ValueError(f"Invalid SQL syntax: {exc}") from exc

    if len(statements) != 1 or statements[0] is None:
        raise ValueError("Only one SQL statement is allowed.")

    tree = statements[0]

    if not isinstance(tree, exp.Query):
        raise ValueError("Only SELECT queries are allowed.")

    if tree.find(exp.Into):
        raise ValueError("SELECT INTO is not allowed.")

    tables = list(tree.find_all(exp.Table))

    if not tables:
        raise ValueError("Query must reference the sales table.")

    for table in tables:
        if table.name.lower() != "sales":
            raise ValueError(f"Table '{table.name}' is not allowed.")

    return sql
