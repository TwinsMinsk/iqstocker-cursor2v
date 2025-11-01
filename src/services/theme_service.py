"""
Сервис для генерации тем контента

Генерация тем по категориям, проверка лимитов
"""

import random
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.config.logging import get_logger
from src.core.exceptions import LimitExceededException
from src.database.models import ThemeRequest
from src.database.repositories.limits_repo import LimitsRepository
from src.database.repositories.theme_repo import ThemeRepository
from src.database.repositories.theme_template_repo import ThemeTemplateRepository

logger = get_logger(__name__)


class ThemeService:
    """Сервис для генерации тем"""
    
    def __init__(
        self,
        theme_repo: ThemeRepository,
        limits_repo: LimitsRepository,
        theme_template_repo: ThemeTemplateRepository | None = None,
    ):
        """
        Инициализация сервиса
        
        Args:
            theme_repo: Репозиторий тем
            limits_repo: Репозиторий лимитов
            theme_template_repo: Репозиторий шаблонов тем
        """
        self.theme_repo = theme_repo
        self.limits_repo = limits_repo
        self.theme_template_repo = theme_template_repo
    
    async def can_use_themes(
        self,
        session: AsyncSession,
        user_id: int,
    ) -> bool:
        """
        Проверить, может ли пользователь использовать генерацию тем
        
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
        if limits.themes_limit == -1:
            return True
        
        return limits.themes_used < limits.themes_limit
    
    async def generate_theme(
        self,
        session: AsyncSession,
        user_id: int,
        category: str,
    ) -> ThemeRequest:
        """
        Сгенерировать тему для пользователя
        
        Args:
            session: AsyncSession
            user_id: ID пользователя
            category: Категория темы (vectors, photos, videos, audio, templates)
            
        Returns:
            Созданная тема
            
        Raises:
            LimitExceededException: Превышен лимит тем
        """
        # Проверяем лимиты
        if not await self.can_use_themes(session, user_id):
            limits = await self.limits_repo.get_by_user_id(session, user_id)
            raise LimitExceededException(
                f"Превышен лимит тем. Использовано: {limits.themes_used}/{limits.themes_limit}"
            )
        
        # Генерация темы из БД
        theme_text = await self._generate_theme_from_db(session, category)
        
        # Создаем запрос темы
        theme_request = ThemeRequest(
            user_id=user_id,
            theme=theme_text,
            category=category,
        )
        
        theme_request = await self.theme_repo.create(session, theme_request)
        
        # Увеличиваем счетчик использованных тем
        await self.limits_repo.increment_themes(session, user_id)
        
        logger.info(
            "theme_generated",
            theme_id=theme_request.id,
            user_id=user_id,
            category=category,
        )
        
        return theme_request
    
    async def get_user_themes(
        self,
        session: AsyncSession,
        user_id: int,
        limit: int = 20,
    ) -> list[ThemeRequest]:
        """
        Получить все темы пользователя
        
        Args:
            session: AsyncSession
            user_id: ID пользователя
            limit: Максимальное количество записей
            
        Returns:
            Список тем
        """
        return await self.theme_repo.get_by_user_id(session, user_id, limit)
    
    async def _generate_theme_from_db(
        self,
        session: AsyncSession,
        category: str,
    ) -> str:
        """
        Генерация темы из БД
        
        Args:
            session: AsyncSession
            category: Категория темы
            
        Returns:
            Текст темы
        """
        # Пытаемся получить случайную тему из БД
        if self.theme_template_repo:
            template = await self.theme_template_repo.get_random_by_category(
                session,
                category,
            )
            if template:
                return template.theme
        
        # Fallback на заглушку, если БД пуста
        themes_by_category = {
            "vectors": "Векторные иллюстрации для современного дизайна",
            "photos": "Профессиональные фотографии для стоков",
            "videos": "Видео контент для творческих проектов",
            "audio": "Аудио материалы для медиа проектов",
            "templates": "Шаблоны дизайна для быстрого старта",
        }
        
        return themes_by_category.get(category, "Общая тема для контента")

