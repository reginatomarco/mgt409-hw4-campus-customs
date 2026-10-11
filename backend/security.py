"""Password hashing and session tokens (Python standard library only).

Passwords use the course format: PBKDF2-HMAC-SHA256 with 120,000 iterations,
stored as pbkdf2_sha256$<salt>$<hex digest>. Every password gets its own random
salt, so two people with the same password get different hashes, and precomputed
"rainbow tables" of common passwords are useless.
"""

import hashlib
import hmac
import os
import secrets
import time
from pathlib import Path

ALGORITHM = "pbkdf2_sha256"
ITERATIONS = 120_000

SESSION_COOKIE = "cc_session"
SESSION_TTL_SECONDS = 7 * 24 * 3600
_SECRET_FILE = Path(__file__).resolve().parent / ".session_secret"


def _digest(password: str, salt: str) -> str:
    return hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), ITERATIONS).hex()


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)  # 128 random bits, unique per password
    return f"{ALGORITHM}${salt}${_digest(password, salt)}"


def verify_password(password: str, stored: str) -> bool:
    parts = stored.split("$")
    if len(parts) != 3 or parts[0] != ALGORITHM:
        return False
    _, salt, expected = parts
    # compare_digest takes the same time however many characters match.
    return hmac.compare_digest(_digest(password, salt), expected)


# Checked against when the email doesn't exist, so a wrong email takes as long as
# a wrong password and the response time doesn't reveal which accounts exist.
DUMMY_HASH = hash_password(secrets.token_hex(16))


def _secret() -> bytes:
    """Signing key: SESSION_SECRET env var, else a random key kept in backend/.session_secret."""
    if env := os.getenv("SESSION_SECRET"):
        return env.encode()
    if not _SECRET_FILE.exists():
        _SECRET_FILE.write_text(secrets.token_hex(32))
    return _SECRET_FILE.read_text().strip().encode()


def _sign(payload: str) -> str:
    return hmac.new(_secret(), payload.encode(), hashlib.sha256).hexdigest()


def make_session_token(user_id: int) -> str:
    payload = f"{user_id}.{int(time.time()) + SESSION_TTL_SECONDS}"
    return f"{payload}.{_sign(payload)}"


def read_session_token(token: str | None) -> int | None:
    """Return the user id if the token is genuine and unexpired, else None."""
    if not token or token.count(".") != 2:
        return None
    user_id, expires, signature = token.split(".")
    if not hmac.compare_digest(_sign(f"{user_id}.{expires}"), signature):
        return None
    if not (user_id.isdigit() and expires.isdigit()) or int(expires) < time.time():
        return None
    return int(user_id)


class LoginThrottle:
    """Locks out an email/IP pair for a while after too many failed logins."""

    def __init__(self, max_failures: int = 5, window_seconds: int = 15 * 60):
        self.max_failures = max_failures
        self.window = window_seconds
        self._failures: dict[str, list[float]] = {}

    def _recent(self, key: str) -> list[float]:
        cutoff = time.time() - self.window
        recent = [t for t in self._failures.get(key, []) if t > cutoff]
        self._failures[key] = recent
        return recent

    def is_locked(self, key: str) -> bool:
        return len(self._recent(key)) >= self.max_failures

    def fail(self, key: str) -> None:
        self._recent(key).append(time.time())

    def reset(self, key: str) -> None:
        self._failures.pop(key, None)


class RateLimit:
    """Allows at most `limit` hits per key in any rolling `window_seconds` (kept in memory)."""

    def __init__(self, limit: int, window_seconds: int):
        self.limit = limit
        self.window = window_seconds
        self._hits: dict[str, list[float]] = {}

    def _recent(self, key: str) -> list[float]:
        cutoff = time.time() - self.window
        recent = [t for t in self._hits.get(key, []) if t > cutoff]
        self._hits[key] = recent
        return recent

    def retry_after(self, key: str) -> int:
        """Seconds until `key` may hit again; 0 if it may hit now."""
        recent = self._recent(key)
        if len(recent) < self.limit:
            return 0
        if not recent:  # limit of 0 (chat switched off): blocked for a full window
            return self.window
        return max(1, int(recent[0] + self.window - time.time()) + 1)

    def hit(self, key: str) -> None:
        self._recent(key).append(time.time())
