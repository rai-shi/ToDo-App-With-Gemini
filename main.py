from fastapi import FastAPI 

from models import Base 
from database import engine

app = FastAPI()

# Create the database tables
Base.metadata.create_all(bind=engine)

