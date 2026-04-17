from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from app.models.task import TaskStatus, TaskPriority


class TaskCreate(BaseModel):
    """Schema for creating a task"""
    assigned_to_id: int
    name: str
    description: Optional[str] = None
    priority: TaskPriority = TaskPriority.MEDIUM
    status: TaskStatus = TaskStatus.PENDING


class TaskUpdate(BaseModel):
    """Schema for updating a task"""
    name: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[TaskPriority] = None
    status: Optional[TaskStatus] = None


class TaskResponse(BaseModel):
    """Schema for task response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_by_id: int
    assigned_to_id: int
    name: str
    description: Optional[str]
    priority: TaskPriority
    status: TaskStatus
    is_admin_assigned: bool
    created_at: datetime
    updated_at: datetime
