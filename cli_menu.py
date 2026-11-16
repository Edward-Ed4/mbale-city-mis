from database import get_db, init_db


def show_businesses():
    with get_db() as connection:
        rows = connection.execute(
            "SELECT license_no, business_name, owner_name, division, annual_fee_ugx, status FROM businesses ORDER BY id"
        ).fetchall()
    print("\nBUSINESS & TRADING LICENSES")
    print("-" * 98)
    for row in rows:
        print(f"{row['license_no']:<21} {row['business_name']:<27} {row['owner_name']:<20} {row['status']:<8} UGX {row['annual_fee_ugx']:,}")


def show_properties():
    with get_db() as connection:
        rows = connection.execute(
            "SELECT plot_no, owner_name, division, annual_rate_ugx, payment_status FROM properties ORDER BY plot_no"
        ).fetchall()
    print("\nPROPERTY RATES")
    print("-" * 85)
    for row in rows:
        print(f"{row['plot_no']:<15} {row['owner_name']:<22} {row['division']:<27} UGX {row['annual_rate_ugx']:>10,}  {row['payment_status']}")


def show_complaints():
    with get_db() as connection:
        rows = connection.execute(
            "SELECT ticket_no, category, location_detail, priority, status FROM complaints ORDER BY logged_at DESC"
        ).fetchall()
    print("\nCITIZEN SERVICE REQUESTS")
    print("-" * 100)
    for row in rows:
        print(f"{row['ticket_no']:<18} {row['category']:<22} {row['location_detail']:<34} {row['priority']:<7} {row['status']}")


def show_revenue():
    with get_db() as connection:
        license_revenue = connection.execute(
            "SELECT COALESCE(SUM(annual_fee_ugx), 0) FROM businesses WHERE status = 'Paid'"
        ).fetchone()[0]
        property_revenue = connection.execute(
            "SELECT COALESCE(SUM(annual_rate_ugx), 0) FROM properties WHERE payment_status = 'Cleared'"
        ).fetchone()[0]
        pending = connection.execute(
            "SELECT COUNT(*) FROM businesses WHERE status = 'Pending'"
        ).fetchone()[0]
    print("\nREVENUE SUMMARY")
    print("-" * 38)
    print(f"Collected business license fees: UGX {license_revenue:,}")
    print(f"Collected property rates:        UGX {property_revenue:,}")
    print(f"Total revenue collected:         UGX {license_revenue + property_revenue:,}")
    print(f"Pending license payments:        {pending}")


def main():
    init_db()
    actions = {"1": show_businesses, "2": show_properties, "3": show_complaints, "4": show_revenue}
    while True:
        print("\nMBALE CITY COUNCIL | INFORMATION SYSTEM")
        print("1. Business Licenses")
        print("2. Property Rates")
        print("3. Citizen Complaints")
        print("4. Revenue Summary")
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
