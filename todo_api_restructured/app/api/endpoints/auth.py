import secrets

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import EmailStr
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.db.session import get_db
from app.models.user import User, UserRole
from app.schemas.user import Token, UserCreate, UserLogin, UserResponse
from app.services.auth_service import create_access_token

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new standard user. Admin accounts must be created with the
    management script so clients cannot grant themselves elevated access.

    - **email**: Valid email address
    - **password**: Password (min 8 characters)
    """
    # Check if user exists
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    # Create user
    db_user = User(
        email=user.email,
        hashed_password=hash_password(user.password),
        role=UserRole.USER,
        email_verification_token=secrets.token_urlsafe(32),
    )

    db.add(db_user)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        ) from exc
    db.refresh(db_user)

    return db_user


@router.post("/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    """
    Login user and return JWT token.

    - **email**: User's email
    - **password**: User's password
    """
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token({"sub": db_user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/verify-email")
def verify_email(email: EmailStr, token: str, db: Session = Depends(get_db)):
    """
    Verify user's email address.

    - **email**: User's email
    - **token**: Verification token sent to email
    """
    user = db.query(User).filter(User.email == str(email).lower()).first()
    if not user or user.email_verification_token != token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")

    user.is_email_verified = True
    user.email_verification_token = None
    db.commit()

    return {"message": "Email verified successfully"}
