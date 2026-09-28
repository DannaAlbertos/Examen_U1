from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List

from database import engine, SessionLocal, Base
from models import LaptopModel

Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
def startup_event():
    db = SessionLocal()
    try:
        count = db.query(LaptopModel).count()
        if count == 0:
            laptops_iniciales = [
                LaptopModel(marca="Dell", modelo="Latitude 5440", ram_gb=16, disponible=True),
                LaptopModel(marca="Lenovo", modelo="ThinkPad E14", ram_gb=8, disponible=False),
                LaptopModel(marca="HP", modelo="ProBook 450", ram_gb=16, disponible=True)
            ]
            db.add_all(laptops_iniciales)
            db.commit()
    finally:
        db.close()

class LaptopResponse(BaseModel):
    id: int
    marca: str
    modelo: str
    ram_gb: int
    disponible: bool

    class Config:
        orm_mode = True

class LaptopCreate(BaseModel):
    marca: str
    modelo: str
    ram_gb: int

@app.get("/")
def leer_mensaje():
    return {"mensaje": "API del laboratorio de cómputo"}

@app.get("/laptops", response_model=List[LaptopResponse])
def obtener_laptops(db: Session = Depends(get_db)):
    return db.query(LaptopModel).all()

@app.get("/laptops/disponibles", response_model=List[LaptopResponse])
def obtener_laptops_disponibles(db: Session = Depends(get_db)):
    return db.query(LaptopModel).filter(LaptopModel.disponible == True).all()

@app.get("/laptops/{laptop_id}", response_model=LaptopResponse)
def obtener_laptop_por_id(laptop_id: int, db: Session = Depends(get_db)):
    laptop = db.query(LaptopModel).filter(LaptopModel.id == laptop_id).first()
    if not laptop:
        raise HTTPException(status_code=404, detail="Laptop no encontrada")
    return laptop

@app.post("/laptops", response_model=LaptopResponse, status_code=status.HTTP_201_CREATED)
def crear_laptop(laptop: LaptopCreate, db: Session = Depends(get_db)):
    nueva_laptop = LaptopModel(
        marca=laptop.marca,
        modelo=laptop.modelo,
        ram_gb=laptop.ram_gb,
        disponible=True
    )
    db.add(nueva_laptop)
    db.commit()
    db.refresh(nueva_laptop)
    return nueva_laptop