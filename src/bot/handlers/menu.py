"""
Handler для главного меню

Навигация по разделам бота
"""

from aiogram import Router
from aiogram.types import CallbackQuery

from src.bot.keyboards.factories import get_main_menu_keyboard
from src.bot.lexicon.lexicon_ru import LEXICON_RU
from src.config.logging import get_logger

logger = get_logger(__name__)
router = Router(name=__name__)


@router.callback_query(lambda c: c.data == "main_menu")
async def callback_main_menu(callback: CallbackQuery):
    """Обработчик возврата в главное меню"""
    await callback.message.edit_text(
        LEXICON_RU["main_menu"],
        reply_markup=get_main_menu_keyboard(),
    )
    await callback.answer()

