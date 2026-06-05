import uuid

from fastapi import APIRouter, Depends

from api.routes import API_V1_PREFIX, OFFERS
from api.v1.dependencies import CurrentDriverDep, get_current_user
from data.schemas.Offer import OfferCreate, OfferRead
from services.OfferService import OfferService, OfferServiceDep

router = APIRouter(
    prefix=f"{API_V1_PREFIX}{OFFERS}",
    tags=["Offers"],
    dependencies=[Depends(get_current_user)],
)

_r = OfferService.to_read


@router.post("", response_model=OfferRead, status_code=201)
async def create_offer(data: OfferCreate, current_user: CurrentDriverDep, service: OfferServiceDep):
    offer = await service.create(current_user.id, data)
    return _r(offer)


@router.get("/me", response_model=list[OfferRead])
async def my_offers(current_user: CurrentDriverDep, service: OfferServiceDep):
    items = await service.list_for_driver(current_user.id)
    return [_r(o) for o in items]


@router.post("/{offer_id}/withdraw", response_model=OfferRead)
async def withdraw_offer(
    offer_id: uuid.UUID, current_user: CurrentDriverDep, service: OfferServiceDep
):
    offer = await service.withdraw(current_user.id, offer_id)
    return _r(offer)
