# app/main.py
import uuid
from typing import List
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr

from app.database import engine, get_db, Base
from app import models

Base.metadata.create_all(bind=engine)

app = FastAPI(title="RistoHub - Users Service")
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # per sviluppo; da restringere in produzione
    allow_methods=["*"],
    allow_headers=["*"],
)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ---------- SCHEMI: Utenti ----------

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


# ---------- SCHEMI: Menù ----------

class MenuItemCreate(BaseModel):
    name: str
    description: str | None = None
    category: str
    price: float

class MenuItemOut(BaseModel):
    id: int
    name: str
    description: str | None
    category: str
    price: float
    is_available: int
    sort_order: int 

    class Config:
        from_attributes = True

class ReorderRequest(BaseModel):
    ordered_ids: List[int] 
# ---------- ENDPOINT: Utenti ----------

@app.post("/users/register", response_model=UserOut)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email già registrata")

    hashed = pwd_context.hash(user.password)
    card_id = str(uuid.uuid4())[:8].upper()

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


# ---------- ENDPOINT: Menù ----------

@app.post("/menu", response_model=MenuItemOut)
def create_menu_item(item: MenuItemCreate, db: Session = Depends(get_db)):
    new_item = models.MenuItem(
        name=item.name,
        description=item.description,
        category=item.category,
        price=item.price,
        is_available=1,
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item

@app.put("/menu/{item_id}", response_model=MenuItemOut)
def update_menu_item(item_id: int, item: MenuItemCreate, db: Session = Depends(get_db)):
    existing = db.query(models.MenuItem).filter(models.MenuItem.id == item_id).first()
    if not existing:
        raise HTTPException(status_code=404, detail="Piatto non trovato")
    existing.name = item.name
    existing.description = item.description
    existing.category = item.category
    existing.price = item.price
    db.commit()
    db.refresh(existing)
    return existing


@app.get("/menu", response_model=List[MenuItemOut])
def get_menu(category: str | None = None, db: Session = Depends(get_db)):
    query = db.query(models.MenuItem)
    if category:
        query = query.filter(models.MenuItem.category == category)
    return query.all()


@app.delete("/menu/{item_id}")
def delete_menu_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(models.MenuItem).filter(models.MenuItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Piatto non trovato")
    db.delete(item)
    db.commit()
    return {"detail": "Eliminato"}

@app.get("/menu", response_model=List[MenuItemOut])
def get_menu(category: str | None = None, db: Session = Depends(get_db)):
    query = db.query(models.MenuItem)
    if category:
        query = query.filter(models.MenuItem.category == category)
    return query.order_by(models.MenuItem.sort_order).all()  # MODIFICATO: ordina


@app.put("/menu/reorder")
def reorder_menu(payload: ReorderRequest, db: Session = Depends(get_db)):
    for position, item_id in enumerate(payload.ordered_ids):
        db.query(models.MenuItem).filter(models.MenuItem.id == item_id).update(
            {"sort_order": position}
        )
    db.commit()
    return {"detail": "Ordine aggiornato"}
        


# ---------- Health check ----------

@app.get("/health")
def health_check():
    return {"status": "ok"}
