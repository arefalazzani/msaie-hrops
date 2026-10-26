"""Idempotently import Milestone 3 synthetic JSON into PostgreSQL.

Run: python -m scripts.seed_database
This updates seed-defined rows, but does not delete unrelated/new mock tickets.
"""
import json
from pathlib import Path

from psycopg import sql

from db.connection import open_connection

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "mock_data"


def load_json(name):
    with (DATA_DIR / name).open(encoding="utf-8") as f:
        return json.load(f)


def upsert(cur, table, row, key_columns):
    """Values are parameterized; names originate only from our hard-coded mappings."""
    cols = list(row)
    non_keys = [column for column in cols if column not in key_columns]
    insert = sql.SQL("INSERT INTO {} ({}) VALUES ({}) ON CONFLICT ({}) ").format(
        sql.Identifier(table),
        sql.SQL(", ").join(map(sql.Identifier, cols)),
        sql.SQL(", ").join(sql.Placeholder() for _ in cols),
        sql.SQL(", ").join(map(sql.Identifier, key_columns)),
    )
    if non_keys:
        action = sql.SQL("DO UPDATE SET ") + sql.SQL(", ").join(
            sql.SQL("{} = EXCLUDED.{}").format(sql.Identifier(col), sql.Identifier(col))
            for col in non_keys
        )
    else:
        action = sql.SQL("DO NOTHING")
    cur.execute(insert + action, [row[col] for col in cols])


def main():
    manifest = load_json("manifest.json")
    if manifest.get("synthetic") is not True:
        raise RuntimeError("Refusing to seed: manifest does not confirm synthetic=true")

    offices = load_json("office_locations.json")
    employees = load_json("employees.json")
    pto = load_json("pto_balances.json")
    wfa = load_json("wfa_balances.json")
    benefits = load_json("benefits.json")
    tickets = load_json("hr_tickets.json")

    with open_connection(admin=True) as conn:
        with conn.cursor() as cur:
            for item in offices:
                upsert(cur, "office_locations", {
                    k: v for k, v in item.items() if k != "working_days"
                }, ("office_id",))
                for day in item["working_days"]:
                    upsert(cur, "office_working_days", {
                        "office_id": item["office_id"], "weekday": day
                    }, ("office_id", "weekday"))

            # The manager foreign key is DEFERRABLE: manager rows may appear later.
            for item in employees:
                upsert(cur, "employees", item, ("employee_id",))
            for item in pto:
                upsert(cur, "pto_balances", item, ("employee_id", "as_of_date"))
            for item in wfa:
                upsert(cur, "wfa_balances", item, ("employee_id", "calendar_year"))
            for item in benefits:
                upsert(cur, "benefits", item, ("employee_id", "as_of_date"))
            for item in tickets:
                upsert(cur, "hr_tickets", item, ("ticket_id",))

    print("Import completed and committed:")
    for name, rows in [
        ("offices", offices), ("employees", employees), ("pto_balances", pto),
        ("wfa_balances", wfa), ("benefits", benefits), ("hr_tickets", tickets),
    ]:
        print(f"  {name}: {len(rows)} seed rows")
    print("Safe to re-run; source snapshot date is 2026-10-24.")


if __name__ == "__main__":
    main()
