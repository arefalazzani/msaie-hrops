# Vendelligent Synthetic HR Data — Milestone 3

**Purpose:** Offline, synthetic structured fixtures for the Quantic HR Agent.
No real employee names, addresses, email accounts, benefits or HR cases are used.

## Snapshot and scope
- Snapshot date: **2026-10-24**. Treat balances as a fixed point-in-time example.
- All `employee_id` references are stable and shared across datasets.
- `@example.com` addresses are fictitious; never send messages to them.
- All operational actions on these datasets are **mock actions** only.
- The policy documents are the source of truth for eligibility and rules.
  These JSON fixtures report facts or recorded balances, **not approvals**.
- Do **not** commit actual employee data or secrets into `mock_data/`.

## Files
| File | Purpose |
| --- | --- |
| `employees.json` | Employee profile, type, job, grade, manager, anchor office, probation, PIP and warning flags |
| `pto_balances.json` | Fixed PTO balances in working days, annual entitlement and intern monthly accrual |
| `wfa_balances.json` | Calendar-year international Work-from-Anywhere allowance used and remaining |
| `benefits.json` | Medical status, dependants enrolled (aggregate only), insurance flags, remaining allowance balances, EAP usage count |
| `office_locations.json` | Riyadh and Dubai anchor-office calendars and time zones |
| `hr_tickets.json` | Existing, clearly mocked PeopleDesk cases |
| `manifest.json` | Date, version, provenance, counts and synthetic-data declaration |

**Terminology:** FT = full-time, PT = part-time, CT = contractor, IN = intern.
**Not modelled:** payroll details, national ID, full names of dependants, medical history,
visa information, actual leave requests, approvals or exact public-holiday calendars.
Those are not required to demonstrate the two selected agent workflows.

## Sample identities / intended tests
- `VND-E001` — Amina Demo, Riyadh AI engineer, **12 PTO days available**.
  Example: 3-day PTO request. The assistant still has to check notice, manager approval and dates.
- `VND-E003` — Noor Demo, Remote Engineering Hub, Riyadh anchor office,
  **16 WFA working days remaining**. A 6-week trip (roughly 30 working days)
  to an approved country exceeds the standard annual allowance and trip-length limit.
- `VND-E004` — Sara Demo, 20-hour PT employee in Dubai, **11 days annual pro-rata entitlement**.
  Employee medical cover only, no eligible dependants.
- `VND-E006` — Malik Demo, site-based Field Operations technician.
  WFA is not available despite full-time employment.
- `VND-E007` — Rami Demo, intern, 1-day-per-month leave rule.
- `VND-E008` — Yasmin Demo, contractor, no PTO accrual.
- `VND-E009` — Nadia Demo, new hire **still in probation and first 60 days**.
  PTO accrues but normally cannot yet be taken; WFA not eligible before probation ends.
- `VND-E012` — Lina Demo, active performance-improvement plan, WFA ineligible.
- `VND-E002`, `VND-E010`, `VND-E011` — FT employees with 5+ completed years,
  having 30 annual PTO days under VND-HR-004.

## Policy mapping
- Anchor office / holidays / workweek: `VND-HR-003` §§3–4, 7
- PTO entitlements / accrual / first 60 days: `VND-HR-004` §§5, 12–15
- PTO approval and notice: `VND-HR-004` §6 and `VND-SOP-103` §5
- Remote/WFA role and allowances: `VND-HR-005` §§4, 7, 10
- WFA eligibility and exceptions: `VND-SOP-106` §§5–8
- Medical and other benefits: `VND-HR-009` §§10, 14, 17
- HR case categories and status: `VND-SOP-104` §§6, 10

## Validation and tests
From repository root, in the existing virtual environment:

```powershell
python scripts/validate_mock_data.py
python -m pytest -v
```

The validation script uses only Python standard library.
`tests/test_mock_data.py` adds four tests to the Milestone 1 pytest suite.

## Architecture reminder
Future MCP tools will load these files through a data-access module.
The agent should **not** parse JSON directly in its LLM prompt, decide eligibility
solely from a balance, or make an irreversible HR change without confirmation.
