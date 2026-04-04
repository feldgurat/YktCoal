import logging

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from config import settings
from data.entities.Role import Role
from data.entities.User import User

logger = logging.getLogger(__name__)


async def create_default_admin(session: AsyncSession) -> None:
    result = await session.execute(select(User))
    all_users = result.scalars().all()

    admins = [u for u in all_users if u.has_role("admin")]
    if admins:
        logger.info("Admin already exists (%s), skipping", admins[0].name)
        return

    admin = User(
        name=settings.DEFAULT_ADMIN_NAME,
        contact_number=settings.DEFAULT_ADMIN_PHONE,
        roles=int(Role.ADMIN),
    )
    session.add(admin)
    await session.commit()

    logger.info(
        "Default admin created: name=%s, phone=%s, id=%s",
        admin.name,
        admin.contact_number,
        admin.id,
    )
