"""
User service for database operations
"""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import verify_password
from app.models.database import User


async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    """Get user by username"""
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


async def authenticate_user(
    db: AsyncSession, username: str, password: str
) -> Optional[User]:
    """Authenticate user with username and password"""
    user = await get_user_by_username(db, username)

    if not user:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    return user
