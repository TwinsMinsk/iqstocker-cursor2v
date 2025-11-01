"""
ARQ Workers для IQStocker v2.0

Фоновые задачи для обработки CSV и других асинхронных операций
"""

from typing import Any

from arq import create_pool
from arq.connections import RedisSettings
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.logging import get_logger
from src.config.settings import settings
from src.core.analytics.csv_processor import CSVProcessor
from src.core.analytics.kpi_calculator import KPICalculator
from src.core.analytics.report_generator import ReportGenerator
from src.database.connection import AsyncSessionLocal, get_session
from src.database.models import AnalysisStatus, AnalyticsReport
from src.database.repositories.analytics_repo import (
    CSVAnalysisRepository,
    AnalyticsReportRepository,
)

logger = get_logger(__name__)


async def process_csv(ctx: dict[str, Any], csv_analysis_id: int) -> None:
    """
    Обработать CSV файл и создать отчет
    
    Args:
        ctx: Контекст ARQ worker
        csv_analysis_id: ID анализа CSV
    """
    logger.info("csv_processing_started", csv_analysis_id=csv_analysis_id)
    
    async with AsyncSessionLocal() as session:
        try:
            csv_analysis_repo = CSVAnalysisRepository()
            analytics_report_repo = AnalyticsReportRepository()
            
            # Получаем анализ
            analysis = await csv_analysis_repo.get_by_id(session, csv_analysis_id)
            if not analysis:
                logger.error("csv_analysis_not_found", csv_analysis_id=csv_analysis_id)
                return
            
            # Обновляем статус на PROCESSING
            await csv_analysis_repo.update_status(
                session,
                csv_analysis_id,
                AnalysisStatus.PROCESSING,
            )
            
            # TODO: Скачать файл через Telegram Bot API
            # Для MVP используем file_id напрямую
            # file = await bot.get_file(analysis.file_id)
            # content = await bot.download_file(file.file_path)
            
            # Заглушка для MVP - нужно будет реализовать загрузку файла
            logger.warning(
                "csv_file_download_placeholder",
                csv_analysis_id=csv_analysis_id,
                file_id=analysis.file_id,
            )
            
            # Временно возвращаемся - нужно загрузить файл
            # Пока создаем тестовый контент
            # content = await download_telegram_file(analysis.file_id)
            
            # Парсим CSV
            # parsed_data = CSVProcessor.parse_csv(content)
            
            # TODO: Реальная загрузка файла через Telegram API
            # Пока используем заглушку
            parsed_data = []
            
            # Валидируем данные
            CSVProcessor.validate_csv(parsed_data)
            
            # Рассчитываем KPI
            kpi_data = KPICalculator.calculate_kpi(parsed_data)
            
            # Генерируем текст отчета
            summary_text = ReportGenerator.generate_summary(kpi_data)
            
            # Создаем отчет
            report_obj = AnalyticsReport(
                csv_analysis_id=csv_analysis_id,
                kpi_data=kpi_data,
                summary_text=summary_text,
            )
            await analytics_report_repo.create(session, report_obj)
            
            # Обновляем статус на COMPLETED
            await csv_analysis_repo.update_status(
                session,
                csv_analysis_id,
                AnalysisStatus.COMPLETED,
            )
            
            logger.info(
                "csv_processing_completed",
                csv_analysis_id=csv_analysis_id,
                total_sales=kpi_data.get("total_sales", 0),
            )
        
        except Exception as e:
            logger.error(
                "csv_processing_failed",
                csv_analysis_id=csv_analysis_id,
                error=str(e),
                exc_info=True,
            )
            
            # Обновляем статус на FAILED
            try:
                await csv_analysis_repo.update_status(
                    session,
                    csv_analysis_id,
                    AnalysisStatus.FAILED,
                    error_message=str(e),
                )
            except Exception:
                pass


# Настройки ARQ Worker
class WorkerSettings:
    """Настройки ARQ Worker"""
    
    redis_settings = RedisSettings(
        host=settings.redis.host,
        port=settings.redis.port,
        database=settings.redis.db,
    )
    
    functions = [process_csv]
    
    # Настройки для cron задач (если нужны)
    cron_jobs = [
        # {
        #     "function": "some_periodic_task",
        #     "cron": "0 0 * * *",  # Каждый день в полночь
        # },
    ]


# Для запуска worker:
# arq src.workers.main.WorkerSettings

