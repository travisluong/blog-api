from datetime import datetime
from fastapi import APIRouter
from psycopg.rows import class_row
from pydantic import BaseModel

from app.dependencies import DBDep


router = APIRouter(prefix="/categories")


class Category(BaseModel):
    category_id: int
    name: str
    created_at: datetime
    updated_at: datetime


@router.get("/")
def get_categories(conn: DBDep):
    with conn.cursor(row_factory=class_row(Category)) as cur:
        return cur.execute("select * from categories").fetchall()
