"""
Handler для оплаты подписок

Выбор тарифа, создание платежных ссылок
"""

from aiogram import Router
from aiogram.types import CallbackQuery

from src.bot.keyboards.factories import get_back_keyboard, get_payment_keyboard, get_subscription_keyboard
from src.bot.lexicon.lexicon_ru import LEXICON_RU
from src.config.logging import get_logger
from src.database.connection import get_session
from src.database.models import SubscriptionTier
from src.database.repositories.payment_repo import PaymentRepository
from src.services.payment_service import PaymentService

logger = get_logger(__name__)
router = Router(name=__name__)


@router.callback_query(lambda c: c.data in ["buy_pro", "buy_ultra"])
async def callback_buy_subscription(callback: CallbackQuery):
    """Обработчик покупки подписки"""
    async for session in get_session():
        try:
            # Определяем тариф
            tier = SubscriptionTier.PRO if callback.data == "buy_pro" else SubscriptionTier.ULTRA
            
            # Создаем сервисы
            payment_repo = PaymentRepository()
            payment_service = PaymentService(payment_repo)
            
            # Получаем пользователя
            from src.database.repositories.user_repo import UserRepository
            user_repo = UserRepository()
            user = await user_repo.get_by_telegram_id(session, callback.from_user.id)
            if not user:
                await callback.answer("Пользователь не найден", show_alert=True)
                return
            
            # Создаем платежную ссылку
            payment_data = await payment_service.create_payment_link(
                session,
                user.id,
                tier,
                days=30,
            )
            
            # Формируем сообщение
            amount = payment_service.get_price_for_tier(tier) / 100  # Конвертируем копейки в рубли
            
            await callback.message.edit_text(
                LEXICON_RU["payment_link"].format(
                    subscription=tier.value.upper(),
                    amount=int(amount),
                    payment_url=payment_data["payment_url"],
                ),
                reply_markup=get_payment_keyboard(payment_data["payment_url"]),
            )
            await callback.answer()
        
        except Exception as e:
            logger.error("payment_handler_error", error=str(e), exc_info=True)
            await callback.answer("Ошибка создания платежа", show_alert=True)
        finally:
            break

