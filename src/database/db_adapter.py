import os
from pathlib import Path
from typing import Union
from dotenv import load_dotenv
from sqlalchemy import (
    MetaData, 
    event, 
    inspect
)
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.asyncio import (
    create_async_engine, 
    async_sessionmaker
)
from sqlalchemy.orm import DeclarativeBase

class Model(DeclarativeBase):
    """Model _summary_
    DOC‐DeclarativeBase: See the the description:
    https://github.com/maxzaikin/TgramBuddy/wiki/DOC%E2%80%90DeclarativeBase
    
    Configure naming conventions for indexes and constraints

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
    def __init__(self, db_engine: str = 'sqlite'):
        env_path = Path(__file__).parent.parent.parent / '.env'
        load_dotenv(dotenv_path=env_path)

        self.db_engine = db_engine
        if db_engine == 'sqlite':
            self.db_url: Union[str,URL,None]= os.getenv('ASYNCSQLITE_DB_URL')
            self.engine = create_async_engine(self.db_url, echo=True )
            self.session = async_sessionmaker(self.engine, expire_on_commit=False)        
        else:
            raise ValueError(f"Unsupported database engine: {db_engine}")

    async def get_session(self):
        if self.db_engine == 'sqlite':
            return self.session()
        else:
            raise ValueError(f"Unsupported database engine: {self.db_engine}")

    async def close(self):
        if self.db_engine == 'sqlite' and self.engine:
            await self.engine.dispose()        
        else:
            raise ValueError(f"Unsupported database engine: {self.db_engine}")

    @event.listens_for(Model, "init", propagate=True)
    def init_relationships(self, tgt, arg, kw):
        mapper = inspect(tgt.__class__)
        
        for arg in mapper.relationships:
            if arg.collection_class is None and arg.uselist:
                continue
            if arg.key not in kw:
                kw.setdefault(arg.key, None if not arg.uselist else arg.collection_class())