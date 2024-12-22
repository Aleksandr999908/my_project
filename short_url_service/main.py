from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import random
import string

DATABASE_URL = "sqlite:///./data/urlshortener.db"

Base = declarative_base()
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class URLMapping(Base):
    __tablename__ = "url_mapping"
    short_id = Column(String, primary_key=True)
    full_url = Column(String, index=True)


Base.metadata.create_all(bind=engine)

app = FastAPI()


class URLCreate(BaseModel):
    url: str


def generate_short_id(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


@app.post("/shorten")
def shorten_url(url: URLCreate):
    db = SessionLocal()
    short_id = generate_short_id()
    db_item = URLMapping(short_id=short_id, full_url=url.url)
    db.add(db_item)
    db.commit()
    db.close()
    return {"short_id": short_id}


@app.get("/{short_id}")
def redirect_to_url(short_id: str):
    db = SessionLocal()
    item = db.query(URLMapping).filter(URLMapping.short_id == short_id).first()
    db.close()
    if item is None:
        raise HTTPException(status_code=404, detail="URL not found")
    return {"full_url": item.full_url}


@app.get("/stats/{short_id}")
def get_url_stats(short_id: str):
    db = SessionLocal()
    item = db.query(URLMapping).filter(URLMapping.short_id == short_id).first()
    db.close()
    if item is None:
        raise HTTPException(status_code=404, detail="URL not found")
    return {"short_id": item.short_id, "full_url": item.full_url}
