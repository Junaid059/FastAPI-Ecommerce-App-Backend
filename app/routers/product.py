from fastapi import FastAPI, Depends, HTTPException, status, APIRouter
from sqlalchemy.orm import Session  
from app.database import get_db
from app.models import models
from app.schemas import schemas
from .Oauth2 import getCurrentUser

router = APIRouter()

def userRole(user = Depends(getCurrentUser)):
    if user.role not in ("seller","admin","customer"):
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail="access required")
    return user

@router.post("/createProduct",response_model = schemas.ProductCreate)
def createProduct(id: int, product: schemas.ProductCreate, db: Session = Depends(get_db),user =Depends(userRole) ):
    if user.role != "seller" and user.role != "admin":
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail="Seller or admin access required")
    product = models.Product(name = product.name, price= product.price, description = product.description, image_url = product.image_url, category=product.category)
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

@router.get("/getProducts/{category}",response_model = schemas.ProductCreate)
def getProducts(category:str,db: Session = Depends(get_db)):
    products = db.query(models.Product).filter(models.Product.category == category).limit(10).all()
    db.commit()
    return products

@router.get("/getProduct/{product_id}",response_model = schemas.ProductCreate)
def getProduct(id: int,db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == id).first()
    if product is None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail="Product not found")
    db.commit()
    return product

@router.put("/updateProduct/{product_id}",response_model = schemas.ProductCreate)
def updateProduct(id:int, product_update: schemas.ProductCreate,db: Session = Depends(get_db),user = Depends(userRole)):
    if user.role != "seller" and user.role != "admin":
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail="Seller or admin access required")
    product = db.query(models.Product).filter(models.Product.id == id).first()
    if not product:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail="Product not found")
    setattr(product, "name",product_update.name)
    setattr(product, "price",product_update.price)
    setattr(product, "description",product_update.description)
    setattr(product, "image_url",product_update.image_url)
    setattr(product, "category",product_update.category)
    db.commit()
    db.refresh(product)
    return product

@router.delete("/deleteProduct/{product_id}",response_model = schemas.ProductCreate)
def deleteProduct(id: int, db: Session = Depends(get_db),user = Depends(userRole)):
    if user.role != "seller" and user.role != "admin":
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail="Seller or admin access required")
    product = db.query(models.Product).filter(models.Product.id == id).first()
    if not product:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail="Product not found")
    db.delete(product)
    db.commit()
    return product

