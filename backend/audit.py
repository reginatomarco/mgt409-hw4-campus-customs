"""Append-only audit trail of agent-loop activity: output/audit_trail.json.

The file is a JSON array of events. New events are appended by replacing only the closing "]"
at the end of the file, so earlier events are never rewritten or wiped, and the file is always
valid JSON. If the file is ever damaged, logging stops (with a server warning) rather than
overwriting it.
"""

import json
import logging
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path

from pydantic import BaseModel
from pydantic_ai.messages import (
    ModelMessage,
    ModelRequest,
    ModelResponse,
    RetryPromptPart,
    ToolCallPart,
    ToolReturnPart,
)

from models import ChatReply, CustomerProfile, ProductDetails, SearchResults, StockCheck

AUDIT_PATH = Path(__file__).resolve().parent.parent / "output" / "audit_trail.json"
MAX_TEXT = 160  # characters kept from messages, arguments and results

log = logging.getLogger("campus_customs.audit")
_lock = threading.Lock()


def new_run_id() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ-") + uuid.uuid4().hex[:6]


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def short(value, limit: int = MAX_TEXT) -> str:
    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, default=str)
    text = " ".join(text.split())
    return text if len(text) <= limit else text[: limit - 1] + "…"


def summarize_result(content) -> str:
    """One-line summary of a tool result. Never includes the shopper's email."""
    if isinstance(content, SearchResults):
        top = ", ".join(p.name for p in content.products[:3])
        text = f"{content.total_matches} matches; top: {top}" if content.products else "0 matches"
        if content.sold_out_in_requested_size:
            text += f"; sold out in requested size: {len(content.sold_out_in_requested_size)}"
        return short(text)
    if isinstance(content, ProductDetails):
        return short(
            f"{content.name} ${content.price:.2f}; in stock: {','.join(content.sizes_in_stock) or 'none'}; "
            f"sold out: {','.join(content.sold_out_sizes) or 'none'}"
        )
    if isinstance(content, StockCheck):
        return short(f"{content.name} {content.size}: {content.quantity} left ({content.status})")
    if isinstance(content, CustomerProfile):
        return f"own profile returned ({content.saved_messages} saved messages, {len(content.products_discussed)} past products)"
    if isinstance(content, BaseModel):
        return short(content.model_dump())
    return short(content)


def events_from_messages(run_id: str, messages: list[ModelMessage], base: dict) -> list[dict]:
    """Turn the run's new messages into tool_call / tool_result / retry events, in order."""
    events = []
    for message in messages:
        if isinstance(message, ModelResponse):
            for part in message.parts:
                if isinstance(part, ToolCallPart) and part.tool_name != "final_result":
                    events.append({
                        **base, "time": message.timestamp.isoformat(timespec="milliseconds"),
                        "step": "tool_call", "tool": part.tool_name, "args": short(part.args_as_dict()),
                    })
        elif isinstance(message, ModelRequest):
            for part in message.parts:
                if isinstance(part, ToolReturnPart) and part.tool_name != "final_result":
                    events.append({
                        **base, "time": part.timestamp.isoformat(timespec="milliseconds"),
                        "step": "tool_result", "tool": part.tool_name, "result": summarize_result(part.content),
                    })
                elif isinstance(part, RetryPromptPart):
                    events.append({
                        **base, "time": part.timestamp.isoformat(timespec="milliseconds"),
                        "step": "retry", "tool": part.tool_name, "result": short(part.model_response()),
                    })
    return events


def usage_from_messages(messages: list[ModelMessage]) -> dict:
    responses = [m for m in messages if isinstance(m, ModelResponse)]
    return {
        "model_requests": len(responses),
        "input_tokens": sum(r.usage.input_tokens or 0 for r in responses),
        "output_tokens": sum(r.usage.output_tokens or 0 for r in responses),
        "finish_reason": responses[-1].finish_reason if responses else None,
    }


def summarize_output(output: ChatReply) -> str:
    return short(
        f"{len(output.product_ids)} product card(s); show_results_on_page={output.show_results_on_page}; "
        f"reply: {output.reply}"
    )


def append_events(events: list[dict]) -> None:
    """Append events to the audit file without touching anything already in it. Never raises."""
    if not events:
        return
    try:
        with _lock:
            _append(events)
    except Exception:
        log.exception("Could not write the audit trail")


def _append(events: list[dict]) -> None:
    chunk = ",\n".join("  " + json.dumps(e, ensure_ascii=False, indent=2).replace("\n", "\n  ") for e in events)
    AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not AUDIT_PATH.exists() or AUDIT_PATH.stat().st_size == 0:
        AUDIT_PATH.write_text("[\n" + chunk + "\n]\n", encoding="utf-8")
        return
    with open(AUDIT_PATH, "r+b") as f:
        f.seek(0, 2)
        size = f.tell()
        f.seek(max(0, size - 4096))
        tail = f.read()
        close = tail.rstrip().rfind(b"]")
        if close < 0 or tail.rstrip()[close + 1 :]:
            raise ValueError(f"{AUDIT_PATH} doesn't end with ']'; refusing to modify it")
        close_pos = size - len(tail) + close
        f.seek(max(0, close_pos - 4096))
        before = f.read(close_pos - max(0, close_pos - 4096)).rstrip()
        separator = b"\n" if before.endswith(b"[") else b",\n"
        f.seek(close_pos)
        f.truncate()  # removes only the closing "]" (and trailing whitespace)
        f.write(separator + chunk.encode("utf-8") + b"\n]\n")
