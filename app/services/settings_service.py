from sqlalchemy.orm import Session

from app.models.app_setting import AppSetting


DEFAULT_SETTING_ID = 1


def get_app_settings(db: Session) -> AppSetting:
    """
    Global app settings return karta hai.
    Agar settings row missing ho to default row create karta hai.
    """

    settings = (
        db.query(AppSetting)
        .filter(AppSetting.id == DEFAULT_SETTING_ID)
        .first()
    )

    if settings:
        return settings

    settings = AppSetting(
        id=DEFAULT_SETTING_ID,
        scheduler_interval=10,
        notification_mode="once",
        notification_cooldown=0,
    )

    db.add(settings)
    db.commit()
    db.refresh(settings)

    return settings


def update_notification_settings(
    db: Session,
    mode: str,
    cooldown_seconds: int,
) -> AppSetting:
    """
    Notification mode aur cooldown update karta hai.
    """

    allowed_modes = ["once", "repeat"]
    allowed_cooldowns = [0, 10, 60, 300, 1800]

    if mode not in allowed_modes:
        raise ValueError("Invalid notification mode.")

    if cooldown_seconds not in allowed_cooldowns:
        raise ValueError("Invalid notification cooldown.")

    if mode == "once":
        cooldown_seconds = 0

    settings = get_app_settings(db)

    settings.notification_mode = mode
    settings.notification_cooldown = cooldown_seconds

    db.commit()
    db.refresh(settings)

    return settings


def update_saved_scheduler_interval(
    db: Session,
    seconds: int,
) -> AppSetting:
    """
    Scheduler interval ko database me save karta hai.
    """

    allowed_intervals = [10, 30, 60, 120]

    if seconds not in allowed_intervals:
        raise ValueError("Invalid scheduler interval.")

    settings = get_app_settings(db)
    settings.scheduler_interval = seconds

    db.commit()
    db.refresh(settings)

    return settings