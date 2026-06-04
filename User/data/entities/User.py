import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime
from sqlmodel import Field, SQLModel

from data.entities.Role import RoleHelpers


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=255)
    contact_number: str = Field(max_length=20, unique=True, index=True)
    telegram_user_id: str | None = Field(default=None)
    address: str | None = Field(default=None, max_length=512)
    roles: int = Field(default=0)
    token_version: int = Field(default=0)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_type=DateTime(timezone=True),  # ← изменить
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_type=DateTime(timezone=True),  # ← изменить
    )
    # ── Role helpers ───────────────────────────────────────────

    def has_role(self, role_name: str) -> bool:
        bit = RoleHelpers.role_name_to_bit(role_name)
        return bool(self.roles & bit)

    def add_role(self, role_name: str) -> None:
        bit = RoleHelpers.role_name_to_bit(role_name)
        self.roles |= bit

    def remove_role(self, role_name: str) -> None:
        bit = RoleHelpers.role_name_to_bit(role_name)
        self.roles &= ~bit

    @property
    def role_names(self) -> list[str]:
        return RoleHelpers.mask_to_names(self.roles)
