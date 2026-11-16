import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta


DATABASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mbale_city.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS businesses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    license_no TEXT NOT NULL UNIQUE,
    business_name TEXT NOT NULL,
    owner_name TEXT NOT NULL,
    phone TEXT NOT NULL,
    category TEXT NOT NULL CHECK (category IN ('Retail', 'Hospitality', 'Agro-Processing', 'Hardware', 'Transport')),
    division TEXT NOT NULL CHECK (division IN ('Industrial City Division', 'Northern City Division')),
    street_ward TEXT NOT NULL,
    annual_fee_ugx INTEGER NOT NULL CHECK (annual_fee_ugx >= 0),
    status TEXT NOT NULL CHECK (status IN ('Paid', 'Pending', 'Expired')),
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS properties (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plot_no TEXT NOT NULL UNIQUE,
    owner_name TEXT NOT NULL,
    property_type TEXT NOT NULL CHECK (property_type IN ('Commercial', 'Residential', 'Industrial')),
    division TEXT NOT NULL CHECK (division IN ('Industrial City Division', 'Northern City Division')),
    ward TEXT NOT NULL,
    annual_rate_ugx INTEGER NOT NULL CHECK (annual_rate_ugx >= 0),
    payment_status TEXT NOT NULL CHECK (payment_status IN ('Cleared', 'Arrears')),
    last_paid_date TEXT
);
CREATE TABLE IF NOT EXISTS complaints (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticket_no TEXT NOT NULL UNIQUE,
    citizen_name TEXT NOT NULL,
    phone TEXT NOT NULL,
    division TEXT NOT NULL CHECK (division IN ('Industrial City Division', 'Northern City Division')),
    location_detail TEXT NOT NULL,
    category TEXT NOT NULL CHECK (category IN ('Garbage Collection', 'Street Lighting', 'Road Maintenance', 'Water & Drainage')),
    description TEXT NOT NULL,
    priority TEXT NOT NULL CHECK (priority IN ('High', 'Medium', 'Low')),
    status TEXT NOT NULL CHECK (status IN ('Open', 'In Progress', 'Resolved')),
    logged_at TEXT NOT NULL
);
"""


@contextmanager
def get_db():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def _seed_rows(connection):
    now = datetime.now()
    businesses = [
        ("MCC-TL-2026-001", "Elgon View Guest House", "Wambwa Geofrey", "+256 772 310 481", "Hospitality", "Industrial City Division", "Republic Street", 850000, "Paid", now - timedelta(days=32)),
        ("MCC-TL-2026-002", "Namatala Fresh Produce", "Namukose Sarah", "+256 701 448 209", "Retail", "Industrial City Division", "Namatala", 320000, "Pending", now - timedelta(days=28)),
        ("MCC-TL-2026-003", "Masaba Hardware Centre", "Masaba Denis", "+256 782 614 552", "Hardware", "Northern City Division", "Naboa Road", 650000, "Paid", now - timedelta(days=24)),
        ("MCC-TL-2026-004", "Wanale Coffee Works", "Nandutu Grace", "+256 759 420 187", "Agro-Processing", "Northern City Division", "Wanale Ward", 1200000, "Paid", now - timedelta(days=20)),
        ("MCC-TL-2026-005", "Busamaga Taxi Services", "Watsemwa Brenda", "+256 776 503 611", "Transport", "Northern City Division", "Busamaga", 480000, "Expired", now - timedelta(days=18)),
        ("MCC-TL-2026-006", "Pallisa Road Pharmacy", "Wekesa Andrew", "+256 703 882 146", "Retail", "Industrial City Division", "Pallisa Road", 560000, "Pending", now - timedelta(days=14)),
        ("MCC-TL-2026-007", "Kumi Road Restaurant", "Nabirye Esther", "+256 751 267 930", "Hospitality", "Industrial City Division", "Kumi Road", 720000, "Paid", now - timedelta(days=11)),
        ("MCC-TL-2026-008", "Republic Street Traders", "Wafula Martin", "+256 784 119 365", "Retail", "Industrial City Division", "Republic Street", 390000, "Paid", now - timedelta(days=8)),
        ("MCC-TL-2026-009", "Naboa Road Grain Mill", "Nakalembe Ruth", "+256 740 552 814", "Agro-Processing", "Northern City Division", "Naboa Road", 940000, "Pending", now - timedelta(days=4)),
    ]
    connection.executemany(
        """INSERT INTO businesses
        (license_no, business_name, owner_name, phone, category, division, street_ward, annual_fee_ugx, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        [(r[0], *r[1:9], r[9].isoformat(timespec="seconds")) for r in businesses],
    )

    properties = [
        ("PLT-IND-104", "Wambwa Geofrey", "Commercial", "Industrial City Division", "Republic Street", 1450000, "Cleared", now - timedelta(days=12)),
        ("PLT-IND-118", "Namukose Sarah", "Residential", "Industrial City Division", "Namatala", 420000, "Arrears", None),
        ("PLT-NOR-026", "Masaba Denis", "Commercial", "Northern City Division", "Naboa Road", 980000, "Cleared", now - timedelta(days=31)),
        ("PLT-NOR-041", "Nandutu Grace", "Industrial", "Northern City Division", "Wanale", 2250000, "Arrears", None),
        ("PLT-NOR-053", "Watsemwa Brenda", "Residential", "Northern City Division", "Busamaga", 510000, "Cleared", now - timedelta(days=16)),
        ("PLT-IND-133", "Wekesa Andrew", "Commercial", "Industrial City Division", "Pallisa Road", 1120000, "Arrears", None),
        ("PLT-IND-147", "Nabirye Esther", "Commercial", "Industrial City Division", "Kumi Road", 870000, "Cleared", now - timedelta(days=7)),
        ("PLT-NOR-068", "Wafula Martin", "Residential", "Northern City Division", "Naboa Road", 360000, "Arrears", None),
        ("PLT-IND-159", "Nakalembe Ruth", "Industrial", "Industrial City Division", "Republic Street", 1980000, "Cleared", now - timedelta(days=3)),
    ]
    connection.executemany(
        """INSERT INTO properties
        (plot_no, owner_name, property_type, division, ward, annual_rate_ugx, payment_status, last_paid_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        [(r[0], *r[1:6], r[6], r[7].isoformat(timespec="seconds") if r[7] else None) for r in properties],
    )

    complaints = [
        ("MCC-SR-2026-01", "Nabirye Esther", "+256 751 267 930", "Industrial City Division", "Namatala Market, Block B", "Garbage Collection", "Missed waste collection has left refuse near the market entrance.", "High", "Open", now - timedelta(days=2)),
        ("MCC-SR-2026-02", "Wekesa Andrew", "+256 703 882 146", "Industrial City Division", "Republic Street, near taxi stage", "Street Lighting", "Two street lights are not working along the pedestrian crossing.", "Medium", "In Progress", now - timedelta(days=3)),
        ("MCC-SR-2026-03", "Masaba Denis", "+256 782 614 552", "Northern City Division", "Naboa Road, trading centre", "Road Maintenance", "A large pothole is affecting traffic and boda-boda access.", "High", "Open", now - timedelta(days=5)),
        ("MCC-SR-2026-04", "Namukose Sarah", "+256 701 448 209", "Industrial City Division", "Namatala drainage channel", "Water & Drainage", "Drainage is blocked and water is pooling near homes.", "High", "In Progress", now - timedelta(days=6)),
        ("MCC-SR-2026-05", "Watsemwa Brenda", "+256 776 503 611", "Northern City Division", "Busamaga Community Road", "Road Maintenance", "Road surface requires grading after recent heavy rain.", "Low", "Resolved", now - timedelta(days=8)),
        ("MCC-SR-2026-06", "Nandutu Grace", "+256 759 420 187", "Northern City Division", "Wanale Ward, upper access road", "Garbage Collection", "Household waste has not been collected this week.", "Medium", "Open", now - timedelta(days=9)),
        ("MCC-SR-2026-07", "Wafula Martin", "+256 784 119 365", "Industrial City Division", "Pallisa Road junction", "Street Lighting", "The junction lamp is out, making evening crossing difficult.", "Medium", "Resolved", now - timedelta(days=12)),
        ("MCC-SR-2026-08", "Nakalembe Ruth", "+256 740 552 814", "Northern City Division", "Naboa Road, near primary school", "Water & Drainage", "Open drain needs clearing before it overflows into the school path.", "High", "Open", now - timedelta(days=14)),
        ("MCC-SR-2026-09", "Wambwa Geofrey", "+256 772 310 481", "Industrial City Division", "Kumi Road, taxi stage", "Road Maintenance", "Request to repair uneven road surface at the stage entrance.", "Low", "In Progress", now - timedelta(days=16)),
    ]
    connection.executemany(
        """INSERT INTO complaints
        (ticket_no, citizen_name, phone, division, location_detail, category, description, priority, status, logged_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        [(r[0], *r[1:9], r[9].isoformat(timespec="seconds")) for r in complaints],
    )


def init_db(reset=False):
    """Create the schema and seed clean demonstration rows when tables are empty."""
    with get_db() as connection:
        connection.executescript(SCHEMA)
        if reset:
            connection.execute("DELETE FROM businesses")
            connection.execute("DELETE FROM properties")
            connection.execute("DELETE FROM complaints")
        counts = [
            connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            for table in ("businesses", "properties", "complaints")
        ]
        if not any(counts):
            _seed_rows(connection)
