from fastapi import APIRouter, Depends
from psycopg import Connection
from pydantic import BaseModel
from psycopg.rows import class_row

from app.db import get_db
from app.dependencies import get_current_user_id

router = APIRouter(prefix="/users")


class UserRes(BaseModel):
    user_id: int
    email: str
    username: str


@router.get("/me")
def me(
    current_user_id: str = Depends(get_current_user_id),
    conn: Connection = Depends(get_db),
):
    with conn.cursor(row_factory=class_row(UserRes)) as cur:
        record = cur.execute(
            "select * from users where user_id = %s", [current_user_id]
        ).fetchone()
        return record


@router.get("/")
def get_users(conn: Connection = Depends(get_db)):
    with conn.cursor(row_factory=class_row(UserRes)) as cur:
        records = cur.execute("select * from users where is_admin = true").fetchall()
        return records


@router.get("/{user_id}")
def get_user(user_id: int, conn: Connection = Depends(get_db)):
    with conn.cursor(row_factory=class_row(UserRes)) as cur:
        record = cur.execute(
            "select * from users where user_id = %s", [user_id]
        ).fetchone()
        return record
