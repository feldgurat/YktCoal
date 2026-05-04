from uuid import UUID

from fastapi import APIRouter, HTTPException

from api.routes import API_V1_PREFIX, ORDERS
from api.v1.dependencies import (
    CurrentAdminDep,
    CurrentDriverDep,
    CurrentTokenUserDep,
)
from data.entities.Order import OrderStatus
from data.schemas.Order import (
    MessageResponse,
    OrderCreate,
    OrderRead,
    OrderStatusUpdate,
    OrderUpdate,
)
from services.Exceptions import AppException
from services.OrderService import OrderServiceDep

router = APIRouter(prefix=f"{API_V1_PREFIX}{ORDERS}", tags=["Orders"])


def _handle(exc: AppException):
    raise HTTPException(status_code=exc.status_code, detail=exc.message)


# ══════════════════════════════════════════════════════════════
# Client endpoints
# ══════════════════════════════════════════════════════════════


@router.post("", response_model=OrderRead, status_code=201)
async def create_order(
    data: OrderCreate,
    token_user: CurrentTokenUserDep,
    order_service: OrderServiceDep,
):
    """Клиент создаёт заявку. Цена будет определена через офферы водителей."""
    try:
        order = await order_service.create(token_user.id, data)
    except AppException as exc:
        _handle(exc)
    return order_service.to_read(order)


@router.get("/my", response_model=list[OrderRead])
async def get_my_orders(
    token_user: CurrentTokenUserDep,
    order_service: OrderServiceDep,
):
    """Заказы текущего пользователя (как клиента)."""
    orders = await order_service.get_by_client(token_user.id)
    return [order_service.to_read(o) for o in orders]


@router.patch("/{order_id}", response_model=OrderRead)
async def update_order(
    order_id: UUID,
    data: OrderUpdate,
    token_user: CurrentTokenUserDep,
    order_service: OrderServiceDep,
):
    """Клиент редактирует свой заказ (только в статусе NEW)."""
    try:
        order = await order_service.update(order_id, data, token_user.id)
    except AppException as exc:
        _handle(exc)
    return order_service.to_read(order)


@router.post("/{order_id}/cancel", response_model=OrderRead)
async def cancel_order(
    order_id: UUID,
    token_user: CurrentTokenUserDep,
    order_service: OrderServiceDep,
):
    """Клиент отменяет свой заказ."""
    try:
        order = await order_service.cancel(order_id, token_user.id)
    except AppException as exc:
        _handle(exc)
    return order_service.to_read(order)


# ══════════════════════════════════════════════════════════════
# Driver endpoints
# ══════════════════════════════════════════════════════════════


@router.get("/available", response_model=list[OrderRead])
async def get_available_orders(
    _driver: CurrentDriverDep,
    order_service: OrderServiceDep,
):
    """Доступные заказы для водителей (NEW, открыты для офферов)."""
    orders = await order_service.get_available()
    return [order_service.to_read(o) for o in orders]


@router.get("/driver/my", response_model=list[OrderRead])
async def get_driver_orders(
    token_user: CurrentDriverDep,
    order_service: OrderServiceDep,
):
    """Заказы, назначенные текущему водителю (оффер принят)."""
    orders = await order_service.get_by_driver(token_user.id)
    return [order_service.to_read(o) for o in orders]


@router.post("/{order_id}/start", response_model=OrderRead)
async def start_delivery(
    order_id: UUID,
    token_user: CurrentDriverDep,
    order_service: OrderServiceDep,
):
    """Водитель начинает доставку."""
    try:
        order = await order_service.get(order_id)
    except AppException as exc:
        _handle(exc)

    if order.driver_id != token_user.id:
        raise HTTPException(status_code=403, detail="Это не ваш заказ")

    try:
        order = await order_service.change_status(
            order_id, int(OrderStatus.IN_PROGRESS)
        )
    except AppException as exc:
        _handle(exc)
    return order_service.to_read(order)


@router.post("/{order_id}/complete", response_model=OrderRead)
async def complete_delivery(
    order_id: UUID,
    token_user: CurrentDriverDep,
    order_service: OrderServiceDep,
):
    """Водитель завершает доставку."""
    try:
        order = await order_service.get(order_id)
    except AppException as exc:
        _handle(exc)

    if order.driver_id != token_user.id:
        raise HTTPException(status_code=403, detail="Это не ваш заказ")

    try:
        order = await order_service.change_status(
            order_id, int(OrderStatus.COMPLETED)
        )
    except AppException as exc:
        _handle(exc)
    return order_service.to_read(order)


# ══════════════════════════════════════════════════════════════
# Admin endpoints
# ══════════════════════════════════════════════════════════════


@router.get("/by-status/{status}", response_model=list[OrderRead])
async def get_orders_by_status(
    status: int,
    _admin: CurrentAdminDep,
    order_service: OrderServiceDep,
):
    """Все заказы с определённым статусом (admin)."""
    orders = await order_service.get_by_status(status)
    return [order_service.to_read(o) for o in orders]


@router.get("", response_model=list[OrderRead])
async def get_all_orders(
    _admin: CurrentAdminDep,
    order_service: OrderServiceDep,
):
    """Все заказы (admin)."""
    orders = await order_service.get_all()
    return [order_service.to_read(o) for o in orders]


@router.get("/{order_id}", response_model=OrderRead)
async def get_order(
    order_id: UUID,
    token_user: CurrentTokenUserDep,
    order_service: OrderServiceDep,
):
    """Получить заказ по ID."""
    try:
        order = await order_service.get(order_id)
    except AppException as exc:
        _handle(exc)

    is_owner = order.client_id == token_user.id
    is_driver = order.driver_id == token_user.id
    is_admin = token_user.has_role("admin")

    if not (is_owner or is_driver or is_admin):
        raise HTTPException(status_code=403, detail="Нет доступа к этому заказу")

    return order_service.to_read(order)


@router.post("/{order_id}/status", response_model=OrderRead)
async def change_status(
    order_id: UUID,
    data: OrderStatusUpdate,
    _admin: CurrentAdminDep,
    order_service: OrderServiceDep,
):
    """Админ меняет статус заказа."""
    try:
        order = await order_service.change_status(order_id, data.status)
    except AppException as exc:
        _handle(exc)
    return order_service.to_read(order)
