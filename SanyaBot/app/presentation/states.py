"""FSM-состояния диалогов бота."""
from __future__ import annotations

from aiogram.fsm.state import State, StatesGroup


class Onboarding(StatesGroup):
    waiting_phone = State()
    waiting_name = State()
    waiting_address = State()


class CreateOrder(StatesGroup):
    choosing_resource = State()
    entering_volume = State()
    entering_address = State()
    entering_date = State()
    entering_comment = State()
    confirming = State()


class CreateOffer(StatesGroup):
    entering_price = State()
    entering_date = State()
    entering_comment = State()
    confirming = State()
