"""Chat agent entry point: builds the PydanticAI agent and runs one shopper turn."""

import json
import os
import time
from pathlib import Path

os.environ.setdefault("PYDANTIC_AI_NO_BANNER", "1")

from dotenv import load_dotenv  # noqa: E402

load_dotenv(Path(__file__).resolve().parent.parent / ".env")  # hw4/.env; real env vars win

import httpx
from openai import AsyncOpenAI
from pydantic_ai import Agent, RunContext, capture_run_messages
from pydantic_ai.exceptions import ModelHTTPError, UsageLimitExceeded
from pydantic_ai.messages import ModelMessage, ModelRequest, ModelResponse, TextPart, UserPromptPart
from pydantic_ai.models import Model
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.usage import UsageLimits

import audit
from models import ChatDeps, ChatReply, PageContext
from tools import TOOLS, product_name

PROMPT_PATH = Path(__file__).resolve().parent / "prompts" / "prompt.md"
CHAT_MODEL = os.getenv("CHAT_MODEL", "gpt-4o-mini")

# Cost guards: each shopper message may use at most this many model calls and tokens.
HISTORY_MESSAGES = 10
USAGE_LIMITS = UsageLimits(request_limit=4, total_tokens_limit=25_000)
MAX_OUTPUT_TOKENS = 600


