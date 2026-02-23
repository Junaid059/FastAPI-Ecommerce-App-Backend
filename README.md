# E-Commerce API - Advanced Platform with Stripe Integration

A modern, production-ready e-commerce API built with FastAPI, PostgreSQL, Stripe payments, and async task processing. Features real-time product suggestions, secure authentication, and complete order management.

## 📋 Architecture Overview

![E-Commerce Architecture Diagram](ecommerce-architetcural%20diagram.png)

The architecture illustrates the complete system design with all integrated components working together seamlessly.

## 🚀 Key Features

### 1. **Authentication & Authorization**
- JWT-based token authentication (Access + Refresh tokens)
- Role-based access control (customer, admin, seller)
- Secure password hashing with bcrypt
- Token refresh mechanism without re-login

### 2. **Product Management**
- Full CRUD operations
- Category-based organization
- Dynamic inventory management with stock tracking
- Image URL support for product display
- Advanced search functionality

### 3. **Smart Product Recommendations**
- AI-based suggestions using purchase history analysis
- Recommends products from previously purchased categories
- Personalized browsing experience
- Cold-start solution with popular products for new users

### 4. **Shopping Cart System**
- Add/update/remove items
- Real-time quantity management
- Persistent cart storage
- Cart validation before checkout

### 5. **Stripe Payment Integration**
- **Secure checkout sessions**: PCI-compliant payment processing
- **Multiple payment methods**: Cards, Apple Pay, Google Pay
- **Real-time payment verification**: Status tracking
- **Session management**: Metadata storage for orders
- **Error handling**: Comprehensive Stripe error management
- **Stock management**: Automatic inventory updates on successful payment

### 6. **Order Management**
- Complete order lifecycle tracking
- Payment status monitoring (pending/paid/failed)
- Stripe session ID correlation
- Address and delivery tracking
- Order history retrieval

### 7. **User Engagement Features**
- **Ratings & Reviews**: 5-star product ratings
- **Comments**: Detailed product feedback
- **Wishlist**: Save favorite products for later
- **Order Tracking**: Real-time order status

### 8. **Async Email Notifications**
- Celery-based background task processing
- Redis-backed task queue
- Order confirmation emails
- Payment receipts
- User notification alerts
- Non-blocking task execution

## 📦 Tech Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| **Framework** | FastAPI | Latest |
| **Database** | PostgreSQL + SQLAlchemy | 14+ |
| **Authentication** | JWT (python-jose) | Latest |
| **Payment** | Stripe API | Live/Test |
| **Async Tasks** | Celery + Redis | 5.6.2 / Latest |
| **Email** | aiosmtplib | Latest |
| **Validation** | Pydantic | Latest |
| **Security** | bcrypt, passlib | Latest |
| **Server** | Uvicorn | Latest |

## 🔧 Installation & Setup

### ⚡ Quick Start (5 Minutes)

#### Prerequisites
- Python 3.10+
- PostgreSQL 13+
- Redis (for Celery)
- Stripe account (free tier at stripe.com)

#### Step 1: Clone & Setup Virtual Environment
```bash
cd E-comm
python -m venv myenv
myenv\Scripts\activate  # Windows
source myenv/bin/activate  # Linux/Mac
```

#### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

#### Step 3: Configure Environment Variables
Create `.env` file in project root (use `.env.example` as template):
```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/ecommerce_db

# JWT Secrets
SECRET_KEY=your-super-secret-key-change-this
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Stripe API Keys (from https://dashboard.stripe.com/apikeys)
STRIPE_SECRET_KEY=sk_test_your-secret-key-here
STRIPE_PUBLISHABLE_KEY=pk_test_your-public-key-here

# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_FROM=noreply@ecommerce.com

# Redis Configuration
REDIS_URL=redis://localhost:6379/0
```

#### Step 4: Create Database
```bash
# Using PostgreSQL CLI
psql -U postgres -c "CREATE DATABASE ecommerce_db;"
```

#### Step 5: Start Services (3 Terminals)

**Terminal 1 - Redis:**
```bash
redis-server
# or with Docker: docker run -d -p 6379:6379 redis:latest
```

**Terminal 2 - Celery Worker:**
```bash
celery -A app.celery_app worker --loglevel=info
```

**Terminal 3 - FastAPI Server:**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Access API Documentation:** http://localhost:8000/docs

---

## 🎯 API Endpoints

### **Authentication**
```
POST   /api/users/register          Create new user account
POST   /api/users/login             Login and get tokens
POST   /api/users/refresh           Refresh access token
GET    /api/users/me                Get current user profile
```

