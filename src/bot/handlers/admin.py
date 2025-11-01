"""
Handler для админ-команд

Административные функции бота
"""

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from src.bot.keyboards.factories import get_back_keyboard
from src.bot.lexicon.lexicon_ru import LEXICON_RU
from src.config.logging import get_logger
from src.config.settings import settings
from src.database.connection import get_session
from src.services.admin_service import AdminService
from src.database.repositories.user_repo import UserRepository
from src.database.repositories.payment_repo import PaymentRepository
from src.database.repositories.analytics_repo import (
    CSVAnalysisRepository,
    AnalyticsReportRepository,
)

logger = get_logger(__name__)
router = Router(name=__name__)


def is_admin(user_id: int) -> bool:
    """Проверяет, является ли пользователь администратором"""
    admin_ids = settings.bot.get_admin_ids()
    return user_id in admin_ids


@router.message(Command("admin"))
async def cmd_admin(message: Message):
    """Обработчик команды /admin"""
    if not is_admin(message.from_user.id):
        await message.answer("У вас нет доступа к этой команде")
        return
    
    await message.answer(
        LEXICON_RU["admin_panel"],
        reply_markup=get_back_keyboard("main_menu"),
    )


@router.callback_query(lambda c: c.data == "admin_stats")
async def callback_admin_stats(callback: CallbackQuery):
    """Обработчик статистики админ-панели"""
    if not is_admin(callback.from_user.id):
        await callback.answer("У вас нет доступа", show_alert=True)
        return
    
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
            
            await callback.message.edit_text(
                LEXICON_RU["admin_stats"].format(
                    total_users=stats["total_users"],
                    new_users_24h=stats["new_users_24h"],
                    active_users_7d=stats["active_users_7d"],
                    free_users=stats["free_users"],
                    pro_users=stats["pro_users"],
                    ultra_users=stats["ultra_users"],
                    payments_today=int(stats["total_revenue_today"]),
                    payments_month=int(stats["total_revenue_month"]),
                    payments_total=int(stats["total_revenue"]),
                    referrals_total=stats["referrals_total"],
                    referral_conversion=round(stats["referrals_total"] / stats["total_users"] * 100, 1) if stats["total_users"] > 0 else 0,
                ),
                reply_markup=get_back_keyboard("main_menu"),
            )
            await callback.answer()
        
        except Exception as e:
            logger.error("admin_stats_error", error=str(e), exc_info=True)
            await callback.answer("Ошибка загрузки статистики", show_alert=True)
        finally:
            break

