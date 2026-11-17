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
    improved_sanitation_count INTEGER CHECK (improved_sanitation_count IS NULL OR improved_sanitation_count >= 0),
    unimproved_sanitation_count INTEGER CHECK (unimproved_sanitation_count IS NULL OR unimproved_sanitation_count >= 0),
    open_defecation_count INTEGER CHECK (open_defecation_count IS NULL OR open_defecation_count >= 0),
    improved_sanitation_pct REAL NOT NULL CHECK (improved_sanitation_pct BETWEEN 0 AND 100),
    unimproved_sanitation_pct REAL NOT NULL CHECK (unimproved_sanitation_pct BETWEEN 0 AND 100),
    average_household_size REAL CHECK (average_household_size IS NULL OR average_household_size > 0),
    unemployment_rate_pct REAL CHECK (unemployment_rate_pct IS NULL OR unemployment_rate_pct BETWEEN 0 AND 100),
    total_population INTEGER CHECK (total_population IS NULL OR total_population > 0),
    vulnerability_index TEXT NOT NULL CHECK (vulnerability_index IN ('High', 'Medium', 'Low')),
    primary_vulnerable_group TEXT NOT NULL DEFAULT 'Not specified in source'
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

SEED_WARDS = (
    ("Boma Ward", "Industrial City Division", 490, 459, 31, 0, 3.5, 10.9, 1716),
    ("Bukasakya Ward", "Industrial City Division", 2093, 1533, 551, 9, 3.7, 17.8, 7847),
    ("Bumboi Ward", "Industrial City Division", 808, 225, 573, 10, 3.2, 3.6, 2582),
    ("Bumutoto Ward", "Industrial City Division", 3327, 1863, 1426, 38, 3.9, 20.9, 12860),
    ("Busamaga East Ward", "Industrial City Division", 627, 427, 198, 2, 4.1, 13.4, 2585),
    ("Busamaga West Ward", "Industrial City Division", 1736, 984, 748, 4, 3.4, 19.4, 5853),
    ("Doko Ward Industrial", "Industrial City Division", 1068, 866, 199, 3, 3.6, 17.7, 3897),
    ("Kijja Ward", "Industrial City Division", 356, 272, 83, 1, 3.5, 7.6, 1262),
    ("Malukhu Ward", "Industrial City Division", 2054, 1709, 325, 20, 3.6, 17.5, 7378),
    ("Marale Ward", "Industrial City Division", 2326, 1514, 791, 21, 4.0, 21.6, 9235),
    ("Masaba Ward", "Industrial City Division", 822, 780, 42, 0, 3.8, 14.9, 3103),
    ("Mooni-Nambale Ward", "Industrial City Division", 822, 321, 488, 13, 3.8, 14.2, 3162),
    ("Mooni-Wanale Ward", "Industrial City Division", 697, 387, 306, 4, 3.1, 22.4, 2193),
    ("Mukhubu Ward", "Industrial City Division", 1040, 711, 314, 15, 3.4, 24.0, 3541),
    ("Muyanda Ward", "Industrial City Division", 498, 106, 356, 36, 4.7, 35.9, 2346),
    ("Nabitiri Ward", "Industrial City Division", 3135, 2073, 1024, 38, 4.1, 15.4, 12826),
    ("Namalogo Ward", "Industrial City Division", 1499, 687, 808, 4, 4.5, 39.7, 6725),
    ("Namatala Ward", "Industrial City Division", 4976, 3733, 1227, 16, 3.3, 21.9, 16227),
    ("Napooli Central Ward", "Industrial City Division", 404, 297, 104, 3, 3.1, 21.1, 1269),
    ("Napooli Lower Ward", "Industrial City Division", 548, 361, 158, 29, 2.9, 4.2, 1602),
    ("Napooli Upper Ward", "Industrial City Division", 331, 209, 120, 2, 3.3, 55.8, 1104),
    ("South Central Ward", "Industrial City Division", 479, 449, 29, 1, 3.5, 7.7, 1680),
    ("Tsabanyanya Ward", "Industrial City Division", 2023, 589, 1322, 112, 4.1, 22.9, 8205),
    ("Wakhwaba Central Ward", "Industrial City Division", 500, 269, 231, 0, 3.2, 24.1, 1584),
    ("Wakhwaba Lower Ward", "Industrial City Division", 280, 179, 101, 0, 3.3, 35.6, 935),
    ("Wakhwaba Upper Ward", "Industrial City Division", 530, 436, 92, 2, 3.6, 20.8, 1901),
    ("Afya Ward", "Northern City Division", 1869, 1357, 511, 1, 4.1, 23.8, 7618),
    ("Aisa Ward", "Northern City Division", 1547, 322, 1175, 50, 4.1, 22.1, 6388),
    ("Bukikali", "Northern City Division", 576, 173, 352, 51, 4.5, 30.4, 2589),
    ("Bulweta", "Northern City Division", 1697, 462, 1190, 45, 4.1, 16.8, 6873),
    ("Bumuluya", "Northern City Division", 705, 323, 370, 12, 4.4, 19.8, 3108),
    ("Bumuyanga", "Northern City Division", 795, 153, 625, 17, 4.0, 19.8, 3169),
    ("Buwangolo", "Northern City Division", 595, 84, 499, 12, 4.5, 22.8, 2670),
    ("Bwana Ward", "Northern City Division", 515, 156, 309, 50, 4.6, 26.9, 2391),
    ("Doko Ward North", "Northern City Division", 1233, 486, 736, 11, 4.2, 39.7, 5210),
    ("Fika Salama Ward", "Northern City Division", 724, 460, 254, 10, 4.9, 39.5, 3553),
    ("Iu-Iu Ward", "Northern City Division", 81, 69, 11, 1, 2.5, 4.8, 201),
    ("Kihuno", "Northern City Division", 749, 203, 520, 26, 4.4, 47.2, 3272),
    ("Kireka-Nakaloke SC Ward", "Northern City Division", 421, 184, 237, 0, 4.2, 47.8, 1750),
    ("Kireka-Nakaloke TC Ward", "Northern City Division", 669, 219, 449, 1, 4.8, 12.9, 3187),
    ("Kolonyi Ward", "Northern City Division", 376, 231, 122, 23, 4.3, 28.0, 1599),
    ("Lwasso", "Northern City Division", 405, 33, 356, 16, 4.3, 49.3, 1746),
    ("Mukunja Ward", "Northern City Division", 739, 503, 228, 8, 4.7, 10.1, 3444),
    ("Nabuyonga Ward", "Northern City Division", 2726, 2251, 469, 6, 3.2, 15.6, 3690),
    ("Nabweya Ward", "Northern City Division", 2769, 2007, 748, 14, 4.1, 25.7, 11365),
    ("Najja Ward", "Northern City Division", 1491, 1356, 131, 4, 4.2, 24.0, 6203),
    ("Nakaloke Ward", "Northern City Division", 1520, 907, 602, 11, 4.7, 24.4, 7071),
    ("Namabasa Ward", "Northern City Division", 1586, 647, 909, 30, 4.3, 25.8, 6825),
    ("Namagumba Ward", "Northern City Division", 1863, 1078, 760, 25, 4.0, 38.5, 7488),
    ("Namakwekwe Ward", "Northern City Division", 3496, 2889, 603, 4, 3.3, 16.0, 11540),
    ("Nambulu/Kasanja Ward", "Northern City Division", 2009, 1177, 811, 21, 4.2, 23.0, 8508),
    ("Namunsi Ward", "Northern City Division", 848, 261, 578, 9, 3.8, 19.0, 3241),
    ("Nanyunza", "Northern City Division", 573, 163, 392, 18, 4.8, 39.1, 2724),
    ("Nkoma-Namanyonyi Ward", "Northern City Division", 3027, 1704, 1307, 16, 3.9, 26.4, 11662),
    ("Nkoma-Northern Ward", "Northern City Division", 2702, 1642, 1038, 22, 3.1, 17.4, 8374),
    ("North Central Ward", "Northern City Division", 594, 565, 28, 1, 3.9, 8.2, 2309),
    ("Rock Ward", "Northern City Division", 1437, 800, 634, 3, 4.2, 16.0, 6085),
    ("Salem Ward", "Northern City Division", 485, 161, 320, 4, 4.5, 13.7, 2163),
)

