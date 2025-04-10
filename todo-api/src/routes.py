from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models, schemas, database

router = APIRouter()

# Create a new todo list
@router.post("/lists/", response_model=schemas.TodoListResponse)
def create_list(list: schemas.TodoListCreate, db: Session = Depends(database.get_db)):
    db_list = models.TodoList(name=list.name)
    db.add(db_list)
    db.commit()
    db.refresh(db_list)
    return db_list

# Get all todo lists
@router.get("/lists/", response_model=list[schemas.TodoListResponse])
def get_lists(db: Session = Depends(database.get_db)):
    return db.query(models.TodoList).all()

# Create a new todo
@router.post("/todos/", response_model=schemas.TodoResponse)
def create_todo(todo: schemas.TodoCreate, list_id: int, db: Session = Depends(database.get_db)):
    db_todo = models.Todo(
        name=todo.name, description=todo.description, list_id=list_id
    )
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo

# Update a todo
@router.put("/todos/{todo_id}", response_model=schemas.TodoResponse)
def update_todo(todo_id: int, todo: schemas.TodoUpdate, db: Session = Depends(database.get_db)):
    db_todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    if not db_todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    if todo.name is not None:
        db_todo.name = todo.name
    if todo.description is not None:
        db_todo.description = todo.description
    if todo.completed is not None:
        db_todo.completed = todo.completed

    db.commit()
    db.refresh(db_todo)
    return db_todo

# Mark a todo as completed
@router.put("/todos/{todo_id}/check", response_model=schemas.TodoResponse)
def check_todo(todo_id: int, db: Session = Depends(database.get_db)):
    return update_todo(todo_id, schemas.TodoUpdate(completed=True), db)

# Mark a todo as not completed
@router.put("/todos/{todo_id}/uncheck", response_model=schemas.TodoResponse)
def uncheck_todo(todo_id: int, db: Session = Depends(database.get_db)):
    return update_todo(todo_id, schemas.TodoUpdate(completed=False), db)

# Delete a todo
@router.delete("/todos/{todo_id}", response_model=schemas.TodoResponse)
def delete_todo(todo_id: int, db: Session = Depends(database.get_db)):
    db_todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    if not db_todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    db.delete(db_todo)
    db.commit()
    return db_todo

# Delete a todo list
@router.delete("/lists/{list_id}", response_model=schemas.TodoListResponse)
def delete_list(list_id: int, db: Session = Depends(database.get_db)):
    db_list = db.query(models.TodoList).filter(models.TodoList.id == list_id).first()
    if not db_list:
        raise HTTPException(status_code=404, detail="Todo list not found")

    db.delete(db_list)
    db.commit()
    return db_list
