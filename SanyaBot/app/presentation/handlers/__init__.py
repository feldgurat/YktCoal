"""Сбор всех роутеров слоя представления в нужном порядке."""

from aiogram import Router

from app.presentation.handlers import customer, driver, start


def build_root_router() -> Router:
    router = Router(name="root")
    # Сначала диалоги старта/онбординга, затем доменные хендлеры.
    router.include_router(start.router)
    router.include_router(customer.router)
    router.include_router(driver.router)
    return router
