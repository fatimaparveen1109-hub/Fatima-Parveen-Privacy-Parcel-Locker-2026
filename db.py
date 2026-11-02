import psycopg2
from psycopg2.extras import RealDictCursor
import streamlit as st
from config import DATABASE_URL


def get_conn():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL missing. Add it to Streamlit secrets.")
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor, connect_timeout=10)


def query(sql, params=None, fetch=True):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
            if fetch and cur.description:
                return cur.fetchall()
            return cur.rowcount


def one(sql, params=None):
    rows = query(sql, params)
    return rows[0] if rows else None


def execute(sql, params=None):
    return query(sql, params, fetch=False)


def db_ready():
    try:
        one("SELECT 1 AS ok")
        return True, "Connected to Supabase PostgreSQL"
    except Exception as exc:
        return False, str(exc)
