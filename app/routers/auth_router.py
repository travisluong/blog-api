from jose import jwt
from datetime import datetime, timedelta
import bcrypt
from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel, EmailStr
from psycopg.rows import class_row

from app.db import get_conn
from app.config import get_settings

settings = get_settings()

router = APIRouter(prefix="/auth")


class SignUpReq(BaseModel):
    email: EmailStr
    username: str
    password: str


class SignInReq(BaseModel):
    email: EmailStr
    password: str


class UserDB(BaseModel):
    user_id: int
    email: str
    username: str | None
    password: str | None


@router.post("/signup")
def signup(sign_up_req: SignUpReq):
    hashed = bcrypt.hashpw(sign_up_req.password.encode("utf8"), bcrypt.gensalt())
    with get_conn() as conn:
        record = conn.execute(
            "select * from users where email = %s or username = %s",
            [sign_up_req.email, sign_up_req.username],
        ).fetchone()
        if record:
            raise HTTPException(status_code=400, detail="user already exists")
        conn.execute(
            "insert into users (email, username, password) values (%s, %s, %s)",
            [sign_up_req.email, sign_up_req.username, hashed.decode("utf8")],
        )
    return {"message": "sign up success"}


@router.post("/signin")
def signin(sign_in_req: SignInReq, response: Response):
    with get_conn() as conn, conn.cursor(row_factory=class_row(UserDB)) as cur:
        record: UserDB = cur.execute(
            "select * from users where email ilike %s", [sign_in_req.email]
        ).fetchone()
        if not record:
            raise HTTPException(status_code=404, detail="user not found")
        is_password_correct = bcrypt.checkpw(
            sign_in_req.password.encode("utf8"), record.password.encode("utf8")
        )
        if not is_password_correct:
            raise HTTPException(status_code=401, detail="incorrect credentials")
        expire = datetime.utcnow() + timedelta(minutes=15)
        payload = {"sub": str(record.user_id), "exp": expire}
        token = jwt.encode(payload, settings.jwt_secret, algorithm="HS256")
        response.set_cookie(key="jwt", value=token)
        return {"message": "sign in success"}