### **Products**
```
GET    /api/products                List all products (paginated)
POST   /api/products                Create product (admin)
GET    /api/products/{id}           Get product details
PUT    /api/products/{id}           Update product (admin)
DELETE /api/products/{id}           Delete product (admin)
GET    /api/search                  Search products by name/category
```

### **Smart Recommendations**
```
GET    /api/checkout/suggestions    Get personalized product suggestions
        Query: ?limit=5 (default)
```

### **Shopping Cart**
```
POST   /api/cart                    Add item to cart
GET    /api/cart                    Get user's cart
PUT    /api/cart/{item_id}          Update cart item quantity
DELETE /api/cart/{item_id}          Remove item from cart
```

### **Checkout & Payment**
```
POST   /api/checkout/create-session      Create Stripe checkout session
    Request Body: {
        "success_url": "https://yoursite.com/success",
        "cancel_url": "https://yoursite.com/cancel",
        "address": "123 Main St, City, State"
    }

POST   /api/checkout/confirm-payment     Verify & finalize payment
    Query: ?session_id=cs_test_xxxxx

GET    /api/checkout/session/{session_id}  Get payment session details
```

### **Orders**
```
GET    /api/orders                  Get user's orders
GET    /api/orders/{order_id}       Get order details
POST   /api/orders                  Create order (legacy, use checkout)
```

### **Wishlist**
```
POST   /api/wishlist                Add product to wishlist
GET    /api/wishlist                Get user's wishlist
DELETE /api/wishlist/{product_id}   Remove from wishlist
```

### **Ratings & Reviews**
```
POST   /api/ratings                 Add product rating
GET    /api/products/{id}/ratings   Get product ratings
POST   /api/comments                Add product comment
GET    /api/products/{id}/comments  Get product comments
```

### **Categories**
```
GET    /api/categories              List all categories
POST   /api/categories              Create category (admin)
GET    /api/categories/{id}         Get category details
```

## 💳 Stripe Integration - Complete Guide

### Checkout Endpoints - Detailed Implementation

#### 1. Create Checkout Session
**Endpoint:** `POST /api/checkout/create-session`

Creates a secure Stripe checkout session for processing payments.

**Request Body:**
```json
{
  "success_url": "https://yourfrontend.com/success?session_id={CHECKOUT_SESSION_ID}",
  "cancel_url": "https://yourfrontend.com/cancel",
  "address": "123 Main Street, Anytown, USA"
}
```

**Response:**
```json
{
  "session_id": "cs_test_xxxxx",
  "client_secret": "xxxxx",
  "url": "https://checkout.stripe.com/pay/cs_test_xxxxx"
}
```

**Example cURL:**
```bash
curl -X POST "http://localhost:8000/api/checkout/create-session" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "success_url": "http://localhost:3000/success?session_id={CHECKOUT_SESSION_ID}",
    "cancel_url": "http://localhost:3000/cancel",
    "address": "123 Main St, City, State"
  }'
```

#### 2. Confirm Payment & Create Orders
**Endpoint:** `POST /api/checkout/confirm-payment?session_id=...`

After user completes Stripe payment, call this endpoint to:
- Verify payment with Stripe
- Create Order records
- Update inventory
- Clear cart
- Send confirmation email

**Response:**
```json
{
  "message": "Payment successful and orders created",
  "orders_count": 3,
  "total_amount": 29999
}
```

**Example cURL:**
```bash
curl -X POST "http://localhost:8000/api/checkout/confirm-payment?session_id=cs_test_xxxxx" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### 3. Get Product Recommendations
**Endpoint:** `GET /api/checkout/suggestions?limit=5`

Returns personalized product suggestions based on user's purchase history.

**Response:**
```json
[
  {
    "id": 2,
    "name": "Product Name",
    "description": "Product Description",
    "price": 9999,
    "image_url": "https://...",
    "category": 1,
    "stock": 50
  }
]
```

### Test Payment Cards

| Card Type | Card Number | Behavior |
|-----------|-------------|----------|
| **Success** | `4242 4242 4242 4242` | ✅ Payment succeeds |
| **Declined** | `4000 0000 0000 0002` | ❌ Payment declined |
| **Expired** | `4000 0000 0000 0069` | ❌ Card expired |
| **3D Secure** | `4000 0025 0000 3155` | 🔐 3D Secure flow |

**Use with:** Any future expiry date (MM/YY) and any 3-digit CVC

---

## 💡 Why We Kept Redis & Celery

### The Problem Without Async
```
Timeline WITHOUT async email:
POST /checkout/confirm-payment
├─ Verify payment (100ms)
├─ Create orders (50ms)
├─ Update stock (50ms)
├─ SEND EMAIL (2-5 seconds) ⏱️ BLOCKS USER
└─ Response time: 5+ seconds 😞
```

### The Solution With Celery
```
Timeline WITH async (Celery + Redis):
POST /checkout/confirm-payment
├─ Verify payment (100ms)
├─ Create orders (50ms)
├─ Update stock (50ms)
├─ Queue email task to Redis (1ms)
└─ Response time: 200ms ✅ INSTANT!

