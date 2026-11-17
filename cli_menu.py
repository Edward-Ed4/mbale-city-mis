from database import get_db, init_db


def show_ward_summary():
    with get_db() as connection:
        rows = connection.execute(
            """SELECT division, COUNT(*) AS ward_count,
            ROUND(AVG(improved_sanitation_pct), 1) AS mean_coverage,
            SUM(CASE WHEN vulnerability_index = 'High' THEN 1 ELSE 0 END) AS high_vulnerability
            FROM wards GROUP BY division ORDER BY division"""
        ).fetchall()
    print("\nWARD-LEVEL SANITATION SUMMARY")
    print("-" * 92)
    for row in rows:
        print(
            f"{row['division']:<30} {row['ward_count']:>2} wards | "
            f"{row['mean_coverage']:>5.1f}% mean coverage | "
            f"{row['high_vulnerability']} high-vulnerability wards"
        )


def show_model_results():
    print("\nBETA REGRESSION SUMMARY")
    print("-" * 74)
    print(f"{'Variable':<22} {'Coefficient':>13} {'Std. error':>13} {'p-value':>10}")
    print(f"{'Household size':<22} {-0.6479:>13.4f} {0.2188:>13.4f} {'0.003':>10}")
    print(f"{'Unemployment':<22} {-0.0235:>13.4f} {0.0098:>13.4f} {'0.017':>10}")
    print(f"{'Constant':<22} {3.3527:>13.4f} {0.8323:>13.4f} {'0.000':>10}")
    print("58 observations | LR chi-square 19.29 | model p-value 0.0001")
    print("Log likelihood 17.05433")


def show_interventions():
    with get_db() as connection:
        rows = connection.execute(
            "SELECT programme_name, target_ward, status, lead_agency FROM interventions ORDER BY id"
        ).fetchall()
    print("\nINTERVENTIONS REGISTER")
    print("-" * 110)
    for row in rows:
        print(f"{row['programme_name']:<39} {row['target_ward']:<28} {row['coverage_pct']:>5.0f}% {row['status']:<17} {row['lead_agency']}")


def show_ward_register():
    with get_db() as connection:
        rows = connection.execute(
            """SELECT ward_name, division, total_households, improved_sanitation_pct,
            vulnerability_index, primary_vulnerable_group
            FROM wards ORDER BY division, ward_name"""
        ).fetchall()
    print("\nWARD-LEVEL SANITATION REGISTER")
    print("-" * 120)
    for row in rows:
        print(
            f"{row['ward_name']:<26} {row['division']:<27} {row['total_households']:>5} households "
            f"{row['improved_sanitation_pct']:>5.1f}% improved "
            f"{row['vulnerability_index']:<7} {row['primary_vulnerable_group']}"
        )


def main():
    init_db()
    actions = {"1": show_ward_register, "2": show_model_results, "3": show_interventions, "4": show_ward_summary}
    while True:
        print("\nMBALE CITY SANITATION ANALYTICS")
        print("1. Ward Data & Surveys")
        print("2. Vulnerability Model Summary")
        print("3. Intervention Tracker")
        print("4. Division Analytics")
        print("0. Exit")
        choice = input("Select an option: ").strip()
        if choice == "0":
            print("Goodbye.")
            break
        action = actions.get(choice)
        if action:
            action()
        else:
            print("Please choose an option from 0 to 4.")


if __name__ == "__main__":
    main()
