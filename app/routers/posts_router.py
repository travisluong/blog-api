from datetime import datetime
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from psycopg.rows import class_row

from app.dependencies import DBDep, JwtDep
from app.routers.auth_router import UserDB
from app.routers.categories_router import Category


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
def get_posts(
    conn: DBDep,
    jwt_payload: JwtDep,
    page: int = 0,
    category: str | None = None,
    author: str | None = None,
    sort: str | None = None,
):
    # fmt: off
    with \
      conn.cursor(row_factory=class_row(Category)) as categories_cur, \
      conn.cursor(row_factory=class_row(UserDB)) as users_cur, \
      conn.cursor(row_factory=class_row(Post)) as posts_cur:
        if not jwt_payload:
            sql = "select * from posts where status = 'public'"
        elif jwt_payload["is_admin"]:
            sql = "select * from posts"
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

        if author:
            a = users_cur.execute(
                "select * from users where username = %s", [author]
            ).fetchone()
            if not a:
                raise HTTPException(status_code=404, detail="author not found")
            if a:
                sql += " and user_id = %(user_id)s"
                params["user_id"] = a.user_id

        limit = 10
        offset = 0
        
        if page:
            offset = page * limit
        
        sql += " limit %(limit)s offset %(offset)s"
        params["limit"] = limit
        params["offset"] = offset

        print(sql)
        print(params)

        return posts_cur.execute(sql, params).fetchall()
