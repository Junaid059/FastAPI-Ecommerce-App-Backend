from fastapi import FastAPI,Depends, HTTPException, status,APIRouter
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import models
from app.schemas import schemas
from .Oauth2 import getCurrentUser

router =APIRouter()

def UserRole(user = Depends(getCurrentUser)):
    if user.role != ("admin","customer"):
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail="access required")
    return user

@router.post("/addToCart",response_model=schemas.CartRead)
def addtocart(cart: schemas.CartCreate, db: Session = Depends(get_db),user = Depends(UserRole)):
    if user.role != "customer":
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail="Customer access required")
    db_cart = db.query(models.Cart).filter(models.Cart.user_id == user.id, models.Cart.product_id == cart.product_id).first()
    if db_cart:
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail="Item already in cart")
    cart_item = models.Cart(user_id = user.id, product_id = cart.product_id, quantity = cart.quantity)
    db.add(cart_item)
    db.commit()
    db.refresh(cart_item)
    return cart_item


@router.get("/getAllCartItems",response_model = list[schemas.CartRead])
def getallCartItem(db: Session = Depends(get_db),user = Depends(UserRole)):
    if user.role != "customer" and user.role != "admin":
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail="Customer access required")
    cart_items = db.query(models.Cart).filter(models.Cart.user_id == user.id).all()
    return cart_items

@router.put("/updateCart",response_model = schemas.CartRead)
def updateCart(id: int, cart_update: schemas.CartCreate,db: Session=Depends(get_db),user = Depends(UserRole)):
    if user.role != "customer" and user.role != "admin":
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail="access required")
    cart_item = db.query(models.Cart).filter(models.Cart.id == id).first()
    if not cart_item:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail="Cart item not found")
    setattr(cart_item, "product_id", cart_update.product_id)
    setattr(cart_item,"quantity", cart_update.quantity)
    db.commit()
    db.refresh(cart_item)
    return cart_item

@router.delete("/deleteCart/{cart_id}",response_model = schemas.CartRead)
def deleteCart(id: int,db: Session = Depends(get_db),user = Depends(UserRole)):
    if user.role != "customer" and user.role != "admin":
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail="access required")
    cart_item = db.query(models.Cart).filter(models.Cart.id == id).first()
    if not cart_item:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail="Cart item not found")
    db.delete(cart_item)
    db.commit()
    return cart_item