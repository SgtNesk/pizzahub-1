# app/main.py
import uuid
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr

from app.database import engine, get_db, Base
from app import models

Base.metadata.create_all(bind=engine)

app = FastAPI(title="RistoHub - Users Service")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str

class UserOut(BaseModel):
    id: int
    email: str
    full_name: str
    card_id: str
    points: int

    class Config:
        from_attributes = True

@app.post("/users/register", response_model=UserOut)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email già registrata")

    hashed = pwd_context.hash(user.password)
    card_id = str(uuid.uuid4())[:8].upper()  # tessera digitale semplice

    new_user = models.User(
        email=user.email,
        hashed_password=hashed,
        full_name=user.full_name,
        card_id=card_id,
        points=0,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.get("/health")
def health_check():
    return {"status": "ok"}
