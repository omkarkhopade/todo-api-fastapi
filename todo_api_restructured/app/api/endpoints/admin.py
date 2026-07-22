import logging

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.email import notify_task_assigned
from app.db.session import get_db
from app.models.task import Task
from app.models.user import User
from app.schemas.task import TaskCreate, TaskResponse, TaskUpdate
from app.services.auth_service import get_admin_user

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    task: TaskCreate,
    background_tasks: BackgroundTasks,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    """
    Create and assign task (Admin only).

    - **assigned_to_id**: User ID to assign task to
    - **name**: Task name
    - **description**: Optional task description
    - **priority**: Task priority (low, medium, high)
    - **status**: Initial status (pending, in_progress, completed, cancelled)
    """
    # Check user exists
    assigned_user = db.query(User).filter(User.id == task.assigned_to_id).first()
    if not assigned_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Create task
    db_task = Task(
        created_by_id=admin.id,
        assigned_to_id=task.assigned_to_id,
        name=task.name,
        description=task.description,
        priority=task.priority,
        status=task.status,
        is_admin_assigned=True,
    )

    db.add(db_task)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    db.refresh(db_task)

    # Send notification
    if assigned_user.receive_notifications:
        background_tasks.add_task(notify_task_assigned, assigned_user.email, task.name, admin.email)

    return db_task


@router.get("/tasks", response_model=list[TaskResponse])
def get_all_tasks(
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=200),
):
    """
    Get all tasks in the system (Admin only).

    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    """
    return db.query(Task).offset(skip).limit(limit).all()


@router.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    task_update: TaskUpdate,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    """
    Update task (Admin only).

    - **task_id**: ID of task to update
    - **name**: New task name (optional)
    - **description**: New description (optional)
    - **priority**: New priority (optional)
    - **status**: New status (optional)
    """
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    update_data = task_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)

    return task


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, admin: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    """
    Delete task (Admin only).

    - **task_id**: ID of task to delete
    """
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    db.delete(task)
    db.commit()

    return None
