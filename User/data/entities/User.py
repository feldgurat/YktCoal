import uuid
from datetime import datetime, timezone

from data.entities.Role import RoleHelpers
from sqlmodel import Field, SQLModel



class User(SQLModel, table=True):
    __tablename__ = "users"

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
        max_length=36,
    )
    name: str = Field(max_length=255)
    contact_number: str = Field(max_length=20, unique=True, index=True)
    telegram_user_id: str | None = Field(default=None)
    address: str | None = Field(default=None, max_length=512)
    roles: int = Field(default=0)
    token_version: int = Field(default=0)
    is_active: bool = Field(default=True)
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    updated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
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
