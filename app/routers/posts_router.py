from datetime import datetime
from fastapi import APIRouter, HTTPException
from psycopg.rows import class_row
from pydantic import BaseModel

from app.dependencies import AdminDep, DBDep, JwtDep


router = APIRouter(prefix="/posts")


class User(BaseModel):
    user_id: int
    username: str


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
    user: User | None = None
    category: Category | None = None


class UpdatePostReq(BaseModel):
    user_id: int
    category_id: int
    title: str | None
    content: str | None
    status: str
    published_at: datetime | None
    updated_at: datetime


@router.get("/")
def get_posts(
    conn: DBDep,
    jwt_payload: JwtDep,
    category: str | None = None,
    author: str | None = None,
    sort: str | None = None,
    page: int = 0,
):
    with (
        conn.cursor(row_factory=class_row(Category)) as categories_cur,
        conn.cursor(row_factory=class_row(Post)) as posts_cur,
        conn.cursor(row_factory=class_row(User)) as users_cur,
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

        if author:
            a = users_cur.execute(
                "select * from users where username = %s", [author]
            ).fetchone()
            if not a:
                raise HTTPException(status_code=404, detail="author not found")
            else:
                sql += " and user_id = %(user_id)s"
                params["user_id"] = a.user_id

        if sort:
            match sort:
                case "-published_at":
                    sql += " order by published_at desc"
                case "published_at":
                    sql += " order by published_at asc"
                case _:
                    raise HTTPException(status_code=400, detail="invalid sort param")

        limit = 10
        offset = 0

        if page:
            offset = page * limit

        sql += " limit %(limit)s offset %(offset)s"
        params["limit"] = limit
        params["offset"] = offset

        print(sql)
        print(params)
        posts = posts_cur.execute(sql, params).fetchall()

        category_ids = [post.category_id for post in posts]
        categories = categories_cur.execute(
            "select * from categories where category_id = any(%s)", [category_ids]
        ).fetchall()

        user_ids = [post.user_id for post in posts]
        users = users_cur.execute(
            "select * from users where user_id = any(%s)", [user_ids]
        ).fetchall()

        for post in posts:
            post.category = next(
                (
                    category
                    for category in categories
                    if category.category_id == post.category_id
                )
            )
            post.user = next((user for user in users if user.user_id == post.user_id))

        return posts


@router.get("/{post_id}")
def get_post(post_id: int, jwt_payload: JwtDep, conn: DBDep):
    with conn.cursor(row_factory=class_row(Post)) as posts_cur:
        if not jwt_payload:
            sql = "select * from posts where status = 'public'"
        elif jwt_payload["is_admin"]:
            sql = "select * from posts where 1 = 1"
        elif not jwt_payload["is_admin"]:
            sql = "select * from posts where status != 'draft'"

        sql += " and post_id = %s"
        record = posts_cur.execute(sql, [post_id]).fetchone()
        if not record:
            raise HTTPException(status_code=404, detail="post not found")

        return record


@router.put("/{post_id}")
def update_post(
    post_id: int, update_post_req: UpdatePostReq, is_admin: AdminDep, conn: DBDep
):
    params = {
        "post_id": post_id,
        "user_id": update_post_req.user_id,
        "category_id": update_post_req.category_id,
        "title": update_post_req.title,
        "content": update_post_req.content,
        "status": update_post_req.status,
        "published_at": update_post_req.published_at,
        "updated_at": update_post_req.updated_at,
    }
    with conn.cursor(row_factory=class_row(Post)) as cur:
        record = cur.execute(
            "update posts set user_id = %(user_id)s, category_id = %(category_id)s, title = %(title)s, content = %(content)s, status = %(status)s, published_at = %(published_at)s, updated_at = %(updated_at)s where post_id = %(post_id)s returning *",
            params,
        ).fetchone()
        return record


@router.delete("/{post_id}")
def delete_post(post_id: int, conn: DBDep, is_admin: AdminDep):
    conn.execute("delete from posts where post_id = %s", [post_id])
    return {"message": "post deleted"}
