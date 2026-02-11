from fastapi import FastAPI, Depends, HTTPException, status, APIRouter
from ..schemas import schemas
from ..models import models  
from ..database import get_db
from sqlalchemy.orm import Session



router = APIRouter()


@router.post("/createCategory",response_model = schemas.CategoryRead)
def createCategory(category: schemas.CategoryCreate,db: Session = Depends(get_db)):
    category = models.Category(name = category.name)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category

@router.get("/getCategories",response_model = schemas.CategoryRead)
def getCategories(db:Session = Depends(get_db)):
    categotries = db.query(models.Category).all()
    db.commit()
    return categotries

@router.get("/getCategory/{category_id}",response_model = schemas.CategoryRead)
def getCategory(id: int, category: schemas.CategoryRead, db:Session = Depends(get_db)):
    category = db.query(models.Category).filter(models.Category.id == id).first()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    db.commit()
    return category

@router.put("/updateCategory/{category_id}",response_model = schemas.CategoryRead)
def updateCategory(id:int,category_update: schemas.CategoryRead, db: Session = Depends(get_db)):
    category = db.query(models.Category).filter(models.Category.id == id).first()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    setattr(category,"name",category_update.name)
    db.commit()
    db.refresh(category)
    return category


@router.delete("/deleteCategory/{category_id}",response_model = schemas.CategoryRead)
def deleteCategory(id: int, db: Session = Depends(get_db)):
    category = db.query(models.Category).filter(models.Category.id == id).first()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    db.delete(category)
    db.commit()
    return category

