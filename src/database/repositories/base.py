"""
Базовый репозиторий для IQStocker v2.0

Предоставляет базовые CRUD операции для всех репозиториев
"""

from typing import Generic, TypeVar, Type, Optional, List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update
from sqlmodel import SQLModel

ModelType = TypeVar("ModelType", bound=SQLModel)
IdType = int | str


class BaseRepository(Generic[ModelType]):
    """
    Базовый репозиторий с общими CRUD операциями
    
    Все репозитории должны наследоваться от этого класса
    """
    
    def __init__(self, model: Type[ModelType]):
        """
        Инициализация репозитория
        
        Args:
            model: SQLModel класс модели
        """
        self.model = model
    
    async def create(
        self,
        session: AsyncSession,
        obj: ModelType,
    ) -> ModelType:
        """
        Создать новую запись
        
        Args:
            session: AsyncSession
            obj: Объект модели для создания
            
        Returns:
            Созданный объект
        """
        session.add(obj)
        await session.commit()
        await session.refresh(obj)
        return obj
    
    async def get_by_id(
        self,
        session: AsyncSession,
        id: IdType,
    ) -> Optional[ModelType]:
        """
        Получить запись по ID
        
        Args:
            session: AsyncSession
            id: ID записи
            
        Returns:
            Объект модели или None
        """
        result = await session.get(self.model, id)
        return result
    
    async def get_all(
        self,
        session: AsyncSession,
        skip: int = 0,
        limit: int = 100,
    ) -> List[ModelType]:
        """
        Получить все записи с пагинацией
        
        Args:
            session: AsyncSession
            skip: Количество пропущенных записей
            limit: Максимальное количество записей
            
        Returns:
            Список объектов модели
        """
        statement = select(self.model).offset(skip).limit(limit)
        result = await session.execute(statement)
        return list(result.scalars().all())
    
    async def update(
        self,
        session: AsyncSession,
        obj: ModelType,
    ) -> ModelType:
        """
        Обновить запись
        
        Args:
            session: AsyncSession
            obj: Объект модели для обновления
            
        Returns:
            Обновленный объект
        """
        session.add(obj)
        await session.commit()
        await session.refresh(obj)
        return obj
    
    async def delete(
        self,
        session: AsyncSession,
        id: IdType,
    ) -> bool:
        """
        Удалить запись по ID
        
        Args:
            session: AsyncSession
            id: ID записи
            
        Returns:
            True если удалено, False если не найдено
        """
        obj = await self.get_by_id(session, id)
        if obj:
            await session.delete(obj)
            await session.commit()
            return True
        return False
    
    async def count(
        self,
        session: AsyncSession,
    ) -> int:
        """
        Получить количество записей
        
        Args:
            session: AsyncSession
            
        Returns:
            Количество записей
        """
        statement = select(self.model)
        result = await session.execute(statement)
        return len(list(result.scalars().all()))

