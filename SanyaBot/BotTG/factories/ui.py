from aiogram.types import (
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)


class Keyboards:
    @staticmethod
    def phone() -> ReplyKeyboardMarkup:
        return ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="📱 Отправить номер", request_contact=True)]],
            resize_keyboard=True,
            one_time_keyboard=True,
        )

    @staticmethod
    def main_menu() -> ReplyKeyboardMarkup:
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="👤 Профиль")],
                [KeyboardButton(text="🚚 Заказать уголь")],
            ],
            resize_keyboard=True,
        )

    @staticmethod
    def remove() -> ReplyKeyboardRemove:
        return ReplyKeyboardRemove()


class Messages:
    @staticmethod
    def ask_phone() -> str:
        return (
            "🔐 Для начала работы отправьте свой номер телефона.\n\n"
            "Нажмите кнопку ниже:"
        )

    @staticmethod
    def ask_code() -> str:
        return "✉️ Введите код подтверждения из SMS:"

    @staticmethod
    def welcome(name: str) -> str:
        return f"✅ Добро пожаловать, {name}! Вы авторизованы."

    @staticmethod
    def already_logged_in(name: str) -> str:
        return f"👋 С возвращением, {name}!"

    @staticmethod
    def error(text: str) -> str:
        return f"❌ {text}"

    @staticmethod
    def logged_out() -> str:
        return "👋 Вы вышли. Для повторного входа — /start"

    @staticmethod
    def not_authorized() -> str:
        return "❌ Вы не авторизованы. Используйте /start"

    @staticmethod
    def profile(data: dict) -> str:
        roles = ", ".join(data.get("roles", []))
        return (
            f"👤 Профиль\n\n"
            f"📛 Имя: {data.get('name', '—')}\n"
            f"📱 Телефон: {data.get('contact_number', '—')}\n"
            f"🏷 Роли: {roles or '—'}\n"
            f"📅 Создан: {data.get('created_at', '—')}"
        )
