"""
Handler для профиля пользователя

Просмотр профиля, подписки, лимитов
"""

from datetime import datetime

from aiogram import Router
from aiogram.types import CallbackQuery

from src.bot.keyboards.factories import get_profile_keyboard, get_subscription_keyboard
from src.bot.lexicon.lexicon_ru import LEXICON_RU
from src.config.logging import get_logger
from src.database.connection import get_session
from src.database.models import SubscriptionTier
from src.database.repositories.limits_repo import LimitsRepository
from src.database.repositories.user_repo import UserRepository
from src.services.referral_service import ReferralService
from src.services.user_service import UserService

logger = get_logger(__name__)
router = Router(name=__name__)


@router.callback_query(lambda c: c.data == "profile")
async def callback_profile(callback: CallbackQuery):
    """Обработчик просмотра профиля"""
    async for session in get_session():
        try:
            user_repo = UserRepository()
            limits_repo = LimitsRepository()
            referral_service = ReferralService(user_repo)
            
            user = await user_repo.get_by_telegram_id(session, callback.from_user.id)
            if not user:
                await callback.answer("Пользователь не найден", show_alert=True)
                return
            
            limits = await limits_repo.get_by_user_id(session, user.id)
            if not limits:
                limits = await limits_repo.create_default(session, user.id, user.subscription_tier)
            
            # Форматируем даты
            registration_date = user.created_at.strftime("%d.%m.%Y") if user.created_at else "N/A"
            expires_at = (
                user.subscription_expires_at.strftime("%d.%m.%Y %H:%M")
                if user.subscription_expires_at
                else "Без ограничений"
            )
            reset_at = limits.reset_at.strftime("%d.%m.%Y") if limits.reset_at else "N/A"
            
            # Получаем реферальную ссылку
            referral_link = referral_service.generate_referral_link(user.id)
            
            # Получаем статистику рефералов
            referrals = await user_repo.get_referrals(session, user.id)
            referrals_count = len(referrals)
            
            await callback.message.edit_text(
                LEXICON_RU["profile"].format(
                    telegram_id=user.telegram_id,
                    username=user.username or "N/A",
                    registration_date=registration_date,
                    subscription=user.subscription_tier.value.upper(),
                    expires_at=expires_at,
                    analytics_used=limits.analytics_used,
                    analytics_limit=limits.analytics_limit if limits.analytics_limit != -1 else "∞",
                    themes_used=limits.themes_used,
                    themes_limit=limits.themes_limit if limits.themes_limit != -1 else "∞",
                    reset_at=reset_at,
                    iq_points=user.iq_points,
                    referrals_count=referrals_count,
                    referral_link=referral_link,
                ),
                reply_markup=get_profile_keyboard(),
            )
            await callback.answer()
        
        except Exception as e:
            logger.error("profile_handler_error", error=str(e), exc_info=True)
            await callback.answer("Ошибка загрузки профиля", show_alert=True)
        finally:
            break


@router.callback_query(lambda c: c.data == "subscription")
async def callback_subscription(callback: CallbackQuery):
    """Обработчик просмотра подписки"""
    async for session in get_session():
        try:
            user_repo = UserRepository()
            user = await user_repo.get_by_telegram_id(session, callback.from_user.id)
            if not user:
                await callback.answer("Пользователь не найден", show_alert=True)
                return
            
            # Формируем текст в зависимости от типа подписки
            if user.subscription_tier == SubscriptionTier.FREE:
                text = LEXICON_RU["subscription_free"]
            elif user.subscription_tier == SubscriptionTier.PRO:
                expires_at = (
                    user.subscription_expires_at.strftime("%d.%m.%Y %H:%M")
                    if user.subscription_expires_at
                    else "Без ограничений"
                )
                text = LEXICON_RU["subscription_pro"].format(expires_at=expires_at)
            elif user.subscription_tier == SubscriptionTier.ULTRA:
                expires_at = (
                    user.subscription_expires_at.strftime("%d.%m.%Y %H:%M")
                    if user.subscription_expires_at
                    else "Без ограничений"
                )
                text = LEXICON_RU["subscription_ultra"].format(expires_at=expires_at)
            else:
                text = LEXICON_RU["subscription_free"]
            
            await callback.message.edit_text(
                text,
                reply_markup=get_subscription_keyboard(),
            )
            await callback.answer()
        
        except Exception as e:
            logger.error("subscription_handler_error", error=str(e), exc_info=True)
            await callback.answer("Ошибка загрузки подписки", show_alert=True)
        finally:
            break


@router.callback_query(lambda c: c.data == "tariffs")
async def callback_tariffs(callback: CallbackQuery):
    """Обработчик просмотра тарифов"""
    await callback.message.edit_text(
        LEXICON_RU["tariffs"],
        reply_markup=get_subscription_keyboard(),
    )
    await callback.answer()

