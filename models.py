# ORM

from database import Base
from sqlalchemy import Column, Integer, String, Boolean, DateTime


class ToDo(Base):
    __tablename__ = "todos"

    id          = Column(Integer, primary_key=True, index=True)
    title       = Column(String, index=True)
    description = Column(String)
    priority    = Column(Integer, default=1) # would be in range 1-5 
    completed   = Column(Boolean, default=False) 
    created_at  = Column(DateTime)
    updated_at  = Column(DateTime)