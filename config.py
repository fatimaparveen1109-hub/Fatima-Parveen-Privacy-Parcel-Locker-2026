import os
import streamlit as st


def setting(name: str, default: str = "") -> str:
    try:
        value = st.secrets.get(name, default)
    except Exception:
        value = os.getenv(name, default)
    return str(value or default)

DATABASE_URL = setting("DATABASE_URL")
ADMIN_EMAIL = setting("ADMIN_EMAIL", "admin@example.com").lower()
ADMIN_PASSWORD_HASH = setting("ADMIN_PASSWORD_HASH")
APP_BASE_URL = setting("APP_BASE_URL", "http://localhost:8501")
