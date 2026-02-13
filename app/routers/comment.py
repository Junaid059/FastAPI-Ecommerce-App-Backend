from fastapi import FastAPI, Depends, HTTPException, status, APIRouter
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import models
from app.schemas import schemas
from .Oauth2 import getCurrentUser

def userRole(user = Depends(getCurrentUser)):
    if user.role not in ("customer","admin","seller"):
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail="Access denied")
    return user


router = APIRouter()

@router.post("/createComment",response_model = schemas.CommentRead)
def createComment(comment: schemas.CommentCreate, db: Session = Depends(get_db),user = Depends(userRole)):
    if user.role not in ("customer","admin","seller"):
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail="Access denied")
    comment = models.Comment(product_id = comment.product_id, user_id = comment.user_id, content = comment.comment)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment

@router.get("/getComments/{product_id}",response_model = schemas.CommentRead)
def getComments(product_id: int, db: Session = Depends(get_db),user = Depends(userRole)):
    if user.role not in ("customer","admin","seller"):
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail="Access denied")
    comments = db.query(models.Comment).filter(models.Comment.product_id == product_id).limit(10).all()
    db.commit()
    return comments

@router.get("/getComment/{comment_id}",response_model = schemas.CommentRead)
def getComment(id: int,db: Session = Depends(get_db),user = Depends(userRole)):
    if user.role not in ("customer","admin","seller"):
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail="Access denied")
    comment = db.query(models.Comment).filter(models.Comment.id == id).first()
    if comment is None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail="Comment not found")
    db.commit()
    return comment

@router.put("/updateComment/{comment_id}",response_model = schemas.CommentRead)
def updateComment(id: int, comment_update: schemas.CommentCreate, db: Session = Depends
(get_db),user = Depends(userRole)):
    if user.role not in ("customer","admin","seller"):
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail="Access denied")
    comment = db.query(models.Comment).filter(models.Comment.id == id).first()
    if not comment:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail="Comment not found")
    setattr(comment, "product_id", comment_update.product_id)
    setattr(comment, "user_id", comment_update.user_id)
    setattr(comment, "comment", comment_update.comment)
    db.commit()
    db.refresh(comment)
    return comment

@router.delete("/deleteComment/{comment_id}",response_model = schemas.CommentRead)
def deleteComment(id: int, db: Session = Depends(get_db),user = Depends(userRole)):
    if user.role not in ("customer","admin","seller"):
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail="Access denied")
    comment = db.query(models.Comment).filter(models.Comment.id == id).first()
    if not comment:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail="Comment not found")
    db.delete(comment)
    db.commit()
    return comment
