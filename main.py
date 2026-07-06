from fastapi import FastAPI

from app.database.database import Base, engine
from app.models.user import User
from app.models.product import Product
from app.routes.product import router as product_router
from app.scheduler.scheduler import start_scheduler

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Stock Tracker API")


@app.on_event("startup")
def startup_event():
    start_scheduler()


app.include_router(product_router)


@app.get("/")
def home():
    return {
        "message": "Stock Tracker Running Successfully 🚀"
    }