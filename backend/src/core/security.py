"""
Security utilities and authentication
"""
import hashlib
import secrets
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from passlib.context import CryptContext


# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def generate_token(
    data: Dict[str, Any], 
    secret_key: str, 
    expires_delta: Optional[timedelta] = None
) -> str:
    """Generate a JWT token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm="HS256")
    return encoded_jwt


def verify_token(token: str, secret_key: str) -> Optional[Dict[str, Any]]:
    """Verify and decode a JWT token"""
    try:
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        return payload
    except jwt.PyJWTError:
        return None


def generate_api_key() -> str:
    """Generate a secure API key"""
    return secrets.token_urlsafe(32)


def hash_api_key(api_key: str) -> str:
    """Hash an API key for storage"""
    return hashlib.sha256(api_key.encode()).hexdigest()


def verify_api_key(api_key: str, hashed_key: str) -> bool:
    """Verify an API key against its hash"""
    return hash_api_key(api_key) == hashed_key


def sanitize_filename(filename: str) -> str:
    """Sanitize a filename for safe storage"""
    import re
    # Remove or replace dangerous characters
    filename = re.sub(r'[^\w\s-.]', '', filename)
    # Replace spaces with underscores
    filename = re.sub(r'[-\s]+', '_', filename)
    return filename


def validate_file_type(filename: str, allowed_extensions: set) -> bool:
    """Validate file type based on extension"""
    if not filename:
        return False
    
    extension = filename.lower().split('.')[-1] if '.' in filename else ''
    return extension in allowed_extensions


def generate_secure_id() -> str:
    """Generate a secure random ID"""
    return secrets.token_urlsafe(16)
