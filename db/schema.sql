-- Vendelligent HR: synthetic-only, normalized PostgreSQL schema.
-- This script is safe to re-run (IF NOT EXISTS). For future schema changes,
-- use migrations rather than editing already deployed columns in place.

CREATE TABLE IF NOT EXISTS office_locations (
    office_id TEXT PRIMARY KEY,
    country_code CHAR(2) NOT NULL,
    country TEXT NOT NULL,
    time_zone TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS office_working_days (
    office_id TEXT NOT NULL REFERENCES office_locations(office_id),
    weekday TEXT NOT NULL CHECK (weekday IN (
        'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'
    )),
    PRIMARY KEY (office_id, weekday)
);

CREATE TABLE IF NOT EXISTS employees (
    employee_id TEXT PRIMARY KEY,
    display_name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    employment_type TEXT NOT NULL CHECK (employment_type IN ('FT', 'PT', 'IN', 'CT')),
    job_title TEXT NOT NULL,
    grade TEXT,
    department TEXT NOT NULL,
    work_site TEXT,
    anchor_office TEXT NOT NULL REFERENCES office_locations(office_id),
    work_arrangement TEXT,
    start_date DATE NOT NULL,
    contract_end_date DATE,
    manager_id TEXT REFERENCES employees(employee_id) DEFERRABLE INITIALLY DEFERRED,
    contracted_hours_per_week NUMERIC(6,2),
    probation_status TEXT,
    performance_improvement_plan_active BOOLEAN NOT NULL DEFAULT FALSE,
    disciplinary_warning_active BOOLEAN NOT NULL DEFAULT FALSE,
    employment_status TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS pto_balances (
    employee_id TEXT NOT NULL REFERENCES employees(employee_id),
    as_of_date DATE NOT NULL,
    unit TEXT NOT NULL,
    annual_entitlement_days NUMERIC(8,2),
    monthly_accrual_days NUMERIC(8,2),
    available_days NUMERIC(8,2) NOT NULL CHECK (available_days >= 0),
    carryover_days_remaining NUMERIC(8,2) NOT NULL CHECK (carryover_days_remaining >= 0),
    balance_source TEXT NOT NULL,
    PRIMARY KEY (employee_id, as_of_date)
);

CREATE TABLE IF NOT EXISTS wfa_balances (
    employee_id TEXT NOT NULL REFERENCES employees(employee_id),
    calendar_year INTEGER NOT NULL,
    annual_allowance_working_days INTEGER NOT NULL CHECK (annual_allowance_working_days >= 0),
    used_working_days INTEGER NOT NULL CHECK (used_working_days >= 0),
    remaining_working_days INTEGER NOT NULL CHECK (remaining_working_days >= 0),
    usage_source TEXT NOT NULL,
    note TEXT,
    PRIMARY KEY (employee_id, calendar_year),
    CHECK (annual_allowance_working_days = used_working_days + remaining_working_days)
);

CREATE TABLE IF NOT EXISTS benefits (
    employee_id TEXT NOT NULL REFERENCES employees(employee_id),
    as_of_date DATE NOT NULL,
    medical_coverage TEXT,
    medical_dependents_enrolled_count INTEGER NOT NULL DEFAULT 0 CHECK (medical_dependents_enrolled_count >= 0),
    life_disability_coverage_active BOOLEAN NOT NULL DEFAULT FALSE,
    learning_budget_remaining_sar NUMERIC(12,2),
    wellness_allowance_remaining_sar NUMERIC(12,2),
    eap_sessions_used_ytd INTEGER NOT NULL DEFAULT 0 CHECK (eap_sessions_used_ytd >= 0),
    benefits_source TEXT,
    PRIMARY KEY (employee_id, as_of_date)
);

CREATE TABLE IF NOT EXISTS hr_tickets (
    ticket_id TEXT PRIMARY KEY,
    employee_id TEXT NOT NULL REFERENCES employees(employee_id),
    category TEXT NOT NULL,
    priority TEXT,
    status TEXT NOT NULL,
    summary TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    is_mock BOOLEAN NOT NULL DEFAULT TRUE CHECK (is_mock = TRUE)
);

CREATE INDEX IF NOT EXISTS idx_employees_manager ON employees(manager_id);
CREATE INDEX IF NOT EXISTS idx_hr_tickets_employee ON hr_tickets(employee_id);
CREATE INDEX IF NOT EXISTS idx_pto_employee_date ON pto_balances(employee_id, as_of_date DESC);
CREATE INDEX IF NOT EXISTS idx_benefits_employee_date ON benefits(employee_id, as_of_date DESC);
