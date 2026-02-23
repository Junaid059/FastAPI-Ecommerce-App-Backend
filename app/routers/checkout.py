from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import models
from app.schemas import schemas
from app.routers.Oauth2 import getCurrentUser
from app.tasks import send_email
import stripe
import os
from dotenv import load_dotenv

load_dotenv()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY")

if not stripe.api_key:
    raise ValueError("STRIPE_SECRET_KEY environment variable is not set")

router = APIRouter(prefix="/api/checkout", tags=["checkout"])


@router.get("/suggestions", response_model=list[schemas.ProductSuggestionResponse])
def get_product_suggestions(
    db: Session = Depends(get_db),
    user=Depends(getCurrentUser),
    limit: int = 5
):
    """
    Get personalized product suggestions based on user's purchase history.
    
    Returns products from categories the user has previously purchased.
    If no purchase history exists, returns popular products.
    
    **Query Parameters:**
    - limit: Number of suggestions to return (default: 5)
    """
    if user.role != "customer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only customers can view suggestions"
        )
    
    # Get categories from user's past orders
    user_categories = db.query(
        models.Product.category
    ).join(
        models.Order,
        models.Product.id == models.Order.product_id
    ).filter(
        models.Order.user_id == user.id
    ).distinct().all()
    
    if not user_categories:
        # If no purchase history, return popular/recent products
        popular_products = db.query(models.Product).limit(limit).all()
        return popular_products
    
    category_ids = [cat[0] for cat in user_categories]
    
    # Get products from same categories that user hasn't purchased
    purchased_product_ids = db.query(
        models.Order.product_id
    ).filter(
        models.Order.user_id == user.id
    ).all()
    purchased_ids = [p[0] for p in purchased_product_ids]
    
    suggested = db.query(models.Product).filter(
        models.Product.category.in_(category_ids),
        ~models.Product.id.in_(purchased_ids) if purchased_ids else True
    ).limit(limit).all()
    
    return suggested


@router.post("/create-session", response_model=schemas.CheckoutSessionResponse)
def create_checkout_session(
    checkout_data: schemas.CheckoutSessionCreate,
    db: Session = Depends(get_db),
    user=Depends(getCurrentUser)
):
    """
    Create a Stripe checkout session for payment processing.
    
    This endpoint:
    1. Validates cart items
    2. Checks product stock availability
    3. Creates a Stripe session with cart items
    4. Returns session details for frontend redirect
    
    **Request Body:**
    - success_url: Redirect URL after successful payment
    - cancel_url: Redirect URL if payment is cancelled
    - address: Delivery address
    """
    if user.role != "customer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only customers can checkout"
        )
    
    # Get cart items
    cart_items = db.query(models.Cart).filter(
        models.Cart.user_id == user.id
    ).all()
    
    if not cart_items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cart is empty"
        )
    
    # Calculate total and prepare line items for Stripe
    line_items = []
    total_amount = 0
    
    for item in cart_items:
        product = db.query(models.Product).filter(
            models.Product.id == item.product_id
        ).first()
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product {item.product_id} not found"
            )
        
        # Check if enough stock is available
        if product.stock < item.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Not enough stock for {product.name}. Available: {product.stock}, Requested: {item.quantity}"
            )
        
        amount = product.price * item.quantity
        total_amount += amount
        
        line_items.append({
            "price_data": {
                "currency": "usd",
                "product_data": {
                    "name": product.name,
                    "description": product.description or "",
                    "images": [product.image_url] if product.image_url else [],
                },
                "unit_amount": product.price * 100,  # Stripe uses cents
            },
            "quantity": item.quantity,
        })
    
    try:
        # Create Stripe checkout session
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=line_items,
            mode="payment",
            success_url=checkout_data.success_url,
            cancel_url=checkout_data.cancel_url,
            customer_email=user.email,
            metadata={
                "user_id": str(user.id),
                "address": checkout_data.address,
                "total_amount": str(total_amount)
            }
        )
        
        return {
            "session_id": session.id,
            "client_secret": session.client_secret,
            "url": session.url
        }
    
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Stripe error: {str(e)}"
        )


@router.post("/confirm-payment", response_model=schemas.PaymentSuccessResponse)
def confirm_payment(
    session_id: str,
    db: Session = Depends(get_db),
    user=Depends(getCurrentUser)
):
    """
    Confirm successful Stripe payment and create orders.
    
    This endpoint:
    1. Verifies payment status with Stripe
    2. Creates order records from cart items
    3. Updates product stock
    4. Clears user's cart
    5. Sends confirmation email
    
    **Query Parameters:**
    - session_id: Stripe checkout session ID
    """
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        
        if session.payment_status != "paid":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payment not completed"
            )
        
        # Verify the session belongs to the current user
        if str(user.id) != session.metadata.get("user_id"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Payment session does not belong to this user"
            )
        
        # Get cart items
        cart_items = db.query(models.Cart).filter(
            models.Cart.user_id == user.id
        ).all()
        
        if not cart_items:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No items in cart"
            )
        
        # Create orders and update stock
        created_orders = []
        address = session.metadata.get("address", "")
        total_amount = int(session.metadata.get("total_amount", 0))
        
        for item in cart_items:
            product = db.query(models.Product).filter(
                models.Product.id == item.product_id
            ).first()
            
            if product:
                # Create order with Stripe session tracking
                order = models.Order(
                    user_id=user.id,
                    product_id=item.product_id,
                    quantity=item.quantity,
                    address=address,
                    stripe_session_id=session_id,
                    payment_status="paid",
                    total_amount=product.price * item.quantity
                )
                
                # Update product stock
                product.stock -= item.quantity
                
                db.add(order)
                created_orders.append(order)
                
                # Delete from cart
                db.delete(item)
        
        db.commit()
        
        # Send confirmation email asynchronously
        order_details = "\n".join([
            f"- Product: {db.get(models.Product, order.product_id).name}, Qty: {order.quantity}"
            for order in created_orders
        ])
        
        email_body = f"""
        <h2>Order Confirmation</h2>
        <p>Thank you for your purchase!</p>
        <p><strong>Orders:</strong></p>
        <p>{order_details.replace(chr(10), '<br>')}</p>
        <p><strong>Delivery Address:</strong> {address}</p>
        <p><strong>Total Amount:</strong> ${total_amount / 100:.2f}</p>
        <p>Your order will be delivered soon.</p>
        """
        
        send_email.delay(
            subject="Order Confirmation",
            email_to=user.email,
            body=email_body
        )
        
        return {
            "message": "Payment successful and orders created",
            "orders_count": len(created_orders),
            "total_amount": total_amount
        }
    
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Stripe error: {str(e)}"
        )


@router.get("/session/{session_id}")
def get_session_details(
    session_id: str,
    user=Depends(getCurrentUser)
):
    """
    Retrieve Stripe session details for verification.
    """
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        
        return {
            "session_id": session.id,
            "payment_status": session.payment_status,
            "customer_email": session.customer_email,
            "amount_total": session.amount_total,
            "currency": session.currency
        }
    
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Stripe error: {str(e)}"
        )
