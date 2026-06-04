import uuid
from collections.abc import Sequence
from typing import Annotated

from fastapi import Depends
from sqlmodel import select

from data.Database import SessionDep
from data.entities.Offer import Offer, OfferStatus
from data.repositories.BaseRepo import BaseRepository


class OfferRepository(BaseRepository[Offer]):
    async def get_by_order_id(self, order_id: uuid.UUID) -> Sequence[Offer]:
        result = await self._session.exec(
            select(Offer)
            .where(Offer.order_id == order_id)
            .order_by(Offer.created_at.asc())
        )
        return result.all()

    async def get_by_driver_id(self, driver_user_id: uuid.UUID) -> Sequence[Offer]:
        result = await self._session.exec(
            select(Offer)
            .where(Offer.driver_user_id == driver_user_id)
            .order_by(Offer.created_at.desc())
        )
        return result.all()

    async def get_pending_for_order(self, order_id: uuid.UUID) -> Sequence[Offer]:
        result = await self._session.exec(
            select(Offer).where(
                Offer.order_id == order_id,
                Offer.status == OfferStatus.PENDING,
            )
        )
        return result.all()

    async def get_existing_pending(
        self, order_id: uuid.UUID, driver_user_id: uuid.UUID
    ) -> Offer | None:
        result = await self._session.exec(
            select(Offer).where(
                Offer.order_id == order_id,
                Offer.driver_user_id == driver_user_id,
                Offer.status == OfferStatus.PENDING,
            )
        )
        return result.first()


def get_offer_repository(session: SessionDep) -> OfferRepository:
    return OfferRepository(session, Offer)


OfferRepositoryDep = Annotated[OfferRepository, Depends(get_offer_repository)]
