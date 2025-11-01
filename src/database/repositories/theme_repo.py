"""
Репозиторий для работы с темами
"""

from typing import List, Optional
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from src.database.models import ThemeRequest
from src.database.repositories.base import BaseRepository


class ThemeRepository(BaseRepository[ThemeRequest]):
    """Репозиторий для работы с темами"""
    
    def __init__(self):
        super().__init__(ThemeRequest)
    
    async def get_by_user_id(
        self,
        session: AsyncSession,
        user_id: int,
        limit: int = 20,
    ) -> List[ThemeRequest]:
        """
        Получить все темы пользователя
        
        Args:
            session: AsyncSession
            user_id: ID пользователя
            limit: Максимальное количество записей
            
        Returns:
            Список тем
        """
        statement = (
            select(ThemeRequest)
            .where(ThemeRequest.user_id == user_id)
            .order_by(desc(ThemeRequest.created_at))
            .limit(limit)
        )
        result = await session.execute(statement)
        return list(result.scalars().all())
    
    async def get_by_category(
        self,
        session: AsyncSession,
        category: str,
        limit: int = 10,
    ) -> List[ThemeRequest]:
        """
        Получить темы по категории
        
        Args:
            session: AsyncSession
            category: Категория темы
            limit: Максимальное количество записей
            
        Returns:
            Список тем
        """
        statement = (
            select(ThemeRequest)
            .where(ThemeRequest.category == category)
            .order_by(desc(ThemeRequest.created_at))
            .limit(limit)
        )
        result = await session.execute(statement)
        return list(result.scalars().all())
    
    async def get_recent_by_user(
        self,
        session: AsyncSession,
        user_id: int,
        days: int = 7,
    ) -> List[ThemeRequest]:
        """
        Получить недавние темы пользователя за последние N дней
        
        Args:
            session: AsyncSession
            user_id: ID пользователя
            days: Количество дней
            
        Returns:
            Список тем
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        statement = (
            select(ThemeRequest)
            .where(
                ThemeRequest.user_id == user_id,
                ThemeRequest.created_at >= cutoff_date,
            )
            .order_by(desc(ThemeRequest.created_at))
        )
        result = await session.execute(statement)
        return list(result.scalars().all())

