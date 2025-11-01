"""
FSM States для IQStocker v2.0

Определение всех состояний FSM для handlers
"""

from aiogram.fsm.state import State, StatesGroup


class AnalyticsStates(StatesGroup):
    """Состояния для анализа CSV"""
    waiting_for_csv = State()


class ThemeStates(StatesGroup):
    """Состояния для генерации тем"""
    selecting_category = State()


class BroadcastStates(StatesGroup):
    """Состояния для рассылки сообщений"""
    waiting_for_text = State()
    confirming = State()


class PaymentStates(StatesGroup):
    """Состояния для оплаты подписки"""
    selecting_tier = State()
    confirming_payment = State()


class ReferralStates(StatesGroup):
    """Состояния для реферальной программы"""
    selecting_exchange = State()
    confirming_exchange = State()

