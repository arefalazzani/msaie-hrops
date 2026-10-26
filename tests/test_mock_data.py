"""Milestone 3 tests; run with python -m pytest -v."""
from scripts.validate_mock_data import load, validate_dataset


def test_mock_data_integrity():
    counts = validate_dataset()
    assert counts["employees"] == 12


def test_demo_pto_employee_has_balance():
    # Eligibility still requires policy checks: notice, dates, manager approval.
    balances = {r["employee_id"]: r for r in load("pto_balances.json")}
    assert balances["VND-E001"]["available_days"] >= 3


def test_six_week_wfa_requires_exception_review():
    # Approx 30 working days exceeds the remaining allowance of E003.
    balances = {r["employee_id"]: r for r in load("wfa_balances.json")}
    assert balances["VND-E003"]["remaining_working_days"] < 30


def test_noneligible_personas_exist():
    staff = {r["employee_id"]: r for r in load("employees.json")}
    assert staff["VND-E006"]["work_arrangement"] == "site_based"
    assert staff["VND-E009"]["probation_status"] == "in_progress"
    assert staff["VND-E012"]["performance_improvement_plan_active"] is True
