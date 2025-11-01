"""
Unit тесты для UserService

Тестирование бизнес-логики пользователей
"""

import pytest
from datetime import datetime, timedelta

from src.database.models import User, SubscriptionTier
from src.database.repositories.user_repo import UserRepository
from src.database.repositories.limits_repo import LimitsRepository
from src.services.user_service import UserService


@pytest.mark.asyncio
async def test_get_or_create_new_user(test_session):
    """Тест создания нового пользователя"""
    user_repo = UserRepository()
    limits_repo = LimitsRepository()
    user_service = UserService(user_repo, limits_repo)
    
    telegram_id = 123456789
    username = "test_user"
    
    user = await user_service.get_or_create(
        test_session,
        telegram_id,
        username,
    )
    
    assert user is not None
    assert user.telegram_id == telegram_id
    assert user.username == username
    assert user.subscription_tier == SubscriptionTier.FREE
    assert user.iq_points == 0
    assert user.is_banned is False


@pytest.mark.asyncio
async def test_check_subscription_active(test_session):
    """Тест проверки активности подписки"""
    user_repo = UserRepository()
    limits_repo = LimitsRepository()
    user_service = UserService(user_repo, limits_repo)
    
    # Создаем пользователя с активной подпиской
    user = User(
        telegram_id=123456789,
        username="test_user",
        subscription_tier=SubscriptionTier.PRO,
        subscription_expires_at=datetime.utcnow() + timedelta(days=30),
    )
    
    assert user_service.check_subscription_active(user) is True
    
    # Пользователь с истекшей подпиской
    user_expired = User(
        telegram_id=987654321,
        username="expired_user",
        subscription_tier=SubscriptionTier.PRO,
        subscription_expires_at=datetime.utcnow() - timedelta(days=1),
    )
    
    assert user_service.check_subscription_active(user_expired) is False

