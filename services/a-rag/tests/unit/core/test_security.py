from passlib.context import CryptContext
from core.security import verify_password,get_password_hash
from datetime import timezone, timedelta
import datetime as dt
from jose import jwt
from core.security import create_access_token
from _pytest.monkeypatch import MonkeyPatch

def test_verify_password_w_correct_pwd():
    # Arrange
    test_password = "SecurePass123!"    
    
    test_password_hash = get_password_hash(test_password)
    
    # Act
    is_valid = verify_password(plain_password=test_password, hashed_password=test_password_hash)
    
    # Assert
    assert is_valid is True
    
def test_verify_password_w_incorrect_pwd():
    # Arrange
    correct_pwd = "SecurePass123!"
    incorrect_pwd = "WrongPass456!"
    
    correct_pwd_hash = get_password_hash(correct_pwd)
    
    # Act
    is_valid = verify_password(plain_password=incorrect_pwd, hashed_password=correct_pwd_hash)
    
    # Assert
    assert is_valid is False
    
def test_get_password_hash():
    # Arrange
    test_password = "test_password"
        
    # Act
    generated_hash = get_password_hash(test_password)
        
    #Assert
    assert isinstance(generated_hash, str)    
    assert generated_hash != test_password
    assert verify_password(test_password, generated_hash) is True
    
def test_get_pwd_hash_salted():
    # Arrange
    test_password = "test_password"
    
    # Act
    hash1 = get_password_hash(test_password)
    hash2 = get_password_hash(test_password)
    
    # Assert
    assert hash1 != hash2
    
def test_create_access_token_uses_default_expiry(monkeypatch: MonkeyPatch):
    # Arrange
    fake_now= dt.datetime(2024,1,1,12,0,0, tzinfo=dt.timezone.utc)
    
    class MockDateTime(dt.datetime):
        @classmethod
        def now(cls, tz=None):
            return fake_now
        
    monkeypatch.setattr(dt,'datetime', MockDateTime)
    
    monkeypatch.setattr("core.config.settings", "ACCESS_TOKEN_EXPIRE_MINUTES", 1)
    
    user_email= "fake@email.com"
    token_data= {"sub": user_email}
    
    # Act
    encoded_token= create_access_token(token_data)
    
    # Assert
    from core.config import settings as current_settings
    
    decoded_token= jwt.decode(encoded_token, current_settings.settings.SECRET_KEY,algorithms=[current_settings.settings.ALGORITHM])
    
    assert decoded_token['sub']==user_email
    
    expected_expiry_timestamp= int((fake_now +timedelta(minutes=1)).timestamp())
    assert expected_expiry_timestamp ==decoded_token['exp']
    

    
    