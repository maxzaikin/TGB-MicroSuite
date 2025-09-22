from dependency_injector import containers, providers
from .config import get_settings
from .services.auth_service import AuthService

class AppContainer(containers.DeclarativeContainer):
    config = providers.Singleton(get_settings)
    
    auth_service = providers.Factory(AuthService,
                                     secret_key=config.provided.SECRET_KEY,
                                     algorithm=config.provided.ALGORITHM)
                                     