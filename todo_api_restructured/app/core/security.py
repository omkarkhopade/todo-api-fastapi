from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

# Initialize Argon2 password hasher
ph = PasswordHasher()


def hash_password(password: str) -> str:
    """
    Hash password using Argon2.
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password
        
    Raises:
        ValueError: If password is too short
    """
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters")
    return ph.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify password against hash.
    
    Args:
        plain_password: Plain text password
        hashed_password: Hashed password from database
        
    Returns:
        True if password matches, False otherwise
    """
    try:
        ph.verify(hashed_password, plain_password)
        return True
    except (VerifyMismatchError, Exception):
        return False
