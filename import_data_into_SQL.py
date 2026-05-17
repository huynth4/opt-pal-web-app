"""Load cleaned employer data into SQLite.

Run from the project root:
    uv run python import_data_into_SQL.py
"""

import sqlite3
from pathlib import Path
from helpers import load_clean

# None means load the full cleaned dataset.
# Set this to a small number like 500 while testing.
MAX_ROWS = None

# Database path setup.
PROJECT_ROOT = Path(__file__).resolve().parent
INSTANCE_DIR = PROJECT_ROOT / "instance"
DB_PATH = INSTANCE_DIR / "opt_pal.db"


def main() -> None:
    # Step 1: make sure the instance/ folder exists.
    INSTANCE_DIR.mkdir(parents=True, exist_ok=True)

    # Step 2: get the cleaned DataFrame from helpers.py.
    df = load_clean()

    # Step 3: optionally load only a small subset for faster testing.
    if MAX_ROWS is not None:
        df = df.head(MAX_ROWS)

    # Step 4: open the SQLite database connection.
    conn = sqlite3.connect(DB_PATH)

    try:
        # Step 5: write the DataFrame into a table called "employers".
        # if_exists="replace" means: delete the old table and rebuild it.
        # index=False means: do not save the pandas row numbers as a column.
        df.to_sql("employers", conn, if_exists="replace", index=False)
        conn.commit()
    finally:
        # Step 6: always close the database connection.
        conn.close()

    print(f"Loaded {len(df)} cleaned rows into SQLite table 'employers'.")
    print(f"Database file: {DB_PATH}")


if __name__ == "__main__":
    main()
