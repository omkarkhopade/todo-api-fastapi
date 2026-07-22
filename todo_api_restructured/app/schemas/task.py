from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.task import TaskPriority, TaskStatus


class TaskCreate(BaseModel):
    """Schema for creating a task"""

    assigned_to_id: int = Field(gt=0)
    name: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=5000)
    priority: TaskPriority = TaskPriority.MEDIUM
    status: TaskStatus = TaskStatus.PENDING

    @field_validator("name")
    @classmethod
    def strip_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Task name cannot be blank")
        return value


class TaskUpdate(BaseModel):
    """Schema for updating a task"""

    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=5000)
    priority: TaskPriority | None = None
    status: TaskStatus | None = None

    @field_validator("name")
    @classmethod
    def strip_name(cls, value: str | None) -> str | None:
        if value is None:
            return value
        value = value.strip()
        if not value:
            raise ValueError("Task name cannot be blank")
        return value


class TaskResponse(BaseModel):
    """Schema for task response"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_by_id: int
    assigned_to_id: int
    name: str
    description: str | None
    priority: TaskPriority
    status: TaskStatus
    is_admin_assigned: bool
    created_at: datetime
    updated_at: datetime
