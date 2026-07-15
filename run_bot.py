from app.scheduler.scheduler import start_scheduler
from app.telegram.bot import start_bot


if __name__ == "__main__":
    start_scheduler()
    start_bot()