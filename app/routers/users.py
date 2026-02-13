from fastapi import FastAPI,Depends, HTTPException, status,APIRouter
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import models
from app.schemas import schemas
from ..utils import hashPassword
from .Oauth2 import getCurrentUser  

router = APIRouter()

def UserRole(user = Depends(getCurrentUser)):
    if user.role != "admin":
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return user

@router.post("/createUser",response_model=schemas.UserCreate)
def createUser(user: schemas.UserCreate, db: Session = Depends(get_db)):

    db_user = db.query(models.User).filter(models.User.email == user.email).first()

    if db_user:
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    
    user = models.User(email = user.email,password = hashPassword(user.password))
    db.add(user)
    db.commit()
    db.refresh(user)

    return user

@router.get("/getUsers",response_model = schemas.UserCreate)
def getUsers(db: Session = Depends(get_db),user = Depends(UserRole)):
    if user.role != "admin":
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail="Admin access required")
    users = db.query(models.User).limit(10).all()
    return users

@router.get("/getUser/{user_id}",response_model = schemas.UserCreate)
def getUser(user_id: int,db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

@router.put("/updateUser/{user_id}",response_model = schemas.UserCreate)
def updateUser(user_id: int,user_update:schemas.UserCreate, db: Session = Depends(get_db),user = Depends(UserRole)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail="User not found")
    if getattr(user, "user_id", None) != user_id and getattr(user, "role", None) != "admin":
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail="Access denied")
    setattr(user, "email", user_update.email)
    setattr(user, "password", hashPassword(user_update.password))
    db.commit()
    db.refresh(user)
    return user

@router.delete("/deleteUser/{user_id}",response_model = schemas.UserCreate)
def deleteUser(user_id: int, db:Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail="User not found")
    if getattr(user, "user_id", None) != user_id and getattr(user, "role", None) != "admin":
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail="Access denied")
    db.delete(user)
    db.commit()
    return user

@router.put("/updatePassword/{user_id}",response_model = schemas.UserCreate)
def updatePassword(user_id: int,password_update: schemas.UserCreate,db: Session = Depends(get_db),user = Depends(UserRole)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail="User not found")
    if getattr(user, "user_id", None) != user_id and getattr(user, "role", None) != "admin":
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail="Access denied")
    setattr(user,"password",hashPassword(password_update.password))
    db.commit()
    db.refresh(user)
    return user