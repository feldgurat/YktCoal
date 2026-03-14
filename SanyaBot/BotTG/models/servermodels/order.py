from decimal import Decimal
from models.user import User
from models.driver import Driver

class Order:
    id: int
    user: User
    driver: Driver
    resource_type: int
    address: str
    sum: int
    weight: int