from datetime import datetime
from fastapi import APIRouter, HTTPException
from psycopg.rows import class_row
from pydantic import BaseModel

from app.dependencies import AuthDep, DBDep


router = APIRouter(prefix="/categories")


class Category(BaseModel):
    category_id: int
    name: str
    created_at: datetime
    updated_at: datetime


class CategoryReq(BaseModel):
    name: str


class CategoryRes(BaseModel):
    category_id: int
    name: str
    created_at: datetime
    updated_at: datetime


@router.get("/")
def get_categories(conn: DBDep):
    with conn.cursor(row_factory=class_row(Category)) as cur:
        return cur.execute("select * from categories").fetchall()


@router.post("/")
def create_category(conn: DBDep, current_user_id: AuthDep, category_req: CategoryReq):
    with conn.cursor(row_factory=class_row(CategoryRes)) as cur:
        is_exists = cur.execute(
            "select * from categories where name = %s", [category_req.name]
        ).fetchone()
        if is_exists:
            return HTTPException(status_code=400, detail="category already exists")
        record = cur.execute(
            "insert into categories (name) values (%s) returning *", [category_req.name]
        ).fetchone()
        return record
