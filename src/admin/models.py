"""
Pydantic модели для админ-панели

Схемы для API запросов и ответов
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from src.database.models import (
    BroadcastStatus,
    PaymentStatus,
    SubscriptionTier,
)


# User Models
class UserResponse(BaseModel):
    """Модель ответа для пользователя"""
    id: int
    telegram_id: int
    username: Optional[str] = None
    subscription_tier: str
    subscription_expires_at: Optional[datetime] = None
    iq_points: int
    referrer_id: Optional[int] = None
    is_banned: bool
    created_at: datetime
    updated_at: datetime


class UserListResponse(BaseModel):
    """Модель ответа для списка пользователей"""
    users: list[UserResponse]
    total: int
    page: int
    limit: int


class ExtendSubscriptionRequest(BaseModel):
    """Модель запроса на продление подписки"""
    days: int = Field(gt=0, le=365)
    tier: SubscriptionTier


class BanUserRequest(BaseModel):
    """Модель запроса на бан пользователя"""
    reason: Optional[str] = None


# Payment Models
class PaymentResponse(BaseModel):
    """Модель ответа для платежа"""
    id: int
    user_id: int
    tribute_transaction_id: str
    amount: int
    currency: str
    status: PaymentStatus
    subscription_tier: SubscriptionTier
    subscription_days: int
    created_at: datetime
    completed_at: Optional[datetime] = None


class PaymentListResponse(BaseModel):
    """Модель ответа для списка платежей"""
    payments: list[PaymentResponse]
    total: int
    total_revenue: float
    page: int
    limit: int


# Analytics Models
class AnalyticsStatsResponse(BaseModel):
    """Модель ответа для статистики аналитики"""
    total_reports: int
    avg_cpm: float
    top_users_by_analyses: list[tuple[int, int]]


# Dashboard Models
class DashboardStatsResponse(BaseModel):
    """Модель ответа для дашборда"""
    total_users: int
    new_users_24h: int
    active_users_7d: int
    free_users: int
    pro_users: int
    ultra_users: int
    payments_today: int
    payments_month: int
    total_revenue_today: float
    total_revenue_month: float
    total_revenue: float
    referrals_total: int
    total_analyses: int


# Broadcast Models
class BroadcastCreateRequest(BaseModel):
    """Модель запроса на создание рассылки"""
    message_text: str = Field(min_length=1, max_length=4096)
    target_subscription: Optional[SubscriptionTier] = None


class BroadcastResponse(BaseModel):
    """Модель ответа для рассылки"""
    id: int
    admin_id: int
    message_text: str
    target_subscription: Optional[str] = None
    status: BroadcastStatus
    sent_count: int
    error_count: int
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class BroadcastListResponse(BaseModel):
    """Модель ответа для списка рассылок"""
    broadcasts: list[BroadcastResponse]
    total: int

