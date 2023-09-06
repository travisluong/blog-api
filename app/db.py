import psycopg

from app.config import get_settings

settings = get_settings()

conninfo = f"user={settings.db_user} password={settings.db_password} host={settings.db_host} port={settings.db_port} dbname={settings.db_name}"


def get_conn():
    return psycopg.connect(conninfo=conninfo)


def get_db():
    with get_conn() as conn:
        yield conn
