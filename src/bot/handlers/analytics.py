"""
Handler для анализа CSV файлов

Загрузка CSV, создание анализов, просмотр отчетов
"""

from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from arq import create_pool
from arq.connections import RedisSettings

from src.bot.keyboards.factories import get_analytics_keyboard, get_back_keyboard
from src.bot.lexicon.lexicon_ru import LEXICON_RU
from src.bot.states.fsm import AnalyticsStates
from src.config.logging import get_logger
from src.config.settings import settings
from src.core.exceptions import LimitExceededException
from src.database.connection import get_session
from src.database.repositories.analytics_repo import CSVAnalysisRepository
from src.services.analytics_service import AnalyticsService

logger = get_logger(__name__)
router = Router(name=__name__)


@router.callback_query(lambda c: c.data == "analytics")
async def callback_analytics(callback: CallbackQuery):
    """Обработчик раздела аналитики"""
    await callback.message.edit_text(
        LEXICON_RU["analytics_start"],
        reply_markup=get_analytics_keyboard(),
    )
    await callback.answer()


@router.callback_query(lambda c: c.data == "new_analysis")
async def callback_new_analysis(callback: CallbackQuery, state: FSMContext):
    """Обработчик начала нового анализа"""
    await state.set_state(AnalyticsStates.waiting_for_csv)
    await callback.message.edit_text(
        LEXICON_RU["analytics_start"],
        reply_markup=get_back_keyboard("analytics"),
    )
    await callback.answer()


@router.message(AnalyticsStates.waiting_for_csv, F.document)
async def process_csv_file(message: Message, state: FSMContext, bot: Bot):
    """Обработчик загрузки CSV файла"""
    async for session in get_session():
        try:
            # Получаем документ
            document = message.document
            
            # Проверяем формат файла
            if not document.file_name.endswith('.csv'):
                await message.answer(
                    LEXICON_RU["error_invalid_format"],
                    reply_markup=get_back_keyboard("analytics"),
                )
                await state.clear()
                return
            
            # Создаем сервисы
            csv_analysis_repo = CSVAnalysisRepository()
            from src.database.repositories.analytics_repo import AnalyticsReportRepository
            from src.database.repositories.limits_repo import LimitsRepository
            
            analytics_report_repo = AnalyticsReportRepository()
            limits_repo = LimitsRepository()
            
            analytics_service = AnalyticsService(
                csv_analysis_repo,
                analytics_report_repo,
                limits_repo,
            )
            
            # Получаем пользователя
            from src.database.repositories.user_repo import UserRepository
            user_repo = UserRepository()
            user = await user_repo.get_by_telegram_id(session, message.from_user.id)
            if not user:
                await message.answer(LEXICON_RU["error_generic"].format(error_code="ANALYTICS_001"))
                await state.clear()
                return
            
            # Проверяем лимиты
            if not await analytics_service.can_use_analytics(session, user.id):
                limits = await limits_repo.get_by_user_id(session, user.id)
                reset_date = limits.reset_at.strftime("%d.%m.%Y") if limits.reset_at else "N/A"
                await message.answer(
                    LEXICON_RU["analytics_limit_reached"].format(
                        used=limits.analytics_used,
                        limit=limits.analytics_limit if limits.analytics_limit != -1 else "∞",
                        reset_date=reset_date,
                    ),
                    reply_markup=get_back_keyboard("analytics"),
                )
                await state.clear()
                return
            
            # Скачиваем файл
            file = await bot.get_file(document.file_id)
            file_content = await bot.download_file(file.file_path)
            
            # Читаем файл
            import io
            content_bytes = await file_content.read()
            content_str = content_bytes.decode('utf-8-sig')
            
            # Подсчитываем строки (приблизительно)
            row_count = len(content_str.split('\n')) - 1  # Минус заголовок
            
            # Создаем анализ
            analysis = await analytics_service.create_analysis(
                session,
                user.id,
                document.file_id,
                document.file_name or "upload.csv",
                row_count,
            )
            
            # Отправляем задачу в ARQ
            try:
                redis_pool = await create_pool(
                    RedisSettings(
                        host=settings.redis.host,
                        port=settings.redis.port,
                        database=settings.redis.db,
                    )
                )
                await redis_pool.enqueue_job('process_csv', analysis.id)
                await redis_pool.close()
            except Exception as e:
                logger.error("arq_enqueue_error", error=str(e), exc_info=True)
            
            # Уведомляем пользователя
            await message.answer(
                LEXICON_RU["analytics_file_received"].format(
                    filename=document.file_name or "upload.csv",
                    size=f"{document.file_size / 1024:.2f} KB" if document.file_size else "N/A",
                    rows=row_count,
                ),
                reply_markup=get_back_keyboard("analytics"),
            )
            
            await state.clear()
        
        except LimitExceededException as e:
            await message.answer(str(e), reply_markup=get_back_keyboard("analytics"))
            await state.clear()
        except Exception as e:
            logger.error("csv_upload_error", error=str(e), exc_info=True)
            await message.answer(
                LEXICON_RU["analytics_error"],
                reply_markup=get_back_keyboard("analytics"),
            )
            await state.clear()
        finally:
            break


@router.callback_query(lambda c: c.data == "my_reports")
async def callback_my_reports(callback: CallbackQuery):
    """Обработчик просмотра отчетов"""
    async for session in get_session():
        try:
            from src.database.repositories.user_repo import UserRepository
            from src.database.repositories.analytics_repo import AnalyticsReportRepository
            
            user_repo = UserRepository()
            analytics_report_repo = AnalyticsReportRepository()
            
            user = await user_repo.get_by_telegram_id(session, callback.from_user.id)
            if not user:
                await callback.answer("Пользователь не найден", show_alert=True)
                return
            
            # Получаем отчеты
            reports = await analytics_report_repo.get_by_user_id(session, user.id, limit=5)
            
            if not reports:
                await callback.message.edit_text(
                    "📋 У тебя пока нет отчетов.\n\nЗагрузи CSV файл для первого анализа!",
                    reply_markup=get_back_keyboard("analytics"),
                )
            else:
                # Показываем последний отчет
                last_report = reports[0]
                await callback.message.edit_text(
                    last_report.summary_text,
                    reply_markup=get_back_keyboard("analytics"),
                )
            
            await callback.answer()
        
        except Exception as e:
            logger.error("reports_handler_error", error=str(e), exc_info=True)
            await callback.answer("Ошибка загрузки отчетов", show_alert=True)
        finally:
            break

