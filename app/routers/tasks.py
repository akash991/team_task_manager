from models import Task
from starlette import status
from pydantic import BaseModel, Field
from common.utils import (
    db_dependency,
    jwt_dependency,
    decode_access_token,
    notify_user,
    TaskStatus,
    Roles,
)
from fastapi import APIRouter, HTTPException
from typing import Optional


router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
)


class PostTaskRequest(BaseModel):
    title: str = Field(..., title="Title of the task")
    description: str = Field(..., title="Description of the task")
    assignee: str = Field(..., title="Assignee of the task")
    priority: int = Field(..., title="Priority of the task")


class PutTaskRequest(BaseModel):
    status: str = Field(..., title="Status of the task")
    assignee: str = Field(..., title="Assignee of the task")


@router.post("/add_task", status_code=status.HTTP_201_CREATED)
def add_task(
    task_request: PostTaskRequest,
    db: db_dependency,
    jwt: jwt_dependency,
):
    # Get the current user from the JWT token
    current_user = decode_access_token(jwt)

    # Check if the current user is a manager
    # Only managers can add tasks
    if current_user.role != Roles.MANAGER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only managers can add tasks",
        )

    # If not assigned to anyone, set assignee to None
    args = task_request.model_dump()
    # if args.get("assignee", "") == "":
    #     args["assignee"] = None

    # Create a new task and add it to the db
    task = Task(
        **args,
        reporter=current_user.sub,
        status=TaskStatus.TODO,
    )
    db.add(task)
    db.commit()

    # Return a success message
    return {"message": "Task added successfully"}


@router.get("/get_tasks", status_code=status.HTTP_200_OK)
def get_tasks(
    db: db_dependency,
    jwt: jwt_dependency,
    task_id: Optional[int] = None,
):
    # Get the current user from the JWT token
    current_user = decode_access_token(jwt)

    # Get tasks assigned to the current user or reported by the current user
    tasks = db.query(Task).filter(
        (Task.assignee == current_user.sub) | (Task.reporter == current_user.sub)
    )

    # If task_id is provided, filter by task_id
    # If task_id is not provided, return all tasks
    if task_id and task_id != 0:
        tasks = tasks.filter(Task.task_id == task_id).first()
    else:
        tasks = tasks.all()

    # If no tasks are found, return a message
    if not tasks:
        return {"message": "No tasks found"}

    # Return the tasks
    return tasks


@router.put("/start/{task_id}", status_code=status.HTTP_200_OK)
def start_task(
    task_id: int,
    db: db_dependency,
    jwt: jwt_dependency,
):
    # Get the current user from the JWT token
    current_user = decode_access_token(jwt)

    # Only the assignee can start the task
    task = (
        db.query(Task)
        .filter(
            Task.task_id == task_id,
            Task.assignee == current_user.sub,
        )
        .first()
    )

    # If the task is not found, raise a 404 error
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    # Check if the task is in todo state
    if task.status not in [TaskStatus.TODO, TaskStatus.REJECTED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task is not in todo state",
        )

    # Update the task status to in progress
    task.status = TaskStatus.INPROGRESS
    db.commit()

    # Return a success message
    return {"message": "Task started successfully"}


@router.put("/review/{task_id}", status_code=status.HTTP_200_OK)
def review_task(
    task_id: int,
    db: db_dependency,
    jwt: jwt_dependency,
):
    # Get the current user from the JWT token
    current_user = decode_access_token(jwt)

    # Only the assignne can move the task to review
    task = (
        db.query(Task)
        .filter(
            Task.task_id == task_id,
            Task.assignee == current_user.sub,
        )
        .first()
    )

    # If the task is not found, raise a 404 error
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    # Check if the task is in progress
    if task.status != TaskStatus.INPROGRESS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task is not in progress",
        )

    # Notify the reporter that the task is ready for review
    notify_user(
        email=task.reporter,
        subject="Task Review Notification",
        message=f"Task {task.title} is ready for review.",
    )

    # Update the task status to review
    task.status = TaskStatus.REVIEW
    db.commit()

    # Return a success message
    return {"message": "Reporter notified successfully"}


@router.put("/reject/{task_id}", status_code=status.HTTP_200_OK)
def reject_task(
    task_id: int,
    db: db_dependency,
    jwt: jwt_dependency,
):
    # Get the current user from the JWT token
    current_user = decode_access_token(jwt)

    # Only the reporter can reject the task
    task = (
        db.query(Task)
        .filter(
            Task.task_id == task_id,
            Task.reporter == current_user.sub,
        )
        .first()
    )

    # If the task is not found, raise a 404 error
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    # Check if the task is in review
    if task.status != TaskStatus.REVIEW:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task is not in review state",
        )
    task.status = TaskStatus.REJECTED

    # Notify the assignee that the task is rejected
    notify_user(
        email=task.assignee,
        subject="Task Rejection Notification",
        message=f"Task {task.title} has been rejected.",
    )
    db.commit()

    # Return a success message
    return {"message": "Review rejected."}


@router.put("/complete/{task_id}", status_code=status.HTTP_200_OK)
def reject_task(
    task_id: int,
    db: db_dependency,
    jwt: jwt_dependency,
):
    # Get the current user from the JWT token
    current_user = decode_access_token(jwt)

    # Only the reporter can complete the task
    task = (
        db.query(Task)
        .filter(
            Task.task_id == task_id,
            Task.reporter == current_user.sub,
        )
        .first()
    )

    # If the task is not found, raise a 404 error
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    # Check if the task is in review
    if task.status != TaskStatus.REVIEW:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task is not in review state",
        )
    task.status = TaskStatus.COMPLETED

    # Notify the assignee that the task is completed
    notify_user(
        email=task.assignee,
        subject="Task Completion Notification",
        message=f"Task {task.title} has been completed.",
    )
    db.commit()

    # Return a success message
    return {"message": "Task completed successfully"}
