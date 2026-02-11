from fastapi import FastAPI, Depends, HTTPException, status, APIRouter
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import models
from app.schemas import schemas

router = APIRouter()

@router.post("/createOrder",response_model = schemas.OrderRead)
def createOrder(order: schemas.OrderCreate, db: Session = Depends(get_db)):
    order = models.Order(user_id = order.user_id, product_id = order.product_id, quantity = order.quantity)
    db.add(order)
    db.commit()
    db.refresh(order)
    return order

@router.get("/getOrders/{user_id}",response_model = schemas.OrderRead)
def getOrders(user_id: int, db: Session = Depends(get_db)):
    orders = db.query(models.Order).filter(models.Order.user_id == user_id).all()
    db.commit()
    return orders

@router.get("/getOrder/{order_id}",response_model = schemas.OrderRead)
def getOrder(id: int,db: Session = Depends(get_db)):
    order = db.query(models.Order).filter(models.Order.id == id).first()
    if order is None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail="Order not found")
    db.commit()
    return order

@router.put("/updateOrder/{order_id}",response_model = schemas.OrderRead)
def updateOrder(id: int, order_update: schemas.OrderCreate, db: Session = Depends(get_db)):
    order = db.query(models.Order).filter(models.Order.id == id).first()
    if not order:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail="Order not found")
    setattr(order, "user_id", order_update.user_id)
    setattr(order, "product_id", order_update.product_id)
    setattr(order, "quantity", order_update.quantity)
    db.commit()
    db.refresh(order)
    return order

@router.delete("/deleteOrder/{order_id}",response_model = schemas.OrderRead)
def deleteOrder(id: int, db: Session = Depends(get_db)):
    order = db.query(models.Order).filter(models.Order.id == id).first()
    if not order:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail="Order not found")
    db.delete(order)
    db.commit()
    return order

