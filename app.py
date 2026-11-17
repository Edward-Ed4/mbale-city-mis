import csv
import hmac
import io
import os
import secrets
import sqlite3

from flask import Flask, Response, abort, flash, redirect, render_template, request, session, url_for

from database import DATABASE_PATH, get_db, init_db


app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
app.config["DATABASE_PATH"] = DATABASE_PATH
app.config["TEMPLATES_AUTO_RELOAD"] = True

DIVISIONS = ("Industrial City Division", "Northern City Division")
VULNERABILITY_LEVELS = ("High", "Medium", "Low")
INTERVENTION_STATUSES = ("Active", "Scaling", "Needs Follow-up")
VULNERABLE_GROUPS = (
    "Children under 5",
    "Low-income households",
    "Women & Girls",
    "Persons with disabilities",
    "Informal settlements",
    "Flood-prone communities",
)

BETA_REGRESSION = (
    ("Household size", -0.6479, 0.2188, "0.003"),
    ("Unemployment", -0.0235, 0.0098, "0.017"),
    ("Constant", 3.3527, 0.8323, "0.000"),
)

EXPORTS = {
    "wards": {
        "filename": "mbale-sanitation-ward-register.csv",
        "headers": (
            ("Ward", "ward_name"),
            ("Division", "division"),
            ("Total households", "total_households"),
            ("Improved sanitation (%)", "improved_sanitation_pct"),
            ("Unimproved sanitation (%)", "unimproved_sanitation_pct"),
            ("Vulnerability index", "vulnerability_index"),
            ("Primary vulnerable group", "primary_vulnerable_group"),
        ),
        "query": "SELECT * FROM wards ORDER BY division, ward_name",
    },
    "interventions": {
        "filename": "mbale-sanitation-interventions.csv",
        "headers": (
            ("Programme", "programme_name"),
            ("Target ward", "target_ward"),
            ("Status", "status"),
            ("Lead agency", "lead_agency"),
            ("Coverage (%)", "coverage_pct"),
        ),
        "query": "SELECT * FROM interventions ORDER BY programme_name, target_ward",
    },
}


@app.before_request
def protect_post_requests():
    if request.method == "POST":
        supplied = request.form.get("_csrf_token", "")
        expected = session.get("_csrf_token", "")
        if not expected or not hmac.compare_digest(supplied, expected):
            abort(400, description="The form session expired. Reload the page and try again.")


@app.context_processor
def inject_template_helpers():
    def csrf_token():
        if "_csrf_token" not in session:
            session["_csrf_token"] = secrets.token_urlsafe(32)
        return session["_csrf_token"]

    return {"csrf_token": csrf_token}


