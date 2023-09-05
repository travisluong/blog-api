from fastapi import APIRouter, Depends
from pydantic import BaseModel
from psycopg.rows import class_row

from app.db import get_conn
from app.dependencies import get_current_user_id

router = APIRouter(prefix="/users")


class UserRes(BaseModel):
    user_id: int
    email: str
    username: str


@router.get("/me")
def me(current_user_id: str = Depends(get_current_user_id)):
    with get_conn() as conn, conn.cursor(row_factory=class_row(UserRes)) as cur:
        record = cur.execute(
            "select * from users where user_id = %s", [current_user_id]
        ).fetchone()
        return record
