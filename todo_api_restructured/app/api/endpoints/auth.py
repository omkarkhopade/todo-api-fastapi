from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import secrets
import string

from app.core.security import hash_password, verify_password
from app.services.auth_service import create_access_token
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token
from pydantic import EmailStr

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """
    Register new user or admin.
    
    - **email**: Valid email address
    - **password**: Password (min 8 characters)
    - **role**: USER or ADMIN
    """
    # Check if user exists
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user
    db_user = User(
        email=user.email,
        hashed_password=hash_password(user.password),
        role=user.role,
        email_verification_token=''.join(
            secrets.choice(string.ascii_letters + string.digits) for _ in range(32)
        )
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user


@router.post("/login", response_model=Token)
async def login(user: UserLogin, db: Session = Depends(get_db)):
    """
    Login user and return JWT token.
    
    - **email**: User's email
    - **password**: User's password
    """
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    access_token = create_access_token({"sub": db_user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/verify-email")
async def verify_email(email: EmailStr, token: str, db: Session = Depends(get_db)):
    """
    Verify user's email address.
    
    - **email**: User's email
    - **token**: Verification token sent to email
    """
    user = db.query(User).filter(User.email == email).first()
    if not user or user.email_verification_token != token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token"
        )
    
    user.is_email_verified = True
    user.email_verification_token = None
    db.commit()
    
    return {"message": "Email verified successfully"}
