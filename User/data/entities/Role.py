from enum import IntFlag


class Role(IntFlag):
    USER = 1    # bit 0
    ADMIN = 2   # bit 1
    DRIVER = 4  # bit 2


ROLE_MAP: dict[str, Role] = {
    "user": Role.USER,
    "admin": Role.ADMIN,
    "driver": Role.DRIVER,
}

ROLE_NAMES: dict[Role, str] = {v: k for k, v in ROLE_MAP.items()}


def role_name_to_bit(name: str) -> int:
    role = ROLE_MAP.get(name.lower())
    if role is None:
        raise ValueError(f"Неизвестная роль: {name}")
    return int(role)


def mask_to_names(mask: int) -> list[str]:
    return [name for name, bit in ROLE_MAP.items() if mask & bit]


def names_to_mask(names: list[str]) -> int:
    mask = 0
    for name in names:
        mask |= role_name_to_bit(name)
    return mask
