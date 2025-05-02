from fastapi import FastAPI
from models import Base
from database import engine, SessionLocal
from routers.auth import router as auth_router
from routers.todo import router as todo_router

app = FastAPI()
app.include_router(auth_router, prefix="/auth")
app.include_router(todo_router, prefix="/todo") 



# Create the database tables
Base.metadata.create_all(bind=engine)