Meanwhile (in background):
Celery Worker → Sends email (2-5 seconds)
```

**Benefits:**
- ✅ **Better UX**: Users get instant feedback
- ✅ **Scalability**: Add more workers as needed
- ✅ **Reliability**: Automatic retry on failure
- ✅ **Future-proof**: Easy to add more async tasks (SMS, notifications, etc.)

## Stripe Integration Flow

### Payment Processing Sequence

```
1. USER ADDS ITEMS TO CART
   └─> Save in Cart table

2. USER INITIATES CHECKOUT
   └─> POST /api/checkout/create-session
       ├─> Validate cart items
       ├─> Check product stock
       ├─> Calculate total amount
       └─> Create Stripe session (returns session_id & url)

3. STRIPE CHECKOUT PAGE
   └─> User enters payment details
   └─> Stripe processes payment

4. PAYMENT SUCCESS
   └─> User redirected to success_url with session_id
   └─> POST /api/checkout/confirm-payment?session_id=...
       ├─> Verify payment with Stripe API
       ├─> Create Order records
       ├─> Update product stock (inventory)
       ├─> Clear cart items
       ├─> Send confirmation email (async via Celery)
       └─> Return success response

5. ASYNC EMAIL TASK
   └─> Celery worker picks up task
   └─> Send order confirmation email
   └─> Log delivery status
```

### Test Payment Cards
```
Success:  4242 4242 4242 4242
Decline:  4000 0000 0000 0002
3D Sec:   4000 0025 0000 3155
```
*Any future date and any 3-digit CVC*

---

## 🧪 Testing & Examples

### Setup Stripe Test Environment

1. **Get Stripe Test Keys:**
   - Visit: https://dashboard.stripe.com/apikeys
   - Copy Secret Key (starts with `sk_test_`)
   - Copy Publishable Key (starts with `pk_test_`)
   - Add to `.env` file

2. **Test Mode is Default:** Your account starts in test mode with test keys

### Complete Checkout Flow Example

**1. Register User:**
```bash
curl -X POST "http://localhost:8000/api/users/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123"
  }'
```

**2. Login:**
```bash
curl -X POST "http://localhost:8000/api/users/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123"
  }'
# Save the access_token from response
```

**3. Add Product to Cart:**
```bash
curl -X POST "http://localhost:8000/api/cart" \
  -H "Authorization: Bearer ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": 1,
    "quantity": 2
  }'
```

**4. Get Product Suggestions:**
```bash
curl -X GET "http://localhost:8000/api/checkout/suggestions?limit=5" \
  -H "Authorization: Bearer ACCESS_TOKEN"
```

**5. Create Checkout Session:**
```bash
curl -X POST "http://localhost:8000/api/checkout/create-session" \
  -H "Authorization: Bearer ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "success_url": "http://localhost:3000/success?session_id={CHECKOUT_SESSION_ID}",
    "cancel_url": "http://localhost:3000/cancel",
    "address": "123 Main St, Anytown, USA"
  }'
# Save the session_id and open the returned url
```

**6. Complete Payment:**
- In Stripe checkout page, use test card: `4242 4242 4242 4242`
- Any future expiry date (e.g., 12/25)
- Any 3-digit CVC (e.g., 123)
- Click "Pay"

**7. Confirm Payment:**
```bash
curl -X POST "http://localhost:8000/api/checkout/confirm-payment?session_id=SESSION_ID" \
  -H "Authorization: Bearer ACCESS_TOKEN"
