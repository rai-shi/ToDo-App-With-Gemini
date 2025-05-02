from fastapi import APIRouter, Depends, Path, HTTPException, Request
from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import status
from pydantic import BaseModel, Field
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from fastapi.templating import Jinja2Templates

from datetime import timedelta, datetime, timezone
import os
from dotenv import load_dotenv

from models import Base, User
from database import engine, SessionLocal

# Configurations

load_dotenv()
JWT_SECRET_KEY  = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM   = os.getenv("JWT_ALGORITHM")

templates = Jinja2Templates(directory="templates")

router = APIRouter(
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
oauth_bearer = OAuth2PasswordBearer(tokenUrl="/auth/login")

class CreateUserRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: str = Field(min_length=11, max_length=50)
    first_name: str = Field(min_length=3, max_length=50)
    last_name: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8, max_length=100)

class Token(BaseModel):
    access_token: str
    token_type: str

def authenticate_user(db: Session, 
                      username: str, 
                      password: str):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user

def create_access_token(username:str, user_id:int, expire_time:timedelta):
    payload = {"sub": username, 
                 "user_id": user_id, 
                 "exp": datetime.now(tz=timezone.utc) + expire_time}
    encoded_jwt = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def verify_token(token: Annotated[str, Depends(oauth_bearer)]):
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("user_id")
        if username is None or user_id is None:
            return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                 detail="Invalid token")
        return {"username": username, "user_id": user_id}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid token")



@router.get("/login-page")
def render_login_page(request: Request):
    return templates.TemplateResponse("login.html", 
                                      {"request": request})


@router.get("/register-page")
def render_register_page(request: Request):
    return templates.TemplateResponse("register.html", 
                                      {"request": request})


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
@router.post("/login", 
             status_code=status.HTTP_200_OK,
             response_model=Token)
async def login_user(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                      db: db_dependency):
    
    user = authenticate_user(db, 
                             form_data.username, 
                             form_data.password)
    if not user:
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                             detail="Invalid credentials")
    
    token = create_access_token(
        username=user.username, 
        user_id=user.id, 
        expire_time=timedelta(minutes=30)
    )

    return {
        "access_token": token,
        "token_type": "bearer",
    }
