from fastapi import APIRouter, BackgroundTasks, Body, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.email import notify_task_completed
from app.db.session import get_db
from app.models.task import Task, TaskStatus
from app.models.user import User
from app.schemas.task import TaskResponse
from app.services.auth_service import get_current_user

router = APIRouter()


@router.get("/tasks", response_model=list[TaskResponse])
def get_my_tasks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=200),
):
    """
    Get all tasks assigned to current user.
    """
    return (
        db.query(Task)
        .filter(Task.assigned_to_id == current_user.id)
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task_details(
    task_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Get details of a specific task.

    - **task_id**: ID of the task
    """
    task = db.query(Task).filter(Task.id == task_id, Task.assigned_to_id == current_user.id).first()

    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    return task


@router.put("/tasks/{task_id}/complete")
def complete_task(
    task_id: int,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Mark task as completed.

    - **task_id**: ID of task to complete
    """
    task = db.query(Task).filter(Task.id == task_id, Task.assigned_to_id == current_user.id).first()

    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    task.status = TaskStatus.COMPLETED
    db.commit()

    # Notify admin
    admin = db.query(User).filter(User.id == task.created_by_id).first()

    if admin and admin.receive_notifications:
        background_tasks.add_task(notify_task_completed, admin.email, task.name, current_user.email)

    return {"message": "Task marked as completed"}


@router.put("/notifications")
def update_notifications(
    receive_notifications: bool = Body(..., embed=True),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update notification preferences.

    - **receive_notifications**: true to enable, false to disable
    """
    current_user.receive_notifications = receive_notifications
    db.commit()

    return {"message": f"Notifications {'enabled' if receive_notifications else 'disabled'}"}


@router.post("/unsubscribe")
def unsubscribe(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Unsubscribe from email notifications.

    - **email**: Email address to unsubscribe
    """
    current_user.receive_notifications = False
    db.commit()

    return {"message": "Successfully unsubscribed from notifications"}
