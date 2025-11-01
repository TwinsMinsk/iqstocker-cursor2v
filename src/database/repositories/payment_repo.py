"""
Репозиторий для работы с платежами
"""

from typing import List, Optional
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from src.database.models import Payment, PaymentStatus, SubscriptionTier
from src.database.repositories.base import BaseRepository


class PaymentRepository(BaseRepository[Payment]):
    """Репозиторий для работы с платежами"""
    
    def __init__(self):
        super().__init__(Payment)
    
    async def get_by_user_id(
        self,
        session: AsyncSession,
        user_id: int,
        limit: int = 20,
    ) -> List[Payment]:
        """
        Получить все платежи пользователя
        
        Args:
            session: AsyncSession
            user_id: ID пользователя
            limit: Максимальное количество записей
            
        Returns:
            Список платежей
        """
        statement = (
            select(Payment)
            .where(Payment.user_id == user_id)
            .order_by(desc(Payment.created_at))
            .limit(limit)
        )
        result = await session.execute(statement)
        return list(result.scalars().all())
    
    async def get_by_transaction_id(
        self,
        session: AsyncSession,
        transaction_id: str,
    ) -> Optional[Payment]:
        """
        Получить платеж по ID транзакции Tribute
        
        Args:
            session: AsyncSession
            transaction_id: ID транзакции
            
        Returns:
            Платеж или None
        """
        statement = select(Payment).where(
            Payment.tribute_transaction_id == transaction_id
        )
        result = await session.execute(statement)
        return result.scalar_one_or_none()
    
    async def get_by_status(
        self,
        session: AsyncSession,
        status: PaymentStatus,
        limit: int = 100,
    ) -> List[Payment]:
        """
        Получить платежи по статусу
        
        Args:
            session: AsyncSession
            status: Статус платежа
            limit: Максимальное количество записей
            
        Returns:
            Список платежей
        """
        statement = (
            select(Payment)
            .where(Payment.status == status)
            .order_by(desc(Payment.created_at))
            .limit(limit)
        )
        result = await session.execute(statement)
        return list(result.scalars().all())
    
    async def get_completed_by_period(
        self,
        session: AsyncSession,
        start_date: datetime,
        end_date: datetime,
    ) -> List[Payment]:
        """
        Получить завершенные платежи за период
        
        Args:
            session: AsyncSession
            start_date: Начальная дата
            end_date: Конечная дата
            
        Returns:
            Список завершенных платежей
        """
        statement = (
            select(Payment)
            .where(
                Payment.status == PaymentStatus.COMPLETED,
                Payment.completed_at >= start_date,
                Payment.completed_at <= end_date,
            )
            .order_by(desc(Payment.completed_at))
        )
        result = await session.execute(statement)
        return list(result.scalars().all())
    
    async def update_status(
        self,
        session: AsyncSession,
        payment_id: int,
        status: PaymentStatus,
    ) -> Optional[Payment]:
        """
        Обновить статус платежа
        
        Args:
            session: AsyncSession
            payment_id: ID платежа
            status: Новый статус
            
        Returns:
            Обновленный платеж или None
        """
        payment = await self.get_by_id(session, payment_id)
        if payment:
            payment.status = status
            if status == PaymentStatus.COMPLETED:
                payment.completed_at = datetime.utcnow()
            await session.commit()
            await session.refresh(payment)
        return payment

