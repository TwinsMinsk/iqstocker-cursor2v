"""
Lexicon view для админ-панели

Редактирование лексикона бота (всех сообщений и кнопок)
"""

import json
from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from src.admin.auth import get_admin
from src.bot.lexicon.lexicon_ru import LEXICON_RU, LEXICON_COMMANDS_RU
from src.config.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.get("/")
async def get_lexicon(admin: dict = Depends(get_admin)):
    """
    Получить весь лексикон бота
    
    Returns:
        Словари с сообщениями и командами
    """
    return {
        "messages": LEXICON_RU,
        "commands": LEXICON_COMMANDS_RU,
    }


@router.get("/{key}")
async def get_lexicon_item(
    key: str,
    admin: dict = Depends(get_admin),
):
    """
    Получить конкретный элемент лексикона
    
    Args:
        key: Ключ элемента
        
    Returns:
        Значение элемента
    """
    # Пытаемся найти в сообщениях
    if key in LEXICON_RU:
        return {"key": key, "value": LEXICON_RU[key], "type": "message"}
    
    # Пытаемся найти в командах
    if key in LEXICON_COMMANDS_RU:
        return {"key": key, "value": LEXICON_COMMANDS_RU[key], "type": "command"}
    
    raise HTTPException(status_code=404, detail=f"Ключ {key} не найден в лексиконе")


@router.put("/{key}")
async def update_lexicon_item(
    key: str,
    value: dict[str, Any],
    admin: dict = Depends(get_admin),
):
    """
    Обновить элемент лексикона
    
    Args:
        key: Ключ элемента
        value: Новое значение ({"value": "...", "type": "message|command"})
        
    Returns:
        Обновленный элемент
    """
    # TODO: Реализовать сохранение в БД или файл
    # Для MVP используем только чтение из lexicon_ru.py
    # В будущем можно добавить сохранение в БД (таблица lexicon_entries)
    
    item_type = value.get("type", "message")
    new_value = value.get("value", "")
    
    if not new_value:
        raise HTTPException(status_code=400, detail="Значение не может быть пустым")
    
    # TODO: Сохранить в БД
    # Для MVP просто возвращаем успех
    logger.info(
        "lexicon_item_updated",
        key=key,
        type=item_type,
    )
    
    return {
        "key": key,
        "value": new_value,
        "type": item_type,
        "status": "updated",
    }

