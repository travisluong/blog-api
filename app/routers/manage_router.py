import secrets
import random
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Header
from faker import Faker
import bcrypt

from app.config import get_settings
from app.db import get_conn

settings = get_settings()

router = APIRouter(prefix="/manage")

fake = Faker()


def has_api_key(api_key: Annotated[str | None, Header()] = None):
    api_key_bytes = api_key.encode("utf8")
    correct_api_key_bytes = settings.api_key.encode("utf8")
    if not secrets.compare_digest(api_key_bytes, correct_api_key_bytes):
        raise HTTPException(status_code=403, detail="unauthorized")
    return api_key


def load_fake_data_task():
    print("executing load fake data")
    password = b"blogapi123"
    hashed = bcrypt.hashpw(password, bcrypt.gensalt())
    with get_conn() as conn:
        conn.execute(
            "insert into users (email, password, is_admin) values (%s, %s, %s)",
            ["admin@example.com", hashed, True],
        )

        for i in range(10):
            conn.execute(
                "insert into users (email, password) values (%s, %s)",
                [fake.email(), hashed],
            )

        for category in ["react", "fastapi", "springboot", "nextjs"]:
            conn.execute("insert into categories (name) values (%s)", [category])

        for i in range(20):
            post = {
                "user_id": 1,
                "category_id": random.choice([1, 2, 3]),
                "title": fake.sentence(nb_words=8),
                "content": fake.paragraph(nb_sentences=5),
                "status": random.choice(["draft", "public", "private"]),
            }
            conn.execute(
                "insert into posts (user_id, category_id, title, content, status) values (%(user_id)s, %(category_id)s, %(title)s, %(content)s, %(status)s)",
                post,
            )


@router.get("/ping")
def ping(api_key: Annotated[str, Depends(has_api_key)]):
    with get_conn() as conn:
        record = conn.execute("select 1").fetchone()
        print(record)
        return "pong"


@router.get("/load-fake-data")
def load_fake_data(
    background_tasks: BackgroundTasks, api_key: Annotated[str, Depends(has_api_key)]
):
    background_tasks.add_task(load_fake_data_task)
    return {"message": "load fake data running in background"}
