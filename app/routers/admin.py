from models import Employee
from starlette import status
from pydantic import BaseModel, Field
from sqlalchemy.exc import IntegrityError
from fastapi import APIRouter, HTTPException
from common.utils import (
    db_dependency,
    hash_password,
    Roles,
    jwt_dependency,
    decode_access_token,
)
from typing import Optional


router = APIRouter(
    prefix="/admin",
    tags=["admin"],
)


class EmployeeRequest(BaseModel):
    email: str = Field(..., title="Email of the employee")
    password: str = Field(..., title="Password of the employee")
    first_name: str = Field(..., title="First name of the employee")
    last_name: str = Field(..., title="Last name of the employee")
    manager: str = Field(..., title="Manager of the employee")
    role: str = Field(..., title="Role of the employee")


@router.post("/add_employee", status_code=status.HTTP_201_CREATED)
def add_employee(
    employee_request: EmployeeRequest,
    db: db_dependency,
    jwt: jwt_dependency,
):
    # Get the current user from the JWT token
    current_user = decode_access_token(jwt)

    # Check if the current user is an admin
    # Only admins can add employees
    if current_user.role != Roles.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can add employees",
        )

    # If not assigned to anyone, set manager to None
    args = employee_request.model_dump()
    if args.get("manager", "") == "":
        args["manager"] = None

    # Hash the password
    args["password"] = hash_password(args["password"])

    # Create a new employee and add it to the db
    employee = Employee(**args)

    # Don't allow employee to be their own manager
    if employee.email == employee.manager:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Employee cannot be their own manager",
        )

    # Only admins are allowed to have no manager
    elif employee.role != "admin" and employee.manager == "":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Non-admin employees must have a manager",
        )

    try:
        db.add(employee)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="DB Integrity Error",
        )


@router.get("/get_employees", status_code=status.HTTP_200_OK)
def get_employees(
    db: db_dependency,
    jwt: jwt_dependency,
    email_id: Optional[str] = None,
):
    # Get the current user from the JWT token
    current_user = decode_access_token(jwt)

    # Check if the current user is an admin
    # Only admins can get all employees
    if current_user.role != Roles.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can get all employees",
        )

    # Get all employees from the db
    # Exclude the password field
    employees = db.query(Employee)

    # If email_id is provided, filter by email_id
    if email_id and email_id != "":
        response = employees.filter(Employee.email == email_id).first()
    else:
        response = employees.all()

    if isinstance(response, list):
        for employee in response:
            employee.password = None
    else:
        response.password = None

    # Return the employees
    return response


@router.delete("/delete_employee/{email}", status_code=status.HTTP_200_OK)
def delete_employee(
    email: str,
    db: db_dependency,
    jwt: jwt_dependency,
):
    # Get the current user from the JWT token
    current_user = decode_access_token(jwt)

    # Check if the current user is an admin
    # Only admins can delete employees
    if current_user.role != Roles.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can delete employees",
        )

    # Check if the current user is trying to delete themselves
    if current_user.sub == email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete yourself",
        )

    # Fetch the employee from the database
    employee = db.query(Employee).filter(Employee.email == email).first()

    # Check if employee exists
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found"
        )

    # Check if employee is admin
    if employee.role == "admin":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete admin employee",
        )

    # Check if employee has subordinates
    subordinates = db.query(Employee).filter(Employee.manager == employee.email).all()
    if subordinates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete manager with subordinates",
        )

    # Delete employee
    db.delete(employee)
    db.commit()

    # Return success message
    return {"detail": "Employee deleted successfully"}
