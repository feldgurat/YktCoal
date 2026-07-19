from typing import Annotated

from fastapi import Depends

from config import settings
from ykt_common.token_auth import TokenAuthService


def get_auth_service() -> TokenAuthService:
    return TokenAuthService(settings.JWT_SECRET, settings.JWT_ALGORITHM)


AuthServiceDep = Annotated[TokenAuthService, Depends(get_auth_service)]
