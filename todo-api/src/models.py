from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class TodoList(Base):
    __tablename__ = "todolists"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True)

    todos = relationship("Todo", back_populates="list", cascade="all, delete-orphan")


class Todo(Base):
    __tablename__ = "todos"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True)
    description = Column(String(500), nullable=True)
    completed = Column(Boolean, default=False)
    list_id = Column(Integer, ForeignKey("todolists.id"))

    list = relationship("TodoList", back_populates="todos")
