from sqlalchemy import Column, Integer, String

from app.database.database import Base


class AppSetting(Base):
    __tablename__ = "app_settings"

    id = Column(Integer, primary_key=True, default=1)

    scheduler_interval = Column(
        Integer,
        nullable=False,
        default=10,
    )

    notification_mode = Column(
        String(20),
        nullable=False,
        default="once",
    )

    notification_cooldown = Column(
        Integer,
        nullable=False,
        default=0,
    )