LEGACY_SEED_NAMES = (
    "Namatala", "Maluku", "Industrial Ward", "Namabasa", "Busajabwemi",
    "Naboa", "Republic Street", "Pallisa Road", "Kumi Road", "Senior Quarters",
    "Mooni", "Nkoma", "Busamaga", "Nabuyonga", "Bugema", "Bufumbo",
    "Lwangosia", "Wanale", "Nyondo", "Naboa Road",
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


def vulnerability_for_coverage(coverage):
    if coverage < 40:
        return "High"
    if coverage <= 60:
        return "Medium"
    return "Low"


def _seed_ward_rows():
    rows = []
    for (
        ward_name,
        division,
        household_count,
        improved_count,
        unimproved_count,
        open_defecation_count,
        average_household_size,
        unemployment_rate_pct,
        total_population,
    ) in SEED_WARDS:
        coverage = round(improved_count / household_count * 100, 2)
        rows.append(
            (
                ward_name,
                division,
                household_count,
                improved_count,
                unimproved_count,
                open_defecation_count,
                float(coverage),
                round(unimproved_count / household_count * 100, 2),
                average_household_size,
                unemployment_rate_pct,
                total_population,
                vulnerability_for_coverage(coverage),
                "Not specified in source",
            )
        )
    return rows


def _migrate_ward_columns(connection):
    columns = {
        row["name"]
        for row in connection.execute("PRAGMA table_info(wards)").fetchall()
    }
    new_columns = (
        ("improved_sanitation_count", "INTEGER CHECK (improved_sanitation_count IS NULL OR improved_sanitation_count >= 0)"),
        ("unimproved_sanitation_count", "INTEGER CHECK (unimproved_sanitation_count IS NULL OR unimproved_sanitation_count >= 0)"),
        ("open_defecation_count", "INTEGER CHECK (open_defecation_count IS NULL OR open_defecation_count >= 0)"),
        ("average_household_size", "REAL CHECK (average_household_size IS NULL OR average_household_size > 0)"),
        ("unemployment_rate_pct", "REAL CHECK (unemployment_rate_pct IS NULL OR unemployment_rate_pct BETWEEN 0 AND 100)"),
        ("total_population", "INTEGER CHECK (total_population IS NULL OR total_population > 0)"),
    )
    for name, definition in new_columns:
        if name not in columns:
            connection.execute(f"ALTER TABLE wards ADD COLUMN {name} {definition}")


def _migrate_ward_seed(connection):
    version = connection.execute("PRAGMA user_version").fetchone()[0]
    insert_sql = """INSERT INTO wards
        (ward_name, division, total_households, improved_sanitation_count,
         unimproved_sanitation_count, open_defecation_count,
         improved_sanitation_pct, unimproved_sanitation_pct,
         average_household_size, unemployment_rate_pct, total_population,
         vulnerability_index, primary_vulnerable_group)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
    seed_rows = _seed_ward_rows()

    if version < 2:
        legacy_names = (*LEGACY_SEED_NAMES,)
        placeholders = ", ".join("?" for _ in legacy_names)
        connection.execute(
            f"""DELETE FROM wards
            WHERE ward_name LIKE ? OR ward_name IN ({placeholders})""",
            ("Illustrative Ward %", *legacy_names),
        )
        updates = ", ".join(
            f"{column} = excluded.{column}"
            for column in (
                "division", "total_households", "improved_sanitation_count",
                "unimproved_sanitation_count", "open_defecation_count",
                "improved_sanitation_pct", "unimproved_sanitation_pct",
                "average_household_size", "unemployment_rate_pct",
                "total_population", "vulnerability_index",
                "primary_vulnerable_group",
            )
        )
        connection.executemany(
            f"{insert_sql} ON CONFLICT(ward_name) DO UPDATE SET {updates}",
            seed_rows,
        )
        connection.execute("PRAGMA user_version = 2")
        return

    connection.executemany(
        insert_sql.replace("INSERT INTO wards", "INSERT OR IGNORE INTO wards"),
        seed_rows,
    )


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
    """Create the schema, migrate existing records, and seed missing wards."""
    with get_db() as connection:
        connection.executescript(SCHEMA)
        _migrate_interventions(connection)
        _migrate_ward_columns(connection)
        _migrate_ward_seed(connection)
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
