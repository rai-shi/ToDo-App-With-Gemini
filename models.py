# ORM

from database import Base
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship

class ToDo(Base):
    __tablename__ = "todos"

    id          = Column(Integer, 
                         primary_key=True, 
                         index=True,
                         autoincrement=True)
    title       = Column(String, index=True)
    description = Column(String)
    priority    = Column(Integer, default=1) # would be in range 1-5 
    completed   = Column(Boolean, default=False) 
    created_at  = Column(DateTime)
    updated_at  = Column(DateTime)

    owner_id    = Column(Integer, ForeignKey("users.id")) # foreign key to users table
    owner       = relationship("User", back_populates="todos")  


class User(Base):
    __tablename__ = "users"

    id          = Column(Integer, 
                         primary_key=True, 
                         index=True,
                         autoincrement=True)
    username    = Column(String, unique=True, index=True)
    email       = Column(String, unique=True, index=True)
    first_name  = Column(String)
    last_name   = Column(String)
    hashed_password = Column(String)
    is_active   = Column(Boolean, default=True)

    todos       = relationship("ToDo", back_populates="owner") # one to many relationship with todos