# E-Commerce API - Advanced Platform with Stripe Integration

A modern, production-ready e-commerce API built with FastAPI, PostgreSQL, Stripe payments, and async task processing. Features real-time product suggestions, secure authentication, and complete order management.

## Architecture Overview

![E-Commerce Architecture Diagram](ecommerce-architetcural%20diagram.png)

The architecture illustrates the complete system design with all integrated components working together seamlessly.

## Key Features

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
- **payment methods**: Cards
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

## Tech Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| **Framework** | FastAPI | Latest |
| **Database** | PostgreSQL + SQLAlchemy | 14+ |
| **Authentication** | JWT (python-jose) | Latest |
| **Payment** | Stripe API | Test |
| **Async Tasks** | Celery + Redis |
| **Email** | aiosmtplib | Latest |
| **Validation** | Pydantic | Latest |
| **Security** | bcrypt, passlib | Latest |
| **Server** | Uvicorn | Latest |

##  API Endpoints

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


#### 2. Confirm Payment & Create Orders
**Endpoint:** `POST /api/checkout/confirm-payment?session_id=...`

After user completes Stripe payment, call this endpoint to:
- Verify payment with Stripe
- Create Order records
- Update inventory
- Clear cart
- Send confirmation email

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

##  Security Features

### Authentication
- **JWT Tokens**: Stateless, cryptographically signed
- **Token Refresh**: Secure token rotation mechanism
- **Password Hashing**: bcrypt with salt rounds
- **Role-Based Access**: Customer vs Admin vs Seller endpoints

### Data Protection
- **HTTPS/TLS**: Enforce in production
- **SQL Injection Prevention**: SQLAlchemy parameterized queries
- **CORS**: Configure for your frontend domain
- **Rate Limiting**: Implement to prevent abuse


##  Database Schema

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
