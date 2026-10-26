"""Parameterized read queries intended for future MCP tools (Milestone 7).

The MCP layer, not the LLM, chooses which employee_id to authorize. Never
allow an LLM to supply arbitrary SQL or unrestricted table names.
"""
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from .connection import open_connection


def to_json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: to_json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [to_json_safe(item) for item in value]
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    return value


def get_employee_profile(employee_id: str) -> dict | None:
    with open_connection() as conn:
        row = conn.execute(
            "SELECT * FROM employees WHERE employee_id = %s", (employee_id,)
        ).fetchone()
    return to_json_safe(row)


def get_pto_balance(employee_id: str, as_of_date: str | None = None) -> dict | None:
    """Read latest snapshot, optionally no later than as_of_date (YYYY-MM-DD)."""
    with open_connection() as conn:
        row = conn.execute(
            """SELECT * FROM pto_balances
               WHERE employee_id = %s AND as_of_date <= %s::date
               ORDER BY as_of_date DESC LIMIT 1""",
            (employee_id, as_of_date or "9999-12-31"),
        ).fetchone()
    return to_json_safe(row)


def get_wfa_balance(employee_id: str, year: int) -> dict | None:
    with open_connection() as conn:
        row = conn.execute(
            """SELECT * FROM wfa_balances
               WHERE employee_id = %s AND calendar_year = %s""",
            (employee_id, year),
        ).fetchone()
    return to_json_safe(row)


def get_benefits_status(employee_id: str, as_of_date: str | None = None) -> dict | None:
    with open_connection() as conn:
        row = conn.execute(
            """SELECT * FROM benefits
               WHERE employee_id = %s AND as_of_date <= %s::date
               ORDER BY as_of_date DESC LIMIT 1""",
            (employee_id, as_of_date or "9999-12-31"),
        ).fetchone()
    return to_json_safe(row)


def get_office(office_id: str) -> dict | None:
    with open_connection() as conn:
        row = conn.execute(
            "SELECT * FROM office_locations WHERE office_id = %s", (office_id,)
        ).fetchone()
        if row:
            weekdays = conn.execute(
                """SELECT weekday FROM office_working_days
                   WHERE office_id = %s
                   ORDER BY CASE weekday
                     WHEN 'Monday' THEN 1 WHEN 'Tuesday' THEN 2
                     WHEN 'Wednesday' THEN 3 WHEN 'Thursday' THEN 4
                     WHEN 'Friday' THEN 5 WHEN 'Saturday' THEN 6 ELSE 7 END""",
                (office_id,),
            ).fetchall()
            row["working_days"] = [r["weekday"] for r in weekdays]
    return to_json_safe(row)
