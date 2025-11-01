"""
Аутентификация для админ-панели

Basic Auth для доступа к админ-панели
"""

import secrets
from typing import Optional

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from src.config.logging import get_logger
from src.config.settings import settings

logger = get_logger(__name__)
security = HTTPBasic()


def verify_admin_credentials(credentials: HTTPBasicCredentials = Security(security)) -> bool:
    """
    Проверяет учетные данные администратора
    
    Args:
        credentials: HTTP Basic Auth credentials
        
    Returns:
        True если учетные данные валидны
        
    Raises:
        HTTPException: Если учетные данные неверны
    """
    correct_username = secrets.compare_digest(
        credentials.username, settings.admin.username
    )
    correct_password = secrets.compare_digest(
        credentials.password, settings.admin.password
    )
    
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверные учетные данные",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    return True


def get_admin(credentials: HTTPBasicCredentials = Depends(verify_admin_credentials)) -> dict:
    """
    Получает информацию об администраторе
    
    Args:
        credentials: HTTP Basic Auth credentials
        
    Returns:
        Словарь с информацией об администраторе
    """
    return {
        "username": credentials.username,
        "authenticated": True,
    }

