from fastapi import APIRouter, Depends, Path, HTTPException
from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import status
from pydantic import BaseModel, Field
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer

from models import Base, User
from database import engine, SessionLocal

# Configurations

router = APIRouter(
    prefix="/auth", # ?? main.py'da mı burada mı tanımlanmalı?
    tags=["Authentication"],
)

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

class CreateUserRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: str = Field(min_length=11, max_length=50)
    first_name: str = Field(min_length=3, max_length=50)
    last_name: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8, max_length=100)


def authenticate_user(db: Session, 
                      username: str, 
                      password: str):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user


@router.post("/register", status_code=status.HTTP_201_CREATED)  
async def create_user(createUserRequest: CreateUserRequest,
                      db: db_dependency):
    
    user = User(
        username = createUserRequest.username,
        email = createUserRequest.email,
        first_name = createUserRequest.first_name,
        last_name = createUserRequest.last_name,
        hashed_password = bcrypt_context.hash(createUserRequest.password),
        is_active = True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# when user tries to login, we will check if the user exists in the database
# then return the token
@router.post("/login", status_code=status.HTTP_200_OK)
async def login_user(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                      db: db_dependency):
    
    user = authenticate_user(db, 
                             form_data.username, 
                             form_data.password)
    if not user:
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                             detail="Invalid credentials")
    token = "fake-jwt-token"

    return {
        "access_token": token,
        "token_type": "bearer",
    }
