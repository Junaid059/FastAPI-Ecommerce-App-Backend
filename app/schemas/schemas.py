from fastapi import FastAPI
from pydantic import BaseModel


class UserBase(BaseModel):
    email: str
    password: str

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

class ProductCreate(ProductBase):
    pass

    class Config:
        from_attributes = True

class OrderCreate(BaseModel):
    user_id: int
    product_id: int
    quantity: int

class OrderRead(OrderCreate):
    order_id: int
    user_id: int
    product_id: int
    quantity: int


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





        
