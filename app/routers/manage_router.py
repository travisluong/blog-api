from fastapi import APIRouter

from app.db import get_conn

router = APIRouter(prefix="/manage")


@router.get("/ping")
def ping():
    with get_conn() as conn:
        record = conn.execute("select 1").fetchone()
        print(record)
        return "pong"
