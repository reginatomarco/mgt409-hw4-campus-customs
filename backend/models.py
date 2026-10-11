"""Structured types shared by the chat agent, its tools, and the chat API."""

from dataclasses import dataclass, field
from typing import Literal

from pydantic import BaseModel, Field, field_validator

MAX_PRODUCT_CARDS = 6
MAX_PAGE_RESULTS = 60

# --- Agent output ---------------------------------------------------------------


class ChatReply(BaseModel):
    """What the agent must return for every shopper message."""

    reply: str = Field(description="Your message to the shopper, in short Markdown.")
    product_ids: list[str] = Field(
        default_factory=list,
        description="product_id of each product your reply recommends or talks about, best first, "
        "at most 6. Only ids returned by a tool. Empty if no specific product is relevant.",
    )

    show_results_on_page: bool = Field(
        default=False,
        description="True when the shopper is browsing or searching for a set of products "
        "(e.g. 'what hoodies do you have?'). The website then shows every match from your latest "
        "search_products call as product cards on the page. False for single-item questions, "
        "stock checks, greetings and off-topic messages.",
    )

    @field_validator("product_ids")
    @classmethod
    def tidy_ids(cls, ids: list[str]) -> list[str]:
        # Trim instead of rejecting: a rejection would send the model back for another (paid) try.
        return list(dict.fromkeys(i.strip() for i in ids if i.strip()))[:MAX_PRODUCT_CARDS]


# --- What tools return to the agent ---------------------------------------------


LOW_STOCK_THRESHOLD = 5  # fewer than this many left counts as "low_stock"

StockStatus = Literal["in_stock", "low_stock", "sold_out"]


def stock_status(quantity: int) -> StockStatus:
    if quantity <= 0:
        return "sold_out"
    return "low_stock" if quantity < LOW_STOCK_THRESHOLD else "in_stock"


class ProductSummary(BaseModel):
    """One search hit: enough to recommend or compare without a second lookup."""

    product_id: str = Field(description="Exact id to pass to other tools and to list in product_ids.")
    name: str
    garment_type: str
    price: float = Field(description="Price in USD, straight from the catalogue.")
    colors: list[str]
    description: str = Field(description="Catalogue description, shortened to about 220 characters.")
    sizes_in_stock: list[str] = Field(description="Sizes with at least 1 left, XS to XXL.")
    sold_out_sizes: list[str] = Field(description="Sizes with 0 left. Tell the shopper if they want one of these.")


class SizeStock(BaseModel):
    size: str
    quantity: int = Field(description="Units left in this size. 0 means sold out.")
    status: StockStatus


class ProductDetails(BaseModel):
    """Everything we know about one product, including stock for every size."""

    product_id: str
    name: str
    garment_type: str
    price: float = Field(description="Price in USD, straight from the catalogue.")
    colors: list[str]
    description: str = Field(description="Full catalogue description. Don't add details it doesn't mention.")
    search_tags: list[str]
    stock: list[SizeStock] = Field(description="Every size XS to XXL with its quantity and status.")
    sizes_in_stock: list[str]
    sold_out_sizes: list[str]
    total_in_stock: int
    completely_sold_out: bool = Field(description="True if every size is at 0.")


class StockCheck(BaseModel):
    """Answer to "do you have product X in size Y?"."""

    product_id: str
    name: str
    size: str
    quantity: int = Field(description="Units left in this size. 0 means sold out.")
    status: StockStatus
    other_sizes_in_stock: list[str] = Field(description="Sizes to offer instead if this one is sold out.")


class SearchResults(BaseModel):
    total_matches: int = Field(description="How many products matched, even if only the top few are listed.")
    products: list[ProductSummary]
    sold_out_in_requested_size: list[str] = Field(
        default_factory=list,
        description="Names of products that matched everything except being sold out in the requested size.",
    )
    note: str | None = None


# --- Run context ----------------------------------------------------------------


@dataclass
class SearchCapture:
    """Every match from a search_products call, kept for the website (the model only sees the top 8)."""

    label: str  # human-readable summary of the search, e.g. "hoodie · under $70"
    product_ids: list[str]  # all matches in the tool's order, capped at MAX_PAGE_RESULTS
    total: int


class CustomerInfo(BaseModel):
    """The logged-in shopper, loaded from the users table by the backend (never from the browser)."""

    user_id: int
    first_name: str
    last_name: str
    email: str
    member_since: str  # users.created_at, e.g. "2026-10-11 20:01:12"


PageType = Literal["home", "products", "assistant_results", "product", "about", "login", "create_account", "other"]


class PageContext(BaseModel):
    """What the shopper has on screen when they send a message. Sent by the website with each message."""

    page: PageType = "other"
    viewing_product_id: str | None = Field(default=None, max_length=200)
    selected_size: str | None = Field(default=None, max_length=10)
    search_text: str | None = Field(default=None, max_length=100)  # Products page search box
    category: str | None = Field(default=None, max_length=50)  # Products page category filter
    results_label: str | None = Field(default=None, max_length=200)  # assistant results on the page
    results_product_ids: list[str] = Field(default_factory=list, max_length=6)  # first few result cards


@dataclass
class ChatDeps:
    """Per-request facts the agent and its tools can see."""

    customer: CustomerInfo | None = None  # None means a guest who isn't logged in
    page: PageContext = field(default_factory=PageContext)
    last_search: SearchCapture | None = None  # set by search_products; read by the chat route

    @property
    def first_name(self) -> str | None:
        return self.customer.first_name if self.customer else None


class PastProduct(BaseModel):
    product_id: str
    name: str


class CustomerProfile(BaseModel):
    """What get_customer_profile returns: the logged-in shopper's own account and chat memory."""

    first_name: str
    last_name: str
    email: str
    member_since: str
    saved_messages: int = Field(description="How many messages are saved in their chat history.")
    first_chat_at: str | None = Field(description="When they first chatted with the assistant.")
    products_discussed: list[PastProduct] = Field(
        description="Products the assistant showed them in past chats, most recent first (up to 10)."
    )


# --- Chat API -------------------------------------------------------------------


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=1000)
    page: PageContext = Field(default_factory=PageContext)


class ProductCard(BaseModel):
    """A product shown under a bot reply. Saved in chat_messages.products_json."""

    product_id: str
    name: str
    garment_type: str
    price: float
    colors: list[str]
    image_file_path: str


class ChatMessageOut(BaseModel):
    role: Literal["user", "assistant"]
    content: str
    products: list[ProductCard] = []


class CatalogProduct(BaseModel):
    """A full product as the website's product cards need it (same shape as GET /api/products)."""

    product_id: str
    name: str
    garment_type: str
    description: str
    colors: list[str]
    search_tags: list[str]
    image_file_path: str
    price: float
    blurb: str


class PageResults(BaseModel):
    """Search results the website shows as product cards on the Products page."""

    label: str
    total: int
    products: list[CatalogProduct]


class ChatResponse(BaseModel):
    reply: str
    products: list[ProductCard]
    page_results: PageResults | None = Field(
        default=None, description="Present when the agent chose to show its search results on the page."
    )
    saved: bool = Field(description="True if the exchange was saved to the shopper's history.")
