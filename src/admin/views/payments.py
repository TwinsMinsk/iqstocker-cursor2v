"""
Payments view для админ-панели

Управление платежами
"""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from src.admin.auth import get_admin
from src.admin.models import PaymentListResponse, PaymentResponse
from src.config.logging import get_logger
from src.core.exceptions import PaymentException
from src.database.connection import get_session
from src.database.models import PaymentStatus
from src.database.repositories.payment_repo import PaymentRepository
from src.services.payment_service import PaymentService

logger = get_logger(__name__)
router = APIRouter()


@router.get("/", response_model=PaymentListResponse)
async def get_payments(
    status: Optional[PaymentStatus] = Query(None),
    from_date: Optional[str] = Query(None),
    to_date: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    admin: dict = Depends(get_admin),
):
    """Получить список платежей"""
    async for session in get_session():
        try:
            payment_repo = PaymentRepository()
            
            # Получаем платежи
            if status:
                payments = await payment_repo.get_by_status(session, status, limit=10000)
            else:
                payments = await payment_repo.get_all(session, limit=10000)
            
            # Фильтруем по датам
            if from_date:
                from_date_obj = datetime.fromisoformat(from_date)
                payments = [
                    p for p in payments
                    if p.created_at >= from_date_obj
                ]
            
            if to_date:
                to_date_obj = datetime.fromisoformat(to_date)
                payments = [
                    p for p in payments
                    if p.created_at <= to_date_obj
                ]
            
            # Подсчитываем общий доход
            total_revenue = sum(p.amount for p in payments if p.status == PaymentStatus.COMPLETED) / 100
            
            # Пагинация
            total = len(payments)
            start = (page - 1) * limit
            end = start + limit
            payments_page = payments[start:end]
            
            return PaymentListResponse(
                payments=[PaymentResponse.model_validate(p) for p in payments_page],
                total=total,
                total_revenue=total_revenue,
                page=page,
                limit=limit,
            )
        
        except Exception as e:
            logger.error("payments_list_error", error=str(e), exc_info=True)
            raise HTTPException(status_code=500, detail="Ошибка получения платежей")
        finally:
            break


@router.post("/{payment_id}/refund")
async def refund_payment(
    payment_id: int,
    admin: dict = Depends(get_admin),
):
    """Оформить возврат платежа"""
    async for session in get_session():
        try:
            payment_repo = PaymentRepository()
            payment_service = PaymentService(payment_repo)
            
            payment = await payment_service.refund_payment(session, payment_id)
            
            if not payment:
                raise HTTPException(status_code=404, detail="Платеж не найден")
            
            return PaymentResponse.model_validate(payment)
        
        except PaymentException as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error("refund_payment_error", error=str(e), exc_info=True)
            raise HTTPException(status_code=500, detail="Ошибка возврата платежа")
        finally:
            break

