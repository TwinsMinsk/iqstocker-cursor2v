"""
Сервис для работы с пользователями

Содержит бизнес-логику регистрации, управления подписками и пользователями
"""

from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.config.logging import get_logger
from src.core.exceptions import UserNotFoundException
from src.database.models import User, SubscriptionTier
from src.database.repositories.user_repo import UserRepository
from src.database.repositories.limits_repo import LimitsRepository

logger = get_logger(__name__)


class UserService:
    """Сервис для работы с пользователями"""
    
    def __init__(
        self,
        user_repo: UserRepository,
        limits_repo: LimitsRepository,
    ):
        """
        Инициализация сервиса
        
        Args:
            user_repo: Репозиторий пользователей
            limits_repo: Репозиторий лимитов
        """
        self.user_repo = user_repo
        self.limits_repo = limits_repo
    
    async def get_or_create(
        self,
        session: AsyncSession,
        telegram_id: int,
        username: str | None = None,
        referrer_id: int | None = None,
    ) -> User:
        """
        Получить или создать пользователя
        
        Args:
            session: AsyncSession
            telegram_id: Telegram ID пользователя
            username: Username пользователя
            referrer_id: ID реферера (опционально)
            
        Returns:
            Пользователь
        """
        user = await self.user_repo.get_by_telegram_id(session, telegram_id)
        
        if user:
            # Обновляем username если изменился
            if username and user.username != username:
                user.username = username
                user.updated_at = datetime.utcnow()
                await session.commit()
                await session.refresh(user)
            
            logger.info(
                "user_found",
                user_id=user.id,
                telegram_id=telegram_id,
            )
            return user
        
        # Создаем нового пользователя
        user = User(
            telegram_id=telegram_id,
            username=username,
            subscription_tier=SubscriptionTier.FREE,
            referrer_id=referrer_id,
            iq_points=0,
            is_banned=False,
        )
        
        user = await self.user_repo.create(session, user)
        
        # Создаем лимиты с дефолтными значениями
        await self.limits_repo.create_default(
            session,
            user.id,
            SubscriptionTier.FREE,
        )
        
        logger.info(
            "user_created",
            user_id=user.id,
            telegram_id=telegram_id,
            referrer_id=referrer_id,
        )
        
        return user
    
    async def get_by_telegram_id(
        self,
        session: AsyncSession,
        telegram_id: int,
    ) -> Optional[User]:
        """
        Получить пользователя по Telegram ID
        
        Args:
            session: AsyncSession
            telegram_id: Telegram ID пользователя
            
        Returns:
            Пользователь или None
        """
        return await self.user_repo.get_by_telegram_id(session, telegram_id)
    
    async def get_by_id(
        self,
        session: AsyncSession,
        user_id: int,
    ) -> Optional[User]:
        """
        Получить пользователя по ID
        
        Args:
            session: AsyncSession
            user_id: ID пользователя
            
        Returns:
            Пользователь или None
        """
        return await self.user_repo.get_by_id(session, user_id)
    
    async def activate_subscription(
        self,
        session: AsyncSession,
        user_id: int,
        tier: SubscriptionTier,
        days: int = 30,
    ) -> User:
        """
        Активировать подписку пользователю
        
        Args:
            session: AsyncSession
            user_id: ID пользователя
            tier: Тип подписки
            days: Количество дней подписки
            
        Returns:
            Обновленный пользователь
            
        Raises:
            UserNotFoundException: Пользователь не найден
        """
        user = await self.user_repo.get_by_id(session, user_id)
        if not user:
            raise UserNotFoundException(f"User {user_id} not found")
        
        # Обновляем подписку
        user.subscription_tier = tier
        user.subscription_expires_at = datetime.utcnow() + timedelta(days=days)
        user.updated_at = datetime.utcnow()
        
        await session.commit()
        await session.refresh(user)
        
        # Обновляем лимиты для новой подписки
        await self.limits_repo.update_for_subscription(
            session,
            user_id,
            tier,
        )
        
        logger.info(
            "subscription_activated",
            user_id=user_id,
            tier=tier.value,
            days=days,
        )
        
        return user
    
    async def extend_subscription(
        self,
        session: AsyncSession,
        user_id: int,
        days: int,
    ) -> User:
        """
        Продлить текущую подписку
        
        Args:
            session: AsyncSession
            user_id: ID пользователя
            days: Количество дней для продления
            
        Returns:
            Обновленный пользователь
            
        Raises:
            UserNotFoundException: Пользователь не найден
        """
        user = await self.user_repo.get_by_id(session, user_id)
        if not user:
            raise UserNotFoundException(f"User {user_id} not found")
        
        # Если подписка уже истекла, начинаем с текущего времени
        if user.subscription_expires_at and user.subscription_expires_at > datetime.utcnow():
            user.subscription_expires_at += timedelta(days=days)
        else:
            user.subscription_expires_at = datetime.utcnow() + timedelta(days=days)
        
        user.updated_at = datetime.utcnow()
        
        await session.commit()
        await session.refresh(user)
        
        logger.info(
            "subscription_extended",
            user_id=user_id,
            days=days,
        )
        
        return user
    
    async def ban_user(
        self,
        session: AsyncSession,
        user_id: int,
    ) -> User:
        """
        Забанить пользователя
        
        Args:
            session: AsyncSession
            user_id: ID пользователя
            
        Returns:
            Обновленный пользователь
            
        Raises:
            UserNotFoundException: Пользователь не найден
        """
        user = await self.user_repo.get_by_id(session, user_id)
        if not user:
            raise UserNotFoundException(f"User {user_id} not found")
        
        user.is_banned = True
        user.updated_at = datetime.utcnow()
        
        await session.commit()
        await session.refresh(user)
        
        logger.info("user_banned", user_id=user_id)
        
        return user
    
    async def unban_user(
        self,
        session: AsyncSession,
        user_id: int,
    ) -> User:
        """
        Разбанить пользователя
        
        Args:
            session: AsyncSession
            user_id: ID пользователя
            
        Returns:
            Обновленный пользователь
            
        Raises:
            UserNotFoundException: Пользователь не найден
        """
        user = await self.user_repo.get_by_id(session, user_id)
        if not user:
            raise UserNotFoundException(f"User {user_id} not found")
        
        user.is_banned = False
        user.updated_at = datetime.utcnow()
        
        await session.commit()
        await session.refresh(user)
        
        logger.info("user_unbanned", user_id=user_id)
        
        return user
    
    def check_subscription_active(self, user: User) -> bool:
        """
        Проверить, активна ли подписка
        
        Args:
            user: Пользователь
            
        Returns:
            True если подписка активна
        """
        if user.subscription_tier == SubscriptionTier.FREE:
            return True  # FREE всегда доступен
        
        if not user.subscription_expires_at:
            return True  # Нет даты истечения = пожизненная
        
        return user.subscription_expires_at > datetime.utcnow()
    
    def get_subscription_tier_for_test(self) -> SubscriptionTier:
        """
        Получить тип подписки для тестового режима
        
        TEST_PRO имеет лимиты: 1 анализ + 2 темы в неделю
        
        Returns:
            SubscriptionTier.TEST_PRO
        """
        return SubscriptionTier.TEST_PRO

