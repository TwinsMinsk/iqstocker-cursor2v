"""
Repository для шаблонов тем

Доступ к данным шаблонов тем для генерации
"""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import ThemeTemplate
from src.database.repositories.base import BaseRepository

logger = None  # Логирование будет добавлено при необходимости


class ThemeTemplateRepository(BaseRepository[ThemeTemplate]):
    """Repository для шаблонов тем"""
    
    def __init__(self):
        super().__init__(ThemeTemplate)
    
    async def get_random_by_category(
        self,
        session: AsyncSession,
        category: str,
    ) -> Optional[ThemeTemplate]:
        """
        Получить случайную тему по категории
        
        Args:
            session: AsyncSession
            category: Категория темы
            
        Returns:
            Случайная тема или None
        """
        from sqlalchemy import func
        
        statement = (
            select(ThemeTemplate)
            .where(
                ThemeTemplate.category == category,
                ThemeTemplate.is_active == True,
            )
            .order_by(func.random())
            .limit(1)
        )
        
        result = await session.exec(statement)
        return result.first()
    
    async def get_all_by_category(
        self,
        session: AsyncSession,
        category: str,
        limit: int = 100,
    ) -> list[ThemeTemplate]:
        """
        Получить все темы по категории
        
        Args:
            session: AsyncSession
            category: Категория темы
            limit: Максимальное количество записей
            
        Returns:
            Список тем
        """
        statement = (
            select(ThemeTemplate)
            .where(
                ThemeTemplate.category == category,
                ThemeTemplate.is_active == True,
            )
            .limit(limit)
        )
        
        result = await session.exec(statement)
        return list(result.all())

