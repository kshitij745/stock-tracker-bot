from sqlalchemy import Column, Integer, String
from app.database.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    telegram_id = Column(String(50), unique=True, nullable=False)

    username = Column(String(100), nullable=True)

    full_name = Column(String(100), nullable=True)

    role = Column(String(20), nullable=False, default="admin")