import pytest
import datetime as dt
from jose import jwt
from core.services.auth_service import AuthService
from pytest import MonkeyPatch

def test_password_verification():
    # Arrange
    auth_service= AuthService("key","algo",30)    
    password= "MySecurePassword"
    
    # Act
    hashed_password= auth_service.get_password_hash(password)
    
    # Assert
    assert auth_service.verify_password(password, hashed_password) is True
    assert auth_service.verify_password("WrongPassword", hashed_password) is False
    
def test_pwd_using_salt():
    # Arrange
    auth_service= AuthService("key","algo",30)
    password="MySecurePassword"
    # Act
    hash1= auth_service.get_password_hash(password) 
    hash2= auth_service.get_password_hash(password)
    # Assert
    assert hash1 != hash2   

def test_create_access_token_with_default_expiry(monkeypatch: MonkeyPatch): 
        
    # Arrange
    mocked_time= dt.datetime(2024,1,1,12,0,0, tzinfo=dt.timezone.utc)
    
    class MockDateTime(dt.datetime):
        @classmethod
        def now(cls,tz=None):
            return mocked_time
        
    auth_service= AuthService(secret_key="mysecret", 
                              algorithm="HS256", 
                              expire_minutes=1)
    
    
    monkeypatch.setattr("core.services.auth_service.datetime", MockDateTime)
    
    token_data= {"sub":"user1"}
    
    # Act
    encoded_jwt= auth_service.create_access_token(data=token_data)
    
    # Assert
    decoded_payload= jwt.decode(encoded_jwt,key="mysecret", algorithms=["HS256"],options={"verify_exp": False})
    
    expected_expiry= int((mocked_time + dt.timedelta(minutes=1)).timestamp())
    assert decoded_payload["sub"] == "user1"
    assert decoded_payload["exp"] == expected_expiry
    