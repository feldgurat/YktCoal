import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlmodel import SQLModel

from api.routes import API_V1_PREFIX, TELEGRAM
from config import settings
from data.schemas.Offer import OfferRead, TgOfferCreate
from data.schemas.Order import OrderCreate, OrderRead, TgOrderCreate
from data.schemas.Resource import ResourceRead
from services.OfferService import OfferService, OfferServiceDep
from services.OrderService import OrderService, OrderServiceDep
from services.ResourceService import ResourceService, ResourceServiceDep


async def verify_bot_key(
    x_service_key: str = Header(..., alias="X-Service-Key"),
) -> None:
    if x_service_key != settings.INTERNAL_TELEGRAM_SERVICE_KEY:
        raise HTTPException(status_code=403, detail="Неверный сервисный ключ")


router = APIRouter(
    prefix=f"{API_V1_PREFIX}{TELEGRAM}",
    tags=["Telegram"],
    dependencies=[Depends(verify_bot_key)],
)

_r_order = OrderService.to_read
_r_offer = OfferService.to_read
_r_resource = ResourceService.to_read


class TgAcceptOffer(SQLModel):
    user_id: uuid.UUID
    order_id: uuid.UUID
    offer_id: uuid.UUID


class TgOrderAction(SQLModel):
    user_id: uuid.UUID


# ── Resources ──────────────────────────────────────────────────


@router.get("/resources", response_model=list[ResourceRead])
async def tg_list_resources(service: ResourceServiceDep):
    items = await service.list_active()
    return [_r_resource(x) for x in items]


# ── Orders ─────────────────────────────────────────────────────


@router.post("/orders", response_model=OrderRead, status_code=201)
async def tg_create_order(data: TgOrderCreate, service: OrderServiceDep):
    payload = OrderCreate(
        resource_id=data.resource_id,
        dest_address=data.dest_address,
        volume=data.volume,
        cost=data.cost,
        requested_delivery_date=data.requested_delivery_date,
        comment=data.comment,
        latitude=data.latitude,
        longitude=data.longitude,
    )
    o = await service.create(data.user_id, payload)
    return _r_order(o)


@router.get("/orders/by-user/{user_id}", response_model=list[OrderRead])
async def tg_my_orders(user_id: uuid.UUID, service: OrderServiceDep):
    items = await service.list_my(user_id)
    return [_r_order(o) for o in items]


@router.get("/orders/by-driver/{user_id}", response_model=list[OrderRead])
async def tg_driver_orders(user_id: uuid.UUID, service: OrderServiceDep):
    items = await service.list_driver_orders(user_id)
    return [_r_order(o) for o in items]


@router.get("/orders/available", response_model=list[OrderRead])
async def tg_available_orders(service: OrderServiceDep):
    items = await service.list_available()
    return [_r_order(o) for o in items]


@router.get("/orders/{order_id}", response_model=OrderRead)
async def tg_get_order(
    order_id: uuid.UUID,
    user_id: uuid.UUID,
    service: OrderServiceDep,
    roles: Annotated[list[str] | None, Query()] = None,
):
    o = await service.get_for_actor(user_id, roles or [], order_id)
    return _r_order(o)


@router.post("/orders/{order_id}/accept-offer", response_model=OrderRead)
async def tg_accept_offer(order_id: uuid.UUID, data: TgAcceptOffer, service: OrderServiceDep):
    if data.order_id != order_id:
        raise HTTPException(status_code=400, detail="order_id в пути и теле не совпадают")
    order, _offer = await service.accept_offer(data.user_id, order_id, data.offer_id)
    return _r_order(order)


@router.post("/orders/{order_id}/start", response_model=OrderRead)
async def tg_start_order(order_id: uuid.UUID, data: TgOrderAction, service: OrderServiceDep):
    o = await service.start(data.user_id, order_id)
    return _r_order(o)


@router.post("/orders/{order_id}/complete", response_model=OrderRead)
async def tg_complete_order(order_id: uuid.UUID, data: TgOrderAction, service: OrderServiceDep):
    o = await service.complete(data.user_id, order_id)
    return _r_order(o)


@router.post("/orders/{order_id}/cancel", response_model=OrderRead)
async def tg_cancel_order(order_id: uuid.UUID, data: TgOrderAction, service: OrderServiceDep):
    o = await service.cancel(data.user_id, order_id)
    return _r_order(o)


@router.post("/orders/{order_id}/driver-withdraw", response_model=OrderRead)
async def tg_driver_withdraw(order_id: uuid.UUID, data: TgOrderAction, service: OrderServiceDep):
    o = await service.driver_withdraw(data.user_id, order_id)
    return _r_order(o)


# ── Offers ─────────────────────────────────────────────────────


@router.get("/orders/{order_id}/offers", response_model=list[OfferRead])
async def tg_list_offers_for_order(
    order_id: uuid.UUID,
    user_id: uuid.UUID,
    service: OfferServiceDep,
):
    # user_id передаётся как query — это user-заказчик. Внутри сервис проверит права.
    items = await service.list_for_order(user_id, order_id)
    return [_r_offer(o) for o in items]


@router.post("/offers", response_model=OfferRead, status_code=201)
async def tg_create_offer(data: TgOfferCreate, service: OfferServiceDep):
    from data.schemas.Offer import OfferCreate

    payload = OfferCreate(
        order_id=data.order_id,
        price=data.price,
        comment=data.comment,
        delivery_date=data.delivery_date,
    )
    offer = await service.create(data.user_id, payload)
    return _r_offer(offer)


@router.get("/offers/by-driver/{user_id}", response_model=list[OfferRead])
async def tg_my_offers(user_id: uuid.UUID, service: OfferServiceDep):
    items = await service.list_for_driver(user_id)
    return [_r_offer(o) for o in items]


class TgOfferAction(SQLModel):
    user_id: uuid.UUID


@router.post("/offers/{offer_id}/withdraw", response_model=OfferRead)
async def tg_withdraw_offer(offer_id: uuid.UUID, data: TgOfferAction, service: OfferServiceDep):
    offer = await service.withdraw(data.user_id, offer_id)
    return _r_offer(offer)
