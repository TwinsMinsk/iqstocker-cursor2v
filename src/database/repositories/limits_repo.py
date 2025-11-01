"""
Репозиторий для работы с лимитами пользователей
"""

from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.database.models import Limits, SubscriptionTier
from src.database.repositories.base import BaseRepository


class LimitsRepository(BaseRepository[Limits]):
    """Репозиторий для работы с лимитами"""
    
    def __init__(self):
        super().__init__(Limits)
    
    async def get_by_user_id(
        self,
        session: AsyncSession,
        user_id: int,
    ) -> Optional[Limits]:
        """
        Получить лимиты пользователя
        
        Args:
            session: AsyncSession
            user_id: ID пользователя
            
        Returns:
            Лимиты пользователя или None
        """
        return await self.get_by_id(session, user_id)
    
    async def create_default(
        self,
        session: AsyncSession,
        user_id: int,
        tier: SubscriptionTier = SubscriptionTier.FREE,
    ) -> Limits:
        """
        Создать лимиты с дефолтными значениями для подписки
        
        Args:
            session: AsyncSession
            user_id: ID пользователя
            tier: Тип подписки
            
        Returns:
            Созданные лимиты
        """
        # Определяем лимиты в зависимости от подписки
        analytics_limit, themes_limit = self._get_limits_for_tier(tier)
        
        limits = Limits(
            user_id=user_id,
            analytics_limit=analytics_limit,
            themes_limit=themes_limit,
            reset_at=datetime.utcnow() + timedelta(days=30),
        )
        
        return await self.create(session, limits)
    
    async def update_for_subscription(
        self,
        session: AsyncSession,
        user_id: int,
        tier: SubscriptionTier,
    ) -> Optional[Limits]:
        """
        Обновить лимиты при смене подписки
        
        Args:
            session: AsyncSession
            user_id: ID пользователя
            tier: Новый тип подписки
            
        Returns:
            Обновленные лимиты или None
        """
        limits = await self.get_by_user_id(session, user_id)
        if limits:
            analytics_limit, themes_limit = self._get_limits_for_tier(tier)
            limits.analytics_limit = analytics_limit
            limits.themes_limit = themes_limit
            limits.updated_at = datetime.utcnow()
            await session.commit()
            await session.refresh(limits)
        return limits
    
    async def reset_if_needed(
        self,
        session: AsyncSession,
        user_id: int,
    ) -> Optional[Limits]:
        """
        Сбросить лимиты если нужно (прошло 30 дней)
        
        Args:
            session: AsyncSession
            user_id: ID пользователя
            
        Returns:
            Обновленные лимиты или None
        """
        limits = await self.get_by_user_id(session, user_id)
        if limits and limits.reset_at <= datetime.utcnow():
            limits.analytics_used = 0
            limits.themes_used = 0
            limits.reset_at = datetime.utcnow() + timedelta(days=30)
            limits.updated_at = datetime.utcnow()
            await session.commit()
            await session.refresh(limits)
        return limits
    
    async def increment_analytics(
        self,
        session: AsyncSession,
        user_id: int,
    ) -> Optional[Limits]:
        """
        Увеличить счетчик использованных анализов
        
        Args:
            session: AsyncSession
            user_id: ID пользователя
            
        Returns:
            Обновленные лимиты или None
        """
        limits = await self.get_by_user_id(session, user_id)
        if limits:
            limits.analytics_used += 1
            limits.updated_at = datetime.utcnow()
            await session.commit()
            await session.refresh(limits)
        return limits
    
    async def increment_themes(
        self,
        session: AsyncSession,
        user_id: int,
    ) -> Optional[Limits]:
        """
        Увеличить счетчик использованных тем
        
        Args:
            session: AsyncSession
            user_id: ID пользователя
            
        Returns:
            Обновленные лимиты или None
        """
        limits = await self.get_by_user_id(session, user_id)
        if limits:
            limits.themes_used += 1
            limits.updated_at = datetime.utcnow()
            await session.commit()
            await session.refresh(limits)
        return limits
    
    def _get_limits_for_tier(
        self,
        tier: SubscriptionTier,
    ) -> tuple[int, int]:
        """
        Получить лимиты для типа подписки
        
        Args:
            tier: Тип подписки
            
        Returns:
            Кортеж (analytics_limit, themes_limit)
            -1 означает безлимит
        """
        if tier == SubscriptionTier.FREE:
            return (5, 10)
        elif tier == SubscriptionTier.PRO:
            return (-1, 100)  # Безлимит анализов, 100 тем
        elif tier == SubscriptionTier.ULTRA:
            return (-1, -1)  # Безлимит всего
        elif tier == SubscriptionTier.TEST_PRO:
            return (1, 2)  # 1 анализ, 2 темы в неделю (управляется отдельно)
        else:
            return (5, 10)  # По умолчанию FREE

