# IQStocker v2.0 - Technical Implementation Document (TID)

## 📋 Содержание

1. [Введение](#введение)
2. [Архитектурные принципы](#архитектурные-принципы)
3. [Модели данных](#модели-данных)
4. [Технологический стек](#технологический-стек)
5. [Структура проекта](#структура-проекта)
6. [Функциональные требования](#функциональные-требования)
7. [Безопасность и логирование](#безопасность-и-логирование)
8. [Деплой и инфраструктура](#деплой-и-инфраструктура)

---

## Введение

### Цель Ре-Архитектуринга

Создание современной версии IQStocker 2.0 с чистым кодом, оптимизированным для:
- Разработки AI-агентом в Cursor IDE
- Масштабируемости и поддерживаемости
- Строгой типизации и тестируемости
- Быстрой итерации и развертывания

### Ключевые Улучшения v2.0

- ✅ 100% async архитектура (aiogram 3.x + FastAPI)
- ✅ Repository + Service Pattern для четкого разделения слоев
- ✅ SQLModel вместо SQLAlchemy + Pydantic (сокращение кода на 40-50%)
- ✅ ARQ вместо Celery (легковесность, нативная async поддержка)
- ✅ Ruff + Mypy для быстрого линтинга и строгой типизации
- ✅ Poetry для управления зависимостями
- ✅ Полная Docker конфигурация

---

## Архитектурные принципы

### Разделение слоев

```
┌─────────────────────────────────────┐
│  Handlers (UI Layer)                │  ← Aiogram handlers, keyboards, FSM
├─────────────────────────────────────┤
│  Services (Business Logic)          │  ← Бизнес-правила, валидация
├─────────────────────────────────────┤
│  Repositories (Data Access)         │  ← CRUD операции с БД
├─────────────────────────────────────┤
│  Models (Data Layer)                │  ← SQLModel таблицы
└─────────────────────────────────────┘
```

### Repository Pattern

**Преимущества:**
- Изоляция доступа к БД
- Легкое тестирование (мокирование repositories)
- Возможность смены СУБД без изменения бизнес-логики
- Централизация запросов к данным

**Пример:**
```python
# Repository - только доступ к данным
class UserRepository:
    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        ...
    
# Service - бизнес-логика
class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo
    
    async def register_user(self, telegram_id: int) -> User:
        # Бизнес-правила здесь
        ...
```

### Service Layer

**Ответственность:**
- Бизнес-логика (проверка лимитов, начисление бонусов)
- Транзакции через несколько repositories
- Валидация данных перед сохранением
- Координация между различными доменами

---

## Модели данных

### 1. User - Пользователи

```python
class User(SQLModel, table=True):
    __tablename__ = "users"
    
    id: int | None = Field(default=None, primary_key=True)
    telegram_id: int = Field(unique=True, index=True)
    username: str | None = Field(default=None, max_length=255)
    subscription_tier: SubscriptionTier = Field(default=SubscriptionTier.FREE)
    subscription_expires_at: datetime | None = Field(default=None)
    referrer_id: int | None = Field(default=None, foreign_key="users.id")
    is_banned: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

**Индексы:**
- `telegram_id` (unique)
- `subscription_tier`, `subscription_expires_at` (composite для активных подписок)
- `referrer_id` (для реферальной программы)
- `created_at` (для статистики)

### 2. Limits - Лимиты пользователей

```python
class Limits(SQLModel, table=True):
    __tablename__ = "limits"
    
    user_id: int = Field(primary_key=True, foreign_key="users.id")
    analytics_used: int = Field(default=0)
    analytics_limit: int = Field(default=5)  # FREE: 5, PRO: -1 (unlimited)
    themes_used: int = Field(default=0)
    themes_limit: int = Field(default=10)  # FREE: 10, PRO: 100, ULTRA: -1
    reset_at: datetime = Field(default_factory=lambda: datetime.utcnow() + timedelta(days=30))
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

**Логика лимитов:**
- `-1` = безлимит
- Сброс каждые 30 дней
- Автоматический пересчет при смене подписки

### 3. CSVAnalysis - Загруженные CSV файлы

```python
class CSVAnalysis(SQLModel, table=True):
    __tablename__ = "csv_analyses"
    
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    file_id: str = Field(max_length=255)  # Telegram file_id
    filename: str = Field(max_length=255)
    row_count: int
    analysis_status: AnalysisStatus = Field(default=AnalysisStatus.PENDING)
    error_message: str | None = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

### 4. AnalyticsReport - Сгенерированные отчеты

```python
class AnalyticsReport(SQLModel, table=True):
    __tablename__ = "analytics_reports"
    
    id: int | None = Field(default=None, primary_key=True)
    csv_analysis_id: int = Field(foreign_key="csv_analyses.id", unique=True)
    kpi_data: dict = Field(sa_column=Column(JSON))  # CPM, conversion, etc.
    summary_text: str = Field(sa_column=Column(Text))
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

**kpi_data структура:**
```json
{
  "total_sales": 1234,
  "total_revenue": 567.89,
  "cpm": 12.34,
  "conversion_rate": 2.5,
  "average_check": 0.46,
  "trend": "growing",
  "top_assets": [...],
  "type_distribution": {...}
}
```

### 5. ThemeRequest - Выданные темы

```python
class ThemeRequest(SQLModel, table=True):
    __tablename__ = "theme_requests"
    
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    theme: str = Field(sa_column=Column(Text))
    category: str = Field(max_length=50)  # vectors, photos, videos, audio, templates
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
```

### 6. Referral - Реферальная программа
**Как это работает:**
Есть уникальная ссылка.
Когда кто-то регистрируется по ней и оформляет подписку PRO или ULTRA, пользователь получает +1 IQ Балл.
Баллы копятся и не сгорают— их можно обменять на бонусы в любое время, в разделе 🎁 Использовать баллы.

🎁 На что можно обменять баллы?1️⃣ IQ Балл — скидка 25% на месяц PRO или ULTRA2️⃣ IQ Балла — скидка 50% на месяц PRO или ULTRA 3️⃣ IQ Балла — 1 месяц PRO бесплатно4️⃣ IQ Балла — 1 месяц ULTRA бесплатно5️⃣ IQ Баллов — бесплатный пожизненный доступ в закрытый канал IQ Radar

### 7. Payment - Платежи через Tribute.tg

```python
class Payment(SQLModel, table=True):
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
```

### 8. SystemMessage - Системные сообщения

```python
class SystemMessage(SQLModel, table=True):
    __tablename__ = "system_messages"
    
    id: int | None = Field(default=None, primary_key=True)
    message_type: MessageType = Field(default=MessageType.INFO)
    priority: MessagePriority = Field(default=MessagePriority.NORMAL)
    title: str = Field(max_length=255)
    content: str = Field(sa_column=Column(Text))
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

### 9. BroadcastMessage - Массовые рассылки

```python
class BroadcastMessage(SQLModel, table=True):
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
```

### Enums

```python
class SubscriptionTier(str, Enum):
    FREE = "free"
    PRO = "pro"
    ULTRA = "ultra"
    TEST_PRO = "test_pro"

class AnalysisStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class PaymentStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"

class PaymentProvider(str, Enum):
    TRIBUTE = "tribute"

class BroadcastStatus(str, Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class MessageType(str, Enum):
    INFO = "info"
    WARNING = "warning"
    PROMO = "promo"

class MessagePriority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"
```

---

## Технологический стек

### Backend

**Core:**
- Python 3.11+
- Aiogram 3.4+ (Telegram Bot framework)
- FastAPI 0.109+ (Admin panel + API)

**Database:**
- SQLModel 0.0.16+ (ORM + Pydantic)
- PostgreSQL 16 (primary database)
- Redis 7.2 (кеширование, ARQ)

**Background Tasks:**
- ARQ 0.26+ (async task queue)

**Quality Tools:**
- Ruff 0.3+ (linting + formatting)
- Mypy 1.9+ (static type checking)
- Pytest 8.1+ (testing)

**Deployment:**
- Docker + Docker Compose
- Railway.app (hosting)
- Alembic (migrations)

### Обоснование выбора

#### ARQ вместо Celery

**Преимущества:**
- 100% async (нативная интеграция с aiogram/fastapi)
- 10x меньше кода конфигурации
- 2x меньше потребление памяти
- Встроенная поддержка cron-like задач
- Простая настройка для AI-агента

**Пример:**
```python
# ARQ - простая конфигурация
async def process_csv(ctx, csv_analysis_id: int):
    # Обработка CSV
    pass

class WorkerSettings:
    functions = [process_csv]
    redis_settings = RedisSettings()
```

#### SQLModel вместо SQLAlchemy + Pydantic

**Преимущества:**
- Одна декларация для ORM + API схем
- Сокращение кода на 40-50%
- Автоматическая валидация
- Совместимость с FastAPI

**Было (2 декларации):**
```python
# ORM model
class UserORM(Base):
    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger)

# Pydantic schema
class UserSchema(BaseModel):
    id: int
    telegram_id: int
```

**Стало (1 декларация):**
```python
class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    telegram_id: int = Field(unique=True)
```

#### Ruff вместо flake8 + black

**Преимущества:**
- 100x быстрее (написан на Rust)
- Единый инструмент (линтинг + форматирование)
- Автофикс большинства проблем
- Поддержка Python 3.11+

---

## Структура проекта

```
iqstocker-v2/
├── src/
│   ├── bot/                        # Telegram Bot
│   │   ├── handlers/               # Обработчики команд
│   │   │   ├── start.py           # /start, регистрация
│   │   │   ├── menu.py            # Главное меню
│   │   │   ├── profile.py         # Профиль пользователя
│   │   │   ├── analytics.py       # Загрузка CSV, аналитика
│   │   │   ├── themes.py          # Генерация тем
│   │   │   ├── lessons.py         # Обучающие материалы
│   │   │   ├── calendar.py        # Календарь генераций
│   │   │   ├── faq.py             # FAQ
│   │   │   ├── channel.py         # Проверка подписки
│   │   │   ├── referral.py        # Реферальная программа
│   │   │   ├── payments.py        # Оплата подписок
│   │   │   └── admin.py           # Админ-команды
│   │   ├── keyboards/              # Клавиатуры
│   │   │   └── factories.py       # Callback factories
│   │   ├── states/                 # FSM состояния
│   │   │   └── fsm.py             # FSM группы
│   │   ├── lexicon/                # Тексты бота
│   │   │   └── lexicon_ru.py      # Русский лексикон
│   │   └── main.py                 # Точка входа бота
│   ├── admin/                      # FastAPI Admin Panel
│   │   ├── views/                  # CRUD views
│   │   │   ├── users.py
│   │   │   ├── analytics.py
│   │   │   └── payments.py
│   │   ├── static/                 # CSS, JS
│   │   ├── templates/              # Jinja2 шаблоны
│   │   ├── auth.py                 # Авторизация
│   │   ├── models.py               # Pydantic схемы для API
│   │   └── main.py                 # FastAPI app
│   ├── api/                        # API endpoints
│   │   ├── health.py              # Health checks
│   │   └── webhooks.py            # Tribute.tg webhooks
│   ├── database/                   # Database layer
│   │   ├── repositories/           # Repository pattern
│   │   │   ├── base.py            # BaseRepository
│   │   │   ├── user_repo.py
│   │   │   ├── limits_repo.py
│   │   │   ├── analytics_repo.py
│   │   │   ├── theme_repo.py
│   │   │   ├── referral_repo.py
│   │   │   ├── payment_repo.py
│   │   │   ├── system_repo.py
│   │   │   └── broadcast_repo.py
│   │   ├── models.py               # SQLModel models
│   │   └── connection.py           # DB connection
│   ├── services/                   # Business logic
│   │   ├── user_service.py
│   │   ├── analytics_service.py
│   │   ├── theme_service.py
│   │   ├── referral_service.py
│   │   ├── payment_service.py
│   │   ├── broadcast_service.py
│   │   └── admin_service.py
│   ├── workers/                    # ARQ workers
│   │   └── main.py                # Task definitions
│   ├── core/                       # Core utilities
│   │   ├── analytics/             # CSV processing
│   │   │   ├── csv_processor.py
│   │   │   ├── kpi_calculator.py
│   │   │   └── report_generator.py
│   │   └── utils/                 # Общие утилиты
│   └── config/                     # Configuration
│       ├── settings.py            # Pydantic Settings
│       └── logging.py             # Logging setup
├── alembic/                        # Database migrations
│   ├── versions/
│   └── env.py
├── tests/                          # Tests
│   ├── unit/
│   ├── integration/
│   └── conftest.py
├── logs/                           # Log files
├── .env.example                    # Example environment
├── .gitignore
├── pyproject.toml                  # Poetry configuration
├── docker-compose.yml              # Local development
├── Dockerfile.bot                  # Bot Docker image
├── Dockerfile.admin                # Admin Docker image
├── Dockerfile.worker               # Worker Docker image
└── README.md
```

---

## Функциональные требования

### 1. Регистрация и Авторизация

**Handler:** `start.py`

**Флоу:**
1. Пользователь отправляет `/start` (опционально с referral кодом)
2. Проверка подписки на канал
3. Создание User в БД (если новый)
4. Создание Limits с дефолтными значениями
5. Обработка реферального кода (если есть)
6. Отображение главного меню

**Service метод:**
```python
async def register_user(
    telegram_id: int,
    username: str | None,
    referrer_id: int | None = None
) -> User:
    # 1. Создать пользователя
    # 2. Создать лимиты
    # 3. Обработать реферальную связь
    # 4. Начислить бонус рефереру
    pass
```

### 2. Анализ CSV файлов

**Handler:** `analytics.py`
**Worker:** `workers/main.py::process_csv`
**Service:** `analytics_service.py`

**Флоу:**
1. Пользователь отправляет CSV файл
2. Проверка лимитов (через `limits_repo`)
3. Сохранение CSVAnalysis с status=PENDING
4. Отправка задачи в ARQ: `process_csv.delay(csv_analysis_id)`
5. Worker скачивает файл через Telegram Bot API
6. Парсинг CSV через `csv_processor.py`
7. Расчет KPI через `kpi_calculator.py`
8. Генерация текста отчета через `report_generator.py`
9. Сохранение AnalyticsReport
10. Отправка результата пользователю

**KPI метрики:**
- **CPM** (Cost Per Mille): `(total_revenue / total_impressions) * 1000`
- **Conversion Rate**: `(total_sales / total_impressions) * 100`
- **Average Check**: `total_revenue / total_sales`
- **Trend**: Анализ изменений за последние 30 дней

**CSV структура (Adobe Stock):**
```csv
Date,Asset ID,Title,Type,Impressions,Downloads,Revenue
2024-01-01,123456789,Example Image,Photo,1234,5,2.50
```

### 3. Генерация тем для контента

**Handler:** `themes.py`
**Service:** `theme_service.py`

**Категории:**
- `vectors` - Векторные иллюстрации
- `photos` - Фотографии
- `videos` - Видео
- `audio` - Аудио
- `templates` - Шаблоны дизайна

**Флоу:**
1. Пользователь выбирает категорию
2. Проверка лимитов
3. Генерация темы (AI или из предзаполненной БД)
4. Сохранение ThemeRequest
5. Инкремент `themes_used` в Limits
6. Отображение темы с деталями

**Структура темы:**
```python
{
    "category": "photos",
    "theme": "Sustainable Living in Urban Spaces",
    "description": "Фотографии людей, использующих экологичные решения в городской среде",
    "relevance": "Растущий тренд на осознанное потребление",
    "keywords": ["sustainable", "eco-friendly", "urban", "green living"]
}
```

### 4. Реферальная программа

**Handler:** `referral.py`
**Service:** `referral_service.py`

**Как это работает:**
- У каждого пользователя есть уникальная реферальная ссылка
- Когда кто-то регистрируется по ней и оформляет подписку PRO или ULTRA, пользователь получает **+1 IQ Балл**
- Баллы копятся и не сгорают — их можно обменять на бонусы в любое время, в разделе 🎁 Использовать баллы

**🎁 На что можно обменять баллы:**
- **1 IQ Балл** — скидка 25% на месяц PRO или ULTRA
- **2 IQ Балла** — скидка 50% на месяц PRO или ULTRA
- **3 IQ Балла** — 1 месяц PRO бесплатно
- **4 IQ Балла** — 1 месяц ULTRA бесплатно
- **5 IQ Баллов** — бесплатный пожизненный доступ в закрытый канал IQ Radar

**Реферальная ссылка:**
```
https://t.me/iqstocker_bot?start=ref_{user_id}
```

**Логика начисления баллов:**
- Баллы начисляются только при покупке PRO или ULTRA подписки рефералом
- Каждая покупка = +1 IQ Балл
- Баллы хранятся в поле `iq_points` таблицы `users`
- Баллы никогда не сгорают


### 5. Интеграция Tribute.tg

**Handler:** `payments.py`
**API Endpoint:** `api/webhooks.py::tribute_webhook`
**Service:** `payment_service.py`

**Продукты:**
- **PRO**: 300₽ / 30 дней
- **ULTRA**: 600₽ / 30 дней

**Флоу оплаты:**
1. Пользователь выбирает тариф
2. Создание Payment с status=PENDING
3. Генерация payment link через Tribute API:
```python
import httpx

async def create_payment_link(amount: int, user_id: int, tier: str) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.tribute.tg/payments",
            headers={"Authorization": f"Bearer {TRIBUTE_API_KEY}"},
            json={
                "amount": amount,
                "currency": "RUB",
                "description": f"IQStocker {tier} подписка",
                "metadata": {
                    "user_id": user_id,
                    "subscription_tier": tier
                },
                "webhook_url": f"{BASE_URL}/api/webhooks/tribute"
            }
        )
        return response.json()["payment_url"]
```
4. Отправка ссылки пользователю
5. Пользователь оплачивает → Tribute отправляет webhook
6. Webhook обработчик:
   - Проверка подписи (HMAC)
   - Обновление Payment status=COMPLETED
   - Активация подписки (обновление User)
   - Обновление Limits
   - Уведомление пользователя

**Webhook payload:**
```json
{
  "event": "payment.succeeded",
  "transaction_id": "trib_abc123",
  "amount": 300,
  "currency": "RUB",
  "metadata": {
    "user_id": 123,
    "subscription_tier": "pro"
  },
  "timestamp": "2024-01-15T10:30:00Z",
  "signature": "hmac_signature_here"
}
```

**Signature verification:**
```python
import hmac
import hashlib

def verify_tribute_signature(payload: bytes, signature: str) -> bool:
    expected = hmac.new(
        TRIBUTE_WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)
```

### 6. Админ-панель (FastAPI)

**Endpoints:**

#### Dashboard
```
GET /admin/
- Общая статистика (пользователи, продажи, рефералы)
- Графики активности
- Последние платежи
```

#### Пользователи
```
GET /admin/users?page=1&limit=50
- Список пользователей с фильтрами. Разделение по  тарифам
- Поиск по telegram_id, username

GET /admin/users/{user_id}
- Детальная информация о пользователе
- История анализов, платежей, рефералов

POST /admin/users/{user_id}/ban
- Забанить пользователя

POST /admin/users/{user_id}/extend-subscription
Body: {"days": 30, "tier": "pro"}
- Продлить подписку вручную
```

#### Аналитика
```
GET /admin/analytics
- Статистика использования
- Топ пользователей по анализам
- Средний CPM по всем пользователям

GET /admin/analytics/reports?user_id=123
- Все отчеты пользователя
```

#### Платежи
```
GET /admin/payments?status=completed&from_date=2024-01-01
- Список платежей с фильтрами
- Сумма за период
- Статистика по тарифам

POST /admin/payments/{payment_id}/refund
- Оформить возврат
```
#### Сообщения
``` В жтом разделе мы имеем доступ ко всем сообщениям и кнопкам из lexicon_ru.py и можем их исправлять и корректировать

#### Рассылки
```
GET /admin/broadcasts
- Список всех рассылок

POST /admin/broadcasts
Body: {
  "message_text": "Привет!",
  "target_subscription": "pro"
}
- Создать рассылку

POST /admin/broadcasts/{broadcast_id}/send
- Запустить рассылку
```

**Аутентификация:**
- Basic Auth или JWT
- ENV переменные: `ADMIN_USERNAME`, `ADMIN_PASSWORD`

**Frontend:**
- Jinja2 templates
- Bootstrap 5 для UI
- HTMX для интерактивности (опционально)

### 7. Проверка подписки на канал

**Handler:** `channel.py`

**Флоу:**
1. При любом действии проверяем подписку
2. Если не подписан → показываем сообщение с кнопкой
3. Пользователь подписывается → нажимает "Проверить"
4. Бот проверяет через `bot.get_chat_member(channel_id, user_id)`
5. Если подписан → продолжение работы
6. Если нет → повторное сообщение

**Middleware:**
```python
class ChannelSubscriptionMiddleware:
    async def __call__(self, handler, event, data):
        user_id = event.from_user.id
        
        try:
            member = await bot.get_chat_member(CHANNEL_ID, user_id)
            if member.status in ["member", "administrator", "creator"]:
                return await handler(event, data)
        except Exception:
            pass
        
        # Не подписан
        await event.answer("Подпишись на канал!")
        return
```

---

## Безопасность и логирование

### Безопасность

**ENV переменные (никогда в коде!):**
```bash
# .env
BOT_TOKEN=123456:ABC-DEF...
DATABASE_URL=postgresql+asyncpg://user:pass@host/db
REDIS_URL=redis://localhost:6379/0
TRIBUTE_API_KEY=trib_key_...
TRIBUTE_WEBHOOK_SECRET=webhook_secret_...
ADMIN_USERNAME=admin
ADMIN_PASSWORD=secure_password_here
SECRET_KEY=random_secret_for_jwt
```

**Валидация webhook:**
- Всегда проверять HMAC signature
- Использовать `hmac.compare_digest()` для защиты от timing attacks

**SQL Injection:**
- SQLModel использует параметризованные запросы автоматически
- Никогда не конкатенировать SQL строки

**Rate Limiting:**
```python
from aiogram.filters import Command
from aiogram import Router

router = Router()

# Лимит: 5 команд в минуту
@router.message(Command("start"), flags={"throttling_key": "default"})
async def start_handler(...):
    ...
```

### Логирование (structlog)

**Конфигурация:**
```python
import structlog

structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer()  # Production
        # structlog.dev.ConsoleRenderer()  # Development
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)
```

**Использование:**
```python
import structlog

logger = structlog.get_logger()

# Structured logging
logger.info(
    "csv_analysis_started",
    user_id=user.id,
    telegram_id=user.telegram_id,
    filename=csv.filename,
    row_count=csv.row_count
)

logger.error(
    "csv_processing_failed",
    user_id=user.id,
    csv_analysis_id=csv.id,
    error=str(e),
    exc_info=True
)
```

**Логирование в JSON (production):**
```json
{
  "event": "csv_analysis_started",
  "user_id": 123,
  "telegram_id": 987654321,
  "filename": "sales_2024.csv",
  "row_count": 5430,
  "timestamp": "2024-01-15T10:30:45.123Z",
  "level": "info"
}
```

---

## Деплой и инфраструктура

### Railway.app Deployment

**Сервисы:**
1. **PostgreSQL** (Railway addon)
2. **Redis** (Railway addon)
3. **Bot** (Python service)
4. **Admin** (Python service)
5. **Worker** (Python service)

**Environment Variables:**
```bash
# Railway автоматически предоставит:
DATABASE_URL=postgresql://...
REDIS_URL=redis://...

# Добавить вручную:
BOT_TOKEN=...
ADMIN_USERNAME=...
ADMIN_PASSWORD=...
TRIBUTE_API_KEY=...
TRIBUTE_WEBHOOK_SECRET=...
SECRET_KEY=...
CHANNEL_ID=-100...
ADMIN_IDS=123456,789012
```

**Procfile (не нужен для Railway, но для справки):**
```
bot: python -m src.bot.main
admin: uvicorn src.admin.main:app --host 0.0.0.0 --port $PORT
worker: arq src.workers.main.WorkerSettings
```

**Railway Services:**

1. **PostgreSQL:**
   - Plan: Developer ($5/mo)
   - Storage: 1GB

2. **Redis:**
   - Plan: Developer ($5/mo)
   - Memory: 100MB

3. **Bot Service:**
   - Build: `poetry install --no-dev`
   - Start: `python -m src.bot.main`
   - Resources: 512MB RAM

4. **Admin Service:**
   - Build: `poetry install --no-dev`
   - Start: `uvicorn src.admin.main:app --host 0.0.0.0 --port $PORT`
   - Resources: 256MB RAM
   - Public URL: Enabled

5. **Worker Service:**
   - Build: `poetry install --no-dev`
   - Start: `arq src.workers.main.WorkerSettings`
   - Resources: 256MB RAM

**Health Checks:**
```python
# src/api/health.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }
```

### Alembic Migrations

**Инициализация:**
```bash
poetry run alembic init alembic
```

**Создание миграции:**
```bash
poetry run alembic revision --autogenerate -m "Initial schema"
```

**Применение миграций:**
```bash
# В Dockerfile.bot (перед запуском)
RUN poetry run alembic upgrade head
```

**alembic.ini (excerpt):**
```ini
[alembic]
script_location = alembic
sqlalchemy.url = ${DATABASE_URL}  # Подставляется из ENV
```

### Docker Compose (локальная разработка)

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_USER: iqstocker
      POSTGRES_PASSWORD: iqstocker
      POSTGRES_DB: iqstocker
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7.2-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  bot:
    build:
      context: .
      dockerfile: Dockerfile.bot
    env_file: .env
    depends_on:
      - postgres
      - redis
    restart: unless-stopped

  admin:
    build:
      context: .
      dockerfile: Dockerfile.admin
    env_file: .env
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis
    restart: unless-stopped

  worker:
    build:
      context: .
      dockerfile: Dockerfile.worker
    env_file: .env
    depends_on:
      - postgres
      - redis
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
```

**Команды:**
```bash
# Запуск всех сервисов
docker compose up -d

# Просмотр логов
docker compose logs -f bot

# Остановка
docker compose down

# Пересборка после изменений
docker compose up -d --build
```

---

## Приложения

### A. ENV переменные (полный список)

```bash
# Bot Configuration
BOT_TOKEN=your_bot_token_here
ADMIN_IDS=123456,789012  # Comma-separated
CHANNEL_ID=-1001234567890

# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/iqstocker
DATABASE_ECHO=false  # Set to true for SQL query logging

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Admin Panel
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your_secure_password
SECRET_KEY=your_random_secret_key_for_jwt

# Tribute.tg
TRIBUTE_API_KEY=trib_key_...
TRIBUTE_WEBHOOK_SECRET=webhook_secret_...
TRIBUTE_MERCHANT_ID=merchant_id_...

# Application
ENVIRONMENT=development  # or production
LOG_LEVEL=INFO
BASE_URL=https://your-domain.railway.app  # For webhooks
```

### B. Poetry Scripts

**pyproject.toml (scripts section):**
```toml
[tool.poetry.scripts]
bot = "src.bot.main:main"
admin = "src.admin.main:main"
worker = "src.workers.main:main"
```

**Использование:**
```bash
poetry run bot      # Запуск бота
poetry run admin    # Запуск админки
poetry run worker   # Запуск воркера
```

### C. Полезные команды

```bash
# Development
poetry install                    # Установка зависимостей
poetry run pytest                 # Запуск тестов
poetry run mypy src/              # Проверка типов
poetry run ruff check src/        # Линтинг
poetry run ruff format src/       # Форматирование

# Database
poetry run alembic revision --autogenerate -m "Message"
poetry run alembic upgrade head
poetry run alembic downgrade -1

# Docker
docker compose up -d              # Запуск сервисов
docker compose logs -f bot        # Просмотр логов бота
docker compose exec postgres psql -U iqstocker  # Подключение к БД
docker compose down -v            # Остановка + удаление volumes
```

---

## Заключение

Этот документ является **единственным источником правды** для проекта IQStocker v2.0. Все изменения архитектуры, моделей данных или функциональности должны быть задокументированы здесь.

Для разработки следуйте **AGENT_PLAN.md**, который содержит пошаговые инструкции реализации с примерами кода.

---

**Версия:** 2.0.0  
**Дата обновления:** 2024-10-30  
**Автор:** IQStocker Team
