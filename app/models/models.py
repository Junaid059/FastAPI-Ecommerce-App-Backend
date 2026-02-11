from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True,autoincrement=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    role = Column(String, default='user')

    orders = relationship("Order", back_populates="user", cascade="all, delete-orphan")
    ratings = relationship("Rating", back_populates="user", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="user", cascade="all, delete-orphan")
    
class Product(Base):
    __tablename__ = "products"
    id = Column(Integer,primary_key = True,index = True,autoincrement=True)
    name = Column(String,nullable=False)
    price = Column(Integer, nullable = False)
    description = Column(String, nullable = True)
    image_url = Column(String, nullable = True)
    category= Column(Integer,ForeignKey("categories.id",ondelete="SET NULL"), nullable=True)

    orders = relationship("Order",lazy="joined", innerjoin=True,back_populates="product", cascade="all, delete-orphan")
    ratings = relationship("Rating",lazy="joined", innerjoin=True,back_populates="product", cascade="all, delete-orphan")
    comments = relationship("Comment",lazy="joined", innerjoin=True,back_populates="product", cascade="all, delete-orphan")

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)

class Rating(Base):
    __tablename__ = "ratings"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    product_id = Column(Integer,ForeignKey("products.id",ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    rating = Column(Integer, nullable=False)

    user = relationship("User",lazy="joined", innerjoin=True,back_populates="ratings")
    product = relationship("Product",lazy="joined", innerjoin=True,back_populates="ratings")

class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    product_id = Column(Integer,ForeignKey("products.id",ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer,ForeignKey("users.id",ondelete="CASCADE"), nullable=False)
    comment = Column(String, nullable=True)

    user = relationship("User",lazy="joined", innerjoin=True,back_populates="comments")
    product = relationship("Product",lazy="joined", innerjoin=True,back_populates="comments")


class Order(Base):
    __tablename__ = "orders"
    order_id = Column(Integer,primary_key = True,index = True,autoincrement=True)
    product_id = Column(Integer,ForeignKey("products.id",ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer,ForeignKey("users.id",ondelete="CASCADE"), nullable=False)
    quantity = Column(Integer, nullable=False)

    user = relationship("User",lazy="joined", innerjoin=True,back_populates="orders")
    product = relationship("Product",lazy="joined", innerjoin=True,back_populates="orders")
