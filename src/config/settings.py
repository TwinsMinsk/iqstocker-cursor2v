"""
Настройки приложения IQStocker v2.0

Использует Pydantic Settings для загрузки переменных окружения
"""

from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class BotSettings(BaseSettings):
    """Настройки Telegram бота"""
    
    model_config = SettingsConfigDict(env_prefix="BOT_", env_file=".env", extra="ignore")
    
    token: str
    admin_ids: str  # Comma-separated
    channel_id: str
    
    def get_admin_ids(self) -> List[int]:
        """Парсит admin_ids из строки в список"""
        return [int(id_.strip()) for id_ in self.admin_ids.split(",") if id_.strip()]


class DatabaseSettings(BaseSettings):
    """Настройки базы данных"""
    
    model_config = SettingsConfigDict(env_prefix="DATABASE_", env_file=".env", extra="ignore")
    
    url: str
    echo: bool = False


class RedisSettings(BaseSettings):
    """Настройки Redis"""
    
    model_config = SettingsConfigDict(env_prefix="REDIS_", env_file=".env", extra="ignore")
    
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    
    def get_url(self) -> str:
        """Возвращает URL для подключения к Redis"""
        return f"redis://{self.host}:{self.port}/{self.db}"


class AdminSettings(BaseSettings):
    """Настройки админ-панели"""
    
    model_config = SettingsConfigDict(env_prefix="ADMIN_", env_file=".env", extra="ignore")
    
    username: str
    password: str


class TributeSettings(BaseSettings):
    """Настройки Tribute.tg"""
    
    model_config = SettingsConfigDict(env_prefix="TRIBUTE_", env_file=".env", extra="ignore")
    
    api_key: str = "placeholder"
    webhook_secret: str = "placeholder"
    merchant_id: str | None = None
    base_url: str = "https://api.tribute.tg"


class AppSettings(BaseSettings):
    """Настройки приложения"""
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    
    environment: str = "development"
    log_level: str = "INFO"
    secret_key: str
    base_url: str = "http://localhost:8000"


class Settings:
    """Главный класс настроек"""
    
    def __init__(self):
        self.bot = BotSettings()
        self.database = DatabaseSettings()
        self.redis = RedisSettings()
        self.admin = AdminSettings()
        self.tribute = TributeSettings()
        self.app = AppSettings()


# Глобальный экземпляр настроек
settings = Settings()

