"""
Users view для админ-панели

Управление пользователями
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from src.admin.auth import get_admin
from src.admin.models import (
    BanUserRequest,
    ExtendSubscriptionRequest,
    UserListResponse,
    UserResponse,
)
from src.config.logging import get_logger
from src.core.exceptions import UserNotFoundException
from src.database.connection import get_session
from src.database.models import SubscriptionTier
from src.database.repositories.user_repo import UserRepository
from src.services.user_service import UserService
from src.database.repositories.limits_repo import LimitsRepository

logger = get_logger(__name__)
router = APIRouter()


@router.get("/", response_model=UserListResponse)
async def get_users(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    subscription_tier: Optional[SubscriptionTier] = Query(None),
    search: Optional[str] = Query(None),
    admin: dict = Depends(get_admin),
):
    """Получить список пользователей"""
    async for session in get_session():
        try:
            user_repo = UserRepository()
            
            # Получаем всех пользователей
            all_users = await user_repo.get_all(session, limit=10000)
            
            # Фильтруем по подписке
            if subscription_tier:
                all_users = [u for u in all_users if u.subscription_tier == subscription_tier]
            
            # Поиск по telegram_id или username
            if search:
                try:
                    search_id = int(search)
                    all_users = [u for u in all_users if u.telegram_id == search_id]
                except ValueError:
                    all_users = [
                        u for u in all_users
                        if search.lower() in (u.username or "").lower()
                    ]
            
            # Пагинация
            total = len(all_users)
            start = (page - 1) * limit
            end = start + limit
            users_page = all_users[start:end]
            
            return UserListResponse(
                users=[UserResponse.model_validate(u) for u in users_page],
                total=total,
                page=page,
                limit=limit,
            )
        
        except Exception as e:
            logger.error("users_list_error", error=str(e), exc_info=True)
            raise HTTPException(status_code=500, detail="Ошибка получения пользователей")
        finally:
            break


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    admin: dict = Depends(get_admin),
):
    """Получить детальную информацию о пользователе"""
    async for session in get_session():
        try:
            user_repo = UserRepository()
            user = await user_repo.get_by_id(session, user_id)
            
            if not user:
                raise HTTPException(status_code=404, detail="Пользователь не найден")
            
            return UserResponse.model_validate(user)
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error("user_detail_error", error=str(e), exc_info=True)
            raise HTTPException(status_code=500, detail="Ошибка получения пользователя")
        finally:
            break


@router.post("/{user_id}/ban")
async def ban_user(
    user_id: int,
    request: BanUserRequest,
    admin: dict = Depends(get_admin),
):
    """Забанить пользователя"""
    async for session in get_session():
        try:
            user_repo = UserRepository()
            limits_repo = LimitsRepository()
            user_service = UserService(user_repo, limits_repo)
            
            user = await user_service.ban_user(session, user_id)
            
            return UserResponse.model_validate(user)
        
        except UserNotFoundException:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        except Exception as e:
            logger.error("ban_user_error", error=str(e), exc_info=True)
            raise HTTPException(status_code=500, detail="Ошибка блокировки пользователя")
        finally:
            break


@router.post("/{user_id}/extend-subscription")
async def extend_subscription(
    user_id: int,
    request: ExtendSubscriptionRequest,
    admin: dict = Depends(get_admin),
):
    """Продлить подписку пользователю"""
    async for session in get_session():
        try:
            user_repo = UserRepository()
            limits_repo = LimitsRepository()
            user_service = UserService(user_repo, limits_repo)
            
            user = await user_service.activate_subscription(
                session,
                user_id,
                request.tier,
                request.days,
            )
            
            return UserResponse.model_validate(user)
        
        except UserNotFoundException:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        except Exception as e:
            logger.error("extend_subscription_error", error=str(e), exc_info=True)
            raise HTTPException(status_code=500, detail="Ошибка продления подписки")
        finally:
            break

