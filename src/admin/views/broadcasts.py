"""
Broadcasts view для админ-панели

Управление рассылками
"""

from typing import Optional

from aiogram import Bot
from fastapi import APIRouter, Depends, HTTPException

from src.admin.auth import get_admin
from src.admin.models import BroadcastCreateRequest, BroadcastListResponse, BroadcastResponse
from src.config.logging import get_logger
from src.config.settings import settings
from src.database.connection import get_session
from src.database.repositories.broadcast_repo import BroadcastRepository
from src.database.repositories.user_repo import UserRepository
from src.services.broadcast_service import BroadcastService

logger = get_logger(__name__)
router = APIRouter()


@router.get("/", response_model=BroadcastListResponse)
async def get_broadcasts(
    admin: dict = Depends(get_admin),
):
    """Получить список рассылок"""
    async for session in get_session():
        try:
            broadcast_repo = BroadcastRepository()
            broadcasts = await broadcast_repo.get_all(session, limit=100)
            
            return BroadcastListResponse(
                broadcasts=[BroadcastResponse.model_validate(b) for b in broadcasts],
                total=len(broadcasts),
            )
        
        except Exception as e:
            logger.error("broadcasts_list_error", error=str(e), exc_info=True)
            raise HTTPException(status_code=500, detail="Ошибка получения рассылок")
        finally:
            break


@router.post("/", response_model=BroadcastResponse)
async def create_broadcast(
    request: BroadcastCreateRequest,
    admin: dict = Depends(get_admin),
):
    """Создать рассылку"""
    async for session in get_session():
        try:
            broadcast_repo = BroadcastRepository()
            user_repo = UserRepository()
            broadcast_service = BroadcastService(broadcast_repo, user_repo)
            
            # Получаем ID администратора из базы
            admin_user = await user_repo.get_by_telegram_id(session, admin["authenticated_user_id"] if "authenticated_user_id" in admin else 0)
            admin_id = admin_user.id if admin_user else 0
            
            broadcast = await broadcast_service.create_broadcast(
                session,
                admin_id,
                request.message_text,
                request.target_subscription,
            )
            
            return BroadcastResponse.model_validate(broadcast)
        
        except Exception as e:
            logger.error("create_broadcast_error", error=str(e), exc_info=True)
            raise HTTPException(status_code=500, detail="Ошибка создания рассылки")
        finally:
            break


@router.post("/{broadcast_id}/send")
async def send_broadcast(
    broadcast_id: int,
    admin: dict = Depends(get_admin),
):
    """Запустить рассылку"""
    async for session in get_session():
        try:
            broadcast_repo = BroadcastRepository()
            user_repo = UserRepository()
            broadcast_service = BroadcastService(broadcast_repo, user_repo)
            
            # Запускаем рассылку
            broadcast = await broadcast_service.start_broadcast(session, broadcast_id)
            
            if not broadcast:
                raise HTTPException(status_code=404, detail="Рассылка не найдена")
            
            # TODO: Реализовать отправку сообщений через Bot API
            # Получаем получателей
            recipients = await broadcast_service.get_recipients(
                session,
                broadcast.target_subscription,
            )
            
            # Отправляем сообщения (заглушка)
            logger.info(
                "broadcast_started",
                broadcast_id=broadcast_id,
                recipients_count=len(recipients),
            )
            
            return BroadcastResponse.model_validate(broadcast)
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error("send_broadcast_error", error=str(e), exc_info=True)
            raise HTTPException(status_code=500, detail="Ошибка отправки рассылки")
        finally:
            break

