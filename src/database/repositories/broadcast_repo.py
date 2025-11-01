"""
Репозиторий для работы с массовыми рассылками
"""

from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from src.database.models import BroadcastMessage, BroadcastStatus, SubscriptionTier
from src.database.repositories.base import BaseRepository


class BroadcastRepository(BaseRepository[BroadcastMessage]):
    """Репозиторий для работы с рассылками"""
    
    def __init__(self):
        super().__init__(BroadcastMessage)
    
    async def get_by_status(
        self,
        session: AsyncSession,
        status: BroadcastStatus,
        limit: int = 50,
    ) -> List[BroadcastMessage]:
        """
        Получить рассылки по статусу
        
        Args:
            session: AsyncSession
            status: Статус рассылки
            limit: Максимальное количество записей
            
        Returns:
            Список рассылок
        """
        statement = (
            select(BroadcastMessage)
            .where(BroadcastMessage.status == status)
            .order_by(desc(BroadcastMessage.created_at))
            .limit(limit)
        )
        result = await session.execute(statement)
        return list(result.scalars().all())
    
    async def get_by_admin(
        self,
        session: AsyncSession,
        admin_id: int,
        limit: int = 50,
    ) -> List[BroadcastMessage]:
        """
        Получить рассылки администратора
        
        Args:
            session: AsyncSession
            admin_id: ID администратора
            limit: Максимальное количество записей
            
        Returns:
            Список рассылок
        """
        statement = (
            select(BroadcastMessage)
            .where(BroadcastMessage.admin_id == admin_id)
            .order_by(desc(BroadcastMessage.created_at))
            .limit(limit)
        )
        result = await session.execute(statement)
        return list(result.scalars().all())
    
    async def update_status(
        self,
        session: AsyncSession,
        broadcast_id: int,
        status: BroadcastStatus,
    ) -> Optional[BroadcastMessage]:
        """
        Обновить статус рассылки
        
        Args:
            session: AsyncSession
            broadcast_id: ID рассылки
            status: Новый статус
            
        Returns:
            Обновленная рассылка или None
        """
        broadcast = await self.get_by_id(session, broadcast_id)
        if broadcast:
            broadcast.status = status
            await session.commit()
            await session.refresh(broadcast)
        return broadcast
    
    async def increment_sent(
        self,
        session: AsyncSession,
        broadcast_id: int,
        count: int = 1,
    ) -> Optional[BroadcastMessage]:
        """
        Увеличить счетчик отправленных сообщений
        
        Args:
            session: AsyncSession
            broadcast_id: ID рассылки
            count: Количество отправленных
            
        Returns:
            Обновленная рассылка или None
        """
        broadcast = await self.get_by_id(session, broadcast_id)
        if broadcast:
            broadcast.sent_count += count
            await session.commit()
            await session.refresh(broadcast)
        return broadcast
    
    async def increment_errors(
        self,
        session: AsyncSession,
        broadcast_id: int,
        count: int = 1,
    ) -> Optional[BroadcastMessage]:
        """
        Увеличить счетчик ошибок
        
        Args:
            session: AsyncSession
            broadcast_id: ID рассылки
            count: Количество ошибок
            
        Returns:
            Обновленная рассылка или None
        """
        broadcast = await self.get_by_id(session, broadcast_id)
        if broadcast:
            broadcast.error_count += count
            await session.commit()
            await session.refresh(broadcast)
        return broadcast

