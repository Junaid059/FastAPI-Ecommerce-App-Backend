from fastapi import FastAPI, Depends, HTTPException, status, APIRouter
from ..schemas import schemas
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import models
from .Oauth2 import getCurrentUser

def userRole(user = Depends(getCurrentUser)):
    if user.role not in ("customer","admin"):
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail="Customer access required")
    return user


router = APIRouter()

@router.post("/createRating",response_model = schemas.RatingRead)
def createRating(rating:schemas.RatingCreate,db: Session = Depends(get_db)):
    rating = models.Rating(product_id = rating.product_id,user_id = rating.user_id, rating = rating.rating)
    db.add(rating)
    db.commit()
    db.refresh(rating)
    return rating

@router.get("/getRatings/{product_id}",response_model = schemas.RatingRead)
def getRatings(product_id: int, db: Session = Depends(get_db),user = Depends(userRole)):
    if user.role != "customer" and user.role != "admin":
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail="access denied")
    ratings = db.query(models.Rating).filter(models.Rating.product_id == product_id).limit(10).all()
    db.commit()
    return ratings

@router.get("/getRating/{rating_id}",response_model = schemas.RatingRead)
def getRating(id: int,db: Session = Depends(get_db),user = Depends(userRole)):
    if user.role != "customer" and user.role != "admin":
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail="access denied")
    rating = db.query(models.Rating).filter(models.Rating.id == id).first()
    if rating is None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail="Rating not found")
    db.commit()
    return rating

@router.put("/updateRating/{rating_id}",response_model = schemas.RatingRead)
def updateRating(id: int, rating_update: schemas.RatingCreate, db: Session = Depends(get_db),user = Depends(userRole)):
    if user.role != "customer" and user.role != "admin":
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail="access denied")
    rating = db.query(models.Rating).filter(models.Rating.id == id).first()
    if not rating:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail="Rating not found")
    setattr(rating, "product_id", rating_update.product_id)
    setattr(rating, "user_id", rating_update.user_id)
    setattr(rating, "rating", rating_update.rating)
    db.commit()
    db.refresh(rating)
    return rating

@router.delete("/deleteRating/{rating_id}",response_model = schemas.RatingRead)
def deleteRating(id: int, db: Session = Depends(get_db),user = Depends(userRole)):
    if user.role != "customer" and user.role != "admin":
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail="access denied")
    rating = db.query(models.Rating).filter(models.Rating.id == id).first()
    if not rating:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail="Rating not found")
    db.delete(rating)
    db.commit()
    return rating
