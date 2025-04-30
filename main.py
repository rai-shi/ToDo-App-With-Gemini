from fastapi import FastAPI
from models import Base, ToDo
from database import engine, SessionLocal
from routers.auth import router as auth_router
from routers.todo import router as todo_router

app = FastAPI()
app.add_route(auth_router)
app.add_route(todo_router) 

# Create the database tables
Base.metadata.create_all(bind=engine)
