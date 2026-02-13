from fastapi import FastAPI
from .models import models
from .database import engine
from .routers import users, product, categories, order, comment, ratings, search, addToCart,wishlists

  


app = FastAPI()
models.Base.metadata.create_all(bind=engine)

app.include_router(users.router)
app.include_router(product.router)
app.include_router(categories.router)
app.include_router(order.router)
app.include_router(comment.router)
app.include_router(ratings.router)
app.include_router(search.router)
app.include_router(addToCart.router)
app.include_router(wishlists.router)


