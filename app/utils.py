from passlib.context import CryptContext
from fastapi import UploadFile, HTTPException
import os
import shutil


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hashPassword(password: str) -> str:
    return pwd_context.hash(password)

def verifyPassword(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def save_image(file: UploadFile) -> str:
    """
    Saves an uploaded image file to the 'uploads/' directory.
    Validates that the file is an image and returns the file path.
    """
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Uploaded file must be an image")
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    filename = file.filename or ""
    file_extension = os.path.splitext(filename)[1]
    unique_filename = f"{os.urandom(16).hex()}{file_extension}"
    file_path = os.path.join(upload_dir, unique_filename)
    
    # Save the file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return file_path