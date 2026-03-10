from typing import Optional, List
from models.botmodels.user import User
from models.botmodels.auth import AuthSession
from .base_repo import BaseRepo


class UserRepo(BaseRepo):
    USERS_FILE = "users.json"
    AUTH_SESSIONS_FILE = "auth_sessions.json"
    
    async def create_user(self, user: User) -> User:
        users = await self._read_json(self.USERS_FILE)
        users[str(user.telegram_id)] = {
            "telegram_id": user.telegram_id,
            "phone_number": user.phone_number,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "is_registered": user.is_registered,
            "created_at": str(user.created_at),
            "updated_at": str(user.updated_at)
        }
        await self._write_json(self.USERS_FILE, users)
        return user
    
    async def get_user(self, telegram_id: int) -> Optional[User]:
        users = await self._read_json(self.USERS_FILE)
        user_data = users.get(str(telegram_id))
        
        if user_data:
            return User(**user_data)
        return None
    
    async def update_user(self, telegram_id: int, **kwargs) -> Optional[User]:
        users = await self._read_json(self.USERS_FILE)
        if str(telegram_id) not in users:
            return None
        
        users[str(telegram_id)].update(kwargs)
        await self._write_json(self.USERS_FILE, users)
        return await self.get_user(telegram_id)
    
    async def create_auth_session(self, session: AuthSession) -> AuthSession:
        sessions = await self._read_json(self.AUTH_SESSIONS_FILE)
        sessions[str(session.telegram_id)] = {
            "telegram_id": session.telegram_id,
            "phone_number": session.phone_number,
            "step": session.step,
            "created_at": str(session.created_at),
            "expires_at": str(session.expires_at) if session.expires_at else None
        }
        await self._write_json(self.AUTH_SESSIONS_FILE, sessions)
        return session
    
    async def get_auth_session(self, telegram_id: int) -> Optional[AuthSession]:
        sessions = await self._read_json(self.AUTH_SESSIONS_FILE)
        session_data = sessions.get(str(telegram_id))
        
        if session_data:
            return AuthSession(**session_data)
        return None
    
    async def update_auth_session(self, telegram_id: int, **kwargs) -> Optional[AuthSession]:
        sessions = await self._read_json(self.AUTH_SESSIONS_FILE)
        if str(telegram_id) not in sessions:
            return None
        
        sessions[str(telegram_id)].update(kwargs)
        await self._write_json(self.AUTH_SESSIONS_FILE, sessions)
        return await self.get_auth_session(telegram_id)
    
    async def delete_auth_session(self, telegram_id: int) -> bool:
        sessions = await self._read_json(self.AUTH_SESSIONS_FILE)
        if str(telegram_id) in sessions:
            del sessions[str(telegram_id)]
            await self._write_json(self.AUTH_SESSIONS_FILE, sessions)
            return True
        return False
    
    async def get_all_users(self) -> List[User]:
        users = await self._read_json(self.USERS_FILE)
        return [User(**data) for data in users.values()]