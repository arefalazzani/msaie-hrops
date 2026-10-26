"""Validate Vendelligent mock HR fixtures with only the Python standard library.

Run from project root: python scripts/validate_mock_data.py
No real HR action is made; no network access or secrets are required.
"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MOCK = ROOT / "mock_data"


def load(filename: str):
    with (MOCK / filename).open(encoding="utf-8") as f:
        return json.load(f)


def five_years_completed(start: date, as_of: date) -> bool:
    try:
        anniversary = start.replace(year=start.year + 5)
    except ValueError:  # Feb 29
        anniversary = start.replace(year=start.year + 5, day=28)
    return as_of >= anniversary


def validate_dataset() -> dict[str, int]:
    manifest = load("manifest.json")
    as_of = date.fromisoformat(manifest["as_of_date"])
    assert manifest["synthetic"] is True

    employees = load("employees.json")
    pto = load("pto_balances.json")
    wfa = load("wfa_balances.json")
    benefits = load("benefits.json")
    offices = load("office_locations.json")
    tickets = load("hr_tickets.json")

    ids = [e["employee_id"] for e in employees]
    assert len(ids) == len(set(ids)), "Employee IDs must be unique"
    by_id = {e["employee_id"]: e for e in employees}

    office_names = {o["office_id"] for o in offices}
    assert office_names == {"Riyadh HQ", "Dubai Office"}
    assert len(office_names) == len(offices)

    for e in employees:
        assert e["email"].endswith("@example.com"), "Never use real email domains"
        assert e["employment_type"] in {"FT", "PT", "IN", "CT"}
        assert e["employment_status"] == "active"
        assert date.fromisoformat(e["start_date"]) <= as_of
        assert e["anchor_office"] in office_names
        assert e["work_site"] in office_names | {"Remote Engineering Hub"}
        assert e["probation_status"] in {"completed", "in_progress", "not_applicable"}
        assert e["manager_id"] is None or e["manager_id"] in by_id
        assert e["manager_id"] != e["employee_id"]
        if e["employment_type"] == "PT":
            assert 20 <= e["contracted_hours_per_week"] <= 32
        if e["employment_type"] == "FT":
            assert e["contracted_hours_per_week"] == 40

    for eid in ids:
        visited = set()
        current = eid
        while current is not None:
            assert current not in visited, f"Cyclic manager hierarchy at {eid}"
            visited.add(current)
            current = by_id[current]["manager_id"]

    for filename, records in [
        ("pto_balances.json", pto),
        ("wfa_balances.json", wfa),
        ("benefits.json", benefits),
    ]:
        keys = [r["employee_id"] for r in records]
        assert len(keys) == len(set(keys)), f"Duplicate ID in {filename}"
        assert set(keys) == set(ids), f"Missing or unknown employees in {filename}"

    for p in pto:
        e = by_id[p["employee_id"]]
        emp_type = e["employment_type"]
        start = date.fromisoformat(e["start_date"])
        entitlement = 30.0 if five_years_completed(start, as_of) else 22.0
        if emp_type == "PT":
            entitlement *= e["contracted_hours_per_week"] / 40
        elif emp_type == "CT":
            entitlement = 0.0
        elif emp_type == "IN":
            entitlement = None
        assert p["annual_entitlement_days"] == entitlement, p["employee_id"]
        assert p["as_of_date"] == manifest["as_of_date"]
        assert p["unit"] == "working_days"
        assert p["available_days"] >= 0
        assert 0 <= p["carryover_days_remaining"] <= 5
        # The snapshot is after the 31 March expiration cutoff.
        assert p["carryover_days_remaining"] == 0
        if emp_type == "CT":
            assert p["available_days"] == 0
        if emp_type == "IN":
            assert p["monthly_accrual_days"] == 1.0

    for w in wfa:
        e = by_id[w["employee_id"]]
        allowed_type = e["employment_type"] in {"FT", "PT"}
        site_tech = (e["department"] == "Hardware & Field Operations"
                     and e["work_arrangement"] == "site_based")
        cap = 20 if allowed_type and not site_tech else 0
        assert w["calendar_year"] == as_of.year
        assert w["annual_allowance_working_days"] == cap
        assert 0 <= w["used_working_days"] <= cap
        assert w["remaining_working_days"] == cap - w["used_working_days"]

    for b in benefits:
        e = by_id[b["employee_id"]]
        t = e["employment_type"]
        probation_done = e["probation_status"] == "completed"
        expected_med = ("full_employee" if t in {"FT", "PT"}
                        else "emergency_only" if t == "IN"
                        else "not_eligible")
        assert b["medical_coverage"] == expected_med
        assert 0 <= b["medical_dependents_enrolled_count"] <= 4
        if t != "FT" or not probation_done:
            assert b["medical_dependents_enrolled_count"] == 0
        assert b["life_disability_coverage_active"] == (t == "FT" and probation_done)
        assert 0 <= b["learning_budget_remaining_sar"] <= 3000
        if t != "FT" or not probation_done:
            assert b["learning_budget_remaining_sar"] == 0
        assert 0 <= b["wellness_allowance_remaining_sar"] <= 1200
        if t != "FT":
            assert b["wellness_allowance_remaining_sar"] == 0
        assert 0 <= b["eap_sessions_used_ytd"] <= 6
        assert b["as_of_date"] == manifest["as_of_date"]

    ticket_ids = [t["ticket_id"] for t in tickets]
    assert len(ticket_ids) == len(set(ticket_ids))
    for t in tickets:
        assert t["employee_id"] in by_id
        assert t["priority"] in {"P1", "P2", "P3", "P4"}
        assert t["status"] in {
            "New", "Triaged", "In Progress", "Awaiting Employee", "Resolved", "Closed"
        }
        assert t["is_mock"] is True
        assert t["summary"] and "@" not in t["summary"]

    for filename, expected_count in manifest["files"].items():
        assert len(load(filename)) == expected_count

    return {
        "employees": len(employees),
        "pto_balances": len(pto),
        "wfa_balances": len(wfa),
        "benefits": len(benefits),
        "offices": len(offices),
        "tickets": len(tickets)
    }


if __name__ == "__main__":
    counts = validate_dataset()
    for kind, count in counts.items():
        print(f"PASS {kind}: {count}")
    print("PASS All data integrity and policy-consistency checks passed.")
