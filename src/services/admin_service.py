"""
Сервис для админ-панели

Статистика, управление пользователями, аналитика
"""

from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from src.config.logging import get_logger
from src.core.exceptions import UserNotFoundException
from src.database.models import (
    User,
    Payment,
    PaymentStatus,
    SubscriptionTier,
    CSVAnalysis,
    AnalyticsReport,
)
from src.database.repositories.user_repo import UserRepository
from src.database.repositories.payment_repo import PaymentRepository
from src.database.repositories.analytics_repo import (
    CSVAnalysisRepository,
    AnalyticsReportRepository,
)

logger = get_logger(__name__)


class AdminService:
    """Сервис для админ-панели"""
    
    def __init__(
        self,
        user_repo: UserRepository,
        payment_repo: PaymentRepository,
        csv_analysis_repo: CSVAnalysisRepository,
        analytics_report_repo: AnalyticsReportRepository,
    ):
        """
        Инициализация сервиса
        
        Args:
            user_repo: Репозиторий пользователей
            payment_repo: Репозиторий платежей
            csv_analysis_repo: Репозиторий CSV анализов
            analytics_report_repo: Репозиторий отчетов
        """
        self.user_repo = user_repo
        self.payment_repo = payment_repo
        self.csv_analysis_repo = csv_analysis_repo
        self.analytics_report_repo = analytics_report_repo
    
    async def get_dashboard_stats(
        self,
        session: AsyncSession,
    ) -> dict[str, int | float]:
        """
        Получить статистику для дашборда
        
        Args:
            session: AsyncSession
            
        Returns:
            Словарь со статистикой
        """
        now = datetime.utcnow()
        yesterday = now - timedelta(days=1)
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)
        
        # Общая статистика пользователей
        all_users = await self.user_repo.get_all(session, limit=10000)
        total_users = len(all_users)
        
        # Новые пользователи за 24 часа
        new_users_24h = sum(
            1 for u in all_users
            if u.created_at >= yesterday
        )
        
        # Активные пользователи за неделю
        active_users_7d = sum(
            1 for u in all_users
            if u.updated_at >= week_ago
        )
        
        # Статистика по подпискам
        free_users = sum(1 for u in all_users if u.subscription_tier == SubscriptionTier.FREE)
        pro_users = sum(1 for u in all_users if u.subscription_tier == SubscriptionTier.PRO)
        ultra_users = sum(1 for u in all_users if u.subscription_tier == SubscriptionTier.ULTRA)
        
        # Статистика платежей
        completed_payments = await self.payment_repo.get_by_status(
            session,
            PaymentStatus.COMPLETED,
            limit=10000,
        )
        
        payments_today = sum(
            1 for p in completed_payments
            if p.completed_at and p.completed_at >= yesterday
        )
        
        payments_month = sum(
            1 for p in completed_payments
            if p.completed_at and p.completed_at >= month_ago
        )
        
        total_revenue_today = sum(
            p.amount for p in completed_payments
            if p.completed_at and p.completed_at >= yesterday
        ) / 100  # Конвертируем копейки в рубли
        
        total_revenue_month = sum(
            p.amount for p in completed_payments
            if p.completed_at and p.completed_at >= month_ago
        ) / 100
        
        total_revenue = sum(p.amount for p in completed_payments) / 100
        
        # Статистика рефералов
        referrals_total = sum(
            1 for u in all_users
            if u.referrer_id is not None
        )
        
        # Статистика анализов
        all_analyses = await self.csv_analysis_repo.get_all(session, limit=10000)
        total_analyses = len(all_analyses)
        
        return {
            "total_users": total_users,
            "new_users_24h": new_users_24h,
            "active_users_7d": active_users_7d,
            "free_users": free_users,
            "pro_users": pro_users,
            "ultra_users": ultra_users,
            "payments_today": payments_today,
            "payments_month": payments_month,
            "total_revenue_today": total_revenue_today,
            "total_revenue_month": total_revenue_month,
            "total_revenue": total_revenue,
            "referrals_total": referrals_total,
            "total_analyses": total_analyses,
        }
    
    async def get_user_detail(
        self,
        session: AsyncSession,
        user_id: int,
    ) -> dict:
        """
        Получить детальную информацию о пользователе
        
        Args:
            session: AsyncSession
            user_id: ID пользователя
            
        Returns:
            Словарь с детальной информацией
            
        Raises:
            UserNotFoundException: Пользователь не найден
        """
        user = await self.user_repo.get_by_id(session, user_id)
        if not user:
            raise UserNotFoundException(f"User {user_id} not found")
        
        # Получаем связанные данные
        referrals = await self.user_repo.get_referrals(session, user_id)
        payments = await self.payment_repo.get_by_user_id(session, user_id)
        analyses = await self.csv_analysis_repo.get_by_user_id(session, user_id)
        reports = await self.analytics_report_repo.get_by_user_id(session, user_id)
        
        return {
            "user": user,
            "referrals_count": len(referrals),
            "payments_count": len(payments),
            "analyses_count": len(analyses),
            "reports_count": len(reports),
            "referrals": referrals,
            "payments": payments,
            "analyses": analyses,
            "reports": reports,
        }
    
    async def get_analytics_stats(
        self,
        session: AsyncSession,
    ) -> dict:
        """
        Получить статистику по аналитике
        
        Args:
            session: AsyncSession
            
        Returns:
            Словарь со статистикой аналитики
        """
        all_reports = await self.analytics_report_repo.get_all(session, limit=10000)
        
        # Подсчитываем средний CPM
        cpms = [
            report.kpi_data.get("cpm", 0)
            for report in all_reports
            if report.kpi_data and "cpm" in report.kpi_data
        ]
        avg_cpm = sum(cpms) / len(cpms) if cpms else 0
        
        # Топ пользователей по анализам
        all_analyses = await self.csv_analysis_repo.get_all(session, limit=10000)
        user_analyses_count = {}
        for analysis in all_analyses:
            user_analyses_count[analysis.user_id] = (
                user_analyses_count.get(analysis.user_id, 0) + 1
            )
        
        top_users_by_analyses = sorted(
            user_analyses_count.items(),
            key=lambda x: x[1],
            reverse=True,
        )[:10]
        
        return {
            "total_reports": len(all_reports),
            "avg_cpm": round(avg_cpm, 2),
            "top_users_by_analyses": top_users_by_analyses,
        }

