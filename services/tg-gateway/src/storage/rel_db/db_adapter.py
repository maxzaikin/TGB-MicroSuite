"""
file: TGB-MicroSuite/services/tg-gateway/src/storage/rel_db/db_adapter.py

Database adapter for asynchronous SQLAlchemy engine and session management.

This module provides a centralized way to configure and interact with the
application's database. It defines a base declarative model and an adapter
class that manages the lifecycle of the database engine and sessions.
"""

from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from core.config import settings


class Model(DeclarativeBase):
    r"""
    A base model class for all SQLAlchemy ORM models.

    This class provides a shared `metadata` object with a predefined naming
    convention for db constraints (indexes, unique constraints, foreign keys, etc.)
    Using a consistent naming convention is crucial for reliable Alembic
    auto-generation of migrations.

    All application models should inherit from this class.

    Wiki: https://github.com/maxzaikin/TGB-MicroSuite/wiki/DOC‐DeclarativeBase
    """

    metadata = MetaData(
        naming_convention={
            "ix": "ix_%(column_0_label)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s",
        }
    )


class DBAdapter:
    """
    Manages the database engine and provides asynchronous sessions.

    This class acts as a singleton-like manager for the database connection.
    It reads the database URL from the central configuration, creates an
    async engine, and provides a session factory for use throughout the application,
    typically via dependency injection.

    Attributes:
        engine (AsyncEngine): The SQLAlchemy asynchronous engine instance.
        session_factory (async_sessionmaker[AsyncSession]): A factory for creating
            new asynchronous sessions.
    """

    engine: AsyncEngine
    session_factory: async_sessionmaker[AsyncSession]

    def __init__(self) -> None:
        """
        Initializes the DBAdapter.

        Reads the database URL from the global settings, creates the async engine,
        and sets up the session factory.
        """
        self.db_url = settings.DATABASE_URL

        # Create the async engine. `echo=False` is recommended for production
        # and cleaner development logs.
        self.engine = create_async_engine(self.db_url, echo=False)

        # Create a session factory that will produce new sessions.
        self.session_factory = async_sessionmaker(
            bind=self.engine, expire_on_commit=False
        )

    async def get_session(self) -> AsyncSession:
        """
        Provides a new asynchronous database session.

        This method should be used as a dependency to inject a session
        into services or handlers that need database access.

        Returns:
            AsyncSession: An active SQLAlchemy async session.
        """
        return self.session_factory()

    async def create_all_tables(self) -> None:
        """
        Creates all database tables defined in the metadata.

        This method is useful for initial setup or testing environments.
        It connects to the database and issues CREATE TABLE statements for all
        tables that do not yet exist. In production, schema changes should be
        managed by Alembic migrations.
        """
        async with self.engine.begin() as conn:
            await conn.run_sync(Model.metadata.create_all)

    async def close(self) -> None:
        """
        Gracefully disposes of the database engine's connection pool.

        This should be called during the application's shutdown sequence
        to release all database connections.
        """
        if self.engine:
            await self.engine.dispose()
