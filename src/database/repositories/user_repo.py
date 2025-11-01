"""
Репозиторий для работы с пользователями
"""

from datetime import datetime
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.database.models import User, SubscriptionTier
from src.database.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Репозиторий для работы с пользователями"""
    
    def __init__(self):
        super().__init__(User)
    
    async def get_by_telegram_id(
        self,
        session: AsyncSession,
        telegram_id: int,
    ) -> Optional[User]:
        """
        Получить пользователя по Telegram ID
        
        Args:
            session: AsyncSession
            telegram_id: Telegram ID пользователя
            
        Returns:
            Пользователь или None
        """
        statement = select(User).where(User.telegram_id == telegram_id)
        result = await session.execute(statement)
        return result.scalar_one_or_none()
    
    async def get_active_subscriptions(
        self,
        session: AsyncSession,
        tier: Optional[SubscriptionTier] = None,
    ) -> list[User]:
        """
        Получить всех пользователей с активной подпиской
        
        Args:
            session: AsyncSession
            tier: Фильтр по типу подписки (опционально)
            
        Returns:
            Список пользователей с активной подпиской
        """
        now = datetime.utcnow()
        statement = select(User).where(
            User.subscription_tier != SubscriptionTier.FREE,
            User.subscription_expires_at > now,
        )
        
        if tier:
            statement = statement.where(User.subscription_tier == tier)
        
        result = await session.execute(statement)
        return list(result.scalars().all())
    
    async def get_referrals(
        self,
        session: AsyncSession,
        referrer_id: int,
    ) -> list[User]:
        """
        Получить всех рефералов пользователя
        
        Args:
            session: AsyncSession
            referrer_id: ID реферера
            
        Returns:
            Список рефералов
        """
        statement = select(User).where(User.referrer_id == referrer_id)
        result = await session.execute(statement)
        return list(result.scalars().all())
    
    async def increment_iq_points(
        self,
        session: AsyncSession,
        user_id: int,
        points: int = 1,
    ) -> Optional[User]:
        """
        Увеличить IQ баллы пользователя
        
        Args:
            session: AsyncSession
            user_id: ID пользователя
            points: Количество баллов (по умолчанию 1)
            
        Returns:
            Обновленный пользователь или None
        """
        user = await self.get_by_id(session, user_id)
        if user:
            user.iq_points += points
            user.updated_at = datetime.utcnow()
            await session.commit()
            await session.refresh(user)
        return user
    
    async def decrement_iq_points(
        self,
        session: AsyncSession,
        user_id: int,
        points: int = 1,
    ) -> Optional[User]:
        """
        Уменьшить IQ баллы пользователя
        
        Args:
            session: AsyncSession
            user_id: ID пользователя
            points: Количество баллов (по умолчанию 1)
            
        Returns:
            Обновленный пользователь или None
        """
        user = await self.get_by_id(session, user_id)
        if user:
            if user.iq_points >= points:
                user.iq_points -= points
                user.updated_at = datetime.utcnow()
                await session.commit()
                await session.refresh(user)
        return user

