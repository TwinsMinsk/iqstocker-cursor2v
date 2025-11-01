"""
Сервис для массовых рассылок

Создание и отправка рассылок пользователям
"""

from datetime import datetime
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.config.logging import get_logger
from src.core.exceptions import UserNotFoundException
from src.database.models import BroadcastMessage, BroadcastStatus, SubscriptionTier
from src.database.repositories.broadcast_repo import BroadcastRepository
from src.database.repositories.user_repo import UserRepository

logger = get_logger(__name__)


class BroadcastService:
    """Сервис для массовых рассылок"""
    
    def __init__(
        self,
        broadcast_repo: BroadcastRepository,
        user_repo: UserRepository,
    ):
        """
        Инициализация сервиса
        
        Args:
            broadcast_repo: Репозиторий рассылок
            user_repo: Репозиторий пользователей
        """
        self.broadcast_repo = broadcast_repo
        self.user_repo = user_repo
    
    async def create_broadcast(
        self,
        session: AsyncSession,
        admin_id: int,
        message_text: str,
        target_subscription: Optional[SubscriptionTier] = None,
    ) -> BroadcastMessage:
        """
        Создать новую рассылку
        
        Args:
            session: AsyncSession
            admin_id: ID администратора
            message_text: Текст сообщения
            target_subscription: Целевая подписка (None = всем)
            
        Returns:
            Созданная рассылка
            
        Raises:
            UserNotFoundException: Администратор не найден
        """
        admin = await self.user_repo.get_by_id(session, admin_id)
        if not admin:
            raise UserNotFoundException(f"Admin {admin_id} not found")
        
        broadcast = BroadcastMessage(
            admin_id=admin_id,
            message_text=message_text,
            target_subscription=target_subscription,
            status=BroadcastStatus.DRAFT,
        )
        
        broadcast = await self.broadcast_repo.create(session, broadcast)
        
        logger.info(
            "broadcast_created",
            broadcast_id=broadcast.id,
            admin_id=admin_id,
            target_subscription=target_subscription.value if target_subscription else None,
        )
        
        return broadcast
    
    async def get_recipients(
        self,
        session: AsyncSession,
        target_subscription: Optional[SubscriptionTier] = None,
    ) -> list:
        """
        Получить список получателей рассылки
        
        Args:
            session: AsyncSession
            target_subscription: Целевая подписка (None = всем активным)
            
        Returns:
            Список пользователей для рассылки
        """
        if target_subscription:
            users = await self.user_repo.get_active_subscriptions(
                session,
                target_subscription,
            )
        else:
            # Все пользователи с активной подпиской
            users = await self.user_repo.get_active_subscriptions(session)
        
        # Исключаем забаненных
        return [u for u in users if not u.is_banned]
    
    async def start_broadcast(
        self,
        session: AsyncSession,
        broadcast_id: int,
    ) -> Optional[BroadcastMessage]:
        """
        Запустить рассылку
        
        Args:
            session: AsyncSession
            broadcast_id: ID рассылки
            
        Returns:
            Обновленная рассылка или None
        """
        broadcast = await self.broadcast_repo.get_by_id(session, broadcast_id)
        if not broadcast:
            return None
        
        broadcast.status = BroadcastStatus.IN_PROGRESS
        broadcast.started_at = datetime.utcnow()
        
        await session.commit()
        await session.refresh(broadcast)
        
        logger.info("broadcast_started", broadcast_id=broadcast_id)
        
        return broadcast
    
    async def complete_broadcast(
        self,
        session: AsyncSession,
        broadcast_id: int,
        sent_count: int,
        error_count: int,
    ) -> Optional[BroadcastMessage]:
        """
        Завершить рассылку
        
        Args:
            session: AsyncSession
            broadcast_id: ID рассылки
            sent_count: Количество отправленных сообщений
            error_count: Количество ошибок
            
        Returns:
            Обновленная рассылка или None
        """
        broadcast = await self.broadcast_repo.get_by_id(session, broadcast_id)
        if not broadcast:
            return None
        
        broadcast.status = BroadcastStatus.COMPLETED
        broadcast.sent_count = sent_count
        broadcast.error_count = error_count
        broadcast.completed_at = datetime.utcnow()
        
        await session.commit()
        await session.refresh(broadcast)
        
        logger.info(
            "broadcast_completed",
            broadcast_id=broadcast_id,
            sent_count=sent_count,
            error_count=error_count,
        )
        
        return broadcast
    
    async def fail_broadcast(
        self,
        session: AsyncSession,
        broadcast_id: int,
        error_message: str,
    ) -> Optional[BroadcastMessage]:
        """
        Пометить рассылку как провалившуюся
        
        Args:
            session: AsyncSession
            broadcast_id: ID рассылки
            error_message: Сообщение об ошибке
            
        Returns:
            Обновленная рассылка или None
        """
        broadcast = await self.broadcast_repo.get_by_id(session, broadcast_id)
        if not broadcast:
            return None
        
        broadcast.status = BroadcastStatus.FAILED
        broadcast.completed_at = datetime.utcnow()
        
        await session.commit()
        await session.refresh(broadcast)
        
        logger.error(
            "broadcast_failed",
            broadcast_id=broadcast_id,
            error_message=error_message,
        )
        
        return broadcast

