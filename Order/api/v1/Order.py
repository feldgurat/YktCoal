import uuid

from fastapi import APIRouter, Depends

from api.routes import API_V1_PREFIX, ORDERS
from api.v1.dependencies import (
    CurrentAdminDep,
    CurrentDriverDep,
    CurrentUserDep,
    get_current_user,
)
from data.schemas.Offer import OfferRead
from data.schemas.Order import OrderCreate, OrderRead, OrderUpdate
from services.OfferService import OfferService, OfferServiceDep
from services.OrderService import OrderService, OrderServiceDep

router = APIRouter(
    prefix=f"{API_V1_PREFIX}{ORDERS}",
    tags=["Orders"],
    dependencies=[Depends(get_current_user)],
)

_r = OrderService.to_read
_r_offer = OfferService.to_read


# ── Customer (любой пользователь) ──────────────────────────────


@router.post("", response_model=OrderRead, status_code=201)
async def create_order(
    data: OrderCreate, current_user: CurrentUserDep, service: OrderServiceDep
):
    o = await service.create(current_user.id, data)
    return _r(o)


@router.get("/me", response_model=list[OrderRead])
async def my_orders(current_user: CurrentUserDep, service: OrderServiceDep):
    items = await service.list_my(current_user.id)
    return [_r(o) for o in items]


@router.get("/{order_id}", response_model=OrderRead)
async def get_order(
    order_id: uuid.UUID, _user: CurrentUserDep, service: OrderServiceDep
):
    o = await service.get(order_id)
    return _r(o)


@router.patch("/{order_id}", response_model=OrderRead)
async def update_order(
    order_id: uuid.UUID,
    data: OrderUpdate,
    current_user: CurrentUserDep,
    service: OrderServiceDep,
):
    o = await service.update(current_user.id, order_id, data)
    return _r(o)


@router.get("/{order_id}/offers", response_model=list[OfferRead])
async def list_offers_for_order(
    order_id: uuid.UUID,
    current_user: CurrentUserDep,
    offer_service: OfferServiceDep,
):
    offers = await offer_service.list_for_order(current_user.id, order_id)
    return [_r_offer(o) for o in offers]


@router.post("/{order_id}/offers/{offer_id}/accept", response_model=OrderRead)
async def accept_offer(
    order_id: uuid.UUID,
    offer_id: uuid.UUID,
    current_user: CurrentUserDep,
    service: OrderServiceDep,
):
    order, _offer = await service.accept_offer(current_user.id, order_id, offer_id)
    return _r(order)


@router.post("/{order_id}/complete", response_model=OrderRead)
async def complete_order(
    order_id: uuid.UUID, current_user: CurrentUserDep, service: OrderServiceDep
):
    o = await service.complete(current_user.id, order_id)
    return _r(o)


@router.post("/{order_id}/cancel", response_model=OrderRead)
async def cancel_order(
    order_id: uuid.UUID, current_user: CurrentUserDep, service: OrderServiceDep
):
    o = await service.cancel(current_user.id, order_id)
    return _r(o)


# ── Driver ─────────────────────────────────────────────────────


@router.get("/available/list", response_model=list[OrderRead])
async def list_available(_driver: CurrentDriverDep, service: OrderServiceDep):
    """Доступные для подачи Offer заказы (status=NEW)."""
    items = await service.list_available()
    return [_r(o) for o in items]


@router.get("/driver/me", response_model=list[OrderRead])
async def my_driver_orders(current_user: CurrentDriverDep, service: OrderServiceDep):
    """Заказы, в которых я — назначенный водитель."""
    items = await service.list_driver_orders(current_user.id)
    return [_r(o) for o in items]


@router.post("/{order_id}/start", response_model=OrderRead)
async def start_order(
    order_id: uuid.UUID, current_user: CurrentDriverDep, service: OrderServiceDep
):
    o = await service.start(current_user.id, order_id)
    return _r(o)


@router.post("/{order_id}/driver-withdraw", response_model=OrderRead)
async def driver_withdraw(
    order_id: uuid.UUID, current_user: CurrentDriverDep, service: OrderServiceDep
):
    o = await service.driver_withdraw(current_user.id, order_id)
    return _r(o)


# ── Admin ──────────────────────────────────────────────────────


@router.get("", response_model=list[OrderRead])
async def list_all_orders(service: OrderServiceDep, _admin: CurrentAdminDep):
    items = await service.list_all()
    return [_r(o) for o in items]
