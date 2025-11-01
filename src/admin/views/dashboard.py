"""
Dashboard view для админ-панели

Общая статистика и дашборд
"""

from fastapi import APIRouter, Depends

from src.admin.auth import get_admin
from src.admin.models import DashboardStatsResponse
from src.config.logging import get_logger
from src.database.connection import get_session
from src.database.repositories.analytics_repo import (
    CSVAnalysisRepository,
    AnalyticsReportRepository,
)
from src.database.repositories.payment_repo import PaymentRepository
from src.database.repositories.user_repo import UserRepository
from src.services.admin_service import AdminService

logger = get_logger(__name__)
router = APIRouter()


@router.get("/", response_model=DashboardStatsResponse)
async def get_dashboard(
    admin: dict = Depends(get_admin),
):
    """Получить статистику для дашборда"""
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
            
            stats = await admin_service.get_dashboard_stats(session)
            
            return DashboardStatsResponse(**stats)
        
        except Exception as e:
            logger.error("dashboard_error", error=str(e), exc_info=True)
            raise
        finally:
            break

