from typing import Optional, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_
from app.models.users import User
from app.core.enums import Department


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: int) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalars().first()

    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalars().first()

    async def create(self, user: User) -> User:
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def update(self, user: User) -> User:
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def delete(self, user: User) -> None:
        await self.db.delete(user)
        await self.db.commit()

    async def get_users(self, query: Optional[str] = None, department: Optional[Department] = None) -> Sequence[User]:
        stmt = select(User)
        filters = []
        if query:
            filters.append(or_(User.email.contains(query), User.name.contains(query)))
        if department:
            filters.append(User.department == department)

        if filters:
            stmt = stmt.where(*filters)

        result = await self.db.execute(stmt)
        return result.scalars().all()
