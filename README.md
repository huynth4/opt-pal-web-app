# OPT Pal (final project)

Personal H-1B employer data explorer — Flask app for browsing USCIS-based employer statistics. See [project.spec.md](project.spec.md) for the full plan.

## Setup

1. Install [uv](https://docs.astral.sh/uv/) if you do not have it.
2. Clone this repository and open the project folder in your editor.
3. Dependencies are listed in `pyproject.toml`. Run any Python command with `uv run` so the project virtual environment is used.

SQLite uses Python’s built-in [`sqlite3`](https://docs.python.org/3/library/sqlite3.html) module — no extra package to install.

## How to Run

From the project root:

```bash
uv run flask --app app run --debug
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000). Press `Ctrl+C` in the terminal to stop the server.

The database file is created at `instance/opt_pal.db` on first run (ignored by git).

## Layout

| Path | Purpose |
|------|--------|
| `app.py` | Flask app and routes |
| `helpers.py` | Data and domain logic |
| `database.py` | SQLite path, connection, `init_db` |
| `templates/` | Jinja HTML |
| `static/` | CSS (and JS later) |
| `data/` | CSV and other data files |

## Project Links

- [Project Spec](project.spec.md)
- [Project Journal](project.journal.md)
- [Flask setup guide (course)](https://csc-121.path.app/unit-3/resources/flask-setup.guide.llm.md)
