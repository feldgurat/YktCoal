# services/bot_service.py
from typing import Dict, Optional, Any
from aiogram import types
from aiogram.fsm.context import FSMContext

from BotTG.bot.main import Bot
from services.server_service import ServerService
from factories.auth_answer_factory import AuthAnswerFactory
from models.botmodels.user import User
from repos.user_repo import UserRepo


class BotService:
    """
    Сервис для обработки логики бота
    Связывает фабрики, репозитории и серверный сервис
    """

    def __init__(self, bot: Bot, server_service: ServerService, user_repo: UserRepo):
        """
        Инициализация сервиса бота
        
        Args:
            bot: Экземпляр бота
            server_service: Сервис для работы с сервером
            user_repo: Репозиторий пользователей
        """
        self.bot = bot
        self.server_service = server_service
        self.user_repo = user_repo
        self.auth_factory = AuthAnswerFactory()

    async def send_message(self, chat_id: int, message: str, reply_markup=None):
        """
        Отправка сообщения пользователю
        
        Args:
            chat_id: ID чата
            message: Текст сообщения
            reply_markup: Клавиатура (опционально)
        """
        await self.bot.send_message(chat_id=chat_id, text=message, reply_markup=reply_markup)

    async def handle_start_command(self, message: types.Message, state: FSMContext):
        """
        Обработка команды /start
        
        Args:
            message: Сообщение от пользователя
            state: Состояние FSM
        """
        user_id = message.from_user.id
        username = message.from_user.username
        
        # Получаем приветственное сообщение и клавиатуру из фабрики
        welcome_text = self.auth_factory.get_auth_start_message(user_id, username)
        keyboard = self.auth_factory.get_contact_keyboard()
        
        # Отправляем сообщение
        await self.send_message(
            chat_id=user_id,
            message=welcome_text,
            reply_markup=keyboard
        )
        
        # Устанавливаем состояние ожидания контакта
        await state.set_state("waiting_for_contact")

    async def handle_contact(self, message: types.Message, state: FSMContext):
        """
        Обработка полученного контакта (номера телефона)
        
        Args:
            message: Сообщение с контактом
            state: Состояние FSM
        """
        contact = message.contact
        user_id = message.from_user.id
        
        # Проверяем, что номер принадлежит пользователю
        if contact.user_id != user_id:
            error_message = self.auth_factory.get_auth_error_message("wrong_user")
            await self.send_message(user_id, error_message)
            return
        
        # Сообщаем о начале обработки
        await self.send_message(
            user_id,
            self.auth_factory.get_contact_processing_message()
        )
        
        # Получаем номер телефона
        phone_number = contact.phone_number
        
        # Проверяем пользователя в локальной БД через репозиторий
        local_user = await self.user_repo.get_by_phone(phone_number)
        
        if local_user:
            # Пользователь найден в локальной БД
            await self._handle_existing_user(message, local_user, state)
        else:
            # Пользователь не найден локально, проверяем на сервере
            await self._handle_new_user(message, phone_number, state)

    async def _handle_existing_user(self, message: types.Message, user: User, state: FSMContext):
        """
        Обработка существующего пользователя
        
        Args:
            message: Сообщение от пользователя
            user: Объект пользователя
            state: Состояние FSM
        """
        user_id = message.from_user.id
        
        # Формируем данные пользователя для ответа
        user_data = {
            'name': user.name or user.username,
            'role': user.role or 'user',
            'phone': user.phone
        }
        
        # Отправляем сообщение об успешной аутентификации
        success_message = self.auth_factory.get_auth_success_message(user_data)
        await self.send_message(user_id, success_message)
        
        # Очищаем состояние
        await state.clear()
        
        # Здесь можно добавить логику для авторизованного пользователя
        await self._handle_authorized_user(message, user)

    async def _handle_new_user(self, message: types.Message, phone_number: str, state: FSMContext):
        """
        Обработка нового пользователя (проверка на сервере)
        
        Args:
            message: Сообщение от пользователя
            phone_number: Номер телефона
            state: Состояние FSM
        """
        user_id = message.from_user.id
        
        # Аутентификация на сервере
        auth_result = await self.server_service.auth_user(phone_number)
        
        if auth_result and auth_result.get('success'):
            # Успешная аутентификация на сервере
            user_data = auth_result.get('user_data', {})
            
            # Создаем пользователя в локальной БД
            new_user = User(
                telegram_id=user_id,
                phone=phone_number,
                name=user_data.get('name', message.from_user.full_name),
                username=message.from_user.username,
                role=user_data.get('role', 'user'),
                is_authenticated=True
            )
            
            # Сохраняем в репозиторий
            await self.user_repo.create(new_user)
            
            # Отправляем сообщение об успехе
            success_message = self.auth_factory.get_auth_success_message(user_data)
            await self.send_message(user_id, success_message)
            
            # Очищаем состояние
            await state.clear()
        else:
            # Ошибка аутентификации на сервере
            error_message = self.auth_factory.get_auth_error_message(
                auth_result.get('error', 'server_error') if auth_result else 'server_error'
            )
            await self.send_message(user_id, error_message)

    async def auth_user(self, credentials: Dict[str, Any]) -> Optional[User]:
        """
        Аутентификация пользователя с переданными данными
        
        Args:
            credentials: Данные для аутентификации (телефон, код и т.д.)
            
        Returns:
            Optional[User]: Объект пользователя или None
        """
        phone = credentials.get('phone')
        
        if not phone:
            return None
        
        # Проверяем в локальной БД
        user = await self.user_repo.get_by_phone(phone)
        
        if user:
            return user
        
        # Если нет локально, проверяем на сервере
        auth_result = await self.server_service.auth_user(phone)
        
        if auth_result and auth_result.get('success'):
            # Создаем пользователя
            user_data = auth_result.get('user_data', {})
            user = User(
                phone=phone,
                name=user_data.get('name'),
                role=user_data.get('role', 'user'),
                is_authenticated=True
            )
            await self.user_repo.create(user)
            return user
        
        return None

    async def register_user(self, user: User) -> bool:
        """
        Регистрация нового пользователя
        
        Args:
            user: Объект пользователя для регистрации
            
        Returns:
            bool: Успешность регистрации
        """
        try:
            # Регистрация на сервере
            server_result = await self.server_service.register_user(user.to_dict())
            
            if server_result and server_result.get('success'):
                # Сохраняем в локальную БД
                user.is_authenticated = True
                await self.user_repo.create(user)
                
                # Отправляем уведомление в Telegram
                await self.send_message(
                    user.telegram_id,
                    "✅ Вы успешно зарегистрированы в системе!"
                )
                return True
            else:
                error_msg = server_result.get('error', 'Ошибка регистрации на сервере')
                await self.send_message(
                    user.telegram_id,
                    f"❌ {error_msg}"
                )
                return False
                
        except Exception as e:
            print(f"Ошибка при регистрации пользователя: {e}")
            await self.send_message(
                user.telegram_id,
                "❌ Произошла ошибка при регистрации. Попробуйте позже."
            )
            return False

    async def _handle_authorized_user(self, message: types.Message, user: User):
        """
        Обработка авторизованного пользователя
        
        Args:
            message: Сообщение от пользователя
            user: Объект пользователя
        """
        # Здесь можно добавить логику для авторизованных пользователей
        # Например, отправить главное меню или информацию о доступных командах
        pass

    async def logout_user(self, telegram_id: int) -> bool:
        """
        Выход пользователя из системы
        
        Args:
            telegram_id: ID пользователя в Telegram
            
        Returns:
            bool: Успешность выхода
        """
        user = await self.user_repo.get_by_telegram_id(telegram_id)
        
        if user:
            user.is_authenticated = False
            await self.user_repo.update(user)
            
            await self.send_message(
                telegram_id,
                "👋 Вы вышли из системы. Для входа используйте /start"
            )
            return True
        
        return False

    async def get_user_info(self, telegram_id: int) -> Optional[Dict]:
        """
        Получение информации о пользователе
        
        Args:
            telegram_id: ID пользователя в Telegram
            
        Returns:
            Optional[Dict]: Информация о пользователе
        """
        user = await self.user_repo.get_by_telegram_id(telegram_id)
        
        if user:
            return {
                'telegram_id': user.telegram_id,
                'username': user.username,
                'name': user.name,
                'phone': user.phone,
                'role': user.role,
                'is_authenticated': user.is_authenticated,
                'created_at': user.created_at
            }
        
        return None