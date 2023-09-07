from fastapi import APIRouter, Depends
from pydantic import BaseModel
from psycopg.rows import class_row

from app.dependencies import AuthDep, DBDep, get_current_user_id

router = APIRouter(prefix="/users")


class UserRes(BaseModel):
    user_id: int
    email: str
    username: str


@router.get("/me")
def me(
    conn: DBDep,
    current_user_id: AuthDep,
):
    with conn.cursor(row_factory=class_row(UserRes)) as cur:
        record = cur.execute(
            "select * from users where user_id = %s", [current_user_id]
        ).fetchone()
        return record


@router.get("/")
def get_users(conn: DBDep):
    with conn.cursor(row_factory=class_row(UserRes)) as cur:
        records = cur.execute("select * from users where is_admin = true").fetchall()
        return records


@router.get("/{user_id}")
def get_user(user_id: int, conn: DBDep):
    with conn.cursor(row_factory=class_row(UserRes)) as cur:
        record = cur.execute(
            "select * from users where user_id = %s", [user_id]
        ).fetchone()
        return record
