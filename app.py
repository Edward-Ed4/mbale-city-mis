import csv
import hmac
import io
import os
import secrets
import sqlite3
from datetime import datetime

from flask import Flask, Response, abort, flash, redirect, render_template, request, session, url_for

from database import DATABASE_PATH, get_db, init_db


app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
app.config["DATABASE_PATH"] = DATABASE_PATH
app.config["TEMPLATES_AUTO_RELOAD"] = True


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

    return {"csrf_token": csrf_token, "current_year": datetime.now().year}


@app.template_filter("currency")
def currency(value):
    return f"UGX {int(value or 0):,}"


@app.template_filter("date_short")
def date_short(value):
    if not value:
        return "—"
    try:
        return datetime.fromisoformat(value).strftime("%d %b %Y")
    except (TypeError, ValueError):
        return value


DIVISIONS = ("Industrial City Division", "Northern City Division")
BUSINESS_CATEGORIES = ("Retail", "Hospitality", "Agro-Processing", "Hardware", "Transport")
WARDS = (
    "Senior Quarters", "Maluku Ward", "Nkoma", "Mooni", "Nabuyonga",
    "Bugema", "Republic Street", "Naboa Road", "Pallisa Road", "Kumi Road",
    "Namatala", "Busamaga", "Wanale",
)
COMPLAINT_CATEGORIES = ("Garbage Collection", "Street Lighting", "Road Maintenance", "Water & Drainage")
EXPORT_COLUMNS = {
    "businesses": (
        ("License number", "license_no"), ("Business name", "business_name"),
        ("Owner name", "owner_name"), ("Phone", "phone"), ("Category", "category"),
        ("Division", "division"), ("Street / ward", "street_ward"),
        ("Annual fee (UGX)", "annual_fee_ugx"), ("Status", "status"),
        ("Registered", "created_at"),
    ),
    "properties": (
        ("Plot number", "plot_no"), ("Owner name", "owner_name"),
        ("Property type", "property_type"), ("Division", "division"),
        ("Ward", "ward"), ("Annual rate (UGX)", "annual_rate_ugx"),
        ("Payment status", "payment_status"), ("Last paid date", "last_paid_date"),
    ),
    "complaints": (
        ("Ticket number", "ticket_no"), ("Citizen name", "citizen_name"),
        ("Phone", "phone"), ("Division", "division"), ("Location", "location_detail"),
        ("Category", "category"), ("Description", "description"),
        ("Priority", "priority"), ("Status", "status"), ("Logged at", "logged_at"),
    ),
}


def _form_value(name):
    return request.form.get(name, "").strip()


def _integer_form_value(name):
    try:
        value = int(_form_value(name))
        if value < 0:
            raise ValueError
        return value
    except ValueError:
        raise ValueError(f"{name.replace('_', ' ').capitalize()} must be a non-negative whole number.")


@app.get("/")
def dashboard():
    with get_db() as connection:
        business_count = connection.execute("SELECT COUNT(*) FROM businesses WHERE status = 'Paid'").fetchone()[0]
        property_count = connection.execute("SELECT COUNT(*) FROM properties").fetchone()[0]
        pending_count = connection.execute("SELECT COUNT(*) FROM complaints WHERE status != 'Resolved'").fetchone()[0]
        business_revenue = connection.execute(
            "SELECT COALESCE(SUM(annual_fee_ugx), 0) FROM businesses WHERE status = 'Paid'"
        ).fetchone()[0]
        property_revenue = connection.execute(
            """SELECT COALESCE(SUM(annual_rate_ugx), 0) FROM properties
            WHERE payment_status = 'Cleared'"""
        ).fetchone()[0]
        divisions = connection.execute(
            """SELECT d.division,
                (SELECT COUNT(*) FROM businesses b WHERE b.division = d.division) AS businesses,
                (SELECT COUNT(*) FROM properties p WHERE p.division = d.division) AS properties,
                (SELECT COUNT(*) FROM complaints c WHERE c.division = d.division AND c.status != 'Resolved') AS requests
            FROM (SELECT ? AS division UNION ALL SELECT ?) d""",
            DIVISIONS,
        ).fetchall()
        recent_businesses = connection.execute(
            """SELECT 'Business license' AS kind, business_name AS title, status AS detail, created_at AS happened_at
            FROM businesses ORDER BY created_at DESC LIMIT 4"""
        ).fetchall()
        recent_complaints = connection.execute(
            """SELECT 'Service request' AS kind, ticket_no AS title, status AS detail, logged_at AS happened_at
            FROM complaints ORDER BY logged_at DESC LIMIT 4"""
        ).fetchall()
    activity = sorted([*recent_businesses, *recent_complaints], key=lambda row: row["happened_at"], reverse=True)[:6]
    return render_template(
        "dashboard.html",
        active_page="dashboard",
        total_revenue=business_revenue + property_revenue,
        active_licenses=business_count,
        registered_properties=property_count,
        pending_requests=pending_count,
        divisions=divisions,
        activity=activity,
    )


