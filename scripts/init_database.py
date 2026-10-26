"""Create PostgreSQL tables using db/schema.sql. Run: python -m scripts.init_database"""
from pathlib import Path

from db.connection import open_connection

ROOT = Path(__file__).resolve().parents[1]


def main():
    script = (ROOT / "db" / "schema.sql").read_text(encoding="utf-8")
    statements = [statement.strip() for statement in script.split(";") if statement.strip()]
    with open_connection(admin=True) as conn:
        for statement in statements:
            conn.execute(statement)
    print(f"Database schema ready ({len(statements)} SQL statements).")


if __name__ == "__main__":
    main()
