"""Типизированные callback-данные (aiogram CallbackData).

Дают безопасную сериализацию данных в inline-кнопки вместо ручного парсинга
строк, что снижает количество ошибок.
"""
from __future__ import annotations

from aiogram.filters.callback_data import CallbackData


class MenuCB(CallbackData, prefix="menu"):
    section: str  # main | customer | driver


class ResourcePickCB(CallbackData, prefix="res"):
    resource_id: str


class OrderActionCB(CallbackData, prefix="ord"):
    # view_offers | cancel | complete | start | withdraw | view
    action: str
    order_id: str


class OfferAcceptCB(CallbackData, prefix="ofa"):
    order_id: str
    offer_id: str


class OfferActionCB(CallbackData, prefix="off"):
    action: str  # withdraw | make
    target_id: str  # offer_id или order_id, в зависимости от action


class ConfirmCB(CallbackData, prefix="cfm"):
    action: str  # yes | no
    scope: str
