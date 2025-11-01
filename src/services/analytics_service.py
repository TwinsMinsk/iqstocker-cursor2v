"""
Сервис для работы с аналитикой CSV файлов

Обработка CSV, проверка лимитов, создание анализов и отчетов
"""

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.config.logging import get_logger
from src.core.exceptions import LimitExceededException, UserNotFoundException
from src.database.models import CSVAnalysis, AnalysisStatus
from src.database.repositories.analytics_repo import (
    CSVAnalysisRepository,
    AnalyticsReportRepository,
)
from src.database.repositories.limits_repo import LimitsRepository

logger = get_logger(__name__)


class AnalyticsService:
    """Сервис для работы с аналитикой"""
    
    def __init__(
        self,
        csv_analysis_repo: CSVAnalysisRepository,
        analytics_report_repo: AnalyticsReportRepository,
        limits_repo: LimitsRepository,
    ):
        """
        Инициализация сервиса
        
        Args:
            csv_analysis_repo: Репозиторий CSV анализов
            analytics_report_repo: Репозиторий отчетов
            limits_repo: Репозиторий лимитов
        """
        self.csv_analysis_repo = csv_analysis_repo
        self.analytics_report_repo = analytics_report_repo
        self.limits_repo = limits_repo
    
    async def can_use_analytics(
        self,
        session: AsyncSession,
        user_id: int,
    ) -> bool:
        """
        Проверить, может ли пользователь использовать аналитику
        
        Args:
            session: AsyncSession
            user_id: ID пользователя
            
        Returns:
            True если может использовать
        """
        limits = await self.limits_repo.get_by_user_id(session, user_id)
        if not limits:
            return False
        
        # Сбрасываем лимиты если нужно
        await self.limits_repo.reset_if_needed(session, user_id)
        limits = await self.limits_repo.get_by_user_id(session, user_id)
        
        # -1 означает безлимит
        if limits.analytics_limit == -1:
            return True
        
        return limits.analytics_used < limits.analytics_limit
    
    async def create_analysis(
        self,
        session: AsyncSession,
        user_id: int,
        file_id: str,
        filename: str,
        row_count: int,
    ) -> CSVAnalysis:
        """
        Создать новый анализ CSV файла
        
        Args:
            session: AsyncSession
            user_id: ID пользователя
            file_id: Telegram file_id
            filename: Имя файла
            row_count: Количество строк в файле
            
        Returns:
            Созданный анализ
            
        Raises:
            LimitExceededException: Превышен лимит анализов
        """
        # Проверяем лимиты
        if not await self.can_use_analytics(session, user_id):
            limits = await self.limits_repo.get_by_user_id(session, user_id)
            raise LimitExceededException(
                f"Превышен лимит анализов. Использовано: {limits.analytics_used}/{limits.analytics_limit}"
            )
        
        # Создаем анализ
        analysis = CSVAnalysis(
            user_id=user_id,
            file_id=file_id,
            filename=filename,
            row_count=row_count,
            analysis_status=AnalysisStatus.PENDING,
        )
        
        analysis = await self.csv_analysis_repo.create(session, analysis)
        
        # Увеличиваем счетчик использованных анализов
        await self.limits_repo.increment_analytics(session, user_id)
        
        logger.info(
            "csv_analysis_created",
            analysis_id=analysis.id,
            user_id=user_id,
            filename=filename,
            row_count=row_count,
        )
        
        return analysis
    
    async def get_user_analyses(
        self,
        session: AsyncSession,
        user_id: int,
        limit: int = 10,
    ) -> list[CSVAnalysis]:
        """
        Получить все анализы пользователя
        
        Args:
            session: AsyncSession
            user_id: ID пользователя
            limit: Максимальное количество записей
            
        Returns:
            Список анализов
        """
        return await self.csv_analysis_repo.get_by_user_id(
            session,
            user_id,
            limit,
        )
    
    async def get_user_reports(
        self,
        session: AsyncSession,
        user_id: int,
        limit: int = 10,
    ) -> list:
        """
        Получить все отчеты пользователя
        
        Args:
            session: AsyncSession
            user_id: ID пользователя
            limit: Максимальное количество записей
            
        Returns:
            Список отчетов
        """
        return await self.analytics_report_repo.get_by_user_id(
            session,
            user_id,
            limit,
        )
    
    async def update_analysis_status(
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
        return await self.csv_analysis_repo.update_status(
            session,
            analysis_id,
            status,
            error_message,
        )

