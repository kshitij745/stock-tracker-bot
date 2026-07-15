from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime
from app.database.database import Base
from datetime import datetime


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)

    product_name = Column(String(255), nullable=False)

    store_name = Column(String(100), nullable=False)

    product_url = Column(String(1000), nullable=False)
    
    affiliate_url = Column(String(1000), nullable=True)

    price = Column(Float, nullable=True)

    in_stock = Column(Boolean, default=False)

    last_checked = Column(DateTime, default=datetime.utcnow)

    last_notification = Column(DateTime, nullable=True)

    is_active = Column(Boolean, default=True)