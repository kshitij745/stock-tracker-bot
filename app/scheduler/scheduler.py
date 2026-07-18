import atexit
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from time import perf_counter

from apscheduler.schedulers.background import BackgroundScheduler

from app.database.database import SessionLocal
from app.models.product import Product
from app.services.product_service import check_product


MAX_WORKERS = 2
SCHEDULER_INTERVAL_SECONDS = 10


# Persistent executor:
# Application ke lifetime me same worker threads reuse honge.
executor = ThreadPoolExecutor(
    max_workers=MAX_WORKERS,
    thread_name_prefix="stock-worker",
)

scheduler = BackgroundScheduler()

last_cycle_completed_at = None
last_cycle_duration_seconds = None


def check_single_product(product_id: int):
    """
    Ek product ko separate database session aur worker thread me
    check karta hai.
    """

    db = SessionLocal()

    try:
        product = (
            db.query(Product)
            .filter(Product.id == product_id)
            .first()
        )

        if not product:
            return {
                "product_id": product_id,
                "product_name": "Unknown",
                "success": False,
                "message": "Product not found",
            }

        product_name = product.product_name

        print(f"Checking: {product_name}")

        checked_product = check_product(
            db=db,
            product=product,
        )

        return {
            "product_id": product_id,
            "product_name": product_name,
            "success": True,
            "in_stock": checked_product.in_stock,
        }

    except Exception as error:
        db.rollback()

        return {
            "product_id": product_id,
            "product_name": "Unknown",
            "success": False,
            "message": str(error),
        }

    finally:
        db.close()


def check_all_products():
    """
    Sabhi active products ko persistent worker threads me
    parallel check karta hai.
    """

    global last_cycle_completed_at
    global last_cycle_duration_seconds

    cycle_start_time = perf_counter()

    db = SessionLocal()

    try:
        product_ids = [
            product_id
            for (product_id,) in (
                db.query(Product.id)
                .filter(Product.is_active == True)
                .all()
            )
        ]

    except Exception as error:
        print(f"Scheduler database error: {error}")
        return

    finally:
        db.close()

    total_products = len(product_ids)

    if total_products == 0:
        print("\nNo active products found.")

        last_cycle_duration_seconds = round(
            perf_counter() - cycle_start_time,
            2,
        )

        last_cycle_completed_at = datetime.now()

        return

    print(
        f"\nChecking {total_products} active products "
        f"with {MAX_WORKERS} persistent workers..."
    )

    successful_checks = 0
    failed_checks = 0

    # Global persistent executor use ho raha hai.
    # Yahan "with ThreadPoolExecutor" nahi lagana.
    futures = {
        executor.submit(
            check_single_product,
            product_id,
        ): product_id
        for product_id in product_ids
    }

    for future in as_completed(futures):
        product_id = futures[future]

        try:
            result = future.result()

            if result["success"]:
                successful_checks += 1

                stock_status = result.get("in_stock")

                if stock_status is True:
                    status = "IN STOCK"

                elif stock_status is False:
                    status = "OUT OF STOCK"

                else:
                    status = "UNKNOWN"

                print(
                    f"Completed: {result['product_name']} "
                    f"- {status}"
                )

            else:
                failed_checks += 1

                print(
                    f"Failed Product ID {product_id}: "
                    f"{result['message']}"
                )

        except Exception as error:
            failed_checks += 1

            print(
                f"Worker Error for Product ID "
                f"{product_id}: {error}"
            )

    last_cycle_duration_seconds = round(
        perf_counter() - cycle_start_time,
        2,
    )

    last_cycle_completed_at = datetime.now()

    print(
        "\nScheduler cycle completed."
        f"\nSuccessful: {successful_checks}"
        f"\nFailed: {failed_checks}"
        f"\nTotal: {total_products}"
        f"\nDuration: {last_cycle_duration_seconds} seconds"
    )


def start_scheduler():
    """
    Scheduler ko start karta hai.
    """

    if scheduler.running:
        print("Scheduler is already running.")
        return

    scheduler.add_job(
        check_all_products,
        trigger="interval",
        seconds=SCHEDULER_INTERVAL_SECONDS,
        id="stock_checker",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )

    scheduler.start()

    print(
        f"Scheduler Started: every "
        f"{SCHEDULER_INTERVAL_SECONDS} seconds, "
        f"{MAX_WORKERS} persistent workers"
    )


def enable_monitoring():
    """
    Scheduler job ko resume karta hai.
    """

    job = scheduler.get_job("stock_checker")

    if not scheduler.running:
        start_scheduler()
        return True

    if not job:
        scheduler.add_job(
            check_all_products,
            trigger="interval",
            seconds=SCHEDULER_INTERVAL_SECONDS,
            id="stock_checker",
            replace_existing=True,
            max_instances=1,
            coalesce=True,
        )

    scheduler.resume_job("stock_checker")

    return True


def disable_monitoring():
    """
    Scheduler job ko temporarily pause karta hai.
    """

    job = scheduler.get_job("stock_checker")

    if not job:
        return False

    scheduler.pause_job("stock_checker")

    return True


def is_monitoring_enabled():
    """
    Monitoring ON ya OFF return karta hai.
    """

    if not scheduler.running:
        return False

    job = scheduler.get_job("stock_checker")

    if not job:
        return False

    return job.next_run_time is not None


def get_scheduler_status():
    """
    Telegram Settings ke liye scheduler details return karta hai.
    """

    db = SessionLocal()

    try:
        active_products = (
            db.query(Product)
            .filter(Product.is_active == True)
            .count()
        )

    finally:
        db.close()

    return {
        "scheduler_running": scheduler.running,
        "monitoring_enabled": is_monitoring_enabled(),
        "interval_seconds": SCHEDULER_INTERVAL_SECONDS,
        "workers": MAX_WORKERS,
        "active_products": active_products,
        "last_cycle_completed_at": last_cycle_completed_at,
        "last_cycle_duration_seconds": (
            last_cycle_duration_seconds
        ),
    }


def update_scheduler_interval(seconds: int):
    """
    Running scheduler job ka interval update karta hai.
    """

    global SCHEDULER_INTERVAL_SECONDS

    allowed_intervals = [
        10,
        30,
        60,
        120,
    ]

    if seconds not in allowed_intervals:
        return False

    SCHEDULER_INTERVAL_SECONDS = seconds

    job = scheduler.get_job("stock_checker")

    if not job:
        return False

    scheduler.reschedule_job(
        "stock_checker",
        trigger="interval",
        seconds=seconds,
    )

    return True


def shutdown_scheduler():
    """
    Application close hone par scheduler aur persistent
    executor ko safely shutdown karta hai.
    """

    try:
        if scheduler.running:
            scheduler.shutdown(wait=False)

    except Exception:
        pass

    try:
        executor.shutdown(
            wait=False,
            cancel_futures=True,
        )

    except Exception:
        pass


atexit.register(shutdown_scheduler)
