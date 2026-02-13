from fastapi import FastAPI, Depends, HTTPException, status, APIRouter
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import models
from app.schemas import schemas
from .Oauth2 import getCurrentUser

router = APIRouter()

def UserRole(user = Depends(getCurrentUser)):
    if user.role not in ("customer","admin"):
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail="access required")
    return user

@router.post("/createWishlist",response_model = schemas.WishListRead)
def createwishlist(wishlist: schemas.WishlistCreate,db: Session = Depends(get_db),user = Depends(UserRole)):
    if user.role != "customer":
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail="you need to be logged in ")
    # Use the correct reference for Wishlist model
    existingProduct = db.query(models.Wishlist).filter(models.Wishlist.user_id == user.id, models.Wishlist.product_id == wishlist.product_id).first()
    if existingProduct:
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail="Product already in wishlist")
    wishlist = models.Wishlist(user_id = user.id, product_id = wishlist.product_id)
    db.add(wishlist)
    db.commit()
    db.refresh(wishlist)
    return wishlist

@router.get("/getWishlist",response_model = schemas.WishListRead)
def getWishList(db:Session = Depends(get_db),user=Depends(UserRole)):
    if user.role != "customer":
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail="you need to be logged in ")
    wishlist = db.query(models.Wishlist).filter(models.Wishlist.user_id == user.id).all()
    db.commit()
    return wishlist

@router.delete("/deleteWishlist/{wishlist_id}",response_model = schemas.WishListRead)
def deleteWishlist(id: int, db: Session = Depends(get_db),user = Depends(UserRole)):
    if user.role !="customer":
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail="you need to be logged in ")
    deleteWishlist = db.query(models.Wishlist).filter(models.Wishlist.id == id, models.Wishlist.user_id == user.id).first()
    if not deleteWishlist:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail="Wishlist item not found")
    db.delete(deleteWishlist)
    db.commit()
    return deleteWishlist