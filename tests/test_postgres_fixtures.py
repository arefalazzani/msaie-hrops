"""Offline referential-integrity checks (no Neon secrets required in CI)."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(filename):
    return json.loads((ROOT / "mock_data" / filename).read_text(encoding="utf-8"))


def test_employee_references_are_valid():
    employees = read("employees.json")
    ids = {e["employee_id"] for e in employees}
    office_ids = {o["office_id"] for o in read("office_locations.json")}
    assert len(ids) == len(employees)
    for employee in employees:
        assert employee["anchor_office"] in office_ids
        assert employee["manager_id"] is None or employee["manager_id"] in ids
    for source in ["pto_balances.json", "wfa_balances.json", "benefits.json", "hr_tickets.json"]:
        assert all(row["employee_id"] in ids for row in read(source))


def test_synthetic_manifest():
    assert read("manifest.json")["synthetic"] is True
