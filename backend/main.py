"""Campus Customs backend: product catalogue, images, accounts, and the chat assistant.

Run from this backend/ folder:
    uvicorn main:app --reload --port 8000
"""

import json
import logging
import os
import sqlite3
from pathlib import Path

from dotenv import load_dotenv

# Read hw4/.env (API key, optional settings) before anything reads the environment.
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from fastapi import Cookie, FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic_ai.exceptions import UsageLimitExceeded

import agent as chat_agent
import audit
from auth import current_user
from auth import router as auth_router
from blurbs import gigachad_blurb
from db import DATA_DIR, connect
from models import CatalogProduct, ChatDeps, ChatReply, ChatMessageOut, ChatRequest, ChatResponse, CustomerInfo, PageResults
from security import RateLimit
from tools import product_cards

log = logging.getLogger("campus_customs")

# Sent when the model provider's content filter blocks a message, so the agent never ran.
# Those messages are often about self-harm or violence, so the reply leads with crisis resources.
CONTENT_FILTER_REPLY = (
    "I'm not able to respond to that message here. If you're going through a hard time or thinking about "
    "hurting yourself, please reach out right now: call or text **988** (Suicide & Crisis Lifeline, US), or "
    "call **911** in an emergency. Yale students can also contact Yale Mental Health & Counseling. "
    "If you meant something else, try rephrasing and I'll help with Yale gear."
)

# Chat rate limits: each message costs real API money, so cap how many anyone can send.
HOUR, DAY = 3600, 24 * 3600
USER_CHAT_LIMIT = RateLimit(int(os.getenv("CHAT_LIMIT_USER_PER_HOUR", "20")), HOUR)
GUEST_CHAT_LIMIT = RateLimit(int(os.getenv("CHAT_LIMIT_GUEST_PER_HOUR", "10")), HOUR)
GLOBAL_CHAT_LIMIT = RateLimit(int(os.getenv("CHAT_LIMIT_GLOBAL_PER_DAY", "300")), DAY)


def client_ip(request: Request) -> str:
    """The shopper's IP. Behind the local Vite proxy, use the address it forwards."""
    host = request.client.host if request.client else "unknown"
    forwarded = request.headers.get("x-forwarded-for")
    # Only trust the header from the local proxy; anyone else could fake it.
    if forwarded and host in ("127.0.0.1", "::1"):
        return forwarded.split(",")[0].strip()
    return host


