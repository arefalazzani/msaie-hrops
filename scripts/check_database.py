"""Verify database rows and read-path used by future MCP tools."""
from db.connection import open_connection
from db.repository import get_employee_profile, get_pto_balance, get_wfa_balance

EXPECTED_COUNTS = {
    "office_locations": 2,
    "office_working_days": 10,
    "employees": 12,
    "pto_balances": 12,
    "wfa_balances": 12,
    "benefits": 12,
    "hr_tickets": 3,
}


def main():
    with open_connection() as conn:
        for table, expected in EXPECTED_COUNTS.items():
            # Table names are hard-coded, not user input.
            actual = conn.execute(f"SELECT COUNT(*) AS count FROM {table}").fetchone()["count"]
            assert actual >= expected, (table, expected, actual)
            print(f"PASS {table}: {actual} rows (at least {expected})")

    emp = get_employee_profile("VND-E001")
    assert emp and emp["display_name"] == "Amina Demo"
    pto = get_pto_balance("VND-E001", "2026-10-24")
    assert pto and pto["available_days"] == 12
    wfa = get_wfa_balance("VND-E003", 2026)
    assert wfa and wfa["remaining_working_days"] == 16
    print("PASS sample SQL repository reads (employee, PTO, WFA).")
    print("Milestone 3 PostgreSQL upgrade verified.")


if __name__ == "__main__":
    main()
