"""
Репозиторий для работы с аналитикой CSV файлов
"""

from typing import Optional, List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from src.database.models import CSVAnalysis, AnalyticsReport, AnalysisStatus
from src.database.repositories.base import BaseRepository


class CSVAnalysisRepository(BaseRepository[CSVAnalysis]):
    """Репозиторий для работы с CSV анализами"""
    
    def __init__(self):
        super().__init__(CSVAnalysis)
    
    async def get_by_user_id(
        self,
        session: AsyncSession,
        user_id: int,
        limit: int = 10,
    ) -> List[CSVAnalysis]:
        """
        Получить все анализы пользователя
        
        Args:
            session: AsyncSession
            user_id: ID пользователя
            limit: Максимальное количество записей
            
        Returns:
            Список анализов
        """
        statement = (
            select(CSVAnalysis)
            .where(CSVAnalysis.user_id == user_id)
            .order_by(desc(CSVAnalysis.created_at))
            .limit(limit)
        )
        result = await session.execute(statement)
        return list(result.scalars().all())
    
    async def get_pending(
        self,
        session: AsyncSession,
    ) -> List[CSVAnalysis]:
        """
        Получить все ожидающие обработки анализы
        
        Args:
            session: AsyncSession
            
        Returns:
            Список ожидающих анализов
        """
        statement = select(CSVAnalysis).where(
            CSVAnalysis.analysis_status == AnalysisStatus.PENDING
        )
        result = await session.execute(statement)
        return list(result.scalars().all())
    
    async def update_status(
        self,
        session: AsyncSession,
        analysis_id: int,
        status: AnalysisStatus,
        error_message: Optional[str] = None,
    ) -> Optional[CSVAnalysis]:
        """
        Обновить статус анализа
        
        Args:
            session: AsyncSession
            analysis_id: ID анализа
            status: Новый статус
            error_message: Сообщение об ошибке (если есть)
            
        Returns:
            Обновленный анализ или None
        """
        analysis = await self.get_by_id(session, analysis_id)
        if analysis:
            analysis.analysis_status = status
            if error_message:
                analysis.error_message = error_message
            await session.commit()
            await session.refresh(analysis)
        return analysis


class AnalyticsReportRepository(BaseRepository[AnalyticsReport]):
    """Репозиторий для работы с отчетами"""
    
    def __init__(self):
        super().__init__(AnalyticsReport)
    
    async def get_by_csv_analysis_id(
        self,
        session: AsyncSession,
        csv_analysis_id: int,
    ) -> Optional[AnalyticsReport]:
        """
        Получить отчет по ID анализа
        
        Args:
            session: AsyncSession
            csv_analysis_id: ID CSV анализа
            
        Returns:
            Отчет или None
        """
        statement = select(AnalyticsReport).where(
            AnalyticsReport.csv_analysis_id == csv_analysis_id
        )
        result = await session.execute(statement)
        return result.scalar_one_or_none()
    
    async def get_by_user_id(
        self,
        session: AsyncSession,
        user_id: int,
        limit: int = 10,
    ) -> List[AnalyticsReport]:
        """
        Получить все отчеты пользователя
        
        Args:
            session: AsyncSession
            user_id: ID пользователя
            limit: Максимальное количество записей
            
        Returns:
            Список отчетов
        """
        statement = (
            select(AnalyticsReport)
            .join(CSVAnalysis)
            .where(CSVAnalysis.user_id == user_id)
            .order_by(desc(AnalyticsReport.created_at))
            .limit(limit)
        )
        result = await session.execute(statement)
        return list(result.scalars().all())
