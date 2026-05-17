""" Search + aggregate functions for OPT Pal.

All SQLite queries live here. No Flask imports.
"""

from pathlib import Path
import sqlite3

DATASET = (
    Path(__file__).resolve().parent / "data" / "Employer Information.csv"
)
DB_PATH = Path(__file__).resolve().parent / "instance" / "opt_pal.db"

def _connect():
    # The _ prefix is a Python convention for "private for this module".
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


APPROVAL_COLS = [
    "new_employment_approval",
    "continuation_approval",
    "change_employer_approval",
    "amended_approval",
]
TOTAL_APPROVALS_SQL = " + ".join(APPROVAL_COLS)

STATE_NAMES = {
    "AL": "Alabama",
    "AK": "Alaska",
    "AZ": "Arizona",
    "AR": "Arkansas",
    "CA": "California",
    "CO": "Colorado",
    "CT": "Connecticut",
    "DE": "Delaware",
    "DC": "District of Columbia",
    "FL": "Florida",
    "GA": "Georgia",
    "HI": "Hawaii",
    "ID": "Idaho",
    "IL": "Illinois",
    "IN": "Indiana",
    "IA": "Iowa",
    "KS": "Kansas",
    "KY": "Kentucky",
    "LA": "Louisiana",
    "ME": "Maine",
    "MD": "Maryland",
    "MA": "Massachusetts",
    "MI": "Michigan",
    "MN": "Minnesota",
    "MS": "Mississippi",
    "MO": "Missouri",
    "MT": "Montana",
    "NE": "Nebraska",
    "NV": "Nevada",
    "NH": "New Hampshire",
    "NJ": "New Jersey",
    "NM": "New Mexico",
    "NY": "New York",
    "NC": "North Carolina",
    "ND": "North Dakota",
    "OH": "Ohio",
    "OK": "Oklahoma",
    "OR": "Oregon",
    "PA": "Pennsylvania",
    "RI": "Rhode Island",
    "SC": "South Carolina",
    "SD": "South Dakota",
    "TN": "Tennessee",
    "TX": "Texas",
    "UT": "Utah",
    "VT": "Vermont",
    "VA": "Virginia",
    "WA": "Washington",
    "WV": "West Virginia",
    "WI": "Wisconsin",
    "WY": "Wyoming",
    # U.S. territories
    "GU": "Guam",
    "MP": "Northern Mariana Islands",
    "PR": "Puerto Rico",
    "VI": "U.S. Virgin Islands",
    # USPS military / overseas (not states, but can appear in datasets)
    "AA": "Armed Forces Americas",
    "AE": "Armed Forces Europe",
    "AP": "Armed Forces Pacific",
}


def state_name(abbr):
    code = (abbr or "").strip().upper()
    return STATE_NAMES.get(code, abbr)

SIZE_RANGES = {
    "small": (0, 50),
    "mid":   (50, 500),
    "large": (500, 10_000_000),
}

def _build_where(filters):
    clauses, params = [],[]
    state = filters.get("state")

    if filters.get("industry"):
        clauses.append("industry LIKE ?")
        params.append(f"%{filters['industry'].strip()}%")

    if isinstance(state, list) and state: 
        placeholders = ",".join("?" for _ in state)
        clauses.append(f"state IN ({placeholders})")
        params.extend(s.strip().upper() for s in state)
    elif isinstance(state, str) and state:
        clauses.append("state = ?")
        params.append(state.strip().upper())

    city = filters.get("city")
    if isinstance(city, list) and city:
        placeholders = ",".join("?" for _ in city)
        clauses.append(f"city IN ({placeholders})")
        params.extend(c.strip().upper() for c in city)
    elif isinstance(city, str) and city:
        clauses.append("city LIKE ?")
        params.append(f"%{city.strip().upper()}%")

    size = (filters.get("size") or "").lower()
    if size in SIZE_RANGES:
        lo, hi = SIZE_RANGES[size]
        clauses.append(f"({TOTAL_APPROVALS_SQL}) BETWEEN ? AND ?")
        params.extend([lo, hi])

    where = " AND ".join(clauses) if clauses else "1=1"

    return where, params

def search_employers(filters, limit=50):
    where, params = _build_where(filters)
    query = f"""
        SELECT employer_name, industry, city, state, fiscal_year,
               ({TOTAL_APPROVALS_SQL}) AS total_approvals
        FROM employers
        WHERE {where}
        ORDER BY total_approvals DESC, employer_name ASC
        LIMIT ?
    """
    params.append(limit)

    with _connect() as conn:
        rows = conn.execute(query, params).fetchall()
    return [dict(r) for r in rows]


def unique_industries():
    with _connect() as conn:
        rows = conn.execute(
            "SELECT DISTINCT industry FROM employers "
            "WHERE industry != '' ORDER BY industry"
        ).fetchall()
    return [r["industry"] for r in rows]


def unique_states():
    with _connect() as conn:
        rows = conn.execute(
            "SELECT DISTINCT state FROM employers "
            "WHERE state != '' ORDER BY state"
        ).fetchall()
    return [
        {"code": r["state"], "name": state_name(r["state"])}
        for r in rows
    ]


def unique_cities(filters):
    city_filters = dict(filters)
    city_filters["city"] = ""
    where, params = _build_where(city_filters)
    query = f"""
        SELECT DISTINCT city, state
        FROM employers
        WHERE {where}
        AND city != ''
        ORDER BY state ASC, city ASC
    """
    with _connect() as conn:
        rows = conn.execute(query, params).fetchall()

    return [
        {
            "city": r["city"],
            "state": r["state"],
            "state_name": state_name(r["state"]),
            "label": f"{r['city'].title()}, {state_name(r['state'])}",
        }
        for r in rows
    ]


def total(filters): #-> {"employers": int, "approvals": int}
    where, params = _build_where(filters)
    # COUNT(*): total number of rows
    # COALESCE(value 1, value 2, value 3,....): checks value from left to right and returns
    # the first one that is not NULL.
    # In this case, if SUM(...) returns a number, use that number.
    # if SUM(...) returns NULL, use 0.
    # If there are no rows to sum, or if all relevant values are NULL, SUM() may return NULL.
    query = f"""
        SELECT COUNT(*) AS employers,
               COALESCE(SUM({TOTAL_APPROVALS_SQL}), 0) AS approvals
        FROM employers
        WHERE {where}
    """
    with _connect() as conn:
        row = conn.execute(query, params).fetchone()
    return {"employers": row["employers"], "approvals": int(row["approvals"])}

def top_employers(filters, n=10):
    where, params = _build_where(filters)
    query = f"""
            SELECT employer_name,
                   COALESCE(SUM({TOTAL_APPROVALS_SQL}), 0) AS approvals,
                   COUNT(*) AS employers
            FROM employers
            WHERE {where}
            GROUP BY employer_name
            ORDER BY approvals DESC, employer_name ASC
            LIMIT ?                   
    """
    params.append(n)
    with _connect() as conn:
        rows = conn.execute(query, params).fetchall()
    return [dict(r) for r in rows]

def approvals_by_state(filters):
    where, params = _build_where(filters)
    query = f"""
            SELECT state,
                   COALESCE(SUM({TOTAL_APPROVALS_SQL}), 0) AS approvals
            FROM employers
            WHERE {where}
            AND state != ''
            GROUP BY state
            ORDER BY approvals DESC, state DESC
    """
    with _connect() as conn:
        rows = conn.execute(query, params).fetchall()
    return [dict(r) for r in rows]