```

**Response:**
```json
{
  "message": "Payment successful and orders created",
  "orders_count": 1,
  "total_amount": 19998
}
```

### Test Different Card Scenarios

**Declined Card:**
```bash
# Use card: 4000 0000 0000 0002
# Same flow as above - payment will be declined
```

**3D Secure Card:**
```bash
# Use card: 4000 0025 0000 3155
# You'll go through 3D Secure authentication flow
```

---

## 🔒 Security Features

### Authentication
- **JWT Tokens**: Stateless, cryptographically signed
- **Token Refresh**: Secure token rotation mechanism
- **Password Hashing**: bcrypt with salt rounds
- **Role-Based Access**: Customer vs Admin endpoints

### Data Protection
- **HTTPS/TLS**: Enforce in production
- **SQL Injection Prevention**: SQLAlchemy parameterized queries
- **CORS**: Configure for your frontend domain
- **Rate Limiting**: Implement to prevent abuse

### Payment Security
- **PCI Compliance**: Stripe handles card data
- **No Card Storage**: Never store sensitive payment info
- **Session Validation**: Verify user ownership of sessions
- **Metadata Verification**: Correlate payments with orders

### Best Practices
```python
# ✅ Environment variables for secrets
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")

# ✅ Verify user ownership
if str(user.id) != session.metadata.get("user_id"):
    raise HTTPException(status_code=403, detail="Unauthorized")

# ✅ Handle Stripe errors gracefully
except stripe.error.StripeError as e:
    raise HTTPException(status_code=400, detail=str(e))
```

## 📊 Database Schema

```
┌─────────────────┐
│     USERS       │
├─────────────────┤
│ id (PK)         │
│ email (UNIQUE)  │
│ password        │
│ role            │◄─────┐
│ is_active       │      │
│ refresh_token   │      │
└─────────────────┘      │
        │                │
        │                │
        └────────┬───────┘
                 │
     ┌───────────┼───────────┐
     │           │           │
     ▼           ▼           ▼
┌─────────┐ ┌────────┐ ┌──────────┐
│ ORDERS  │ │ CART   │ │ WISHLIST │
└─────────┘ └────────┘ └──────────┘
     │           │           │
     └───────────┼───────────┘
                 │
           ┌─────▼──────┐
           │  PRODUCTS  │
           ├────────────┤
           │ id (PK)    │
           │ name       │
           │ price      │
           │ stock      │
           │ category   │
           └────────────┘
                 │
                 ▼
         ┌───────────────┐
         │   CATEGORIES  │
         │ ┌───────────┐ │
         │ │ RATINGS   │ │
         │ │ COMMENTS  │ │
         │ └───────────┘ │
         └───────────────┘
```

## ⚙️ Configuration Reference

### Order Model Fields
```python
Order:
  ├─ order_id: int (Primary Key)
  ├─ product_id: int (Foreign Key → Products)
  ├─ user_id: int (Foreign Key → Users)
  ├─ quantity: int
  ├─ address: str
  ├─ stripe_session_id: str (NEW - Stripe correlation)
  ├─ payment_status: str (NEW - pending/paid/failed)
  └─ total_amount: int (NEW - order total in cents)
```

### Celery Task Example
```python
# Async email task
@celery_app.task
def send_email(subject: str, email_to: str, body: str):
    # Non-blocking email sending
    # Called like: send_email.delay(subject, email, body)
```

## 🧪 Testing the Payment Flow

### 1. Register & Login
```bash
curl -X POST "http://localhost:8000/api/users/register" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'
```

### 2. Add Products to Cart
```bash
curl -X POST "http://localhost:8000/api/cart" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"product_id": 1, "quantity": 2}'
```

### 3. Create Checkout Session
```bash
curl -X POST "http://localhost:8000/api/checkout/create-session" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "success_url": "http://localhost:3000/success",
    "cancel_url": "http://localhost:3000/cancel",
    "address": "123 Main St, Anytown, USA"
  }'
```

### 4. Confirm Payment
```bash
curl -X POST "http://localhost:8000/api/checkout/confirm-payment?session_id=cs_test_xxxxx" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 📚 Key Decisions

### Why Celery + Redis?
- **Async Email Delivery**: Don't block payment responses
- **Scalability**: Queue tasks across multiple workers
- **Reliability**: Retry failed tasks automatically
- **Monitoring**: Track task execution status

### Why PostgreSQL?
- **ACID Compliance**: Reliable transactions
- **Relationships**: Complex queries with JOINs
- **Performance**: Optimized for large datasets
- **Reliability**: Industry standard

### Why Stripe?
- **Security**: PCI DSS Level 1 compliance
- **Features**: Webhooks, subscriptions, disputes
- **Global**: Support for 195+ countries
- **Documentation**: Excellent developer experience

## 🚨 Troubleshooting Guide

### Installation Issues