def _csv_response(filename, headers, rows):
    output = io.StringIO(newline="")
    writer = csv.writer(output)
    writer.writerow([label for label, _ in headers])
    for row in rows:
        values = []
        for _, name in headers:
            raw_value = row[name]
            if raw_value is None:
                value = ""
            elif isinstance(raw_value, (int, float)):
                value = raw_value
            else:
                value = str(raw_value)
                if value.startswith(("=", "+", "-", "@", "\t", "\r")):
                    value = "'" + value
            values.append(value)
        writer.writerow(values)
    return Response(
        "\ufeff" + output.getvalue(),
        mimetype="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@app.get("/")
def overview():
    with get_db() as connection:
        ward_count = connection.execute("SELECT COUNT(*) FROM wards").fetchone()[0]
        high_vulnerability_count = connection.execute(
            "SELECT COUNT(*) FROM wards WHERE vulnerability_index = ?",
            ("High",),
        ).fetchone()[0]
        ward_data = connection.execute(
            """SELECT ward_name, division, improved_sanitation_pct, vulnerability_index
            FROM wards ORDER BY improved_sanitation_pct, ward_name"""
        ).fetchall()
        vulnerability_data = connection.execute(
            """SELECT division, vulnerability_index, COUNT(*) AS ward_count
            FROM wards GROUP BY division, vulnerability_index"""
        ).fetchall()
        top_priority = connection.execute(
            """SELECT id, ward_name, division, total_households, improved_sanitation_pct,
            vulnerability_index FROM wards ORDER BY improved_sanitation_pct, ward_name LIMIT 8"""
        ).fetchall()
    chart_data = {
        "wards": [
            {
                "name": row["ward_name"],
                "coverage": row["improved_sanitation_pct"],
                "division": row["division"],
            }
            for row in ward_data
        ],
        "vulnerability": [
            {
                "division": row["division"],
                "level": row["vulnerability_index"],
                "count": row["ward_count"],
            }
            for row in vulnerability_data
        ],
    }
    return render_template(
        "dashboard.html",
        active_page="overview",
        ward_count=ward_count,
        high_vulnerability_count=high_vulnerability_count,
        top_priority=top_priority,
        chart_data=chart_data,
    )


@app.get("/wards")
def wards():
    with get_db() as connection:
        rows = connection.execute(
            "SELECT * FROM wards ORDER BY division, ward_name"
        ).fetchall()
        edit_id = request.args.get("edit", type=int)
        edit_ward = connection.execute(
            "SELECT * FROM wards WHERE id = ?", (edit_id,)
        ).fetchone() if edit_id else None
    return render_template(
        "wards.html",
        active_page="wards",
        wards=rows,
        divisions=DIVISIONS,
        vulnerability_levels=VULNERABILITY_LEVELS,
        vulnerable_groups=VULNERABLE_GROUPS,
        edit_ward=edit_ward,
    )


def _ward_form_data():
    ward_name = request.form.get("ward_name", "").strip()
    division = request.form.get("division", "")
    group = request.form.get("primary_vulnerable_group", "")
    vulnerability = request.form.get("vulnerability_index", "")
    try:
        households = int(request.form.get("total_households", ""))
        coverage = float(request.form.get("improved_sanitation_pct", ""))
    except ValueError as error:
        raise ValueError("Households must be a whole number and coverage must be numeric.") from error
    if not ward_name or len(ward_name) > 100:
        raise ValueError("Ward name is required and must be 100 characters or fewer.")
    if division not in DIVISIONS or vulnerability not in VULNERABILITY_LEVELS or group not in VULNERABLE_GROUPS:
        raise ValueError("Choose valid division, vulnerability, and vulnerable group values.")
    if households < 1:
        raise ValueError("Total households must be at least 1.")
    if not 0 <= coverage <= 100:
        raise ValueError("Improved sanitation coverage must be between 0 and 100.")
    return {
        "ward_name": ward_name,
        "division": division,
        "total_households": households,
        "improved_sanitation_pct": coverage,
        "unimproved_sanitation_pct": round(100 - coverage, 2),
        "vulnerability_index": vulnerability,
        "primary_vulnerable_group": group,
    }


@app.post("/wards/create")
def create_ward():
    try:
        ward = _ward_form_data()
        with get_db() as connection:
            connection.execute(
                """INSERT INTO wards
                (ward_name, division, total_households, improved_sanitation_pct,
                 unimproved_sanitation_pct, vulnerability_index, primary_vulnerable_group)
                VALUES (?, ?, ?, ?, ?, ?, ?)""",
                tuple(ward.values()),
            )
        flash("Ward survey record added.", "success")
    except ValueError as error:
        flash(str(error), "error")
    except sqlite3.IntegrityError:
        flash("A ward with that name already exists.", "error")
    return redirect(url_for("wards"))


@app.post("/wards/<int:ward_id>/edit")
def edit_ward(ward_id):
    try:
        ward = _ward_form_data()
        with get_db() as connection:
            result = connection.execute(
                """UPDATE wards SET ward_name = ?, division = ?, total_households = ?,
                improved_sanitation_pct = ?, unimproved_sanitation_pct = ?,
                vulnerability_index = ?, primary_vulnerable_group = ? WHERE id = ?""",
                (*ward.values(), ward_id),
            )
        if not result.rowcount:
            flash("Ward record not found.", "error")
        else:
            flash("Ward survey record updated.", "success")
    except ValueError as error:
        flash(str(error), "error")
    except sqlite3.IntegrityError:
        flash("A ward with that name already exists.", "error")
    return redirect(url_for("wards"))


@app.post("/wards/<int:ward_id>/update")
def update_ward(ward_id):
    coverage_text = request.form.get("improved_sanitation_pct", "")
    vulnerability = request.form.get("vulnerability_index", "")
    try:
        coverage = float(coverage_text)
        if not 0 <= coverage <= 100:
            raise ValueError("Coverage must be between 0 and 100.")
        if vulnerability not in VULNERABILITY_LEVELS:
            raise ValueError("Choose a valid vulnerability level.")
        with get_db() as connection:
            result = connection.execute(
                """UPDATE wards SET improved_sanitation_pct = ?,
                unimproved_sanitation_pct = ?, vulnerability_index = ? WHERE id = ?""",
                (coverage, round(100 - coverage, 2), vulnerability, ward_id),
            )
        if not result.rowcount:
            flash("Ward record not found.", "error")
        else:
            flash("Ward coverage and vulnerability updated.", "success")
    except ValueError as error:
        flash(str(error), "error")
    return redirect(url_for("wards"))


@app.post("/wards/<int:ward_id>/delete")
def delete_ward(ward_id):
    with get_db() as connection:
        result = connection.execute("DELETE FROM wards WHERE id = ?", (ward_id,))
    flash(
        "Ward record deleted." if result.rowcount else "Ward record not found.",
        "success" if result.rowcount else "error",
    )
    return redirect(url_for("wards"))


@app.get("/model")
def model():
    return render_template(
        "model.html",
        active_page="model",
        coefficients=BETA_REGRESSION,
    )


@app.get("/interventions")
def interventions():
    with get_db() as connection:
        programmes = connection.execute(
            "SELECT * FROM interventions ORDER BY programme_name, target_ward"
        ).fetchall()
    return render_template(
        "interventions.html",
        active_page="interventions",
        programmes=programmes,
        statuses=INTERVENTION_STATUSES,
    )


@app.post("/interventions/create")
def create_intervention():
    programme_name = request.form.get("programme_name", "").strip()
    target_ward = request.form.get("target_ward", "").strip()
    lead_agency = request.form.get("lead_agency", "").strip()
    status = request.form.get("status", "")
    try:
        coverage = float(request.form.get("coverage_pct", ""))
    except ValueError:
        flash("Coverage must be a number from 0 to 100.", "error")
        return redirect(url_for("interventions"))
    if not programme_name or len(programme_name) > 120 or not target_ward or len(target_ward) > 250 or not lead_agency or len(lead_agency) > 120:
        flash("Enter a programme, assigned ward, and lead agency.", "error")
    elif status not in INTERVENTION_STATUSES or not 0 <= coverage <= 100:
        flash("Choose a valid status and coverage from 0 to 100.", "error")
    else:
        with get_db() as connection:
            connection.execute(
                """INSERT INTO interventions
                (programme_name, target_ward, status, lead_agency, coverage_pct)
                VALUES (?, ?, ?, ?, ?)""",
                (programme_name, target_ward, status, lead_agency, coverage),
            )
        flash("Intervention programme added.", "success")
    return redirect(url_for("interventions"))


@app.post("/interventions/<int:intervention_id>/update")
def update_intervention(intervention_id):
    status = request.form.get("status", "")
    if status not in INTERVENTION_STATUSES:
        flash("Choose a valid intervention status.", "error")
    else:
        try:
            coverage = float(request.form.get("coverage_pct", ""))
            if not 0 <= coverage <= 100:
                raise ValueError
        except ValueError:
            flash("Coverage must be between 0 and 100.", "error")
        else:
            with get_db() as connection:
                result = connection.execute(
                    "UPDATE interventions SET status = ?, coverage_pct = ? WHERE id = ?",
                    (status, coverage, intervention_id),
                )
            flash(
                "Intervention updated." if result.rowcount else "Intervention not found.",
                "success" if result.rowcount else "error",
            )
    return redirect(url_for("interventions"))


@app.post("/interventions/<int:intervention_id>/delete")
def delete_intervention(intervention_id):
    with get_db() as connection:
        result = connection.execute("DELETE FROM interventions WHERE id = ?", (intervention_id,))
    flash(
        "Intervention deleted." if result.rowcount else "Intervention not found.",
        "success" if result.rowcount else "error",
    )
    return redirect(url_for("interventions"))


@app.get("/database")
def database_explorer():
    tables = []
    with get_db() as connection:
        for table_name in ("wards", "interventions"):
            columns = connection.execute(
                f"PRAGMA table_info({table_name})"
            ).fetchall()
            count = connection.execute(
                f"SELECT COUNT(*) FROM {table_name}"
            ).fetchone()[0]
            records = connection.execute(
                f"SELECT * FROM {table_name} ORDER BY id LIMIT 5"
            ).fetchall()
            tables.append(
                {"name": table_name, "columns": columns, "count": count, "records": records}
            )
    return render_template(
        "database_explorer.html",
        active_page="database",
        tables=tables,
    )


@app.get("/export/<dataset>")
def export_csv(dataset):
    export = EXPORTS.get(dataset)
    if export is None:
        abort(404)
    with get_db() as connection:
        rows = connection.execute(export["query"]).fetchall()
    return _csv_response(export["filename"], export["headers"], rows)


@app.get("/export/model")
def export_model_csv():
    headers = (
        ("Variable", "variable"),
        ("Coefficient", "coefficient"),
        ("Standard error", "standard_error"),
        ("P-value", "p_value"),
    )
    rows = [
        {
            "variable": name,
            "coefficient": coefficient,
            "standard_error": standard_error,
            "p_value": p_value,
        }
        for name, coefficient, standard_error, p_value in BETA_REGRESSION
    ]
    return _csv_response("mbale-sanitation-beta-regression.csv", headers, rows)


@app.get("/export/database")
def export_database_summary():
    headers = (("Table", "table"), ("Row count", "rows"), ("Columns", "columns"))
    with get_db() as connection:
        rows = []
        for table_name in ("wards", "interventions"):
            columns = connection.execute(
                f"PRAGMA table_info({table_name})"
            ).fetchall()
            count = connection.execute(
                f"SELECT COUNT(*) FROM {table_name}"
            ).fetchone()[0]
            rows.append(
                {"table": table_name, "rows": count, "columns": ", ".join(column["name"] for column in columns)}
            )
    return _csv_response("mbale-sanitation-data-dictionary.csv", headers, rows)


if __name__ == "__main__":
    init_db()
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", "5000")), debug=False)
else:
    init_db()
