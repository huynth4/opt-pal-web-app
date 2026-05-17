"""Load USCIS-style employer export and print basic profile. Run: uv run python test.py"""

from pathlib import Path

import pandas as pd

DATA_PATH = Path(__file__).resolve().parent / "data" / "Employer Information.csv"


def main() -> None:
    # Tab-separated; this export is UTF-16 (common for Excel), not UTF-8.
    df = pd.read_csv(DATA_PATH, sep="\t", dtype=str, encoding="utf-16")
    df.columns = df.columns.str.strip()

    print("Shape (rows, columns):", df.shape)
    print()
    print("=== First 5 rows ===")
    print(df.head())
    print()
    print("=== Column names and dtypes ===")
    for col in df.columns:
        print(f"  {col!r}: {df[col].dtype}")
    print()
    print("=== Missing values (NaN count per column) ===")
    missing = df.isna().sum()
    print(missing[missing > 0])
    print()
    print("=== Non-null counts ===")
    print(df.notna().sum())


if __name__ == "__main__":
    main()
