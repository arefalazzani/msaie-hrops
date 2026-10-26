# Milestone 3 upgrade — PostgreSQL on Neon, FastAPI on Render

This package is **additive**. Extract it at the ROOT of your existing project; keep all the original `mock_data/*.json`, `policy_corpus/`, `app/`, `requirements.txt`, and `tests/` files.

## 1. Neon database

1. Create a free account at https://neon.com.
2. Create project `vendelligent-hr-agent`, choosing a database region close to the planned Render web service (e.g. Frankfurt for both).
3. Open **Connect**, select the project database, and copy:
   - **pooled** connection string (Connection pooling enabled) for `DATABASE_URL`
   - **direct** connection string (Connection pooling disabled) for `DIRECT_DATABASE_URL`
4. Both connection strings should preserve Neon's SSL/TLS parameters.
5. Do NOT commit these values to GitHub or share screenshots showing secrets.

## 2. Install dependencies

Activate your existing `.venv` and install the PostgreSQL packages:

```powershell
python -m pip install -r requirements-postgres.txt
```

**Append** the two non-comment lines of `requirements-postgres.txt` to your existing `requirements.txt`. Render installs `requirements.txt` on deploy.

## 3. Configure local `.env`

Create `.env` in the repository root if absent; retain other existing values.

```dotenv
DATABASE_URL="postgresql://USER:PASSWORD@HOST-POOLER/DB?sslmode=require"
DIRECT_DATABASE_URL="postgresql://USER:PASSWORD@HOST/DB?sslmode=require"
```

Replace with the ACTUAL connection strings copied from Neon. Never use the examples verbatim. `.env` must be in `.gitignore`. Keep `.env.example` with placeholder-only names, never secrets.

## 4. Create schema and load data

From repository root, with the virtual environment activated:

```powershell
python -m scripts.init_database
python -m scripts.seed_database
python -m scripts.check_database
python -m pytest -v
```

- `init_database` builds seven relational tables and indexes.
- `seed_database` imports **existing** Milestone 3 JSON records (12 employees, 12 PTO, 12 WFA, 12 benefits, 2 offices, 3 mock HR tickets); uses a transaction and idempotent upserts.
- `check_database` confirms database counts and reads real values via parameterized SQL.
- The tests run offline without a Neon connection, to keep CI reproducible.

## 5. Review data using Neon SQL Editor

```sql
SELECT employee_id, display_name, manager_id, anchor_office FROM employees ORDER BY employee_id;
SELECT employee_id, available_days FROM pto_balances WHERE employee_id = 'VND-E001';
SELECT employee_id, remaining_working_days FROM wfa_balances WHERE employee_id = 'VND-E003';
```

Expected: Amina Demo has 12 PTO days; VND-E003 has 16 WFA days remaining in 2026. These are synthetic data snapshots as of 2026-10-24, not live balances.

## 6. Commit code (not secrets)

```powershell
git add db scripts/init_database.py scripts/seed_database.py scripts/check_database.py tests/test_postgres_fixtures.py requirements-postgres.txt POSTGRESQL_SETUP.md requirements.txt .env.example
git commit -m "Milestone 3: Add PostgreSQL schema and synthetic data importer"
git push
```

## 7. Later — Render and MCP

- Render `Web Service` (Python/FastAPI) connects to the **external Neon database**. The database itself is not deployed inside the Render service.
- Add `DATABASE_URL` in Render service **Environment** settings (not in repo). Use **pooled** Neon URL.
- Deploy with start command `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
- MCP server tools invoke `db.repository.get_employee_profile()`, `get_pto_balance()`, `get_wfa_balance()`, and `get_benefits_status()` using permitted, parameterized lookups.
- The policy RAG retriever remains attached to the policy corpus/ChromaDB, not JSON employee records.
- Do not expose raw database SQL as an unrestricted LLM tool; check employee authorization and log safe tool traces.
- Use the synthetic fixture `as_of_date` as the evaluation clock when comparing leave balances to policy rules.

## Database schema choices

| Table | Key | Relationship |
| --- | --- | --- |
| office_locations | office_id | Parent of employees and working days |
| office_working_days | (office_id, weekday) | Office calendar |
| employees | employee_id | Manager self-FK and office FK |
| pto_balances | (employee_id, as_of_date) | Employee PTO snapshots |
| wfa_balances | (employee_id, calendar_year) | Employee WFA annual allocation |
| benefits | (employee_id, as_of_date) | Benefits snapshots |
| hr_tickets | ticket_id | Synthetic HR tickets, FK to employee |

Avoid automatic seeding at every web app start: it could overwrite mock ticket changes, and Render can restart its service. Seed explicitly during development or deployment as a controlled one-off step.

## Notes

- We intentionally retain JSON as versioned **seed data / test fixtures**. The runtime agent will query PostgreSQL instead of reading the JSON directly.
- Initial setup is a one-off schema script. If the database schema evolves later, introduce Alembic migrations.
- `hr_tickets` only permits `is_mock = TRUE`; even mock-write actions require explicit user confirmation per Quantic assignment.
- Neon's free service can scale to zero during inactivity; first query may add latency. Plan latency evaluation accordingly.
