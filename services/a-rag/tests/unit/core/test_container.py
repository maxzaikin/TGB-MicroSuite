from core.container import AppContainer
from core.services.auth_service import AuthService
from core.config import Settings

def test_container_provides_auth_service():
    # Arrange
    container = AppContainer()
    
    # Act
    auth_service = container.auth_service()
    
    # Assert
    assert isinstance(auth_service, AuthService)

def test_container_wires_config_into_auth_service():
    # Arrange
    container= AppContainer()
    
    test_settings=Settings(
        PROJECT_NAME = "A-RAG API Service-Test",
        API_V1_STR= "/api/v1-test",
        SECRET_KEY= "testsecret",
        ALGORITHM = "HS256",
        ACCESS_TOKEN_EXPIRE_MINUTES= 30,
        DEFAULT_USER_EMAIL= "test@email.com",
        DEFAULT_USER_PASSWORD="testpassword",
        DATABASE_URL = "sqlite+aiosqlite:///./test.db",
        LLM_SERVER_BASE_URL= "http://localhost:8000",
        LLM_MODEL_NAME= "test-model",
        REDIS_HOST= "localhost",
        REDIS_PORT= 6379,
        VECTOR_DATABASE_TYPE = "qdrant",
        CHROMA_HOST = "localhost",
        CHROMA_PORT = 8000,
        QDRANT_HOST = "localhost",
        QDRANT_PORT= 6333,
        EMBEDDING_MODEL_NAME = "test-embed-model",
        EMBEDDING_DEVICE= "auto",
        RERANKER_MODEL_NAME= "reranker-model"
              
    )
    
    container.config.override(test_settings)  
    
    # Act
    auth_service = container.auth_service()
    
    # Assert
    assert auth_service.secret_key == "testsecret"
    assert auth_service.algorithm == test_settings.ALGORITHM
    assert auth_service.project_name == test_settings.PROJECT_NAME
    