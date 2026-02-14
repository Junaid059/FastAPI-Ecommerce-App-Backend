from datetime import datetime, timedelta
from ..schemas import schemas
from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import models
import os
from dotenv import load_dotenv


load_dotenv()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

if SECRET_KEY is None:
    raise ValueError("SECRET_KEY environment variable is not set")
if ALGORITHM is None:
    raise ValueError("ALGORITHM environment variable is not set")


def create_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow()+ timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    assert SECRET_KEY is not None and ALGORITHM is not None
    encode_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encode_jwt

def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow()+ timedelta(days=7)
    to_encode.update({"exp":expire})
    assert SECRET_KEY is not None and ALGORITHM is not None
    encode_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encode_jwt

def verifyToken(token: str, credentials_exception):
    try:
        assert SECRET_KEY is not None and ALGORITHM is not None 
        decoded_token = jwt.decode(token,SECRET_KEY,algorithms = [ALGORITHM])
        id = decoded_token.get("id")
        role = decoded_token.get("role")
        if id is None or role is None:
            raise credentials_exception
        token_data = schemas.TokenData(id=id, role=role)    
    except JWTError:
        raise credentials_exception
    
    return token_data

def getCurrentUser(token: str = Depends(oauth2_scheme),db: Session = Depends(get_db)):
    credentials_exception = HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
    user = db.query(models.User).filter(models.User.id == verifyToken(token, credentials_exception).id).first()
    if user is None:
        raise credentials_exception
    return user
