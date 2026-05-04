import uuid
from typing import Annotated, Sequence

from fastapi import Depends
from sqlmodel import select

from data.Database import SessionDep
from data.entities.Offer import Offer, OfferStatus
from data.repositories.BaseRepo import BaseRepository


class OfferRepository(BaseRepository[Offer]):

    async def get_by_order(self, order_id: uuid.UUID) -> Sequence[Offer]:
        result = await self._session.exec(
            select(Offer).where(Offer.order_id == order_id)
        )
        return result.all()

    async def get_pending_by_order(self, order_id: uuid.UUID) -> Sequence[Offer]:
        result = await self._session.exec(
            select(Offer)
            .where(Offer.order_id == order_id)
            .where(Offer.status == int(OfferStatus.PENDING))
        )
        return result.all()

    async def get_by_driver(self, driver_id: uuid.UUID) -> Sequence[Offer]:
        result = await self._session.exec(
            select(Offer).where(Offer.driver_id == driver_id)
        )
        return result.all()

    async def get_by_order_and_driver(
        self, order_id: uuid.UUID, driver_id: uuid.UUID
    ) -> Offer | None:
        result = await self._session.exec(
            select(Offer)
            .where(Offer.order_id == order_id)
            .where(Offer.driver_id == driver_id)
            .where(Offer.status == int(OfferStatus.PENDING))
        )
        return result.one_or_none()


def get_offer_repository(session: SessionDep) -> OfferRepository:
    return OfferRepository(session, Offer)


OfferRepositoryDep = Annotated[OfferRepository, Depends(get_offer_repository)]
