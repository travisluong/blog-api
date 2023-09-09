from datetime import datetime
from fastapi import APIRouter
from psycopg.rows import class_row
from pydantic import BaseModel

from app.dependencies import DBDep


router = APIRouter(prefix="/posts")


class Post(BaseModel):
    post_id: int
    user_id: int
    category_id: int
    title: str | None
    content: str | None
    status: str
    published_at: datetime | None
    created_at: datetime
    updated_at: datetime


@router.get("/")
def get_posts(conn: DBDep):
    with conn.cursor(row_factory=class_row(Post)) as posts_cur:
        return posts_cur.execute("select * from posts").fetchall()
