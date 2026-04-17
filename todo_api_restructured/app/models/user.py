from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.db.base_class import Base


class UserRole(str, enum.Enum):
    """User role enumeration"""
    USER = "USER"
    ADMIN = "ADMIN"


class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    is_email_verified = Column(Boolean, default=False)
    email_verification_token = Column(String(255), nullable=True)
    receive_notifications = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    assigned_tasks = relationship(
        "Task",
        back_populates="assigned_user",
        foreign_keys="Task.assigned_to_id"
    )
    created_tasks = relationship(
        "Task",
        back_populates="creator",
        foreign_keys="Task.created_by_id"
    )
