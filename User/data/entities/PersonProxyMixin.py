from __future__ import annotations

from typing import Optional


class PersonProxyMixin:
    @property
    def name(self) -> str | None:
        return self.person.name if self.person else None

    @name.setter
    def name(self, value: str) -> None:
        if self.person is None:
            raise ValueError("Object is not linked to Person")
        self.person.name = value

    @property
    def contact_number(self) -> str | None:
        return self.person.contact_number if self.person else None

    @contact_number.setter
    def contact_number(self, value: str) -> None:
        if self.person is None:
            raise ValueError("Object is not linked to Person")
        self.person.contact_number = value

    @property
    def telegram_user_id(self) -> str | None:
        return self.person.telegram_user_id if self.person else None

    @telegram_user_id.setter
    def telegram_user_id(self, value: str | None) -> None:
        if self.person is None:
            raise ValueError("Object is not linked to Person")
        self.person.telegram_user_id = value

    @property
    def token_version(self) -> int | None:
        return self.person.token_version if self.person else None

    @token_version.setter
    def token_version(self, value: int) -> None:
        if self.person is None:
            raise ValueError("Object is not linked to Person")
        self.person.token_version = value