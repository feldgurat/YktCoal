from typing import List
from uuid import UUID

from sqlmodel import select
from sqlalchemy.orm import selectinload

from data.entities.Person import Person
from data.entities.User import User
from data.repositories.RoleBaseRepo import RoleBaseRepository


class UserRepository(RoleBaseRepository[User]):
    model = User

