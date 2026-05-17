"""Data helpers for OPT Pal.


Keeping cleaning function here (instead of in analysis.py or app.py) means every
script that needs clean data calls the same function, so behavior stays
consistent.
"""

from pathlib import Path
import sqlite3
import pandas as pd


DATASET = (
    Path(__file__).resolve().parent / "data" / "Employer Information.csv"
)
DB_PATH = Path(__file__).resolve().parent / "instance" / "opt_pal.db"


# Long Excel headers -> short, code-friendly names we will use everywhere.
COLUMN_RENAME = {
    "Line by line": "line_number",
    "Fiscal Year": "fiscal_year",
    "Employer (Petitioner) Name": "employer_name",
    "Tax ID": "tax_id",
    "Industry (NAICS) Code": "industry",
    "Petitioner City": "city",
    "Petitioner State": "state",
    "Petitioner Zip Code": "zip_code",
    "New Employment Approval": "new_employment_approval",
    "New Employment Denial": "new_employment_denial",
    "Continuation Approval": "continuation_approval",
    "Continuation Denial": "continuation_denial",
    "Change with Same Employer Approval": "change_same_employer_approval",
    "Change with Same Employer Denial": "change_same_employer_denial",
    "New Concurrent Approval": "new_concurrent_approval",
    "New Concurrent Denial": "new_concurrent_denial",
    "Change of Employer Approval": "change_employer_approval",
    "Change of Employer Denial": "change_employer_denial",
    "Amended Approval": "amended_approval",
    "Amended Denial": "amended_denial",
}

TEXT_COLUMNS = [
    "employer_name",
    "tax_id",
    "industry",
    "city",
    "state",
    "zip_code",
]

METRIC_COLUMNS = [
    "new_employment_approval",
    "new_employment_denial",
    "continuation_approval",
    "continuation_denial",
    "change_same_employer_approval",
    "change_same_employer_denial",
    "new_concurrent_approval",
    "new_concurrent_denial",
    "change_employer_approval",
    "change_employer_denial",
    "amended_approval",
    "amended_denial",
]


def load_raw(path: Path = DATASET) -> pd.DataFrame:
    """Read the file exactly as it is on disk.

    The file is tab-separated and UTF-16 encoded (an Excel-style export),
    so default pandas arguments fail. 

    -> pd.DataFrame: a return type hint to indicate the function returns a pandas DataFrame.
    -> dtype=str: Read every column as text so numbers like ZIP 02368 keep their leading zeros 
    until we decide what type we want.
    -> path: the file location to open.
    """
    return pd.read_csv(path, sep="\t", dtype=str, encoding="utf-16")


def clean_employers(df: pd.DataFrame) -> pd.DataFrame:
    """Return a cleaned copy of the employer DataFrame.

    Steps are intentionally small and explicit so they are easy to trust:
    1. Strip header whitespace and rename to short codes.
    2. Clean text columns (NaN -> "", trim spaces, upper-case state).
    3. Drop rows with no employer name (useless for an employer filter).
    4. Convert metric columns from text to numbers (missing -> 0).
    5. Label missing industry / state / zip instead of leaving NaN,
       so filters and UI never show "nan".
    """
    # Make a copy of the original dataset so the function wouldn't directlychange the DataFrame passed in.
    df = df.copy()

    # 1) Headers sometimes have trailing spaces (e.g. "Fiscal Year   ").
    df.columns = df.columns.str.strip()

    #set(): returns a list of unique elements.
    #set(COLUMN_RENAME): Python uses the dictionary keys by default. 
    #Otherwise, use: set(COLUMN_RENAME.values())
    #Remove set of columns in DF from orginal set of columns.
    missing_headers = set(COLUMN_RENAME) - set(df.columns)
    #if the set has any elements, raise an error.
    if missing_headers:
        raise ValueError(f"CSV is missing expected columns: {missing_headers}")

    df = df.rename(columns=COLUMN_RENAME)

    # 2) Normalize text columns.
    for col in TEXT_COLUMNS:
        df[col] = df[col].fillna("").astype(str).str.strip()
        #.fillna(""): Python marks empty cells as NaN. We replace them with "" - an empty string.
        #astype(str): Convert every column to a string.

    df["state"] = df["state"].str.upper()
    df["city"] = df["city"].str.upper()

    # 3) Rows with blank employer_name are not useful for an employer filter.
    before = len(df)
    #len(df): number of rows in the DataFrame.
    df = df[df["employer_name"] != ""]
    #df["employer_name"] != ""]: creates a True/False list.
    #df[df["employer_name"] != ""]: keeps only the rows where the condition is True.
    dropped = before - len(df)
    if dropped:
        print(f"Dropped {dropped} rows with no employer name")

    # 4) Petition counts come in as text like "0.0"; make them floats.
    #If something is unparseable we treat it as 0 (safe for counts).
    for col in METRIC_COLUMNS:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)
        #if an invalid value like "abc" is passed, errors="coerce" will convert it to NaN instead of crashing.

    #fiscal_year should be an integer year; line_number is just a row id.
    #Int64: a nullable integer type that can hold NA values.
    df["fiscal_year"] = pd.to_numeric(
        df["fiscal_year"], errors="coerce"
    ).astype("Int64")
    df["line_number"] = pd.to_numeric(df["line_number"], errors="coerce")

    # Rows with no fiscal year can't be trusted; drop them.
    df = df.dropna(subset=["fiscal_year"])

    # 5) Replace empty geography / industry values with explicit labels,
    #    so dropdowns and tables show something readable (not "" or "nan").
    df["industry"] = df["industry"].replace("", "Unknown industry")
    df["state"] = df["state"].replace("", "Unknown state")
    df["city"] = df["city"].replace("", "Unknown city")
    df["zip_code"] = df["zip_code"].replace("", pd.NA)

    # Helpful derived column: did USCIS ever approve at least 1 petition
    # in any bucket? Useful later for "sponsored at least once" filters.
    df["any_approval"] = (
        df[[col for col in METRIC_COLUMNS if col.endswith("_approval")]].sum(axis=1)
        > 0
    )

    # Reset so the index after filtering is 0..N-1 again.
    return df.reset_index(drop=True)


def load_clean(path: Path = DATASET) -> pd.DataFrame:
    """Convenience wrapper: load + clean data in one call."""
    return clean_employers(load_raw(path))



