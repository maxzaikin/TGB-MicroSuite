# src/core/container.py

from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as redis

from .config import get_settings
from .services.auth_service import AuthService
from storage.rel_db.db_adapter import DBAdapter
from agent import engine as rag_engine


class AppContainer(containers.DeclarativeContainer):
    config = providers.Singleton(get_settings)
    db_adapter = providers.Resource(DBAdapter)
    
    db_session_provider = providers.Factory(db_adapter.provided.get_session)   
    
    ai_services_tuple = providers.Singleton(rag_engine.initialize_ai_services)
    redis_client = providers.Resource(redis.from_url,
                                      url=config.provided.REDIS_URL,
                                      encoding="utf-8",
                                      decode_responses=True) 
    rag_engine_provider = providers.Singleton(
        lambda s: s[0], 
        s=ai_services_tuple,
    )
     
    memory_service_provider = providers.Singleton(
        lambda s: s[1], 
        s=ai_services_tuple,
    )
    
    auth_service = providers.Singleton(AuthService,
                                       secret_key=config.provided.SECRET_KEY,
                                       algorithm=config.provided.ALGORITHM,
                                       expire_minutes=config.provided.ACCESS_TOKEN_EXPIRE_MINUTES)
                                     