from fastapi import FastAPI
from .schemas import schemas
from .models import models
from .database import engine
from .routers import users, product, categories

  


app = FastAPI()
models.Base.metadata.create_all(bind=engine)

app.include_router(users.router)
app.include_router(product.router)
app.include_router(categories.router)
