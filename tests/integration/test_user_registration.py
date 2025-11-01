"""
Integration тесты для регистрации пользователей

Тестирование полного флоу регистрации
"""

import pytest
from datetime import datetime

from src.database.models import User, Limits, SubscriptionTier
from src.database.repositories.user_repo import UserRepository
from src.database.repositories.limits_repo import LimitsRepository
from src.services.user_service import UserService


@pytest.mark.asyncio
async def test_full_registration_flow(test_session):
    """Тест полного флоу регистрации пользователя"""
    user_repo = UserRepository()
    limits_repo = LimitsRepository()
    user_service = UserService(user_repo, limits_repo)
    
    telegram_id = 123456789
    username = "new_user"
    referrer_id = None
    
    # Регистрируем пользователя
    user = await user_service.get_or_create(
        test_session,
        telegram_id,
        username,
        referrer_id,
    )
    
    # Проверяем, что пользователь создан
    assert user is not None
    assert user.telegram_id == telegram_id
    assert user.username == username
    assert user.subscription_tier == SubscriptionTier.FREE
    
    # Проверяем, что лимиты созданы
    limits = await limits_repo.get_by_user_id(test_session, user.id)
    assert limits is not None
    assert limits.analytics_limit == 5  # FREE лимит
    assert limits.themes_limit == 10  # FREE лимит

