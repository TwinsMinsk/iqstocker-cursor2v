"""
Репозиторий для работы с системными сообщениями
"""

from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.database.models import SystemMessage, MessageType, MessagePriority
from src.database.repositories.base import BaseRepository


class SystemMessageRepository(BaseRepository[SystemMessage]):
    """Репозиторий для работы с системными сообщениями"""
    
    def __init__(self):
        super().__init__(SystemMessage)
    
    async def get_active(
        self,
        session: AsyncSession,
    ) -> List[SystemMessage]:
        """
        Получить все активные системные сообщения
        
        Args:
            session: AsyncSession
            
        Returns:
            Список активных сообщений
        """
        statement = select(SystemMessage).where(
            SystemMessage.is_active == True
        )
        result = await session.execute(statement)
        return list(result.scalars().all())
    
    async def get_by_type(
        self,
        session: AsyncSession,
        message_type: MessageType,
    ) -> List[SystemMessage]:
        """
        Получить сообщения по типу
        
        Args:
            session: AsyncSession
            message_type: Тип сообщения
            
        Returns:
            Список сообщений
        """
        statement = select(SystemMessage).where(
            SystemMessage.message_type == message_type,
            SystemMessage.is_active == True,
        )
        result = await session.execute(statement)
        return list(result.scalars().all())
    
    async def get_by_priority(
        self,
        session: AsyncSession,
        priority: MessagePriority,
    ) -> List[SystemMessage]:
        """
        Получить сообщения по приоритету
        
        Args:
            session: AsyncSession
            priority: Приоритет сообщения
            
        Returns:
            Список сообщений
        """
        statement = select(SystemMessage).where(
            SystemMessage.priority == priority,
            SystemMessage.is_active == True,
        )
        result = await session.execute(statement)
        return list(result.scalars().all())

