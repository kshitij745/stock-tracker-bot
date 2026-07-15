from fastapi import FastAPI

from app.database.database import Base, engine
from app.models.user import User
from app.models.product import Product
from app.models.app_setting import AppSetting
from app.routes.product import router as product_router
from app.routes.dashboard import router as dashboard_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Stock Tracker API")

# Dashboard Route
app.include_router(dashboard_router)

# Product APIs
app.include_router(product_router)