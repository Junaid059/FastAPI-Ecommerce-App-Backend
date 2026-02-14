from fastapi import FastAPI, Depends, HTTPException, status, APIRouter
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import models
from app.schemas import schemas
from .Oauth2 import getCurrentUser

router = APIRouter()

def userRole(user = Depends(getCurrentUser)):
    if user.role not in ("customer","admin"):
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail="Customer access required")
    return user

@router.post("/createOrder",response_model = schemas.OrderRead)
def createOrder(order: schemas.OrderCreate, db: Session = Depends(get_db),user = Depends(userRole)):
    if user.role != "customer":
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail="Customer access required")
    # Fetch the product from the database
    product = db.query(models.Product).filter(models.Product.id == order.product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    # Use the instance attribute for stock check and update
    current_stock = product.__dict__.get('stock')
    if current_stock is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Product stock not set")
    if current_stock < order.quantity:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not enough stock available")
    # Create the order
    new_order = models.Order(user_id=order.user_id, product_id=order.product_id, quantity=order.quantity, address=order.address)
    # Update the product stock (instance attribute)
    product.__dict__['stock'] = current_stock - order.quantity
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    return new_order

@router.get("/getOrders/{user_id}",response_model = schemas.OrderRead)
def getOrders(user_id: int, offset: int = 0, db: Session = Depends(get_db),user = Depends(userRole)):
    if user.user_id != user_id and user.role != "admin":
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail="access denied")
    orders = db.query(models.Order).filter(models.Order.user_id == user_id).limit(10).offset(offset).all()
    db.commit()
    return orders

@router.get("/getOrder/{order_id}",response_model = schemas.OrderRead)
def getOrder(id: int,db: Session = Depends(get_db),user = Depends(userRole)):
    if user.role != "customer":
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail="Customer access required")
    order = db.query(models.Order).filter(models.Order.id == id).first()
    if order is None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail="Order not found")
    db.commit()
    return order

@router.put("/updateOrder/{order_id}",response_model = schemas.OrderRead)
def updateOrder(id: int, order_update: schemas.OrderCreate, db: Session = Depends(get_db),user = Depends(userRole)):
    if user.role != "customer":
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail="Customer access required")
    order = db.query(models.Order).filter(models.Order.id == id).first()
    if not order:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail="Order not found")
    setattr(order, "user_id", order_update.user_id)
    setattr(order, "product_id", order_update.product_id)
    setattr(order, "quantity", order_update.quantity)
    setattr(order,"address",order_update.address)
    db.commit()
    db.refresh(order)
    return order

@router.delete("/deleteOrder/{order_id}",response_model = schemas.OrderRead)
def deleteOrder(id: int, db: Session = Depends(get_db),user = Depends(userRole)):
    if user.role != "customer":
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail="Customer access required")
    order = db.query(models.Order).filter(models.Order.id == id).first()
    if not order:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail="Order not found")
    db.delete(order)
    db.commit()
    return order

