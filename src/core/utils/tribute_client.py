"""
Клиент для Tribute.tg API

Работа с платежным API Tribute.tg
"""

import hmac
import hashlib
from typing import Any

import httpx

from src.config.logging import get_logger
from src.config.settings import settings
from src.core.exceptions import PaymentException

logger = get_logger(__name__)


class TributeClient:
    """Клиент для работы с Tribute.tg API"""
    
    def __init__(self, api_key: str, base_url: str = "https://api.tribute.tg"):
        """
        Инициализация клиента
        
        Args:
            api_key: API ключ Tribute.tg
            base_url: Базовый URL API (по умолчанию https://api.tribute.tg)
        """
        self.api_key = api_key
        self.base_url = base_url
    
    async def create_payment(
        self,
        amount: int,
        currency: str,
        description: str,
        metadata: dict[str, Any],
        webhook_url: str,
    ) -> dict[str, Any]:
        """
        Создать платеж через Tribute.tg
        
        Args:
            amount: Сумма платежа в копейках
            currency: Валюта (RUB)
            description: Описание платежа
            metadata: Метаданные платежа
            webhook_url: URL для webhook
            
        Returns:
            Словарь с информацией о платеже
            
        Raises:
            PaymentException: Ошибка создания платежа
        """
        # Если API ключ заглушка, возвращаем тестовые данные
        if self.api_key == "placeholder":
            logger.warning("tribute_api_key_placeholder")
            return {
                "transaction_id": f"test_{hash(str(metadata))}",
                "payment_url": f"{settings.app.base_url}/payment/test/{metadata.get('payment_id', 'test')}",
                "status": "pending",
            }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/payments",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "amount": amount,
                        "currency": currency,
                        "description": description,
                        "metadata": metadata,
                        "webhook_url": webhook_url,
                    },
                )
                
                if response.status_code != 200:
                    error_text = response.text
                    logger.error(
                        "tribute_api_error",
                        status_code=response.status_code,
                        error=error_text,
                    )
                    raise PaymentException(
                        f"Ошибка создания платежа в Tribute.tg: {error_text}"
                    )
                
                data = response.json()
                logger.info(
                    "tribute_payment_created",
                    transaction_id=data.get("transaction_id"),
                )
                
                return data
        
        except httpx.HTTPError as e:
            logger.error("tribute_http_error", error=str(e), exc_info=True)
            raise PaymentException(f"Ошибка HTTP при создании платежа: {str(e)}")
        except Exception as e:
            logger.error("tribute_payment_error", error=str(e), exc_info=True)
            raise PaymentException(f"Ошибка создания платежа: {str(e)}")
    
    def verify_signature(
        self,
        payload: bytes,
        signature: str,
        secret: str,
    ) -> bool:
        """
        Проверить подпись webhook
        
        Args:
            payload: Тело запроса
            signature: Подпись из заголовка
            secret: Секретный ключ для проверки
            
        Returns:
            True если подпись валидна
        """
        if secret == "placeholder":
            logger.warning("tribute_webhook_secret_placeholder")
            return True  # Для тестирования
        
        expected = hmac.new(
            secret.encode(),
            payload,
            hashlib.sha256,
        ).hexdigest()
        
        return hmac.compare_digest(expected, signature)

