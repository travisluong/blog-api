import random

from fastapi import APIRouter, BackgroundTasks
from faker import Faker
import bcrypt

from app.db import get_conn

router = APIRouter(prefix="/manage")

fake = Faker()


def load_fake_data_task():
    print("executing load fake data")
    password = b"blogapi123"
    hashed = bcrypt.hashpw(password, bcrypt.gensalt())
    with get_conn() as conn:
        conn.execute(
            "insert into users (email, password, is_admin) values (%s, %s, %s)",
            ["admin@example.com", password, True],
        )
        for i in range(10):
            conn.execute(
                "insert into users (email, password) values (%s, %s)",
                [fake.email(), password],
            )

        for category in ["react", "fastapi", "springboot", "nextjs"]:
            conn.execute("insert into categories (name) values (%s)", [category])

        for i in range(20):
            post = {
                "user_id": random.choice([1, 2, 3]),
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
def ping():
    with get_conn() as conn:
        record = conn.execute("select 1").fetchone()
        print(record)
        return "pong"


@router.get("/load-fake-data")
def load_fake_data(background_tasks: BackgroundTasks):
    background_tasks.add_task(load_fake_data_task)
    return {"message": "load fake data running in background"}
