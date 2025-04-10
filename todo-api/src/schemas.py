from pydantic import BaseModel
from typing import List, Optional

class TodoBase(BaseModel):
    name: str
    description: Optional[str] = None

class TodoCreate(TodoBase):
    pass

class TodoUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None

class TodoResponse(TodoBase):
    id: int
    completed: bool

    class Config:
        orm_mode = True


class TodoListBase(BaseModel):
    name: str

class TodoListCreate(TodoListBase):
    pass

class TodoListResponse(TodoListBase):
    id: int
    todos: List[TodoResponse] = []

    class Config:
        orm_mode = True
