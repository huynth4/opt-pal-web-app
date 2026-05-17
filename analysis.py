"""Before/after look at the employer data using helpers.clean_employers.

Run: uv run python analysis.py
"""

from helpers import load_raw, clean_employers


def main() -> None:
    raw = load_raw()
    print("RAW shape:", raw.shape)
    print("RAW missing per column:")
    print(raw.isna().sum()[raw.isna().sum() > 0])
    print()

    clean = clean_employers(raw)
    print("CLEAN shape:", clean.shape)
    print("CLEAN dtypes:")
    print(clean.dtypes)
    print()
    print("CLEAN missing per column:")
    print(clean.isna().sum()[clean.isna().sum() > 0])
    print()
    print("First 5 clean rows:")
    print(clean.head().to_string())


if __name__ == "__main__":
    main()
