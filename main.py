from fastapi import FastAPI, Request
from models import Base
from database import engine, SessionLocal
from fastapi.staticfiles import StaticFiles
# from fastapi.responses import RedirectResponse
from starlette.responses import RedirectResponse
from starlette import status

from routers.auth import router as auth_router
from routers.todo import router as todo_router

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"))

app.include_router(auth_router, prefix="/auth")
app.include_router(todo_router, prefix="/todos") 


@app.get("/")
async def root(request: Request):
    return RedirectResponse(url="/todos/todo-page",
                            status_code=status.HTTP_302_FOUND)



# Create the database tables
Base.metadata.create_all(bind=engine)
