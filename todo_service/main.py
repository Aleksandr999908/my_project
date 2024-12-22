from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./data/todo.db"

Base = declarative_base()
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class TodoItem(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, index=True, nullable=True)
    completed = Column(Boolean, default=False)


Base.metadata.create_all(bind=engine)

app = FastAPI()


class TodoItemCreate(BaseModel):
    title: str
    description: str = None
    completed: bool = False


@app.post("/items", response_model=TodoItemCreate)
def create_item(item: TodoItemCreate):
    db = SessionLocal()
    db_item = TodoItem(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    db.close()
    return db_item


@app.get("/items")
def read_items():
    db = SessionLocal()
    items = db.query(TodoItem).all()
    db.close()
    return items


@app.get("/items/{item_id}")
def read_item(item_id: int):
    db = SessionLocal()
    item = db.query(TodoItem).filter(TodoItem.id == item_id).first()
    db.close()
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@app.put("/items/{item_id}", response_model=TodoItemCreate)
def update_item(item_id: int, item: TodoItemCreate):
    db = SessionLocal()
    db_item = db.query(TodoItem).filter(TodoItem.id == item_id).first()
    if db_item is None:
        db.close()
        raise HTTPException(status_code=404, detail="Item not found")
    for key, value in item.dict().items():
        setattr(db_item, key, value)
    db.commit()
    db.refresh(db_item)
    db.close()
    return db_item


@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    db = SessionLocal()
    db_item = db.query(TodoItem).filter(TodoItem.id == item_id).first()
    if db_item is None:
        db.close()
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(db_item)
    db.commit()
    db.close()
    return {"detail": "Item deleted"}
