
import pandas as pd
from sqlalchemy import text

from database.db import engine, ROOT_DIR

CSV_PATH = ROOT_DIR / "data" / "sales.csv"
REJECTED_PATH = ROOT_DIR / "data" / "rejected_rows.csv"


def import_sales():
    print("Starting CSV import...")

    # 1. Load the original CSV
    df = pd.read_csv(CSV_PATH)
    print("Original rows:", len(df))

    # 2. Normalize column names
    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace(r"[^a-z0-9]+", "_", regex=True)
        .str.strip("_")
    )

    print("Columns:", df.columns.tolist())

    # 3. Validate the expected schema
    required = [
        "transaction_id",
        "order_date",
        "product",
        "category",
        "region",
        "sales_channel",
        "quantity",
        "unit_price",
        "discount_amount",
        "status",
    ]

    missing_columns = set(required) - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {sorted(missing_columns)}"
        )

    original_count = len(df)

    # 4. Clean text fields without deleting records
    text_columns = [
        "transaction_id",
        "product",
        "category",
        "region",
        "sales_channel",
        "status",
    ]

    for col in text_columns:
        df[col] = df[col].astype("string").str.strip()

    # 5. Convert dates and numeric fields
    df["order_date"] = pd.to_datetime(
        df["order_date"],
        format="%d-%m-%Y",
        errors="coerce",
    )

    numeric_columns = [
        "quantity",
        "unit_price",
        "discount_amount",
    ]

    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # 6. Flag data-quality issues
    df["missing_price"] = df["unit_price"].isna()

    df["invalid_date"] = df["order_date"].isna()

    df["invalid_numeric"] = (
        df["quantity"].isna()
        | df["unit_price"].lt(0)
        | df["discount_amount"].isna()
        | df["quantity"].lt(0)
        | df["discount_amount"].lt(0)
    )

    df["missing_required_text"] = (
        df[text_columns].isna().any(axis=1)
        | df["transaction_id"].eq("").fillna(True)
        | df["product"].eq("").fillna(True)
        | df["category"].eq("").fillna(True)
        | df["region"].eq("").fillna(True)
        | df["sales_channel"].eq("").fillna(True)
        | df["status"].eq("").fillna(True)
    )

    # Flag duplicate transaction IDs; preserve all rows
    has_transaction_id = (
        df["transaction_id"].notna()
        & df["transaction_id"].ne("").fillna(False)
    )

    df["duplicate_transaction_id"] = False

    df.loc[
        has_transaction_id,
        "duplicate_transaction_id",
    ] = (
        df.loc[
            has_transaction_id,
            "transaction_id",
        ].duplicated(keep=False)
    )

    # 7. Create a combined quality flag
    quality_columns = [
        "missing_price",
        "invalid_date",
        "invalid_numeric",
        "missing_required_text",
        "duplicate_transaction_id",
    ]

    df["data_quality_issue"] = df[quality_columns].any(axis=1)

    # Preserve every flagged row in a separate review file
    flagged = df.loc[df["data_quality_issue"]].copy()

    # Convert dates to ISO format for SQLite
    df["order_date"] = df["order_date"].apply(
        lambda value: (
            value.strftime("%Y-%m-%d")
            if pd.notna(value)
            else None
        )
    )

    flagged["order_date"] = flagged["order_date"].apply(
        lambda value: (
            value.strftime("%Y-%m-%d")
            if pd.notna(value)
            else None
        )
    )

    # 8. Save records needing review
    flagged.to_csv(REJECTED_PATH, index=False)

    # 9. Import ALL transactions into SQLite
    # This is a full refresh, not an incremental import.
    with engine.begin() as conn:
        conn.execute(text("DROP TABLE IF EXISTS sales"))

        df.to_sql(
            "sales",
            con=conn,
            if_exists="replace",
            index=False,
        )

    # 10. Verify the import
    with engine.connect() as conn:
        imported_count = conn.execute(
            text("SELECT COUNT(*) FROM sales")
        ).scalar_one()

    print("\nImport completed successfully!")
    print("Original rows:", original_count)
    print("Imported rows:", imported_count)
    print("Rows flagged for review:", len(flagged))
    print("Missing prices:", int(df["missing_price"].sum()))
    print("Invalid dates:", int(df["invalid_date"].sum()))
    print("Duplicate transaction rows:",
          int(df["duplicate_transaction_id"].sum()))
    print("Review file:", REJECTED_PATH)
    print("Database:", engine.url.database)

    if imported_count != original_count:
        raise RuntimeError(
            "Import verification failed: row counts do not match."
        )


if __name__ == "__main__":
    import_sales()
