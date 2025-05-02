from fastapi import APIRouter, Depends, Path, HTTPException
from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import status
from pydantic import BaseModel, Field

from models import Base, ToDo
from database import engine, SessionLocal


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

db_dependency = Annotated[Session, Depends(get_db)]



@router.get("/get_all", status_code=status.HTTP_200_OK)
async def get_all_todo(db: db_dependency):
    return db.query(ToDo).all()


@router.get("/get/{todo_id}", status_code=status.HTTP_200_OK)
async def get_todo(db: db_dependency, 
                    todo_id: int = Path(gt=0)):
    todo = db.query(ToDo).filter(ToDo.id == todo_id).first()
    if not todo: 
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")    
    return todo


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_todo(todo: ToDoRequest, 
                      db: db_dependency):
    todo = ToDo(**todo) # .dict()
    db.add(todo)
    db.commit()
    db.refresh(todo)
    return todo


@router.put("/update/{todo_id}", status_code=status.HTTP_200_OK)
async def update_todo(todo_request: ToDoRequest, 
                      db: db_dependency, 
                      todo_id: int = Path(gt=0)):
    
    todo = db.query(ToDo).filter(ToDo.id == todo_id).first()
    if not todo:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    for key, value in todo_request.dict().items():
        setattr(todo, key, value)
    db.commit()
    db.refresh(todo)
    return todo


# 204 No Content dönebilir
@router.delete("/delete/{todo_id}", status_code=status.HTTP_200_OK)
async def delete_todo(db: db_dependency, 
                       todo_id: int = Path(gt=0)):
    todo = db.query(ToDo).filter(ToDo.id == todo_id).first()
    if not todo:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    db.delete(todo)
    db.commit()
    return {"message": "Todo deleted successfully"}