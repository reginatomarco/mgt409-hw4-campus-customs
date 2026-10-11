"""Tools the chat agent can call. All are read-only lookups in the SQLite catalogue."""

import json
import re
import sqlite3
from typing import Literal

from pydantic_ai import RunContext

from db import connect
from models import (
    MAX_PAGE_RESULTS,
    ChatDeps,
    CustomerProfile,
    PastProduct,
    ProductCard,
    ProductDetails,
    ProductSummary,
    SearchCapture,
    SearchResults,
    SizeStock,
    StockCheck,
    stock_status,
)

SIZES = ["XS", "S", "M", "L", "XL", "XXL"]
MAX_RESULTS = 8

# Shopper words -> words the catalogue actually uses.
SYNONYMS = {
    "tee": "t-shirt",
    "tees": "t-shirt",
    "tshirt": "t-shirt",
    "hoodie": "hood",  # also matches "hooded sweatshirt" and "Full Zip Hood"
    "hoodies": "hood",
    "hoody": "hood",
    "sweatshirts": "sweatshirt",
    "crew": "crewneck",
    "crewnecks": "crewneck",
    "fleeces": "fleece",
    "jackets": "jacket",
    "dan": "bulldog",  # Handsome Dan is Yale's bulldog mascot
    "mascot": "bulldog",
    "dog": "bulldog",
    "grey": "gray",
    "blue": "navy",
}
STOPWORDS = {
    "a", "an", "the", "and", "or", "with", "for", "in", "on", "of", "to", "do", "you", "have", "any",
    "some", "me", "my", "i", "is", "it", "that", "this", "show", "want", "looking", "yale", "item",
    "items", "something", "anything", "got", "u", "what", "your", "handsome",
}


def _normalize(text: str) -> str:
    """Spell quarter-zips one way; the catalogue names them "1 4 Zip"."""
    text = text.lower()
    for variant in ("1/4 zip", "1 4 zip", "1/4-zip", "quarter zip", "quarterzip", "1/4"):
        text = text.replace(variant, "quarter-zip")
    return text


def _terms(text: str) -> list[str]:
    text = _normalize(text)
    words = re.findall(r"[a-z0-9\-]+", text)
    return [SYNONYMS.get(w, w) for w in words if w not in STOPWORDS]


def _size_order(size: str) -> int:
    return SIZES.index(size) if size in SIZES else len(SIZES)


def _stock(conn: sqlite3.Connection, product_id: str) -> list[SizeStock]:
    """Every size for a product, XS to XXL, with quantity and status."""
    rows = conn.execute("SELECT size, quantity FROM inventory WHERE product_id = ?", (product_id,)).fetchall()
    stock = [SizeStock(size=r["size"], quantity=r["quantity"], status=stock_status(r["quantity"])) for r in rows]
    return sorted(stock, key=lambda s: _size_order(s.size))


SIZE_ALIASES = {"SMALL": "S", "MEDIUM": "M", "LARGE": "L", "EXTRA SMALL": "XS", "EXTRA LARGE": "XL", "2XL": "XXL"}


def _normalize_size(size: str) -> str | None:
    size = size.strip().upper()
    size = SIZE_ALIASES.get(size, size)
    return size if size in SIZES else None


def _summary(conn: sqlite3.Connection, row: sqlite3.Row) -> ProductSummary:
    stock = _stock(conn, row["product_id"])
    description = row["description"]
    if len(description) > 220:
        description = description[:217].rsplit(" ", 1)[0] + "..."
    return ProductSummary(
        product_id=row["product_id"],
        name=row["name"],
        garment_type=row["garment_type"],
        price=row["price"],
        colors=json.loads(row["colors"]),
        description=description,
        sizes_in_stock=[s.size for s in stock if s.quantity > 0],
        sold_out_sizes=[s.size for s in stock if s.quantity <= 0],
    )


def _search_label(query, garment_type, color, min_price, max_price, size, sort) -> str:
    """Short summary of a search for the page header, e.g. "gray · hoodie · under $70 · size L"."""
    parts = [p for p in (color, query.strip() if query else None, garment_type) if p]
    if min_price is not None and max_price is not None:
        parts.append(f"${min_price:g} to ${max_price:g}")
    elif max_price is not None:
        parts.append(f"under ${max_price:g}")
    elif min_price is not None:
        parts.append(f"over ${min_price:g}")
    if size:
        parts.append(f"size {size.upper()}")
    if sort == "price_low_to_high":
        parts.append("cheapest first")
    elif sort == "price_high_to_low":
        parts.append("priciest first")
    return " · ".join(parts) or "all products"


