"""
Сервис для работы с платежами через Tribute.tg

Создание платежных ссылок, обработка webhook'ов
"""

from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.config.logging import get_logger
from src.config.settings import settings
from src.core.exceptions import PaymentException, UserNotFoundException
from src.core.utils.tribute_client import TributeClient
from src.database.models import Payment, PaymentStatus, PaymentProvider, SubscriptionTier
from src.database.repositories.payment_repo import PaymentRepository

logger = get_logger(__name__)


class PaymentService:
    """Сервис для работы с платежами"""
    
    def __init__(
        self,
        payment_repo: PaymentRepository,
    ):
        """
        Инициализация сервиса
        
        Args:
            payment_repo: Репозиторий платежей
        """
        self.payment_repo = payment_repo
        self.tribute_client = TributeClient(
            api_key=settings.tribute.api_key,
            base_url=settings.tribute.base_url,
        )
    
    def get_price_for_tier(
        self,
        tier: SubscriptionTier,
    ) -> int:
        """
        Получить цену подписки в копейках
        
        Args:
            tier: Тип подписки
            
        Returns:
            Цена в копейках
        """
        prices = {
            SubscriptionTier.PRO: 30000,  # 300₽
            SubscriptionTier.ULTRA: 60000,  # 600₽
        }
        
        return prices.get(tier, 0)
    
    async def create_payment_link(
        self,
        session: AsyncSession,
        user_id: int,
        tier: SubscriptionTier,
        days: int = 30,
    ) -> dict[str, str]:
        """
        Создать платежную ссылку через Tribute.tg
        
        Args:
            session: AsyncSession
            user_id: ID пользователя
            tier: Тип подписки
            days: Количество дней подписки
            
        Returns:
            Словарь с payment_url и payment_id
            
        Raises:
            PaymentException: Ошибка создания платежной ссылки
        """
        amount = self.get_price_for_tier(tier)
        if amount == 0:
            raise PaymentException(f"Неверный тип подписки: {tier}")
        
        # Создаем запись о платеже
        payment = Payment(
            user_id=user_id,
            tribute_transaction_id="",  # Будет заполнено после создания в Tribute
            amount=amount,
            currency="RUB",
            status=PaymentStatus.PENDING,
            subscription_tier=tier,
            subscription_days=days,
            payment_provider=PaymentProvider.TRIBUTE,
        )
        
        payment = await self.payment_repo.create(session, payment)
        
        # Создаем платежную ссылку через Tribute API
        try:
            payment_data = await self.tribute_client.create_payment(
                amount=amount,
                currency="RUB",
                description=f"IQStocker {tier.value} подписка",
                metadata={
                    "user_id": user_id,
                    "subscription_tier": tier.value,
                    "payment_id": payment.id,
                },
                webhook_url=f"{settings.app.base_url}/api/webhooks/tribute",
            )
            
            # Обновляем transaction_id
            payment.tribute_transaction_id = payment_data.get("transaction_id", "")
            await session.commit()
            await session.refresh(payment)
            
            return {
                "payment_url": payment_data.get("payment_url", ""),
                "payment_id": str(payment.id),
            }
        
        except PaymentException as e:
            logger.error(
                "payment_link_creation_failed",
                payment_id=payment.id,
                error=str(e),
            )
            raise
        except Exception as e:
            logger.error(
                "payment_link_error",
                payment_id=payment.id,
                error=str(e),
                exc_info=True,
            )
            raise PaymentException(f"Ошибка создания платежной ссылки: {str(e)}")
    
    def verify_tribute_signature(
        self,
        payload: bytes,
        signature: str,
    ) -> bool:
        """
        Проверить подпись webhook от Tribute.tg
        
        Args:
            payload: Тело запроса
            signature: Подпись из заголовка
            
        Returns:
            True если подпись валидна
        """
        return self.tribute_client.verify_signature(
            payload,
            signature,
            settings.tribute.webhook_secret,
        )
    
    async def process_payment_webhook(
        self,
        session: AsyncSession,
        transaction_id: str,
        amount: int,
        metadata: dict,
    ) -> Optional[Payment]:
        """
        Обработать webhook от Tribute.tg об успешном платеже
        
        Args:
            session: AsyncSession
            transaction_id: ID транзакции Tribute
            amount: Сумма платежа в копейках
            metadata: Метаданные платежа
            
        Returns:
            Обновленный платеж или None
            
        Raises:
            PaymentException: Ошибка обработки платежа
        """
        # Ищем платеж по transaction_id
        payment = await self.payment_repo.get_by_transaction_id(
            session,
            transaction_id,
        )
        
        if not payment:
            # Пытаемся найти по payment_id из metadata
            if "payment_id" in metadata:
                payment = await self.payment_repo.get_by_id(
                    session,
                    int(metadata["payment_id"]),
                )
            
            if not payment:
                logger.error(
                    "payment_not_found",
                    transaction_id=transaction_id,
                    metadata=metadata,
                )
                raise PaymentException(
                    f"Платеж не найден для transaction_id: {transaction_id}"
                )
        
        # Проверяем сумму
        if payment.amount != amount:
            logger.error(
                "payment_amount_mismatch",
                payment_id=payment.id,
                expected=payment.amount,
                received=amount,
            )
            raise PaymentException("Сумма платежа не совпадает")
        
        # Обновляем статус
        payment.status = PaymentStatus.COMPLETED
        payment.completed_at = datetime.utcnow()
        if not payment.tribute_transaction_id:
            payment.tribute_transaction_id = transaction_id
        
        await session.commit()
        await session.refresh(payment)
        
        logger.info(
            "payment_completed",
            payment_id=payment.id,
            user_id=payment.user_id,
            amount=amount,
        )
        
        return payment
    
    async def refund_payment(
        self,
        session: AsyncSession,
        payment_id: int,
    ) -> Optional[Payment]:
        """
        Оформить возврат платежа
        
        Args:
            session: AsyncSession
            payment_id: ID платежа
            
        Returns:
            Обновленный платеж или None
            
        Raises:
            PaymentException: Ошибка возврата
        """
        payment = await self.payment_repo.get_by_id(session, payment_id)
        if not payment:
            raise PaymentException(f"Платеж {payment_id} не найден")
        
        if payment.status != PaymentStatus.COMPLETED:
            raise PaymentException(
                f"Платеж должен быть завершен для возврата. Текущий статус: {payment.status}"
            )
        
        # TODO: Реальный возврат через Tribute API
        
        payment.status = PaymentStatus.REFUNDED
        await session.commit()
        await session.refresh(payment)
        
        logger.info("payment_refunded", payment_id=payment_id)
        
        return payment

