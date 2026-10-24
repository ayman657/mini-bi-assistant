
from pathlib import Path
from sqlalchemy import create_engine

# Find the project root
ROOT_DIR = Path(__file__).resolve().parent.parent

# SQLite database file
DB_PATH = ROOT_DIR / "sales.db"

# Create the database engine
engine = create_engine(
    f"sqlite:///{DB_PATH}",
    connect_args={"timeout": 10}
)