def search_products(
    ctx: RunContext[ChatDeps],
    query: str = "",
    garment_type: str | None = None,
    color: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    size_in_stock: str | None = None,
    sort: Literal["relevance", "price_low_to_high", "price_high_to_low"] = "relevance",
) -> SearchResults:
    """Search the Campus Customs catalogue. Use it before naming or recommending any product.

    Args:
        query: Free-text keywords, e.g. "bulldog", "Saybrook", "hockey", "Yale Mom". Leave empty to browse.
        garment_type: Kind of item, e.g. "hoodie", "crewneck", "t-shirt", "quarter-zip", "fleece", "jacket".
        color: A color to require, e.g. "gray", "white", "navy".
        min_price: Lowest price in USD.
        max_price: Highest price in USD.
        size_in_stock: Only include items with this size in stock: XS, S, M, L, XL, or XXL. Matches that
            are sold out in that size are listed in sold_out_in_requested_size.
        sort: "relevance", "price_low_to_high" (for "cheapest"), or "price_high_to_low".
    """
    terms = _terms(query)
    with connect() as conn:
        rows = conn.execute("SELECT * FROM catalogue").fetchall()
        scored = []
        for row in rows:
            name = _normalize(row["name"])
            kind = row["garment_type"].lower()
            colors = row["colors"].lower()
            text = " ".join([name, kind, row["description"].lower(), row["search_tags"].lower(), colors])

            if garment_type and not all(t in f"{name} {kind}" for t in _terms(garment_type)):
                continue
            if color and not any(c in colors for c in _terms(color)):
                continue
            if min_price is not None and row["price"] < min_price:
                continue
            if max_price is not None and row["price"] > max_price:
                continue

            score = sum(3 if t in name else 1 for t in terms if t in text)
            if terms and score == 0:
                continue
            scored.append((score, row))

        sold_out_in_size: list[str] = []
        if size_in_stock and (size := _normalize_size(size_in_stock)):
            kept = []
            for score, row in scored:
                quantity = next((s.quantity for s in _stock(conn, row["product_id"]) if s.size == size), 0)
                if quantity > 0:
                    kept.append((score, row))
                else:
                    sold_out_in_size.append(row["name"])
            scored = kept

        if sort == "price_low_to_high":
            scored.sort(key=lambda x: (x[1]["price"], x[1]["name"]))
        elif sort == "price_high_to_low":
            scored.sort(key=lambda x: (-x[1]["price"], x[1]["name"]))
        else:
            scored.sort(key=lambda x: (-x[0], x[1]["name"]))

        products = [_summary(conn, r) for _, r in scored[:MAX_RESULTS]]

    # The model sees the top 8; the website can show every match if the agent asks for it.
    if ctx is not None:
        ctx.deps.last_search = SearchCapture(
            label=_search_label(query, garment_type, color, min_price, max_price, size_in_stock, sort),
            product_ids=[r["product_id"] for _, r in scored[:MAX_PAGE_RESULTS]],
            total=len(scored),
        )

    note = None
    if size_in_stock and not _normalize_size(size_in_stock):
        note = f"'{size_in_stock}' isn't a size we carry. Sizes are XS, S, M, L, XL and XXL."
    elif not products and sold_out_in_size:
        note = f"Everything that matched is sold out in {size_in_stock}. Say so and offer other sizes."
    elif not products:
        note = "No matches. Try fewer filters or a broader word, and tell the shopper what we do carry."
    elif len(scored) > MAX_RESULTS:
        note = f"Showing the top {MAX_RESULTS} of {len(scored)}. Narrow the search to see others."
    return SearchResults(
        total_matches=len(scored),
        products=products,
        sold_out_in_requested_size=sold_out_in_size[:MAX_RESULTS],
        note=note,
    )