def portkey_model(model_name: str = CHAT_MODEL) -> OpenAIChatModel:
    """OpenAI-compatible model routed through the course Portkey gateway."""
    key = os.getenv("PORTKEY_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("Set PORTKEY_API_KEY or OPENAI_API_KEY")
    base_url = os.getenv("PORTKEY_BASE_URL") or os.getenv("OPENAI_BASE_URL") or "https://api.portkey.ai/v1"
    host = httpx.URL(base_url).host
    headers = {"x-portkey-api-key": key} if host == "portkey.ai" or host.endswith(".portkey.ai") else {}
    client = AsyncOpenAI(
        api_key=key,
        base_url=base_url,
        default_headers=headers,
        max_retries=0,  # a failed call is not silently retried (and paid for) again
        timeout=httpx.Timeout(60, connect=15),
    )
    return OpenAIChatModel(model_name, provider=OpenAIProvider(openai_client=client))


def create_agent(model: Model | str | None = None) -> Agent[ChatDeps, ChatReply]:
    prompt = PROMPT_PATH.read_text(encoding="utf-8").strip()
    if not prompt:
        raise ValueError(f"System prompt is empty: {PROMPT_PATH}")
    agent = Agent(
        model,
        deps_type=ChatDeps,
        output_type=ChatReply,
        instructions=prompt,
        tools=TOOLS,
        retries=1,
        model_settings={"max_tokens": MAX_OUTPUT_TOKENS},
        defer_model_check=True,
    )

    @agent.instructions
    def shopper_context(ctx: RunContext[ChatDeps]) -> str:
        return describe_shopper(ctx.deps) + "\n" + describe_page(ctx.deps.page)

    return agent


PAGE_NAMES = {
    "home": "the home page",
    "products": "the Products page",
    "assistant_results": "the Products page, showing your search results",
    "product": "a product page",
    "about": "the About Us page",
    "login": "the Log in page",
    "create_account": "the Create Account page",
    "other": "the website",
}


def describe_shopper(deps: ChatDeps) -> str:
    """Who is chatting. Only the first name goes in every prompt; email etc. come from get_customer_profile."""
    if deps.customer is None:
        return "## Shopper\nA guest (not logged in). Nothing from this chat will be remembered next time."
    return (
        f"## Shopper\nLogged in as {deps.customer.first_name} (member since {deps.customer.member_since[:10]}). "
        "Earlier messages in this conversation come from their saved chat history. "
        "Call get_customer_profile for their full name, email, or products from past chats."
    )


def describe_page(page: PageContext) -> str:
    """What's on the shopper's screen, so "this", "it" and "these" can be resolved.

    Product names are looked up in the database; only ids from the browser are trusted, never its text.
    """
    lines = [f"## On screen\nThe shopper is on {PAGE_NAMES.get(page.page, 'the website')}."]
    if page.viewing_product_id and (name := product_name(page.viewing_product_id)):
        line = f'They have the product page open for "{name}" (product_id: {page.viewing_product_id})'
        if page.selected_size:
            line += f" with size {page.selected_size} selected"
        lines.append(line + '. "This", "it" or "this one" most likely means this product.')
    if page.results_product_ids:
        shown = [f"{n} ({i})" for i in page.results_product_ids if (n := product_name(i))]
        if shown:
            lines.append(
                f'The page shows your search results for "{page.results_label or "a search"}". '
                f"First cards: {', '.join(shown)}. \"These\" means these results."
            )
    filters = [f'search "{page.search_text}"' if page.search_text else "", f"category {page.category}" if page.category else ""]
    if any(filters):
        lines.append("Products page filters: " + ", ".join(f for f in filters if f) + ".")
    return "\n".join(lines)


_agent: Agent[ChatDeps, ChatReply] | None = None


def get_agent() -> Agent[ChatDeps, ChatReply]:
    """The live agent, created on first use so the server can start without an API key."""
    global _agent
    if _agent is None:
        _agent = create_agent(portkey_model())
    return _agent


def history_to_messages(rows: list[dict]) -> list[ModelMessage]:
    """Turn saved chat_messages rows (oldest first) into PydanticAI message history."""
    messages: list[ModelMessage] = []
    for row in rows[-HISTORY_MESSAGES:]:
        if row["role"] == "user":
            messages.append(ModelRequest(parts=[UserPromptPart(content=row["content"])]))
        else:
            text = row["content"]
            ids = [p["product_id"] for p in json.loads(row["products_json"] or "[]") if "product_id" in p]
            if ids:
                # Lets the agent resolve follow-ups like "do you have that one in pink?"
                text += f"\n\n[Products shown: {', '.join(ids)}]"
            messages.append(ModelResponse(parts=[TextPart(content=text)]))
    # History must start with a shopper message.
    while messages and isinstance(messages[0], ModelResponse):
        messages.pop(0)
    return messages


def is_content_filter(exc: BaseException) -> bool:
    """True if the model provider refused the message with its content filter (e.g. Azure OpenAI)."""
    if not isinstance(exc, ModelHTTPError) or exc.status_code != 400:
        return False
    text = str(exc).lower()
    return "content management policy" in text or "content_filter" in text or "content filter" in text


async def run_chat(
    message: str,
    deps: ChatDeps,
    history: list[dict],
    agent: Agent[ChatDeps, ChatReply] | None = None,
) -> ChatReply:
    """Run one shopper turn and record it in output/audit_trail.json (start, tools, end), even if it fails."""
    agent = agent or get_agent()
    past = history_to_messages(history)
    run_id = audit.new_run_id()
    base = {
        "run_id": run_id,
        "shopper": f"user:{deps.customer.user_id}" if deps.customer else "guest",
        "page": deps.page.page,
        "model": getattr(agent.model, "model_name", CHAT_MODEL),
    }
    started = time.perf_counter()
    events = [{**base, "time": audit.now(), "step": "run_start", "args": audit.short(message),
               "history_messages": len(past)}]
    output, stop_reason, error = None, "final_result", None
    with capture_run_messages() as messages:
        try:
            result = await agent.run(message, deps=deps, message_history=past, usage_limits=USAGE_LIMITS)
            output = result.output
        except UsageLimitExceeded as exc:
            stop_reason, error = "usage_limit", exc
        except Exception as exc:  # noqa: BLE001 - logged, then re-raised below
            stop_reason = "content_filter" if is_content_filter(exc) else f"error:{type(exc).__name__}"
            error = exc
    new_messages = messages[len(past):]
    events += audit.events_from_messages(run_id, new_messages, base)
    events.append({
        **base, "time": audit.now(), "step": "run_end", "stop_reason": stop_reason,
        "result": audit.summarize_output(output) if output else audit.short(str(error)),
        **audit.usage_from_messages(new_messages),
        "elapsed_seconds": round(time.perf_counter() - started, 2),
    })
    audit.append_events(events)
    if error is not None:
        raise error
    return output
