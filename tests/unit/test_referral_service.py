"""
Unit тесты для ReferralService

Тестирование реферальной программы
"""

import pytest

from src.database.models import User, SubscriptionTier
from src.database.repositories.user_repo import UserRepository
from src.services.referral_service import ReferralService


@pytest.mark.asyncio
async def test_generate_referral_link():
    """Тест генерации реферальной ссылки"""
    user_repo = UserRepository()
    referral_service = ReferralService(user_repo)
    
    user_id = 123
    link = referral_service.generate_referral_link(user_id)
    
    assert "ref_" in link
    assert str(user_id) in link
    assert link.startswith("https://t.me/")


@pytest.mark.asyncio
async def test_award_referral_points(test_session):
    """Тест начисления реферальных баллов"""
    user_repo = UserRepository()
    referral_service = ReferralService(user_repo)
    
    # Создаем пользователя
    user = User(
        telegram_id=123456789,
        username="referrer",
        iq_points=0,
    )
    user = await user_repo.create(test_session, user)
    
    # Начисляем баллы
    updated_user = await referral_service.award_referral_points(
        test_session,
        user.id,
    )
    
    assert updated_user is not None
    assert updated_user.iq_points == 1

