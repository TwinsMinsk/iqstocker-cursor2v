"""
Handler для FAQ

Ответы на часто задаваемые вопросы
"""

from aiogram import Router
from aiogram.types import CallbackQuery

from src.bot.keyboards.factories import get_back_keyboard, get_faq_keyboard
from src.bot.lexicon.lexicon_ru import LEXICON_RU
from src.config.logging import get_logger

logger = get_logger(__name__)
router = Router(name=__name__)


@router.callback_query(lambda c: c.data == "faq")
async def callback_faq(callback: CallbackQuery):
    """Обработчик раздела FAQ"""
    await callback.message.edit_text(
        LEXICON_RU["faq_start"],
        reply_markup=get_faq_keyboard(),
    )
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("faq_"))
async def callback_faq_answer(callback: CallbackQuery):
    """Обработчик ответа на вопрос FAQ"""
    faq_map = {
        "faq_1": LEXICON_RU["faq_answer_1"],
        "faq_2": LEXICON_RU["faq_answer_2"],
        "faq_3": LEXICON_RU["faq_answer_3"],
        "faq_referral": LEXICON_RU["faq_answer_referral"],
    }
    
    answer = faq_map.get(callback.data)
    if not answer:
        await callback.answer("Ответ не найден", show_alert=True)
        return
    
    await callback.message.edit_text(
        answer,
        reply_markup=get_back_keyboard("faq"),
    )
    await callback.answer()


@router.callback_query(lambda c: c.data == "support")
async def callback_support(callback: CallbackQuery):
    """Обработчик поддержки"""
    await callback.message.edit_text(
        LEXICON_RU["support"],
        reply_markup=get_back_keyboard("main_menu"),
    )
    await callback.answer()

