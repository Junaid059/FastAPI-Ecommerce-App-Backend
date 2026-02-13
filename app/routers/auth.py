from fastapi import APIRouter, Depends, HTTPException, status   
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import models
from app.schemas import schemas
from fastapi.security import OAuth2PasswordRequestForm
from ..utils import hashPassword, verifyPassword
from Oauth2 import create_token
from datetime import timedelta


router = APIRouter(
    tags = ["Authentication"]
)

@router.post("/login",response_model = schemas.Token)
def login(user_credentials: OAuth2PasswordRequestForm = Depends(),db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == user_credentials.username).first()
    if not user:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail="Invalid credentials")
    
    is_password_valid = verifyPassword(user_credentials.password, str(user.password))
    if not is_password_valid:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail="Invalid credentials")
    token = create_token(data = {"id": user.id, "role": user.role})

    return {"access_token": token, "token_type": "bearer"}