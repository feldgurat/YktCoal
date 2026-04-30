import logging

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from data.entities.Resource import Resource

logger = logging.getLogger(__name__)

DEFAULT_RESOURCES = [
    {"name": "Уголь бурый", "unit": "тонна", "price_per_unit": 5000},
    {"name": "Уголь каменный", "unit": "тонна", "price_per_unit": 8000},
    {"name": "Уголь антрацит", "unit": "тонна", "price_per_unit": 12000},
]


async def seed_default_resources(session: AsyncSession) -> None:
    result = await session.exec(select(Resource))
    existing = result.all()

    if existing:
        logger.info("Resources already seeded (%d found), skipping", len(existing))
        return

    for item in DEFAULT_RESOURCES:
        resource = Resource(**item)
        session.add(resource)

    await session.commit()
    logger.info("Seeded %d default resources", len(DEFAULT_RESOURCES))
