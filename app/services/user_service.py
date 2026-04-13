from typing import Optional, Sequence
from fastapi import HTTPException, status
from app.models.users import User
from app.repositories.user_repository import UserRepository
from app.schemas.users import UserCreate, UserUpdate, UserLogin, PasswordUpdate, AdminUserRoleUpdate
from app.core.security import get_password_hash, verify_password, create_access_token, create_refresh_token
from app.core.enums import Department, UserRole


class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def signup(self, user_create: UserCreate) -> User:
        db_user = await self.user_repo.get_by_email(user_create.email)
        if db_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="이미 등록된 이메일입니다.")

        hashed_password = get_password_hash(user_create.password)
        new_user = User(
            email=user_create.email,
            hashed_password=hashed_password,
            name=user_create.name,
            department=user_create.department,
            gender=user_create.gender,
            phone_number=user_create.phone_number,
            role=UserRole.PENDING,
            is_active=True,
        )
        return await self.user_repo.create(new_user)

    async def login(self, user_login: UserLogin) -> dict:
        user = await self.user_repo.get_by_email(user_login.email)
        if not user or not verify_password(user_login.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="이메일 또는 비밀번호가 올바르지 않습니다."
            )

        access_token = create_access_token(data={"user_id": user.id})
        refresh_token = create_refresh_token(data={"user_id": user.id})

        return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

    async def get_me(self, user_id: int) -> User:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="사용자를 찾을 수 없습니다.")
        return user

    async def update_me(self, user_id: int, user_update: UserUpdate) -> User:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="사용자를 찾을 수 없습니다.")

        if user_update.department is not None:
            user.department = user_update.department
        if user_update.phone_number is not None:
            user.phone_number = user_update.phone_number

        return await self.user_repo.update(user)

    async def delete_me(self, user_id: int) -> None:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="사용자를 찾을 수 없습니다.")
        await self.user_repo.delete(user)

    async def get_users_for_admin(
        self, query: Optional[str] = None, department: Optional[Department] = None
    ) -> Sequence[User]:
        return await self.user_repo.get_users(query=query, department=department)

    async def update_user_role(self, role_update: AdminUserRoleUpdate) -> User:
        user = await self.user_repo.get_by_id(role_update.user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="해당 사용자를 찾을 수 없습니다.")

        user.role = role_update.new_role
        return await self.user_repo.update(user)

    async def update_password(self, user_id: int, password_update: PasswordUpdate) -> None:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="해당 사용자를 찾을 수 없습니다.")

        if verify_password(password_update.current_password, user.hashed_passwords):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="현재 비밀번호가 일치하지 않습니다.")

        hashed_password = get_password_hash(password_update.new_password)
        user.password = hashed_password
        await self.user_repo.update(user)
