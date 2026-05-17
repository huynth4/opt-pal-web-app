from flask import Flask, render_template, request, redirect, url_for

from search import (
    unique_industries,
    unique_states,
    unique_cities,
    search_employers,
    total,
    top_employers,
    approvals_by_state,
    state_name,
)

app = Flask(__name__)

@app.context_processor
def template_helpers():
    return {"state_name": state_name}

@app.route("/")
def home():
    return render_template("home.html", title="OPT Pal")
    
@app.route("/quiz")
def quiz():
    # step: a variable to track the current question of the quiz the user is on. Default is 1.
    #answers: carries the user's answers across pages/steps.
    step = int(request.args.get("step", 1))
    answers = {
        "industry": request.args.get("industry", ""),
        "state":    request.args.getlist("state"),
        "city":     request.args.getlist("city"),
        "size":     request.args.get("size", ""),
    }
    return render_template(
        "quiz.html",
        title="OPT Pal",
        step=step,
        answers=answers,
        industries=unique_industries() if step == 1 else [],
        states=unique_states() if step == 2 else [],
        cities=unique_cities(answers) if step == 3 else [],
    )

@app.route("/dashboard")
def dashboard():
    filters = {
        "industry": request.args.get("industry", ""),
        "state":    request.args.getlist("state"),
        "city":     request.args.getlist("city"),
        "size":     request.args.get("size", ""),
    }
    by_state = approvals_by_state(filters)
    for row in by_state:
        row["state_name"] = state_name(row["state"])

    rows = search_employers(filters, 50)
    for row in rows:
        row["state_name"] = state_name(row["state"])

    return render_template(
        "dashboard.html",
        title="OPT Pal — Your matches",
        filters=filters,
        stats=total(filters),
        top=top_employers(filters, 10),
        by_state=by_state,
        rows=rows,
    )