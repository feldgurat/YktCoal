from typing import Optional
from repos.user_repo import UserRepo
from models.botmodels.user import User
from models.botmodels.auth import AuthSession
from factories.user_factory import UserFactory


class UserService:
    def __init__(self):
        self.user_repo = UserRepo()
    
    async def register_user(
        self,
        telegram_id: int,
        phone_number: str,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None
    ) -> User:
        """Регистрация нового пользователя"""
        # Проверяем, существует ли уже пользователь
        existing_user = await self.user_repo.get_user(telegram_id)
        if existing_user:
            # Обновляем данные существующего пользователя
            return await self.user_repo.update_user(
                telegram_id,
                phone_number=phone_number,
                username=username,
                first_name=first_name,
                last_name=last_name,
                is_registered=True
            )
        
        # Создаем нового пользователя
        user = UserFactory.create_from_telegram(
            telegram_id=telegram_id,
            phone_number=phone_number,
            username=username,
            first_name=first_name,
            last_name=last_name
        )
        return await self.user_repo.create_user(user)
    
    async def get_user(self, telegram_id: int) -> Optional[User]:
        """Получение пользователя по telegram_id"""
        return await self.user_repo.get_user(telegram_id)
    
    async def is_user_registered(self, telegram_id: int) -> bool:
        """Проверка, зарегистрирован ли пользователь"""
        user = await self.user_repo.get_user(telegram_id)
        return user is not None and user.is_registered
    
    async def create_auth_session(self, telegram_id: int) -> AuthSession:
        """Создание сессии авторизации"""
        session = AuthSession(telegram_id=telegram_id)
        return await self.user_repo.create_auth_session(session)
    
    async def get_auth_session(self, telegram_id: int) -> Optional[AuthSession]:
        """Получение сессии авторизации"""
        return await self.user_repo.get_auth_session(telegram_id)
    
    async def update_auth_session_phone(self, telegram_id: int, phone_number: str) -> Optional[AuthSession]:
        """Обновление номера телефона в сессии"""
        return await self.user_repo.update_auth_session(
            telegram_id,
            phone_number=phone_number,
            step="complete"
        )
    
    async def clear_auth_session(self, telegram_id: int) -> bool:
        """Очистка сессии авторизации"""
        return await self.user_repo.delete_auth_session(telegram_id)
    
    async def validate_phone_number(self, phone_number: str) -> bool:
        """Валидация номера телефона"""
        # Базовая проверка: начинается с + и содержит только цифры после
        if not phone_number.startswith('+'):
            return False
        
        # Убираем + и проверяем, что остальное - цифры
        digits = phone_number[1:]
        return digits.isdigit() and 10 <= len(digits) <= 15