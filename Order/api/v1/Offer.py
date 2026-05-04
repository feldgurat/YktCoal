from uuid import UUID

from fastapi import APIRouter, HTTPException

from api.routes import API_V1_PREFIX, ORDERS
from api.v1.dependencies import (
    CurrentDriverDep,
    CurrentTokenUserDep,
)
from data.schemas.Offer import OfferCreate, OfferRead
from data.schemas.Order import MessageResponse
from services.Exceptions import AppException
from services.OfferService import OfferServiceDep

router = APIRouter(prefix=f"{API_V1_PREFIX}", tags=["Offers"])


def _handle(exc: AppException):
    raise HTTPException(status_code=exc.status_code, detail=exc.message)


# ── Водитель отправляет предложение ────────────────────────────

@router.post(
    f"{ORDERS}/{{order_id}}/offers",
    response_model=OfferRead,
    status_code=201,
)
async def create_offer(
    order_id: UUID,
    data: OfferCreate,
    token_user: CurrentDriverDep,
    offer_service: OfferServiceDep,
):
    """Водитель предлагает свою цену и срок на заказ."""
    try:
        offer = await offer_service.create(order_id, token_user.id, data)
    except AppException as exc:
        _handle(exc)
    return offer_service.to_read(offer)


# ── Список предложений на заказ ────────────────────────────────

@router.get(
    f"{ORDERS}/{{order_id}}/offers",
    response_model=list[OfferRead],
)
async def get_order_offers(
    order_id: UUID,
    token_user: CurrentTokenUserDep,
    offer_service: OfferServiceDep,
):
    """Предложения по заказу. Клиент видит на своих заказах, водитель — свои офферы."""
    offers = await offer_service.get_by_order(order_id)
    return [offer_service.to_read(o) for o in offers]


# ── Мои предложения (водитель) ─────────────────────────────────

@router.get(
    "/offers/my",
    response_model=list[OfferRead],
)
async def get_my_offers(
    token_user: CurrentDriverDep,
    offer_service: OfferServiceDep,
):
    """Все предложения текущего водителя."""
    offers = await offer_service.get_by_driver(token_user.id)
    return [offer_service.to_read(o) for o in offers]


# ── Клиент принимает предложение ───────────────────────────────

@router.post(
    "/offers/{offer_id}/accept",
    response_model=OfferRead,
)
async def accept_offer(
    offer_id: UUID,
    token_user: CurrentTokenUserDep,
    offer_service: OfferServiceDep,
):
    """Клиент принимает предложение водителя. Остальные автоматически отклоняются."""
    try:
        offer = await offer_service.accept(offer_id, token_user.id)
    except AppException as exc:
        _handle(exc)
    return offer_service.to_read(offer)


# ── Клиент отклоняет предложение ───────────────────────────────

@router.post(
    "/offers/{offer_id}/reject",
    response_model=OfferRead,
)
async def reject_offer(
    offer_id: UUID,
    token_user: CurrentTokenUserDep,
    offer_service: OfferServiceDep,
):
    """Клиент отклоняет конкретное предложение."""
    try:
        offer = await offer_service.reject(offer_id, token_user.id)
    except AppException as exc:
        _handle(exc)
    return offer_service.to_read(offer)


# ── Водитель отзывает своё предложение ─────────────────────────

@router.post(
    "/offers/{offer_id}/withdraw",
    response_model=OfferRead,
)
async def withdraw_offer(
    offer_id: UUID,
    token_user: CurrentDriverDep,
    offer_service: OfferServiceDep,
):
    """Водитель отзывает своё предложение, пока оно ещё не принято."""
    try:
        offer = await offer_service.withdraw(offer_id, token_user.id)
    except AppException as exc:
        _handle(exc)
    return offer_service.to_read(offer)