@app.get("/export/<dataset>")
def export_csv(dataset):
    columns = EXPORT_COLUMNS.get(dataset)
    if columns is None:
        abort(404)
    with get_db() as connection:
        rows = connection.execute(f"SELECT * FROM {dataset} ORDER BY id").fetchall()
    output = io.StringIO(newline="")
    writer = csv.writer(output)
    writer.writerow([label for label, _ in columns])
    for row in rows:
        values = []
        for _, name in columns:
            value = "" if row[name] is None else str(row[name])
            if value.startswith(("=", "+", "-", "@", "\t", "\r")):
                value = "'" + value
            values.append(value)
        writer.writerow(values)
    filename = f"mbale-city-{dataset}.csv"
    return Response(
        "\ufeff" + output.getvalue(),
        mimetype="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@app.get("/businesses")
def businesses():
    division = request.args.get("division", "")
    status = request.args.get("status", "")
    query = "SELECT * FROM businesses WHERE 1 = 1"
    params = []
    if division in DIVISIONS:
        query += " AND division = ?"
        params.append(division)
    if status in ("Paid", "Pending", "Expired"):
        query += " AND status = ?"
        params.append(status)
    query += " ORDER BY created_at DESC, id DESC"
    with get_db() as connection:
        rows = connection.execute(query, params).fetchall()
    return render_template(
        "businesses.html", active_page="businesses", businesses=rows,
        divisions=DIVISIONS, categories=BUSINESS_CATEGORIES, wards=WARDS,
        selected_division=division, selected_status=status,
    )


@app.post("/businesses/save")
def save_business():
    try:
        data = {
            "business_name": _form_value("business_name"),
            "owner_name": _form_value("owner_name"),
            "phone": _form_value("phone"),
            "category": _form_value("category"),
            "division": _form_value("division"),
            "street_ward": _form_value("street_ward"),
            "annual_fee_ugx": _integer_form_value("annual_fee_ugx"),
            "status": _form_value("status"),
        }
        if not all(data[key] for key in ("business_name", "owner_name", "phone", "category", "division", "street_ward", "status")):
            raise ValueError("Complete all business license fields.")
        if data["category"] not in BUSINESS_CATEGORIES or data["division"] not in DIVISIONS or data["street_ward"] not in WARDS or data["status"] not in ("Paid", "Pending", "Expired"):
            raise ValueError("Choose valid license details from the available options.")
        business_id = _form_value("id")
        with get_db() as connection:
            if business_id:
                result = connection.execute(
                    """UPDATE businesses SET business_name = ?, owner_name = ?, phone = ?, category = ?,
                    division = ?, street_ward = ?, annual_fee_ugx = ?, status = ? WHERE id = ?""",
                    (*data.values(), business_id),
                )
                flash(
                    "Business license updated successfully." if result.rowcount else "Business license was not found.",
                    "success" if result.rowcount else "error",
                )
            else:
                next_id = connection.execute("SELECT COALESCE(MAX(id), 0) + 1 FROM businesses").fetchone()[0]
                license_no = f"MCC-TL-{datetime.now().year}-{next_id:03d}"
                connection.execute(
                    """INSERT INTO businesses
                    (license_no, business_name, owner_name, phone, category, division, street_ward, annual_fee_ugx, status, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (license_no, *data.values(), datetime.now().isoformat(timespec="seconds")),
                )
                flash(f"Business registered with license {license_no}.", "success")
    except (ValueError, sqlite3.IntegrityError) as error:
        flash(str(error) or "Could not save this business license.", "error")
    return redirect(url_for("businesses"))


@app.post("/businesses/<int:business_id>/delete")
def delete_business(business_id):
    with get_db() as connection:
        result = connection.execute("DELETE FROM businesses WHERE id = ?", (business_id,))
    flash("Business license deleted." if result.rowcount else "Business license was not found.", "success" if result.rowcount else "error")
    return redirect(url_for("businesses"))


@app.get("/properties")
def properties():
    with get_db() as connection:
        rows = connection.execute("SELECT * FROM properties ORDER BY plot_no").fetchall()
    return render_template("properties.html", active_page="properties", properties=rows)


@app.post("/properties/<int:property_id>/payment")
def record_payment(property_id):
    with get_db() as connection:
        result = connection.execute(
            "UPDATE properties SET payment_status = 'Cleared', last_paid_date = ? WHERE id = ?",
            (datetime.now().isoformat(timespec="seconds"), property_id),
        )
    flash("Property rate payment recorded." if result.rowcount else "Property record was not found.", "success" if result.rowcount else "error")
    return redirect(url_for("properties"))


@app.get("/complaints")
def complaints():
    with get_db() as connection:
        rows = connection.execute("SELECT * FROM complaints ORDER BY logged_at DESC, id DESC").fetchall()
    return render_template(
        "complaints.html", active_page="complaints", complaints=rows,
        divisions=DIVISIONS, categories=COMPLAINT_CATEGORIES,
    )


@app.post("/complaints/create")
def create_complaint():
    fields = ("citizen_name", "phone", "division", "location_detail", "category", "description", "priority")
    data = {field: _form_value(field) for field in fields}
    if not all(data.values()):
        flash("Complete all citizen service request fields.", "error")
        return redirect(url_for("complaints"))
    if data["division"] not in DIVISIONS or data["category"] not in COMPLAINT_CATEGORIES or data["priority"] not in ("High", "Medium", "Low"):
        flash("Choose valid division, category, and priority values.", "error")
        return redirect(url_for("complaints"))
    with get_db() as connection:
        next_id = connection.execute("SELECT COALESCE(MAX(id), 0) + 1 FROM complaints").fetchone()[0]
        ticket_no = f"MCC-SR-{datetime.now().year}-{next_id:02d}"
        connection.execute(
            """INSERT INTO complaints
            (ticket_no, citizen_name, phone, division, location_detail, category, description, priority, status, logged_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Open', ?)""",
            (ticket_no, *data.values(), datetime.now().isoformat(timespec="seconds")),
        )
    flash(f"Service request {ticket_no} logged.", "success")
    return redirect(url_for("complaints"))


@app.post("/complaints/<int:complaint_id>/status")
def update_complaint_status(complaint_id):
    status = _form_value("status")
    if status not in ("Open", "In Progress", "Resolved"):
        flash("Choose a valid service request status.", "error")
    else:
        with get_db() as connection:
            result = connection.execute("UPDATE complaints SET status = ? WHERE id = ?", (status, complaint_id))
        flash("Service request status updated." if result.rowcount else "Service request was not found.", "success" if result.rowcount else "error")
    return redirect(url_for("complaints"))


@app.get("/database")
def database_explorer():
    table_names = ("businesses", "properties", "complaints")
    tables = []
    with get_db() as connection:
        for table_name in table_names:
            columns = connection.execute(f"PRAGMA table_info({table_name})").fetchall()
            count = connection.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
            records = connection.execute(f"SELECT * FROM {table_name} ORDER BY id DESC LIMIT 5").fetchall()
            tables.append({"name": table_name, "columns": columns, "count": count, "records": records})
    return render_template("database_explorer.html", active_page="database", tables=tables)


@app.post("/database/reset")
def reset_demo_data():
    init_db(reset=True)
    flash("The default municipal registry has been restored.", "success")
    return redirect(url_for("database_explorer"))


if __name__ == "__main__":
    init_db()
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", "5000")), debug=False)
else:
    init_db()
