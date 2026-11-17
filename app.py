import csv
import hmac
import io
import os
import secrets

from flask import Flask, Response, abort, render_template, request, session

from database import DATABASE_PATH, get_db, init_db


app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
app.config["DATABASE_PATH"] = DATABASE_PATH
app.config["TEMPLATES_AUTO_RELOAD"] = True

DIVISIONS = ("Industrial City Division", "Northern City Division")
VULNERABILITY_LEVELS = ("High", "Medium", "Low")

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
        division_summary = connection.execute(
            """SELECT division, COUNT(*) AS wards,
            ROUND(AVG(improved_sanitation_pct), 1) AS illustrative_average
            FROM wards GROUP BY division ORDER BY division"""
        ).fetchall()
    return render_template(
        "dashboard.html",
        active_page="overview",
        ward_count=ward_count,
        high_vulnerability_count=high_vulnerability_count,
        division_summary=division_summary,
    )


@app.get("/wards")
def wards():
    search = request.args.get("q", "").strip()[:100]
    division = request.args.get("division", "")
    vulnerability = request.args.get("vulnerability", "")
    conditions = []
    params = []
    if search:
        conditions.append("(ward_name LIKE ? OR primary_vulnerable_group LIKE ?)")
        params.extend((f"%{search}%", f"%{search}%"))
    if division in DIVISIONS:
        conditions.append("division = ?")
        params.append(division)
    if vulnerability in VULNERABILITY_LEVELS:
        conditions.append("vulnerability_index = ?")
        params.append(vulnerability)
    query = "SELECT * FROM wards"
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    query += " ORDER BY division, ward_name"
    with get_db() as connection:
        rows = connection.execute(query, params).fetchall()
    return render_template(
        "wards.html",
        active_page="wards",
        wards=rows,
        search=search,
        selected_division=division,
        selected_vulnerability=vulnerability,
        divisions=DIVISIONS,
        vulnerability_levels=VULNERABILITY_LEVELS,
    )


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
    gaps = (
        ("Uneven coverage across wards", "Compare ward-level coverage before selecting target areas."),
        ("Limited monitoring of sustained behaviour change", "Track follow-up and sustained household practice."),
        ("Fragmented information and reporting", "Coordinate programme data using shared indicators."),
        ("Limited household-level follow-up", "Schedule and record household-level checks."),
        ("Inadequate maintenance and monitoring", "Plan maintenance responsibilities and review intervals."),
    )
    return render_template(
        "interventions.html",
        active_page="interventions",
        programmes=programmes,
        gaps=gaps,
    )


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
