"""
Handler для проверки подписки на канал

Проверка подписки и обработка кнопки проверки
"""

from aiogram import Bot, Router
from aiogram.types import CallbackQuery

from src.bot.keyboards.factories import get_channel_subscription_keyboard, get_main_menu_keyboard
from src.bot.lexicon.lexicon_ru import LEXICON_RU
from src.config.logging import get_logger
from src.config.settings import settings

logger = get_logger(__name__)
router = Router(name=__name__)


async def check_channel_subscription(bot: Bot, user_id: int) -> bool:
    """Проверяет подписку на канал"""
    try:
        channel_id = int(settings.bot.channel_id)
        member = await bot.get_chat_member(channel_id, user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception as e:
        logger.warning("channel_check_error", user_id=user_id, error=str(e))
        return False


@router.callback_query(lambda c: c.data == "check_subscription")
async def callback_check_subscription(callback: CallbackQuery, bot: Bot):
    """Обработчик проверки подписки"""
    is_subscribed = await check_channel_subscription(bot, callback.from_user.id)
    
    if is_subscribed:
        await callback.message.edit_text(
            LEXICON_RU["channel_subscribed"],
            reply_markup=get_main_menu_keyboard(),
        )
        await callback.answer("✅ Подписка подтверждена!")
    else:
        channel_link = f"https://t.me/c/{settings.bot.channel_id.replace('-100', '')}"
        await callback.message.edit_text(
            LEXICON_RU["channel_not_subscribed"].format(channel_link=channel_link),
            reply_markup=get_channel_subscription_keyboard(channel_link),
        )
        await callback.answer("❌ Подписка не найдена", show_alert=True)

