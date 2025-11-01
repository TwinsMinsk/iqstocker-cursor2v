"""
Analytics view для админ-панели

Статистика аналитики
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from src.admin.auth import get_admin
from src.admin.models import AnalyticsStatsResponse
from src.config.logging import get_logger
from src.database.connection import get_session
from src.database.repositories.analytics_repo import (
    CSVAnalysisRepository,
    AnalyticsReportRepository,
)
from src.services.admin_service import AdminService
from src.database.repositories.user_repo import UserRepository
from src.database.repositories.payment_repo import PaymentRepository

logger = get_logger(__name__)
router = APIRouter()


@router.get("/", response_model=AnalyticsStatsResponse)
async def get_analytics_stats(
    admin: dict = Depends(get_admin),
):
    """Получить статистику по аналитике"""
    async for session in get_session():
        try:
            user_repo = UserRepository()
            payment_repo = PaymentRepository()
            csv_analysis_repo = CSVAnalysisRepository()
            analytics_report_repo = AnalyticsReportRepository()
            
            admin_service = AdminService(
                user_repo,
                payment_repo,
                csv_analysis_repo,
                analytics_report_repo,
            )
            
            stats = await admin_service.get_analytics_stats(session)
            
            return AnalyticsStatsResponse(**stats)
        
        except Exception as e:
            logger.error("analytics_stats_error", error=str(e), exc_info=True)
            raise HTTPException(status_code=500, detail="Ошибка получения статистики")
        finally:
            break


@router.get("/reports")
async def get_reports(
    user_id: Optional[int] = Query(None),
    limit: int = Query(10, ge=1, le=100),
    admin: dict = Depends(get_admin),
):
    """Получить отчеты пользователя"""
    async for session in get_session():
        try:
            analytics_report_repo = AnalyticsReportRepository()
            
            if user_id:
                reports = await analytics_report_repo.get_by_user_id(session, user_id, limit)
            else:
                reports = await analytics_report_repo.get_all(session, limit)
            
            return {
                "reports": [
                    {
                        "id": r.id,
                        "user_id": r.csv_analysis_id,  # TODO: исправить связь
                        "kpi_data": r.kpi_data,
                        "summary_text": r.summary_text,
                        "created_at": r.created_at.isoformat(),
                    }
                    for r in reports
                ],
                "total": len(reports),
            }
        
        except Exception as e:
            logger.error("reports_error", error=str(e), exc_info=True)
            raise HTTPException(status_code=500, detail="Ошибка получения отчетов")
        finally:
            break

