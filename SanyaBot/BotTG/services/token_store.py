"""Хранение JWT-токенов пользователей в памяти.

Для продакшена лучше вынести в Redis.
"""

from dataclasses import dataclass


@dataclass
class TokenPair:
    access_token: str
    refresh_token: str


_store: dict[int, TokenPair] = {}


def save(telegram_id: int, access: str, refresh: str) -> None:
    _store[telegram_id] = TokenPair(access, refresh)


def get(telegram_id: int) -> TokenPair | None:
    return _store.get(telegram_id)


def remove(telegram_id: int) -> None:
    _store.pop(telegram_id, None)


def has(telegram_id: int) -> bool:
    return telegram_id in _store
