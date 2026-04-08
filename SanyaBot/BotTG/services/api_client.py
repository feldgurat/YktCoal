"""HTTP-клиент для общения с FastAPI-бэкендом."""

import logging
from typing import Any

import aiohttp

from bot.config import API_BASE_URL

logger = logging.getLogger(__name__)

_session: aiohttp.ClientSession | None = None


async def get_session() -> aiohttp.ClientSession:
    global _session
    if _session is None or _session.closed:
        _session = aiohttp.ClientSession(base_url=API_BASE_URL)
    return _session


async def close_session() -> None:
    global _session
    if _session and not _session.closed:
        await _session.close()
        _session = None


async def _request(
    method: str,
    path: str,
    *,
    json: dict | None = None,
    token: str | None = None,
) -> dict[str, Any]:
    """Универсальный запрос к бэкенду. Возвращает распарсенный JSON."""
    headers: dict[str, str] = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    session = await get_session()
    try:
        async with session.request(method, path, json=json, headers=headers) as resp:
            body = await resp.json()
            if resp.status >= 400:
                logger.warning("API %s %s → %s: %s", method, path, resp.status, body)
            return {"status": resp.status, "body": body}
    except aiohttp.ClientError as exc:
        logger.error("API request failed: %s", exc)
        return {"status": 0, "body": {"detail": str(exc)}}


# ── Auth endpoints ─────────────────────────────────────────────

async def register(
    name: str,
    phone: str,
    telegram_user_id: int | None = None,
    address: str | None = None,
) -> dict:
    return await _request("POST", "/api/v1/auth/register", json={
        "name": name,
        "contact_number": phone,
        "telegram_user_id": telegram_user_id,
        "address": address,
    })


async def request_sign_in_code(phone: str) -> dict:
    return await _request("POST", "/api/v1/auth/sign-in-code-request", json={
        "phone": phone,
    })


async def verify_sign_in_code(phone: str, code: str) -> dict:
    return await _request("POST", "/api/v1/auth/sign-in-code-answer", json={
        "phone": phone,
        "code": code,
    })


async def refresh_tokens(refresh_token: str) -> dict:
    return await _request("POST", "/api/v1/auth/refresh", json={
        "refresh_token": refresh_token,
    })


# ── User endpoints (требуют access_token) ─────────────────────

async def get_me(access_token: str) -> dict:
    return await _request("GET", "/api/v1/users/me", token=access_token)
