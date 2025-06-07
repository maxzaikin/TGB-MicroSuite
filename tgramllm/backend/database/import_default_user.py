"""
tgramllm/src/database/import_default_user.py
"""
import asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import (
    AsyncSession, 
    create_async_engine
)
from passlib.context import CryptContext

from backend.database.models import User
from backend.llm.core.config import settings

DATABASE_URL = settings.ASYNCSQLITE_DB_URL

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_default_user():
    """
    Import default user
    """
    engine = create_async_engine(DATABASE_URL)
    async with AsyncSession(engine) as session:
        result = await session.execute(
            select(User).where(User.email == settings.DEFAULT_USER_EMAIL)
        )
        user = result.scalar_one_or_none()
        
        if user:
            print(f"Default user {settings.DEFAULT_USER_EMAIL} already exists")
        else:
            hashed_password = pwd_context.hash(settings.DEFAULT_USER_PASSWORD)
            user = User(email=settings.DEFAULT_USER_EMAIL, hashed_password=hashed_password)
            session.add(user)
            await session.commit()
            print(f"Created default user: {settings.DEFAULT_USER_EMAIL}")

if __name__ == "__main__":
    asyncio.run(create_default_user())
