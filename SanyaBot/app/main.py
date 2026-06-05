"""Точка входа бота.

Связывает aiogram (Bot/Dispatcher) с контейнером зависимостей и роутерами.
Запуск в режиме long polling.
"""

from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from app.config import settings
from app.container import Container
from app.presentation.handlers import build_root_router
from app.presentation.handlers.common import register_error_handler
from app.presentation.middlewares.auth import AuthMiddleware

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


async def main() -> None:
    container = Container.build(settings)

    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dispatcher = Dispatcher(storage=MemoryStorage())

    # Сервисы доступны во всех хендлерах как именованные аргументы.
    dispatcher.workflow_data.update(container.as_workflow_data())

    # Аутентификация — внешний middleware: резолвит current_user до хендлеров.
    auth_mw = AuthMiddleware()
    dispatcher.message.outer_middleware(auth_mw)
    dispatcher.callback_query.outer_middleware(auth_mw)

    dispatcher.include_router(build_root_router())

    # Перехват доменных ошибок на уровне диспетчера — ловит исключения
    # из всех роутеров.
    register_error_handler(dispatcher)

    try:
        logger.info("Бот запускается (long polling)...")
        await bot.delete_webhook(drop_pending_updates=True)
        await dispatcher.start_polling(bot)
    finally:
        await container.aclose()
        await bot.session.close()
        logger.info("Бот остановлен")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt, SystemExit:
        pass
