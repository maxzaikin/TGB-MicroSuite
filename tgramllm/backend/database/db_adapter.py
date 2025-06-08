"""
tgramllm/src/database/db_adapter.py

Database adapter module for asynchronous SQLAlchemy engine and session handling.

This module includes:
- A base declarative model class with naming conventions.
- A database adapter class for managing asynchronous sessions.
- A utility method for initializing SQLAlchemy relationships.
"""

from pathlib import Path
from typing import Union
from dotenv import load_dotenv
from sqlalchemy import (
    MetaData,
    inspect
)
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker
)
from sqlalchemy.orm import DeclarativeBase

from src.core.config import settings


class Model(DeclarativeBase):
    """Base model class with custom naming conventions for SQLAlchemy constraints and indexes.

    This class serves as the declarative base for all ORM models in the application.
    Naming conventions ensure compatibility with Alembic migrations and database constraints.

    More info: https://github.com/maxzaikin/TgramBuddy/wiki/DOC%E2%80%90DeclarativeBase
    """

    metadata = MetaData(
        naming_convention={
            'ix': 'ix_%(column_0_label)s',
            'uq': 'uq_%(table_name)s_%(column_0_name)s',
            'ck': 'ck_%(table_name)s_%(constraint_name)s',
            'fk': 'fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s',
            'pk': 'pk_%(table_name)s'
        }
    )


class DBAdapter:
    """Database adapter for handling async database sessions using SQLAlchemy.

    Supports only SQLite for now. Handles creation of engine and async sessions.

    Attributes:
        db_engine (str): The type of database engine ('sqlite' supported).
        db_url (Union[str, URL, None]): Database connection URL.
        engine: SQLAlchemy async engine.
        session: SQLAlchemy async session maker.
    """

    def __init__(self, db_engine: str = 'sqlite'):
        """Initializes the DBAdapter with the specified database engine.

        Args:
            db_engine (str): The database engine to use (default is 'sqlite').

        Raises:
            ValueError: If the specified database engine is not supported.
        """
        env_path = Path(__file__).parent.parent.parent / '.env'
        load_dotenv(dotenv_path=env_path)

        self.db_engine = db_engine

        if db_engine == 'sqlite':
            self.db_url: Union[str, URL, None] = settings.get_db_path()
            self.engine = create_async_engine(self.db_url, echo=True)
            self.session = async_sessionmaker(self.engine, expire_on_commit=False)
        else:
            raise ValueError(f"Unsupported database engine: {db_engine}")

    async def get_session(self):
        """Creates and returns an async database session.

        Returns:
            AsyncSession: An instance of SQLAlchemy async session.

        Raises:
            ValueError: If the database engine is unsupported.
        """
        if self.db_engine == 'sqlite':
            return self.session()
        else:
            raise ValueError(f"Unsupported database engine: {self.db_engine}")

    async def close(self):
        """Closes the database engine connection.

        Raises:
            ValueError: If the database engine is unsupported.
        """
        if self.db_engine == 'sqlite' and self.engine:
            await self.engine.dispose()
        else:
            raise ValueError(f"Unsupported database engine: {self.db_engine}")

    def init_relationships(self, tgt, kwargs):
        """Initializes default relationship attributes for a model instance.

        This method inspects the relationships defined on the model class,
        and for each relationship that is missing in the provided kwargs,
        it sets a default value:
        - `None` for scalar relationships,
        - An empty collection for `uselist=True` relationships.

        Args:
            tgt: The target model instance.
            kwargs (dict): The constructor arguments for the model instance.
        """
        mapper = inspect(tgt.__class__)

        for rel in mapper.relationships:
            if rel.collection_class is None and rel.uselist:
                continue
            if rel.key not in kwargs:
                default_value = None if not rel.uselist else rel.collection_class()
                kwargs.setdefault(rel.key, default_value)
