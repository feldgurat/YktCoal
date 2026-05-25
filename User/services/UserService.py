from collections.abc import Sequence
from typing import Annotated

from data.entities.Role import RoleHelpers
from data.entities.User import User
from data.repositories.UserRepo import UserRepository, UserRepositoryDep
from data.schemas.User import UserCreate, UserRead, UserUpdate
from fastapi import Depends

from services.Exeptions import InvalidRoleError, UserAlreadyExistsError, UserNotFoundError


class UserService:
    def __init__(self, repository: UserRepository) -> None:
        self._repo = repository

    # ── Entity → Schema ────────────────────────────────────────

    @staticmethod
    def to_read(user: User) -> UserRead:
        return UserRead(
            id=user.id,
            name=user.name,
            contact_number=user.contact_number,
            telegram_user_id=user.telegram_user_id,
            address=user.address,
            roles=user.role_names,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )

    # ── CRUD ───────────────────────────────────────────────────

    async def get(self, user_id: str) -> User:
        user = await self._repo.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError()
        return user

    async def get_list(self) -> Sequence[User]:
        return await self._repo.get_all()

    async def get_by_role(self, role_name: str) -> Sequence[User]:
        try:
            return await self._repo.get_by_role(role_name)
        except ValueError:
            raise InvalidRoleError(f"Неизвестная роль: {role_name}") from None

    async def get_by_contact_number(self, phone: str) -> User | None:
        return await self._repo.get_by_contact_number(phone)
    
    async def get_by_telegram_user_id(self, telegram_user_id: str) -> User | None:
        return await self._repo.get_by_telegram_user_id(telegram_user_id)

    async def create(self, data: UserCreate) -> User:
        existing = await self._repo.get_by_contact_number(data.contact_number)
        if existing is not None:
            raise UserAlreadyExistsError()

        try:
            role_mask = RoleHelpers.names_to_mask(data.roles)
        except ValueError as e:
            raise InvalidRoleError(str(e)) from e

        user = User(
            name=data.name,
            contact_number=data.contact_number,
            telegram_user_id=data.telegram_user_id,
            address=data.address,
            roles=role_mask,
        )
        return await self._repo.create(user)

    async def update(self, user_id: str, data: UserUpdate) -> User:
        user = await self._repo.update(user_id, data)
        if user is None:
            raise UserNotFoundError()
        return user

    async def delete(self, user_id: str) -> bool:
        return await self._repo.delete(user_id)

    # ── Role management ────────────────────────────────────────

    async def add_role(self, user_id: str, role_name: str) -> User:
        user = await self.get(user_id)
        try:
            user.add_role(role_name)
            await self._repo.flush()
        except ValueError:
            raise InvalidRoleError(f"Неизвестная роль: {role_name}") from None
        return user

    async def remove_role(self, user_id: str, role_name: str) -> User:
        user = await self.get(user_id)
        try:
            user.remove_role(role_name)
            await self._repo.flush()
        except ValueError:
            raise InvalidRoleError(f"Неизвестная роль: {role_name}") from None
        return user


def get_user_service(repo: UserRepositoryDep) -> UserService:
    return UserService(repo)


UserServiceDep = Annotated[UserService, Depends(get_user_service)]
