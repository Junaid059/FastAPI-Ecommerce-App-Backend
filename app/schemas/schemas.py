from fastapi import FastAPI
from pydantic import BaseModel, Field 


class UserBase(BaseModel):
    email: str
    password: str = Field(..., min_length=3, max_length=128)

class UserCreate(UserBase):
    pass

    class Config:
        from_attributes = True

class ProductBase(BaseModel):
    name: str
    description: str
    price: int
    image_url: str
    category: str
    stock: int

class ProductCreate(ProductBase):
    pass

    class Config:
        from_attributes = True

class OrderCreate(BaseModel):
    user_id: int
    product_id: int
    quantity: int
    address: str
    

class OrderRead(OrderCreate):
    order_id: int
    user_id: int
    product_id: int
    quantity: int
    address: str

    class Config:
        from_attributes = True


class Category(BaseModel):
    name: str

class CategoryCreate(Category):
    pass

class CategoryRead(Category):
    id: int    

    class Config:
        from_attributes = True

class RatingCreate(BaseModel):
    product_id: int
    user_id: int
    rating: int

class RatingRead(BaseModel):
    id: int
    product_id: int
    user_id: int
    rating: int

    class Config:
        from_attributes = True

class CommentCreate(BaseModel):
    product_id: int 
    user_id: int
    comment: str

class CommentRead(BaseModel):
    id: int
    product_id: int 
    user_id: int
    content: str

    class Config:
      from_attributes = True

class CartCreate(BaseModel):
    user_id: int
    product_id: int
    quantity: int

class CartRead(BaseModel):
    id: int
    user_id: int
    product_id: int
    quantity: int

    class Config:
        from_attributes = True          
    
class TokenData(BaseModel):
    id: int | None = None
    role: str | None = None


    class Config:
        from_attributes = True

class WishlistCreate(BaseModel):
    product_id:int

class WishListRead(BaseModel):
    id:int
    user_id:int
    product_id:int

    class config:
        from_attributes = True            


class Token(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str