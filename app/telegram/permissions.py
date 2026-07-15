from app.database.database import SessionLocal
from app.models.user import User


def get_user(user_id: int):

    db = SessionLocal()

    try:

        user = (
            db.query(User)
            .filter(User.telegram_id == str(user_id))
            .first()
        )

        return user

    finally:
        db.close()


def is_owner(user_id: int) -> bool:

    user = get_user(user_id)

    if not user:
        return False

    return user.role == "owner"


def is_admin(user_id: int) -> bool:

    user = get_user(user_id)

    if not user:
        return False

    return user.role in ["owner", "admin"]