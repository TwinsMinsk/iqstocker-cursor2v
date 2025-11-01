"""
Сервис для реферальной программы

Управление IQ баллами, реферальными ссылками и обменом баллов
"""

from datetime import datetime
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.config.logging import get_logger
from src.config.settings import settings
from src.core.exceptions import (
    InsufficientPointsException,
    ReferralException,
    UserNotFoundException,
)
from src.database.models import SubscriptionTier, User
from src.database.repositories.user_repo import UserRepository

logger = get_logger(__name__)


class ReferralService:
    """Сервис для реферальной программы"""
    
    def __init__(
        self,
        user_repo: UserRepository,
    ):
        """
        Инициализация сервиса
        
        Args:
            user_repo: Репозиторий пользователей
        """
        self.user_repo = user_repo
    
    def generate_referral_link(self, user_id: int) -> str:
        """
        Сгенерировать реферальную ссылку для пользователя
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Реферальная ссылка
        """
        bot_username = settings.bot.token.split(":")[0]  # Из токена можно получить username
        # Для MVP используем простой формат
        return f"https://t.me/iqstocker_bot?start=ref_{user_id}"
    
    async def award_referral_points(
        self,
        session: AsyncSession,
        referrer_id: int,
    ) -> Optional[User]:
        """
        Начислить IQ баллы рефереру
        
        Начисляется 1 балл за каждую покупку PRO или ULTRA подписки рефералом
        
        Args:
            session: AsyncSession
            referrer_id: ID реферера
            
        Returns:
            Обновленный реферер или None если не найден
        """
        referrer = await self.user_repo.get_by_id(session, referrer_id)
        if not referrer:
            logger.warning(
                "referrer_not_found",
                referrer_id=referrer_id,
            )
            return None
        
        # Начисляем +1 IQ балл
        updated_referrer = await self.user_repo.increment_iq_points(
            session,
            referrer_id,
            points=1,
        )
        
        logger.info(
            "referral_points_awarded",
            referrer_id=referrer_id,
            new_balance=updated_referrer.iq_points if updated_referrer else 0,
        )
        
        return updated_referrer
    
    async def exchange_points_for_discount(
        self,
        session: AsyncSession,
        user_id: int,
        points: int,
        discount_percent: int,
    ) -> dict[str, int]:
        """
        Обменять IQ баллы на скидку
        
        Args:
            session: AsyncSession
            user_id: ID пользователя
            points: Количество баллов (1 или 2)
            discount_percent: Процент скидки (25 или 50)
            
        Returns:
            Словарь с информацией о скидке
            
        Raises:
            InsufficientPointsException: Недостаточно баллов
            UserNotFoundException: Пользователь не найден
        """
        user = await self.user_repo.get_by_id(session, user_id)
        if not user:
            raise UserNotFoundException(f"User {user_id} not found")
        
        if user.iq_points < points:
            raise InsufficientPointsException(
                f"Недостаточно баллов. Требуется: {points}, доступно: {user.iq_points}"
            )
        
        # Списываем баллы
        await self.user_repo.decrement_iq_points(session, user_id, points)
        
        logger.info(
            "points_exchanged_for_discount",
            user_id=user_id,
            points_spent=points,
            discount_percent=discount_percent,
        )
        
        return {
            "points_spent": points,
            "discount_percent": discount_percent,
            "remaining_points": user.iq_points - points,
        }
    
    async def exchange_points_for_free_subscription(
        self,
        session: AsyncSession,
        user_id: int,
        points: int,
        tier: SubscriptionTier,
    ) -> dict[str, int]:
        """
        Обменять IQ баллы на бесплатную подписку
        
        Args:
            session: AsyncSession
            user_id: ID пользователя
            points: Количество баллов (3 для PRO, 4 для ULTRA)
            tier: Тип подписки (PRO или ULTRA)
            
        Returns:
            Словарь с информацией о подписке
            
        Raises:
            InsufficientPointsException: Недостаточно баллов
            UserNotFoundException: Пользователь не найден
            ReferralException: Неверный тип подписки
        """
        if tier not in [SubscriptionTier.PRO, SubscriptionTier.ULTRA]:
            raise ReferralException(
                "Бесплатная подписка доступна только для PRO или ULTRA"
            )
        
        user = await self.user_repo.get_by_id(session, user_id)
        if not user:
            raise UserNotFoundException(f"User {user_id} not found")
        
        if user.iq_points < points:
            raise InsufficientPointsException(
                f"Недостаточно баллов. Требуется: {points}, доступно: {user.iq_points}"
            )
        
        # Списываем баллы
        await self.user_repo.decrement_iq_points(session, user_id, points)
        
        logger.info(
            "points_exchanged_for_subscription",
            user_id=user_id,
            points_spent=points,
            tier=tier.value,
        )
        
        return {
            "points_spent": points,
            "tier": tier.value,
            "days": 30,
            "remaining_points": user.iq_points - points,
        }
    
    async def exchange_points_for_channel_access(
        self,
        session: AsyncSession,
        user_id: int,
        points: int = 5,
    ) -> dict[str, int]:
        """
        Обменять IQ баллы на доступ в закрытый канал
        
        Args:
            session: AsyncSession
            user_id: ID пользователя
            points: Количество баллов (5)
            
        Returns:
            Словарь с информацией о доступе
            
        Raises:
            InsufficientPointsException: Недостаточно баллов
            UserNotFoundException: Пользователь не найден
        """
        user = await self.user_repo.get_by_id(session, user_id)
        if not user:
            raise UserNotFoundException(f"User {user_id} not found")
        
        if user.iq_points < points:
            raise InsufficientPointsException(
                f"Недостаточно баллов. Требуется: {points}, доступно: {user.iq_points}"
            )
        
        # Списываем баллы
        await self.user_repo.decrement_iq_points(session, user_id, points)
        
        logger.info(
            "points_exchanged_for_channel_access",
            user_id=user_id,
            points_spent=points,
        )
        
        return {
            "points_spent": points,
            "channel": "IQ Radar",
            "access": "lifetime",
            "remaining_points": user.iq_points - points,
        }
    
    async def get_referral_stats(
        self,
        session: AsyncSession,
        user_id: int,
    ) -> dict[str, int]:
        """
        Получить статистику реферальной программы для пользователя
        
        Args:
            session: AsyncSession
            user_id: ID пользователя
            
        Returns:
            Словарь со статистикой
        """
        user = await self.user_repo.get_by_id(session, user_id)
        if not user:
            raise UserNotFoundException(f"User {user_id} not found")
        
        referrals = await self.user_repo.get_referrals(session, user_id)
        
        # Подсчитываем рефералов с активными подписками PRO/ULTRA
        referrals_with_subscription = [
            r for r in referrals
            if r.subscription_tier in [SubscriptionTier.PRO, SubscriptionTier.ULTRA]
            and (not r.subscription_expires_at or r.subscription_expires_at > datetime.utcnow())
        ]
        
        return {
            "iq_points": user.iq_points,
            "total_referrals": len(referrals),
            "referrals_with_subscription": len(referrals_with_subscription),
        }

