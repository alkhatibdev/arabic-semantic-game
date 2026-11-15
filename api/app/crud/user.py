"""CRUD operations for User model."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.user import User


class CRUDUser(CRUDBase[User, User, User]):
    """CRUD operations for User model."""

    async def get_by_id(self, db: AsyncSession, user_id: UUID) -> User | None:
        """Get user by UUID."""
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_username(self, db: AsyncSession, username: str) -> User | None:
        """Get user by username."""
        result = await db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    async def get_or_create(
        self, db: AsyncSession, user_id: UUID, username: str | None = None
    ) -> User:
        """Get user by ID or create if doesn't exist."""
        user = await self.get_by_id(db, user_id)
        if not user:
            user = User(id=user_id, username=username)
            db.add(user)
            await db.flush()
            await db.refresh(user)
        return user


user = CRUDUser(User)
