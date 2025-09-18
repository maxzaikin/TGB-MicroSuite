
from passlib.context import CryptContext
from core.security import verify_password,get_password_hash



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