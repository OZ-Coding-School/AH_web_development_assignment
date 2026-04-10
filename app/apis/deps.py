from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db.databases import async_get_db
from app.core.security import decode_token
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService
from app.models.users import User
from app.core.enums import UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/users/login")


async def get_user_service(db: AsyncSession = Depends(async_get_db)) -> UserService:
    user_repo = UserRepository(db)
    return UserService(user_repo)


async def get_current_user(
    token: str = Depends(oauth2_scheme), user_service: UserService = Depends(get_user_service)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="인증 정보가 유효하지 않습니다.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_token(token)
    user_id: Optional[int] = payload.get("user_id")
    if user_id is None:
        raise credentials_exception

    user = await user_service.get_me(user_id)
    if user is None:
        raise credentials_exception
    return user


async def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="관리자 권한이 필요합니다.")
    return current_user
