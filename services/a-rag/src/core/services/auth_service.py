from typing import Any, Dict, Optional
from datetime import timedelta, datetime, timezone
from passlib.context import CryptContext
from jose import jwt

pwd_context= CryptContext(schemes=['bcrypt'], deprecated='auto')

class AuthService:
    
    def __init__(self, secret_key: str, algorithm: str, expire_minutes: int):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.expire_minutes = expire_minutes
        
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password,hashed_password)
    
    def get_password_hash(self, password: str)->str:
        return pwd_context.hash(password)
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta]=None)->str:
        to_encode= data.copy()
        
        if expires_delta:
            expire= datetime.now(timezone.utc) + expires_delta
        else:
            expire=datetime.now(timezone.utc) + timedelta(minutes=self.expire_minutes)
            
        to_encode.update({"exp":expire})
        encoded_jwt=jwt.encode(to_encode,self.secret_key,algorithm=self.algorithm)
        
        return encoded_jwt
    
