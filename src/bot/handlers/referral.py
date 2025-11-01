"""
Handler для реферальной программы

Реферальные ссылки, IQ баллы, обмен баллов
"""

from aiogram import Router
from aiogram.types import CallbackQuery

from src.bot.keyboards.factories import (
    get_back_keyboard,
    get_referral_keyboard,
    get_use_points_keyboard,
)
from src.bot.lexicon.lexicon_ru import LEXICON_RU
from src.config.logging import get_logger
from src.core.exceptions import InsufficientPointsException
from src.database.connection import get_session
from src.database.models import SubscriptionTier
from src.database.repositories.user_repo import UserRepository
from src.services.referral_service import ReferralService

logger = get_logger(__name__)
router = Router(name=__name__)


@router.callback_query(lambda c: c.data == "referral")
async def callback_referral(callback: CallbackQuery):
    """Обработчик раздела рефералов"""
    await callback.message.edit_text(
        LEXICON_RU["referral_start"],
        reply_markup=get_referral_keyboard(),
    )
    await callback.answer()


@router.callback_query(lambda c: c.data == "get_referral_link")
async def callback_get_referral_link(callback: CallbackQuery):
    """Обработчик получения реферальной ссылки"""
    async for session in get_session():
        try:
            user_repo = UserRepository()
            referral_service = ReferralService(user_repo)
            
            user = await user_repo.get_by_telegram_id(session, callback.from_user.id)
            if not user:
                await callback.answer("Пользователь не найден", show_alert=True)
                return
            
            referral_link = referral_service.generate_referral_link(user.id)
            
            await callback.message.edit_text(
                LEXICON_RU["referral_link_generated"].format(referral_link=referral_link),
                reply_markup=get_back_keyboard("referral"),
            )
            await callback.answer()
        
        except Exception as e:
            logger.error("referral_link_error", error=str(e), exc_info=True)
            await callback.answer("Ошибка генерации ссылки", show_alert=True)
        finally:
            break


@router.callback_query(lambda c: c.data == "referral_balance")
async def callback_referral_balance(callback: CallbackQuery):
    """Обработчик просмотра баланса баллов"""
    async for session in get_session():
        try:
            user_repo = UserRepository()
            referral_service = ReferralService(user_repo)
            
            user = await user_repo.get_by_telegram_id(session, callback.from_user.id)
            if not user:
                await callback.answer("Пользователь не найден", show_alert=True)
                return
            
            # Получаем статистику
            stats = await referral_service.get_referral_stats(session, user.id)
            
            referral_link = referral_service.generate_referral_link(user.id)
            
            await callback.message.edit_text(
                LEXICON_RU["referral_balance"].format(
                    iq_points=stats["iq_points"],
                    referrals_count=stats["total_referrals"],
                    referrals_with_subscription=stats["referrals_with_subscription"],
                    referral_link=referral_link,
                ),
                reply_markup=get_back_keyboard("referral"),
            )
            await callback.answer()
        
        except Exception as e:
            logger.error("referral_balance_error", error=str(e), exc_info=True)
            await callback.answer("Ошибка загрузки баланса", show_alert=True)
        finally:
            break


@router.callback_query(lambda c: c.data == "use_points")
async def callback_use_points(callback: CallbackQuery):
    """Обработчик обмена баллов"""
    async for session in get_session():
        try:
            user_repo = UserRepository()
            user = await user_repo.get_by_telegram_id(session, callback.from_user.id)
            if not user:
                await callback.answer("Пользователь не найден", show_alert=True)
                return
            
            await callback.message.edit_text(
                LEXICON_RU["referral_use_points"].format(iq_points=user.iq_points),
                reply_markup=get_use_points_keyboard(),
            )
            await callback.answer()
        
        except Exception as e:
            logger.error("use_points_error", error=str(e), exc_info=True)
            await callback.answer("Ошибка загрузки", show_alert=True)
        finally:
            break


@router.callback_query(lambda c: c.data.startswith("exchange_"))
async def callback_exchange_points(callback: CallbackQuery):
    """Обработчик обмена баллов на бонусы"""
    async for session in get_session():
        try:
            user_repo = UserRepository()
            referral_service = ReferralService(user_repo)
            
            user = await user_repo.get_by_telegram_id(session, callback.from_user.id)
            if not user:
                await callback.answer("Пользователь не найден", show_alert=True)
                return
            
            exchange_type = callback.data.replace("exchange_", "")
            
            # Обрабатываем разные типы обмена
            if exchange_type == "25":
                # Скидка 25%
                result = await referral_service.exchange_points_for_discount(
                    session, user.id, points=1, discount_percent=25
                )
                bonus_description = "Скидка 25% на месяц PRO или ULTRA"
            
            elif exchange_type == "50":
                # Скидка 50%
                result = await referral_service.exchange_points_for_discount(
                    session, user.id, points=2, discount_percent=50
                )
                bonus_description = "Скидка 50% на месяц PRO или ULTRA"
            
            elif exchange_type == "pro":
                # 1 месяц PRO бесплатно
                result = await referral_service.exchange_points_for_free_subscription(
                    session, user.id, points=3, tier=SubscriptionTier.PRO
                )
                bonus_description = "1 месяц PRO бесплатно"
            
            elif exchange_type == "ultra":
                # 1 месяц ULTRA бесплатно
                result = await referral_service.exchange_points_for_free_subscription(
                    session, user.id, points=4, tier=SubscriptionTier.ULTRA
                )
                bonus_description = "1 месяц ULTRA бесплатно"
            
            elif exchange_type == "channel":
                # Доступ в канал
                result = await referral_service.exchange_points_for_channel_access(
                    session, user.id, points=5
                )
                bonus_description = "Пожизненный доступ в закрытый канал IQ Radar"
            
            else:
                await callback.answer("Неверный тип обмена", show_alert=True)
                return
            
            await callback.message.edit_text(
                LEXICON_RU["referral_points_exchanged"].format(
                    points_spent=result["points_spent"],
                    bonus_description=bonus_description,
                    remaining_points=result["remaining_points"],
                ),
                reply_markup=get_back_keyboard("referral"),
            )
            await callback.answer("✅ Бонус активирован!")
        
        except InsufficientPointsException as e:
            user = await user_repo.get_by_telegram_id(session, callback.from_user.id)
            if user:
                await callback.message.edit_text(
                    LEXICON_RU["referral_points_insufficient"].format(
                        required_points=exchange_type == "25" and 1 or exchange_type == "50" and 2 or exchange_type == "pro" and 3 or exchange_type == "ultra" and 4 or 5,
                        current_points=user.iq_points,
                    ),
                    reply_markup=get_back_keyboard("referral"),
                )
            await callback.answer()
        except Exception as e:
            logger.error("exchange_points_error", error=str(e), exc_info=True)
            await callback.answer("Ошибка обмена баллов", show_alert=True)
        finally:
            break

