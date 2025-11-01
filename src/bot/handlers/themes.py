"""
Handler для генерации тем

Выбор категории и генерация тем для контента
"""

from aiogram import Router
from aiogram.types import CallbackQuery

from src.bot.keyboards.factories import get_back_keyboard, get_theme_categories_keyboard
from src.bot.lexicon.lexicon_ru import LEXICON_RU
from src.config.logging import get_logger
from src.core.exceptions import LimitExceededException
from src.database.connection import get_session
from src.database.repositories.limits_repo import LimitsRepository
from src.database.repositories.theme_repo import ThemeRepository
from src.services.theme_service import ThemeService

logger = get_logger(__name__)
router = Router(name=__name__)


@router.callback_query(lambda c: c.data == "themes")
async def callback_themes(callback: CallbackQuery):
    """Обработчик раздела тем"""
    await callback.message.edit_text(
        LEXICON_RU["themes_start"],
        reply_markup=get_theme_categories_keyboard(),
    )
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("theme_"))
async def callback_theme_category(callback: CallbackQuery):
    """Обработчик выбора категории темы"""
    async for session in get_session():
        try:
            # Определяем категорию
            category_map = {
                "theme_vectors": "vectors",
                "theme_photos": "photos",
                "theme_videos": "videos",
                "theme_audio": "audio",
                "theme_templates": "templates",
            }
            
            category = category_map.get(callback.data, "photos")
            
            # Создаем сервисы
            theme_repo = ThemeRepository()
            limits_repo = LimitsRepository()
            from src.database.repositories.theme_template_repo import ThemeTemplateRepository
            theme_template_repo = ThemeTemplateRepository()
            theme_service = ThemeService(theme_repo, limits_repo, theme_template_repo)
            
            # Получаем пользователя
            from src.database.repositories.user_repo import UserRepository
            user_repo = UserRepository()
            user = await user_repo.get_by_telegram_id(session, callback.from_user.id)
            if not user:
                await callback.answer("Пользователь не найден", show_alert=True)
                return
            
            # Проверяем лимиты
            if not await theme_service.can_use_themes(session, user.id):
                limits = await limits_repo.get_by_user_id(session, user.id)
                reset_date = limits.reset_at.strftime("%d.%m.%Y") if limits.reset_at else "N/A"
                await callback.message.edit_text(
                    LEXICON_RU["themes_limit_reached"].format(
                        used=limits.themes_used,
                        limit=limits.themes_limit if limits.themes_limit != -1 else "∞",
                        reset_date=reset_date,
                    ),
                    reply_markup=get_back_keyboard("themes"),
                )
                await callback.answer()
                return
            
            # Генерируем тему
            theme_request = await theme_service.generate_theme(session, user.id, category)
            
            # Формируем ответ
            category_names = {
                "vectors": "Векторные иллюстрации",
                "photos": "Фотографии",
                "videos": "Видео",
                "audio": "Аудио",
                "templates": "Шаблоны дизайна",
            }
            
            category_name = category_names.get(category, category)
            
            # Парсим тему для отображения
            theme_text = theme_request.theme
            description = "Актуальная тема для создания контента"
            relevance = "Тренд на рынке стоков"
            keywords = "ключевые слова, теги, SEO"
            
            await callback.message.edit_text(
                LEXICON_RU["theme_generated"].format(
                    category=category_name,
                    theme=theme_text,
                    description=description,
                    relevance=relevance,
                    keywords=keywords,
                ),
                reply_markup=get_theme_categories_keyboard(),
            )
            await callback.answer("✅ Тема сгенерирована!")
        
        except LimitExceededException as e:
            await callback.answer(str(e), show_alert=True)
        except Exception as e:
            logger.error("theme_handler_error", error=str(e), exc_info=True)
            await callback.answer("Ошибка генерации темы", show_alert=True)
        finally:
            break

