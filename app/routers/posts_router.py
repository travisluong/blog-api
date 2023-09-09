from datetime import datetime
from fastapi import APIRouter, HTTPException
from psycopg.rows import class_row
from pydantic import BaseModel

from app.dependencies import DBDep, JwtDep


router = APIRouter(prefix="/posts")


class Category(BaseModel):
    category_id: int
    name: str


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
def get_posts(conn: DBDep, jwt_payload: JwtDep, category: str | None = None):
    with (
        conn.cursor(row_factory=class_row(Category)) as categories_cur,
        conn.cursor(row_factory=class_row(Post)) as posts_cur,
    ):
        if not jwt_payload:
            sql = "select * from posts where status = 'public'"
        elif jwt_payload["is_admin"]:
            sql = "select * from posts where 1 = 1"
        elif not jwt_payload["is_admin"]:
            sql = "select * from posts where status != 'draft'"

        params = {}

        if category:
            c = categories_cur.execute(
                "select * from categories where name = %s", [category]
            ).fetchone()
            if not c:
                raise HTTPException(status_code=404, detail="category not found")
            else:
                sql += " and category_id = %(category_id)s"
                params["category_id"] = c.category_id

        print(sql)
        print(params)
        return posts_cur.execute(sql, params).fetchall()