def _wait_text(seconds: int) -> str:
    minutes = -(-seconds // 60)
    if minutes >= 120:
        return f"about {round(minutes / 60)} hours"
    return f"{minutes} minute{'s' if minutes != 1 else ''}"


def _blocked(user_id: int | None, reason: str, detail: str) -> HTTPException:
    """Record a blocked message in the audit trail (it never reached the agent) and build the 429."""
    audit.append_events([{
        "run_id": audit.new_run_id(), "shopper": f"user:{user_id}" if user_id else "guest",
        "time": audit.now(), "step": "blocked", "stop_reason": reason, "model_requests": 0,
    }])
    return HTTPException(429, detail)


def check_chat_limits(user_id: int | None, ip: str) -> None:
    """Raise 429 if this shopper (or the whole site) has sent too many chat messages."""
    if wait := GLOBAL_CHAT_LIMIT.retry_after("all"):
        raise _blocked(user_id, "rate_limited:site_daily",
                       f"The assistant has hit its daily message limit. Try again in {_wait_text(wait)}.")
    limit, key = (USER_CHAT_LIMIT, f"user:{user_id}") if user_id else (GUEST_CHAT_LIMIT, f"ip:{ip}")
    if wait := limit.retry_after(key):
        hint = "" if user_id else " Log in for a higher limit."
        raise _blocked(
            user_id, "rate_limited:user" if user_id else "rate_limited:guest",
            f"Easy, legend. That's {limit.limit} messages this hour. Try again in {_wait_text(wait)}.{hint}",
        )
    # Count the message now, before calling the model, so failed calls count too.
    GLOBAL_CHAT_LIMIT.hit("all")
    limit.hit(key)

SIZE_ORDER = ["XS", "S", "M", "L", "XL", "XXL"]

app = FastAPI(title="Campus Customs API")
app.include_router(auth_router)


@app.exception_handler(RequestValidationError)
async def validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Like FastAPI's default 422, but without echoing what was typed (it could be a password)."""
    errors = [{k: v for k, v in e.items() if k in ("type", "loc", "msg")} for e in exc.errors()]
    return JSONResponse(status_code=422, content={"detail": errors})


def product_from_row(row: sqlite3.Row) -> dict:
    product = dict(row)
    product["colors"] = json.loads(product["colors"])
    product["search_tags"] = json.loads(product["search_tags"])
    product["blurb"] = gigachad_blurb(product["product_id"], product["name"])
    return product


@app.get("/api/products")
def list_products() -> list[dict]:
    with connect() as conn:
        rows = conn.execute("SELECT * FROM catalogue ORDER BY name").fetchall()
    return [product_from_row(r) for r in rows]


@app.get("/api/products/{product_id}")
def get_product(product_id: str) -> dict:
    with connect() as conn:
        row = conn.execute("SELECT * FROM catalogue WHERE product_id = ?", (product_id,)).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Product not found")
        stock = conn.execute(
            "SELECT size, quantity FROM inventory WHERE product_id = ?", (product_id,)
        ).fetchall()
    product = product_from_row(row)
    product["inventory"] = sorted(
        ({"size": s["size"], "quantity": s["quantity"]} for s in stock),
        key=lambda s: SIZE_ORDER.index(s["size"]) if s["size"] in SIZE_ORDER else len(SIZE_ORDER),
    )
    return product


def _saved_cards(products_json: str | None):
    ids = [p["product_id"] for p in json.loads(products_json or "[]") if "product_id" in p]
    return product_cards(ids)


def _page_results(show: bool, deps: ChatDeps, fallback_ids: list[str]) -> PageResults | None:
    """Full product data for the page when the agent asked for it.

    Uses every match from the agent's latest search (not just the few ids it typed), falling back
    to the ids in its reply if it didn't search this turn.
    """
    if not show:
        return None
    search = deps.last_search
    ids = search.product_ids if search else fallback_ids
    if not ids:
        return None
    with connect() as conn:
        placeholders = ",".join("?" * len(ids))
        rows = conn.execute(f"SELECT * FROM catalogue WHERE product_id IN ({placeholders})", ids).fetchall()
    by_id = {r["product_id"]: r for r in rows}
    products = [CatalogProduct(**product_from_row(by_id[i])) for i in ids if i in by_id]
    return PageResults(
        label=search.label if search else "the assistant's picks",
        total=search.total if search else len(products),
        products=products,
    )


def _customer_info(user_id: int) -> CustomerInfo | None:
    """Load the shopper from the database using the id in their signed session cookie."""
    with connect() as conn:
        row = conn.execute(
            "SELECT id, name, email, first_name, last_name, created_at FROM users WHERE id = ?", (user_id,)
        ).fetchone()
    if row is None:
        return None
    first, _, last = row["name"].partition(" ")
    return CustomerInfo(
        user_id=row["id"],
        first_name=row["first_name"] or first,
        last_name=row["last_name"] or last,
        email=row["email"],
        member_since=row["created_at"],
    )


@app.post("/api/chat")
async def chat(body: ChatRequest, request: Request, cc_session: str | None = Cookie(default=None)) -> ChatResponse:
    """Send one shopper message to the agent and return its reply plus product cards.

    Logged-in shoppers get their recent history as context, and the exchange is saved.
    Guests get a reply too, but nothing is saved (chat_messages needs a user_id).
    Rate limits are checked first, so a blocked message never reaches the paid model.
    """
    user = current_user(cc_session)
    check_chat_limits(user.id if user else None, client_ip(request))
    history: list[dict] = []
    if user:
        with connect() as conn:
            rows = conn.execute(
                "SELECT role, content, products_json FROM chat_messages WHERE user_id = ? ORDER BY id DESC LIMIT ?",
                (user.id, chat_agent.HISTORY_MESSAGES),
            ).fetchall()
        history = [dict(r) for r in reversed(rows)]

    deps = ChatDeps(customer=_customer_info(user.id) if user else None, page=body.page)
    try:
        output = await chat_agent.run_chat(body.message.strip(), deps, history)
    except UsageLimitExceeded:
        log.warning("Chat run hit its usage limit")
        raise HTTPException(status_code=503, detail="That one was too big for me. Try a simpler question.")
    except Exception as exc:
        if not chat_agent.is_content_filter(exc):
            log.exception("Chat agent failed")
            raise HTTPException(status_code=502, detail="The assistant is having trouble right now. Try again in a bit.")
        # The provider refused the message before the agent ran: answer safely instead of erroring.
        log.warning("Message blocked by the model provider's content filter")
        output = ChatReply(reply=CONTENT_FILTER_REPLY)

    products = product_cards(output.product_ids)
    page_results = _page_results(output.show_results_on_page, deps, output.product_ids)
    if user:
        with connect() as conn:
            conn.execute(
                "INSERT INTO chat_messages (user_id, role, content, products_json) VALUES (?, 'user', ?, NULL)",
                (user.id, body.message.strip()),
            )
            conn.execute(
                "INSERT INTO chat_messages (user_id, role, content, products_json) VALUES (?, 'assistant', ?, ?)",
                (user.id, output.reply, json.dumps([p.model_dump() for p in products])),
            )
    return ChatResponse(reply=output.reply, products=products, page_results=page_results, saved=user is not None)


@app.get("/api/chat/history")
def chat_history(cc_session: str | None = Cookie(default=None)) -> list[ChatMessageOut]:
    """The logged-in shopper's last 30 messages, oldest first. Guests get an empty list."""
    user = current_user(cc_session)
    if not user:
        return []
    with connect() as conn:
        rows = conn.execute(
            "SELECT role, content, products_json FROM chat_messages WHERE user_id = ? ORDER BY id DESC LIMIT 30",
            (user.id,),
        ).fetchall()
    return [
        ChatMessageOut(role=r["role"], content=r["content"], products=_saved_cards(r["products_json"]))
        for r in reversed(rows)
    ]


# image_file_path in the catalogue is relative to data/, e.g. "products/x.jpg".
app.mount("/images", StaticFiles(directory=DATA_DIR), name="images")
