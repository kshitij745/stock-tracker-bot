from sqlalchemy import Column, Integer, String, Boolean
from app.database.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(String(50), unique=True, nullable=False)
    username = Column(String(100))
    full_name = Column(String(100))
    is_admin = Column(Boolean, default=False)