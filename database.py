import os
import sqlite3
from contextlib import contextmanager


DATABASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mbale_city.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS wards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ward_name TEXT NOT NULL UNIQUE,
    division TEXT NOT NULL CHECK (division IN ('Industrial City Division', 'Northern City Division')),
    total_households INTEGER NOT NULL CHECK (total_households > 0),
    improved_sanitation_pct REAL NOT NULL CHECK (improved_sanitation_pct BETWEEN 0 AND 100),
    unimproved_sanitation_pct REAL NOT NULL CHECK (unimproved_sanitation_pct BETWEEN 0 AND 100),
    vulnerability_index TEXT NOT NULL CHECK (vulnerability_index IN ('High', 'Medium', 'Low')),
    primary_vulnerable_group TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS interventions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    programme_name TEXT NOT NULL,
    target_ward TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('Active', 'Scaling', 'Needs Follow-up')),
    lead_agency TEXT NOT NULL,
    coverage_pct REAL NOT NULL DEFAULT 0 CHECK (coverage_pct BETWEEN 0 AND 100)
);
"""

ILLUSTRATIVE_WARD_NAMES = (
    "Namatala", "Busamaga", "Maluku", "Senior Quarters", "Nkoma", "Mooni",
    "Nabuyonga", "Bugema", "Industrial Ward", "Wanale", "Republic Street",
    "Naboa Road", "Pallisa Road",
    *(f"Illustrative Ward {number:02d}" for number in range(14, 59)),
)

VULNERABLE_GROUPS = (
    "Children under 5",
    "Low-income households",
    "Women & Girls",
    "Persons with disabilities",
    "Informal settlements",
    "Flood-prone communities",
)

INTERVENTION_ROWS = (
    ("Government Sanitation Programme", "Namatala, Maluku", "Active", "Government of Uganda", 68),
    ("Community-Led Total Sanitation (CLTS)", "Busamaga, Nkoma", "Scaling", "Mbale City Council", 52),
    ("WaterAid Sanitation Programme", "Mooni, Nabuyonga", "Needs Follow-up", "WaterAid / NGO partners", 34),
    ("Public Health Sanitation", "Senior Quarters, Bugema", "Active", "Mbale City Council", 76),
)


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


def _illustrative_ward_rows():
    rows = []
    for index, ward_name in enumerate(ILLUSTRATIVE_WARD_NAMES):
        ward_number = index + 1
        division = (
            "Industrial City Division"
            if ward_number % 2
            else "Northern City Division"
        )
        vulnerability = "High" if ward_number <= 14 else "Medium" if ward_number <= 36 else "Low"
        household_count = 240 + (ward_number * 137 % 1100)
        coverage = 35 + (ward_number * 19 + 11) % 41
        rows.append(
            (
                ward_name,
                division,
                household_count,
                float(coverage),
                round(100 - coverage, 2),
                vulnerability,
                VULNERABLE_GROUPS[(ward_number - 1) % len(VULNERABLE_GROUPS)],
            )
        )
    return rows


def _migrate_interventions(connection):
    table_sql = connection.execute(
        "SELECT sql FROM sqlite_master WHERE type = 'table' AND name = 'interventions'"
    ).fetchone()[0]
    columns = {
        row["name"]
        for row in connection.execute("PRAGMA table_info(interventions)").fetchall()
    }
    if "needs follow-up" in table_sql.lower() and "coverage_pct" in columns:
        connection.execute(
            """UPDATE interventions SET programme_name = ?
            WHERE programme_name = ?""",
            ("WaterAid Sanitation Programme", "NGO Sanitation Programmes"),
        )
        return

    existing_rows = connection.execute("SELECT * FROM interventions").fetchall()
    connection.execute("ALTER TABLE interventions RENAME TO interventions_legacy")
    connection.execute(
        """CREATE TABLE interventions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            programme_name TEXT NOT NULL,
            target_ward TEXT NOT NULL,
            status TEXT NOT NULL CHECK (status IN ('Active', 'Scaling', 'Needs Follow-up')),
            lead_agency TEXT NOT NULL,
            coverage_pct REAL NOT NULL DEFAULT 0 CHECK (coverage_pct BETWEEN 0 AND 100)
        )"""
    )
    migrated_rows = []
    for row in existing_rows:
        old_status = row["status"]
        status = {
            "Scaled": "Scaling",
            "Monitored": "Active",
            "Underperforming": "Needs Follow-up",
        }.get(old_status, old_status)
        coverage = row["coverage_pct"] if "coverage_pct" in columns else {
            "Active": 68,
            "Scaling": 52,
            "Needs Follow-up": 34,
        }.get(status, 0)
        programme_name = {
            "NGO Sanitation Programmes": "WaterAid Sanitation Programme",
        }.get(row["programme_name"], row["programme_name"])
        migrated_rows.append(
            (row["id"], programme_name, row["target_ward"], status, row["lead_agency"], coverage)
        )
    connection.executemany(
        """INSERT INTO interventions
        (id, programme_name, target_ward, status, lead_agency, coverage_pct)
        VALUES (?, ?, ?, ?, ?, ?)""",
        migrated_rows,
    )
    connection.execute("DROP TABLE interventions_legacy")


def init_db():
    """Create the sanitation schema and seed illustrative rows only when empty."""
    with get_db() as connection:
        connection.executescript(SCHEMA)
        _migrate_interventions(connection)
        ward_count = connection.execute("SELECT COUNT(*) FROM wards").fetchone()[0]
        if ward_count == 0:
            connection.executemany(
                """INSERT INTO wards
                (ward_name, division, total_households, improved_sanitation_pct,
                 unimproved_sanitation_pct, vulnerability_index, primary_vulnerable_group)
                VALUES (?, ?, ?, ?, ?, ?, ?)""",
                _illustrative_ward_rows(),
            )
        intervention_count = connection.execute(
            "SELECT COUNT(*) FROM interventions"
        ).fetchone()[0]
        if intervention_count == 0:
            connection.executemany(
                """INSERT INTO interventions
                (programme_name, target_ward, status, lead_agency, coverage_pct)
                VALUES (?, ?, ?, ?, ?)""",
                INTERVENTION_ROWS,
            )
