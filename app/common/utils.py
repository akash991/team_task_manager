from psgdb import session
from fastapi import Depends
from typing import Annotated
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm


# JWT settings
SECRET = "abcde"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


class DecodedJWTToken:
    def __init__(self, sub: str, role: str, exp: int):
        self.sub = sub
        self.role = role
        self.exp = exp


class TaskStatus:
    TODO = "ToDo"
    INPROGRESS = "InProgress"
    REVIEW = "Review"
    COMPLETED = "Completed"
    REJECTED = "Rejected"


class Roles:
    ADMIN = "admin"
    MANAGER = "manager"
    DEVELOPER = "developer"


def hash_password(password: str) -> str:
    """
    Hashes a password using bcrypt.
    """
    return bcrypt_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a password against a hashed password.
    """
    return bcrypt_context.verify(plain_password, hashed_password)


def create_access_token(payload: dict):
    """
    Creates a JWT access token with an expiration time.
    """
    to_encode = payload.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    return {
        "access_token": jwt.encode(
            claims=to_encode,
            key=SECRET,
            algorithm=ALGORITHM,
        ),
        "token_type": "bearer",
    }


def decode_access_token(token: str):
    """
    Decodes a JWT access token and verifies its validity.
    """
    try:
        payload = jwt.decode(
            token,
            key=SECRET,
            algorithms=[ALGORITHM],
        )
        return DecodedJWTToken(**payload)
    except JWTError:
        return None


def get_db():
    """
    Dependency that provides a database session.
    """
    db = session()
    try:
        yield db
    finally:
        db.close()


def notify_user(email: str, subject: str, message: str):
    """
    Placeholder function to notify a user via email.
    """
    # Implement your email notification logic here
    pass


db_dependency = Annotated[Session, Depends(get_db)]
oauth_dependency = Annotated[OAuth2PasswordRequestForm, Depends()]
jwt_dependency = Annotated[str, Depends(oauth2_scheme)]
