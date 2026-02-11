from fastapi import FastAPI,Depends, HTTPException, status,APIRouter
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import models
from app.schemas import schemas

router = APIRouter()


@router.post("/createUser",response_model=schemas.UserCreate)
def createUser(user: schemas.UserCreate, db: Session = Depends(get_db)):

    db_user = db.query(models.User).filter(models.User.email == user.email).first()

    if db_user:
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    
    user = models.User(email = user.email,password = user.password)
    db.add(user)
    db.commit()
    db.refresh(user)

    return user

@router.get("/getUsers",response_model = schemas.UserCreate)
def getUsers(db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    db.commit()
    return users

@router.get("/getUser/{user_id}",response_model = schemas.UserCreate)
def getUser(id: int,db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()
    if user is None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail="User not found")
    db.commit()
    return user

@router.put("/updateUser/{user_id}",response_model = schemas.UserCreate)
def updateUser(id: int,user_update:schemas.UserCreate, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail="User not found")
    setattr(user, "email", user_update.email)
    setattr(user, "password", user_update.password)
    db.commit()
    db.refresh(user)
    return user

@router.delete("/deleteUser/{user_id}",response_model = schemas.UserCreate)
def deleteUser(id: int, db:Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail="User not found")
    db.delete(user)
    db.commit()
    return user

