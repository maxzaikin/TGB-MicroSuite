import pytest
from _pytest.monkeypatch import MonkeyPatch
from core.config import get_settings

@pytest.fixture(autouse=True)
def clear_lru_cache():
    """Ensures get_settings() is not cached between tests."""
    get_settings.cache_clear()

@pytest.fixture
def minimal_env(monkeypatch: MonkeyPatch):
    """
    A fixture to set up the MINIMUM required environment variables
    for the Settings model to be successfully instantiated.
    This makes tests cleaner as they don't need to know about all required vars.
    """
    monkeypatch.setenv("SECRET_KEY", "dummy-secret-for-testing")
    
def test_settings_overrides_defaults(monkeypatch: MonkeyPatch, minimal_env):
    """
    Verifies that values set in the environment correctly override the default values.
    """
    # Arrange: Set values for variables that HAVE defaults in Settings
    monkeypatch.setenv("PROJECT_NAME", "My Test Project")
   

    # Act
    settings = get_settings()

    # Assert: Check ONLY the values we explicitly overrode.
    assert settings.PROJECT_NAME == "My Test Project"    

def test_settings_uses_defaults(minimal_env):
    """
    Verifies that default values are used when optional env vars are NOT provided.
    """
    # Act: We only use the minimal_env, we don't set any optional variables.
    settings = get_settings()

    # Assert: Check ONLY the default values.
    assert settings.PROJECT_NAME == "A-RAG API Service"
    

@pytest.mark.parametrize("model_name_input, expected_dimension",
    [
        ("sentence-transformers/all-MiniLM-L6-v2", 384), # Path 1
        ("BAAI/bge-large-en-v1.5", 1024),               # Path 2
        ("some-other/unknown-model", 384),             # Path 3 (Fallback)
    ],
)
def test_embedding_dimension_logic(minimal_env, monkeypatch: MonkeyPatch, 
                                   model_name_input: str, expected_dimension: int):
    """
    Tests the computed property `EMBEDDING_DIMENSION` for all possible logic paths.
    """
    # Arrange
    monkeypatch.setenv("EMBEDDING_MODEL_NAME", model_name_input)

    # Act
    settings = get_settings()

    # Assert
    assert settings.EMBEDDING_DIMENSION == expected_dimension