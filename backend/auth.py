"""Create account, log in, log out, and "who am I" endpoints."""

import re
import sqlite3

from fastapi import APIRouter, Cookie, HTTPException, Request, Response
from pydantic import BaseModel, Field, field_validator, model_validator

from db import connect
from security import (
    DUMMY_HASH,
    SESSION_COOKIE,
    SESSION_TTL_SECONDS,
    LoginThrottle,
    hash_password,
    make_session_token,
    read_session_token,
    verify_password,
)

router = APIRouter(prefix="/api/auth")
throttle = LoginThrottle()

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
BAD_LOGIN = "Invalid email or password."


def _clean_email(value: str) -> str:
    value = value.strip().lower()
    if len(value) > 254 or not EMAIL_RE.match(value):
        raise ValueError("Enter a valid email address.")
    return value


class RegisterRequest(BaseModel):
    first_name: str = Field(min_length=1, max_length=50)
    last_name: str = Field(min_length=1, max_length=50)
    email: str
    password: str = Field(min_length=8, max_length=128)
    confirm_password: str

    @field_validator("password")
    @classmethod
    def strong_password(cls, v: str) -> str:
        # Length (8 to 128) is checked by Field above; these add the usual complexity rules.
        missing = [
            label
            for label, ok in [
                ("a letter", any(c.isalpha() for c in v)),
                ("a number", any(c.isdigit() for c in v)),
                ("a special character (like ! @ # $)", any(not c.isalnum() and not c.isspace() for c in v)),
            ]
            if not ok
        ]
        if missing:
            raise ValueError("Password needs " + ", ".join(missing) + ".")
        return v

    @field_validator("first_name", "last_name")
    @classmethod
    def strip_name(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Name can't be blank.")
        return v.strip()

    @field_validator("email")
    @classmethod
    def check_email(cls, v: str) -> str:
        return _clean_email(v)

    @model_validator(mode="after")
    def passwords_match(self) -> "RegisterRequest":
        if self.password != self.confirm_password:
            raise ValueError("Passwords don't match.")
        return self


class LoginRequest(BaseModel):
    email: str = Field(max_length=254)
    password: str = Field(max_length=128)


class UserOut(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str


def _user_out(row: sqlite3.Row) -> UserOut:
    # The seeded users have first/last name columns; fall back to splitting `name` just in case.
    first, _, last = row["name"].partition(" ")
    return UserOut(
        id=row["id"],
        first_name=row["first_name"] or first,
        last_name=row["last_name"] or last,
        email=row["email"],
    )


def _start_session(response: Response, user_id: int, request: Request) -> None:
    response.set_cookie(
        SESSION_COOKIE,
        make_session_token(user_id),
        max_age=SESSION_TTL_SECONDS,
        httponly=True,  # page scripts can't read it, so injected JavaScript can't steal it
        samesite="lax",  # other sites can't make the browser send it with their requests
        secure=request.url.scheme == "https",
    )


def current_user(token: str | None) -> UserOut | None:
    user_id = read_session_token(token)
    if user_id is None:
        return None
    with connect() as conn:
        row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    return _user_out(row) if row else None


@router.post("/register", status_code=201)
def register(body: RegisterRequest, request: Request, response: Response) -> UserOut:
    with connect() as conn:
        try:
            cur = conn.execute(
                "INSERT INTO users (name, email, password_hash, first_name, last_name) VALUES (?, ?, ?, ?, ?)",
                (
                    f"{body.first_name} {body.last_name}",
                    body.email,
                    hash_password(body.password),
                    body.first_name,
                    body.last_name,
                ),
            )
        except sqlite3.IntegrityError:
            raise HTTPException(status_code=409, detail="An account with that email already exists.")
        row = conn.execute("SELECT * FROM users WHERE id = ?", (cur.lastrowid,)).fetchone()
    _start_session(response, row["id"], request)
    return _user_out(row)


@router.post("/login")
def login(body: LoginRequest, request: Request, response: Response) -> UserOut:
    email = body.email.strip().lower()
    key = f"{email}|{request.client.host if request.client else ''}"
    if throttle.is_locked(key):
        raise HTTPException(status_code=429, detail="Too many failed attempts. Try again in 15 minutes.")

    with connect() as conn:
        row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        # Always run a hash check so a missing account takes as long as a wrong password.
        ok = verify_password(body.password, row["password_hash"] if row else DUMMY_HASH) and row is not None
        if not ok:
            throttle.fail(key)
            raise HTTPException(status_code=401, detail=BAD_LOGIN)
        throttle.reset(key)

    _start_session(response, row["id"], request)
    return _user_out(row)


@router.post("/logout", status_code=204)
def logout(response: Response) -> None:
    response.delete_cookie(SESSION_COOKIE)


@router.get("/me")
def me(cc_session: str | None = Cookie(default=None)) -> UserOut:
    user = current_user(cc_session)
    if user is None:
        raise HTTPException(status_code=401, detail="Not logged in.")
    return user
