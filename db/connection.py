"""PostgreSQL connection helpers. Never hard-code connection secrets."""
import os

import psycopg
from dotenv import load_dotenv
from psycopg.rows import dict_row

load_dotenv()


def open_connection(*, admin: bool = False):
    """Admin scripts prefer the direct URL; application queries use pooled URL."""
    url = (
        os.getenv("DIRECT_DATABASE_URL") or os.getenv("DATABASE_URL")
        if admin
        else os.getenv("DATABASE_URL")
    )
    if not url:
        name = "DIRECT_DATABASE_URL or DATABASE_URL" if admin else "DATABASE_URL"
        raise RuntimeError(f"Missing {name}. Put the Neon connection URL in your local .env file.")
    return psycopg.connect(url, row_factory=dict_row, connect_timeout=15)
