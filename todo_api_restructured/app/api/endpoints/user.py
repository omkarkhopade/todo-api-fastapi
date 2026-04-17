from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from pydantic import EmailStr

from app.services.auth_service import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.models.task import Task, TaskStatus
from app.schemas.task import TaskResponse
from app.core.email import notify_task_completed
from app.api.endpoints import admin


router = APIRouter()


@router.get("/tasks", response_model=List[TaskResponse])
async def get_my_tasks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all tasks assigned to current user.
    """
    return db.query(Task).filter(Task.assigned_to_id == current_user.id).all()


@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task_details(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get details of a specific task.
    
    - **task_id**: ID of the task
    """
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.assigned_to_id == current_user.id
    ).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    return task


@router.put("/tasks/{task_id}/complete")
async def complete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark task as completed.
    
    - **task_id**: ID of task to complete
    """
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.assigned_to_id == current_user.id
    ).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Prevent users from cancelling admin-assigned tasks
    if task.is_admin_assigned and task.status == TaskStatus.CANCELLED:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot cancel admin-assigned tasks"
        )
    
    task.status = TaskStatus.COMPLETED
    task.updated_at = datetime.utcnow()
    db.commit()
    
    # Notify admin
    admin = db.query(User).filter(User.id == task.created_by_id).first()

    print("---- EMAIL DEBUG ----")
    print("Admin email:", admin.email if admin else None)
    print("Admin notifications:", admin.receive_notifications if admin else None)
    print("User email:", current_user.email)
    print("Task name:", task.name)

    if admin and admin.receive_notifications:
        try:
            await notify_task_completed(admin.email, task.name, current_user.email)
        except Exception as e:
            print(f"Failed to send notification: {e}")
    
    return {"message": "Task marked as completed"}


@router.put("/notifications")
async def update_notifications(
    receive_notifications: bool = Body(..., embed=True),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update notification preferences.
    
    - **receive_notifications**: true to enable, false to disable
    """
    current_user.receive_notifications = receive_notifications
    db.commit()
    
    return {
        "message": f"Notifications {'enabled' if receive_notifications else 'disabled'}"
    }


@router.post("/unsubscribe")
async def unsubscribe(email: EmailStr, db: Session = Depends(get_db)):
    """
    Unsubscribe from email notifications.
    
    - **email**: Email address to unsubscribe
    """
    user = db.query(User).filter(User.email == email).first()
    if user:
        user.receive_notifications = False
        db.commit()
    
    return {"message": "Successfully unsubscribed from notifications"}
