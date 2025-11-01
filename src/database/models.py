"""
Модели данных IQStocker v2.0

Содержит все SQLModel модели для базы данных:
- User, Limits, CSVAnalysis, AnalyticsReport
- ThemeRequest, Payment, SystemMessage, BroadcastMessage
- ThemeTemplate - шаблоны тем для генерации
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import Any

from sqlalchemy import JSON, Text, Column
from sqlmodel import SQLModel, Field


# ============================================================================
# ENUMS
# ============================================================================

class SubscriptionTier(str, Enum):
    """Типы подписок"""
    FREE = "free"
    PRO = "pro"
    ULTRA = "ultra"
    TEST_PRO = "test_pro"


class AnalysisStatus(str, Enum):
    """Статусы анализа CSV"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class PaymentStatus(str, Enum):
    """Статусы платежей"""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class PaymentProvider(str, Enum):
    """Провайдеры платежей"""
    TRIBUTE = "tribute"


class BroadcastStatus(str, Enum):
    """Статусы рассылок"""
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class MessageType(str, Enum):
    """Типы системных сообщений"""
    INFO = "info"
    WARNING = "warning"
    PROMO = "promo"


class MessagePriority(str, Enum):
    """Приоритеты сообщений"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


# ============================================================================
# MODELS
# ============================================================================

class User(SQLModel, table=True):
    """Модель пользователя"""
    
    __tablename__ = "users"
    
    id: int | None = Field(default=None, primary_key=True)
    telegram_id: int = Field(unique=True, index=True)
    username: str | None = Field(default=None, max_length=255)
    
    # Подписка
    subscription_tier: SubscriptionTier = Field(default=SubscriptionTier.FREE)
    subscription_expires_at: datetime | None = Field(default=None, index=True)
    
    # Реферальная программа
    referrer_id: int | None = Field(default=None, foreign_key="users.id", index=True)
    iq_points: int = Field(default=0)  # IQ Баллы от рефералов
    
    # Статус
    is_banned: bool = Field(default=False)
    
    # Временные метки
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Limits(SQLModel, table=True):
    """Лимиты пользователя"""
    
    __tablename__ = "limits"
    
    user_id: int = Field(primary_key=True, foreign_key="users.id")
    analytics_used: int = Field(default=0)
    analytics_limit: int = Field(default=5)  # FREE: 5, PRO: -1 (unlimited)
    themes_used: int = Field(default=0)
    themes_limit: int = Field(default=10)  # FREE: 10, PRO: 100, ULTRA: -1
    reset_at: datetime = Field(default_factory=lambda: datetime.utcnow() + timedelta(days=30))
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class CSVAnalysis(SQLModel, table=True):
    """Загруженные CSV файлы"""
    
    __tablename__ = "csv_analyses"
    
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    file_id: str = Field(max_length=255)  # Telegram file_id
    filename: str = Field(max_length=255)
    row_count: int
    analysis_status: AnalysisStatus = Field(default=AnalysisStatus.PENDING)
    error_message: str | None = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)


class AnalyticsReport(SQLModel, table=True):
    """Сгенерированные отчеты"""
    
    __tablename__ = "analytics_reports"
    
    id: int | None = Field(default=None, primary_key=True)
    csv_analysis_id: int = Field(foreign_key="csv_analyses.id", unique=True, index=True)
    kpi_data: dict[str, Any] = Field(sa_column=Column(JSON))  # CPM, conversion, etc.
    summary_text: str = Field(sa_column=Column(Text))
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ThemeTemplate(SQLModel, table=True):
    """Шаблоны тем для генерации"""
    
    __tablename__ = "theme_templates"
    
    id: int | None = Field(default=None, primary_key=True)
    category: str = Field(max_length=50, index=True)  # vectors, photos, videos, audio, templates
    theme: str = Field(sa_column=Column(Text))
    description: str | None = Field(default=None, sa_column=Column(Text))
    keywords: list[str] | None = Field(default=None, sa_column=Column(JSON))
    is_active: bool = Field(default=True, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ThemeRequest(SQLModel, table=True):
    """Выданные темы"""
    
    __tablename__ = "theme_requests"
    
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    theme: str = Field(sa_column=Column(Text))
    category: str = Field(max_length=50)  # vectors, photos, videos, audio, templates
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)


class Payment(SQLModel, table=True):
    """Платежи через Tribute.tg"""
    
    __tablename__ = "payments"
    
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    tribute_transaction_id: str = Field(unique=True, max_length=255)
    amount: int  # В копейках
    currency: str = Field(default="RUB", max_length=3)
    status: PaymentStatus = Field(default=PaymentStatus.PENDING)
    subscription_tier: SubscriptionTier
    subscription_days: int = Field(default=30)
    payment_provider: PaymentProvider = Field(default=PaymentProvider.TRIBUTE)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    completed_at: datetime | None = Field(default=None)


class SystemMessage(SQLModel, table=True):
    """Системные сообщения"""
    
    __tablename__ = "system_messages"
    
    id: int | None = Field(default=None, primary_key=True)
    message_type: MessageType = Field(default=MessageType.INFO)
    priority: MessagePriority = Field(default=MessagePriority.NORMAL)
    title: str = Field(max_length=255)
    content: str = Field(sa_column=Column(Text))
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class BroadcastMessage(SQLModel, table=True):
    """Массовые рассылки"""
    
    __tablename__ = "broadcast_messages"
    
    id: int | None = Field(default=None, primary_key=True)
    admin_id: int = Field(foreign_key="users.id")
    message_text: str = Field(sa_column=Column(Text))
    target_subscription: SubscriptionTier | None = Field(default=None)
    status: BroadcastStatus = Field(default=BroadcastStatus.DRAFT)
    sent_count: int = Field(default=0)
    error_count: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: datetime | None = Field(default=None)
    completed_at: datetime | None = Field(default=None)
