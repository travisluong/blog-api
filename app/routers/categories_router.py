from datetime import datetime
from fastapi import APIRouter, HTTPException
from psycopg.rows import class_row
from pydantic import BaseModel

from app.dependencies import AdminDep, AuthDep, DBDep


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
def create_category(conn: DBDep, is_admin: AdminDep, category_req: CategoryReq):
    with conn.cursor(row_factory=class_row(CategoryRes)) as cur:
        is_exists = cur.execute(
            "select * from categories where name = %s", [category_req.name]
        ).fetchone()
        if is_exists:
            raise HTTPException(status_code=400, detail="category already exists")
        record = cur.execute(
            "insert into categories (name) values (%s) returning *", [category_req.name]
        ).fetchone()
        return record


@router.put("/{category_id}")
def update_category(
    conn: DBDep, is_admin: AdminDep, category_id: int, category_req: CategoryReq
):
    with conn.cursor(row_factory=class_row(CategoryRes)) as cur:
        record = cur.execute(
            "update categories set name = %s, updated_at = %s where category_id = %s returning *",
            [category_req.name, datetime.now(), category_id],
        ).fetchone()
        return record


@router.delete("/{category_id}")
def delete_category(conn: DBDep, is_admin: AdminDep, category_id: int):
    with conn.cursor() as cur:
        record = cur.execute(
            "delete from categories where category_id = %s returning name",
            [category_id],
        ).fetchone()
        if record:
            return {"message": f"{record[0]} category deleted"}
        else:
            raise HTTPException(status_code=404, detail="category not found")