def get_product_details(ctx: RunContext[ChatDeps], product_id: str) -> ProductDetails | str:
    """Get everything about one product: full description, price, colors, and stock for every size.

    Use it for questions about a specific item: what it looks like, colors, or how many are left.

    Args:
        product_id: The product's id, as returned by search_products.
    """
    with connect() as conn:
        row = conn.execute("SELECT * FROM catalogue WHERE product_id = ?", (product_id,)).fetchone()
        if row is None:
            return f"No product with id '{product_id}'. Use search_products to find the right id."
        stock = _stock(conn, product_id)
    total = sum(s.quantity for s in stock)
    return ProductDetails(
        product_id=row["product_id"],
        name=row["name"],
        garment_type=row["garment_type"],
        price=row["price"],
        colors=json.loads(row["colors"]),
        description=row["description"],
        search_tags=json.loads(row["search_tags"]),
        stock=stock,
        sizes_in_stock=[s.size for s in stock if s.quantity > 0],
        sold_out_sizes=[s.size for s in stock if s.quantity <= 0],
        total_in_stock=total,
        completely_sold_out=total == 0,
    )


def check_stock(ctx: RunContext[ChatDeps], product_id: str, size: str) -> StockCheck | str:
    """Check how many of one product are left in one size. Quickest way to answer "do you have it in L?".

    Args:
        product_id: The product's id, as returned by search_products.
        size: XS, S, M, L, XL, or XXL.
    """
    wanted = _normalize_size(size)
    if wanted is None:
        return f"'{size}' isn't a size we carry. Sizes are XS, S, M, L, XL and XXL."
    with connect() as conn:
        row = conn.execute("SELECT name FROM catalogue WHERE product_id = ?", (product_id,)).fetchone()
        if row is None:
            return f"No product with id '{product_id}'. Use search_products to find the right id."
        stock = _stock(conn, product_id)
    quantity = next((s.quantity for s in stock if s.size == wanted), 0)
    return StockCheck(
        product_id=product_id,
        name=row["name"],
        size=wanted,
        quantity=quantity,
        status=stock_status(quantity),
        other_sizes_in_stock=[s.size for s in stock if s.quantity > 0 and s.size != wanted],
    )


def get_customer_profile(ctx: RunContext[ChatDeps]) -> CustomerProfile | str:
    """Get the logged-in shopper's own account details and chat memory.

    Use it when they ask about their account ("what email am I using?", "how long have I been a member?")
    or about past chats ("what was that hoodie you showed me last time?"). Only ever returns the shopper
    who is logged in right now; there is no way to look up anyone else.
    """
    customer = ctx.deps.customer
    if customer is None:
        return "The shopper is a guest (not logged in), so there is no account or saved chat history."
    with connect() as conn:
        count, first_at = conn.execute(
            "SELECT COUNT(*), MIN(created_at) FROM chat_messages WHERE user_id = ?", (customer.user_id,)
        ).fetchone()
        rows = conn.execute(
            "SELECT products_json FROM chat_messages WHERE user_id = ? AND role = 'assistant' "
            "AND products_json IS NOT NULL ORDER BY id DESC",
            (customer.user_id,),
        ).fetchall()
    seen: dict[str, str] = {}
    for row in rows:
        for p in json.loads(row["products_json"] or "[]"):
            if "product_id" in p and p["product_id"] not in seen:
                seen[p["product_id"]] = p.get("name", p["product_id"])
    return CustomerProfile(
        first_name=customer.first_name,
        last_name=customer.last_name,
        email=customer.email,
        member_since=customer.member_since,
        saved_messages=count,
        first_chat_at=first_at,
        products_discussed=[PastProduct(product_id=i, name=n) for i, n in list(seen.items())[:10]],
    )


TOOLS = [search_products, get_product_details, check_stock, get_customer_profile]


# --- Helpers for the API (not exposed to the agent) -----------------------------


def product_cards(product_ids: list[str]) -> list[ProductCard]:
    """Look up cards for the given ids, keeping their order and silently dropping unknown ids."""
    if not product_ids:
        return []
    with connect() as conn:
        placeholders = ",".join("?" * len(product_ids))
        rows = conn.execute(
            f"SELECT * FROM catalogue WHERE product_id IN ({placeholders})", product_ids
        ).fetchall()
    by_id = {r["product_id"]: r for r in rows}
    return [
        ProductCard(
            product_id=r["product_id"],
            name=r["name"],
            garment_type=r["garment_type"],
            price=r["price"],
            colors=json.loads(r["colors"]),
            image_file_path=r["image_file_path"],
        )
        for pid in dict.fromkeys(product_ids)
        if (r := by_id.get(pid))
    ]


def product_name(product_id: str) -> str | None:
    with connect() as conn:
        row = conn.execute("SELECT name FROM catalogue WHERE product_id = ?", (product_id,)).fetchone()
    return row["name"] if row else None
