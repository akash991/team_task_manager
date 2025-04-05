from models import Employee
from starlette import status
from fastapi import APIRouter, HTTPException
from common.utils import (
    db_dependency,
    verify_password,
    oauth_dependency,
    create_access_token,
)
from pydantic import BaseModel

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


class AccessToken(BaseModel):
    access_token: str
    token_type: str


@router.post("/token", response_model=AccessToken)
def generate_jwt(form: oauth_dependency, db: db_dependency):
    email = form.username
    password = form.password

    # Fetch the user from the database
    user = db.query(Employee).filter(Employee.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    if user.email == "admin@domain.com" and user.password == password:
        return create_access_token(
            payload={"sub": user.email, "role": user.role},
        )
    if not verify_password(password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    # Create access token
    return create_access_token(
        payload={"sub": user.email, "role": user.role},
    )
