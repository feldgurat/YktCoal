from uuid import UUID

from sqlmodel import select
from sqlalchemy.orm import selectinload

from data.entities.Admin import Admin
from data.entities.Person import Person
from data.repositories.RoleBaseRepo import RoleBaseRepository


class AdminRepository(RoleBaseRepository[Admin]):
    model = Admin

    
    
    