**ModuleNotFoundError: No module named 'stripe'**
```bash
# Solution: Install dependencies
pip install -r requirements.txt --upgrade
```

**PostgreSQL Connection Error**
```bash
# Check if PostgreSQL is running
psql -U postgres -c "SELECT version();"

# Create database if not exists
psql -U postgres -c "CREATE DATABASE ecommerce_db;"

# Verify DATABASE_URL in .env
echo $DATABASE_URL  # Linux/Mac
echo %DATABASE_URL%  # Windows
```

**Redis Connection Refused**
```bash
# Start Redis server
redis-server

# Or with Docker
docker run -d -p 6379:6379 redis:latest

# Test Redis connection
redis-cli ping  # Should return PONG
```

### Runtime Issues

**Celery Worker Not Picking Up Tasks**
```bash
# Check if worker is running
# In separate terminal, start worker:
celery -A app.celery_app worker --loglevel=info

# Verify Redis is running:
redis-cli ping

# Check Celery broker URL in .env:
REDIS_URL=redis://localhost:6379/0
```

**STRIPE_SECRET_KEY not set**
```bash
# Solution: Add to .env file
STRIPE_SECRET_KEY=sk_test_your_key_here

# Restart FastAPI server
# Make sure .env file exists and is properly formatted
```

**Cart is Empty Error**
```bash
# Add products to cart before checkout
curl -X POST "http://localhost:8000/api/cart" \
  -H "Authorization: Bearer TOKEN" \
  -d '{"product_id": 1, "quantity": 1}'
```

**Payment Declined**
```bash
# Probable causes:
# 1. Using production card instead of test card
# 2. Using expired card (use future date)
# 3. Card details entered incorrectly

# Solution: Use test card 4242 4242 4242 4242
# With any future date and any 3-digit CVC
```

**Email Not Sending**
```bash
# Check email configuration in .env:
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password  # Not your regular password
MAIL_FROM=noreply@ecommerce.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587

# For Gmail: Use App Password (not regular password)
# Enable "Less secure app access" or use Google App Passwords:
# https://myaccount.google.com/apppasswords

# Check Celery worker is running
celery -A app.celery_app worker --loglevel=info
```

**Not Enough Stock Error**
```bash
# Check available stock before adding to cart
curl -X GET "http://localhost:8000/api/products/1"

# Update stock in database if needed
# Or reduce quantity in cart
```

**Session Not Found**
```bash
# Verify session_id is correct
# Check Stripe dashboard: https://dashboard.stripe.com/payments

# Ensure you're using correct API key
# Test key vs Production key mismatch
```

---

## 🔄 Deployment Checklist

### Pre-Deployment
- [ ] All dependencies installed: `pip install -r requirements.txt`
- [ ] Database created and migrations applied
- [ ] Redis server configured and running
- [ ] Celery worker ready to start
- [ ] Environment variables configured

### Environment Setup
- [ ] Set all required variables in `.env`
- [ ] Use production Stripe API keys (not test keys)
- [ ] Secure SECRET_KEY for JWT (use strong random string)
- [ ] Configure email service credentials
- [ ] Set CORS for your frontend domain only

### Database & Services
- [ ] PostgreSQL configured and accessible
- [ ] Redis configured and accessible
- [ ] Database backups enabled
- [ ] Celery task monitoring set up

### Stripe Configuration
- [ ] Use production API keys (sk_live_xxx, pk_live_xxx)
- [ ] Configure Stripe webhooks for payment events
- [ ] Test payment flow with real cards
- [ ] Set up dispute handling process

### Security
- [ ] Enable HTTPS/TLS (mandatory for production)
- [ ] Configure CORS properly
- [ ] Set `DEBUG=False` in production
- [ ] Hide error traces from frontend
- [ ] Implement rate limiting
- [ ] Add request validation

### Monitoring & Logging
- [ ] Set up application logging
- [ ] Monitor Celery queue
- [ ] Monitor Redis memory usage
- [ ] Set up alerts for failures
- [ ] Monitor Stripe for issues

### Testing
- [ ] Test complete payment flow
- [ ] Test with different card types
- [ ] Test error scenarios
- [ ] Load test the API
- [ ] Test email notifications

---

## 📞 Support & Contact

For issues, questions, or feature requests:
- Open an issue on GitHub
- Check existing documentation
- Review Stripe API docs: https://stripe.com/docs
- Check FastAPI docs: https://fastapi.tiangolo.com

## 📄 License

MIT License - Feel free to use in your projects

---

**Happy coding! 🚀**
