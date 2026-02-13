from fastapi import FastAPI, Depends, HTTPException, status, APIRouter
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.models import models
from app.schemas import schemas
from .Oauth2 import getCurrentUser


router = APIRouter()

@router.get("/searchProducts",response_model = schemas.ProductCreate)
def searchProducts(query: str, category: Optional[str] = None, db: Session = Depends(get_db)):
    query_stmt = db.query(models.Product).filter(models.Product.name.ilike(f"%{query}%"))
    if category:
        query_stmt = query_stmt.filter(models.Product.category == category)
    products = query_stmt.limit(100).all()
    db.commit()
    return products

@router.get("/getCategories",response_model = schemas.CategoryRead)
def searchCategory(query: str, db: Session = Depends(get_db)):
    categories = db.query(models.Category).filter(models.Category.name.ilike(f"%{query}%")).limit(10).all()
    db.commit()
    return categories