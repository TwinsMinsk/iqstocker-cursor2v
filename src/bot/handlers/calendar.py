"""
Handler для календаря генераций

Планирование загрузок и рекомендации
"""

from aiogram import Router
from aiogram.types import CallbackQuery

from src.bot.keyboards.factories import get_back_keyboard
from src.bot.lexicon.lexicon_ru import LEXICON_RU
from src.config.logging import get_logger

logger = get_logger(__name__)
router = Router(name=__name__)


@router.callback_query(lambda c: c.data == "calendar")
async def callback_calendar(callback: CallbackQuery):
    """Обработчик календаря генераций"""
    # TODO: Реализовать получение данных из БД или сервиса
    weekly_recommendations = "• Понедельник: Фотографии природы\n• Среда: Векторные иллюстрации\n• Пятница: Видео контент"
    upcoming_events = "• День рождения (через 3 дня)\n• Новый год (через 30 дней)"
    seasonal_trends = "• Зимние праздники\n• Новогодние темы\n• Креативные подарки"
    
    await callback.message.edit_text(
        LEXICON_RU["calendar_start"].format(
            weekly_recommendations=weekly_recommendations,
            upcoming_events=upcoming_events,
            seasonal_trends=seasonal_trends,
        ),
        reply_markup=get_back_keyboard("main_menu"),
    )
    await callback.answer()

