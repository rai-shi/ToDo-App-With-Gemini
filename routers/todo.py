from fastapi import APIRouter, Depends, Path, HTTPException
from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import status
from pydantic import BaseModel, Field

from models import Base, ToDo
from database import engine, SessionLocal
from routers.auth import verify_token


router = APIRouter(
    tags=["Todo"],
)


class ToDoRequest(BaseModel):
    title: str = Field(min_length=3, max_length=100)
    description: str = Field(min_length=1, max_length=1000)
    completed: bool = Field(default=False)
    priority: int = Field(default=1, ge=1, le=5)

def get_db():
    db = SessionLocal()
    try:
        # return the database session
        # get_db is a generator function bc of the yield statement
        # it will return the db session and then close it after the request is done
        # fastapi suggest using yield while using SessionLocal
        yield db
    finally:
        db.close()

db_dependency   = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(verify_token)]


@router.get("/", 
            status_code=status.HTTP_200_OK)
async def get_all_todo(user:user_dependency, 
                       db: db_dependency):
    
    if user is None:
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                             detail="User not authenticated")
    
    return db.query(ToDo).filter(ToDo.owner_id == user.get("id")).all()


@router.get("/todo/{todo_id}", 
            status_code=status.HTTP_200_OK)
async def get_todo(db: db_dependency, 
                   user:user_dependency,
                    todo_id: int = Path(gt=0)):
    
    if user is None:
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                             detail="User not authenticated")
    
    todo = db.query(ToDo).filter(ToDo.id == todo_id).filter(ToDo.owner_id == user.get("id")).first()
    
    if not todo: 
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")    
    return todo


@router.post("/create", 
             status_code=status.HTTP_201_CREATED)
async def create_todo(todo: ToDoRequest,
                        user:user_dependency, 
                        db: db_dependency):
    if user is None:
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                             detail="User not authenticated")
    
    todo = ToDo(**todo, owner_id=user.get("id")) # .dict()
    db.add(todo)
    db.commit()
    db.refresh(todo)
    return todo


@router.put("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def update_todo(todo_request: ToDoRequest, 
                      user:user_dependency,
                      db: db_dependency, 
                      todo_id: int = Path(gt=0)):
    
    if user is None:
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                             detail="User not authenticated")
    
    todo = db.query(ToDo).filter(ToDo.id == todo_id).filter(ToDo.owner_id == user.get("id")).first()
    if not todo:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    for key, value in todo_request.dict().items():
        setattr(todo, key, value)
    db.commit()
    db.refresh(todo)
    return todo


@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(db: db_dependency, 
                      user:user_dependency,
                       todo_id: int = Path(gt=0)):
    if user is None:
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                             detail="User not authenticated")
    
    todo = db.query(ToDo).filter(ToDo.id == todo_id).filter(ToDo.owner_id == user.get("id")).first()
    if not todo:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    db.delete(todo)
    db.commit()
    return {"message": "Todo deleted successfully"}