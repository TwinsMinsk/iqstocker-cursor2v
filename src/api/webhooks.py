"""
Webhook handlers для IQStocker v2.0

Обработка webhook'ов от Tribute.tg
"""

from fastapi import APIRouter, Depends, HTTPException, Header, Request
from fastapi.responses import JSONResponse

from src.config.logging import get_logger
from src.config.settings import settings
from src.database.connection import get_session
from src.database.repositories.payment_repo import PaymentRepository
from src.database.repositories.user_repo import UserRepository
from src.database.repositories.limits_repo import LimitsRepository
from src.services.payment_service import PaymentService
from src.services.user_service import UserService
from src.services.referral_service import ReferralService

logger = get_logger(__name__)
router = APIRouter()


@router.post("/tribute")
async def tribute_webhook(
    request: Request,
    x_signature: str | None = Header(None, alias="X-Signature"),
):
    """
    Обработчик webhook от Tribute.tg
    
    Args:
        request: FastAPI Request
        x_signature: Подпись из заголовка X-Signature
    """
    try:
        # Получаем тело запроса
        payload = await request.body()
        
        # Парсим JSON
        import json
        data = json.loads(payload.decode('utf-8'))
        
        # Проверяем подпись
        payment_service = PaymentService(PaymentRepository())
        if not payment_service.verify_tribute_signature(payload, x_signature or ""):
            logger.warning("tribute_signature_invalid", signature=x_signature)
            raise HTTPException(status_code=401, detail="Неверная подпись")
        
        # Проверяем тип события
        event_type = data.get("event")
        if event_type != "payment.succeeded":
            logger.info("tribute_event_ignored", event_type=event_type)
            return JSONResponse({"status": "ok", "message": "Event ignored"})
        
        # Обрабатываем платеж
        async for session in get_session():
            try:
                transaction_id = data.get("transaction_id")
                amount = data.get("amount", 0)
                metadata = data.get("metadata", {})
                
                user_id = metadata.get("user_id")
                subscription_tier = metadata.get("subscription_tier")
                
                if not user_id or not subscription_tier:
                    logger.error("tribute_webhook_invalid_metadata", metadata=metadata)
                    raise HTTPException(status_code=400, detail="Неверные метаданные")
                
                # Обрабатываем платеж
                payment = await payment_service.process_payment_webhook(
                    session,
                    transaction_id,
                    amount,
                    metadata,
                )
                
                if payment:
                    # Активируем подписку
                    user_repo = UserRepository()
                    limits_repo = LimitsRepository()
                    user_service = UserService(user_repo, limits_repo)
                    
                    from src.database.models import SubscriptionTier
                    tier = SubscriptionTier(subscription_tier)
                    
                    await user_service.activate_subscription(
                        session,
                        payment.user_id,
                        tier,
                        payment.subscription_days,
                    )
                    
                    # Начисляем реферальные баллы
                    user = await user_repo.get_by_id(session, payment.user_id)
                    if user and user.referrer_id:
                        referral_service = ReferralService(user_repo)
                        if tier in [SubscriptionTier.PRO, SubscriptionTier.ULTRA]:
                            await referral_service.award_referral_points(
                                session,
                                user.referrer_id,
                            )
                    
                    logger.info(
                        "payment_processed",
                        payment_id=payment.id,
                        user_id=payment.user_id,
                        tier=subscription_tier,
                    )
                
                return JSONResponse({"status": "ok", "message": "Payment processed"})
            
            except Exception as e:
                logger.error("tribute_webhook_error", error=str(e), exc_info=True)
                raise HTTPException(status_code=500, detail="Ошибка обработки платежа")
            finally:
                break
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("tribute_webhook_error", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail="Ошибка обработки webhook")

