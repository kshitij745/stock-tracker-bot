from app.services.browser_manager import create_browser_context
from app.utils.resource_blocker import block_unnecessary_resources
from logs.logger import logger


def check_amazon_stock(product_url: str):
    """
    Checks whether an Amazon product is in stock.

    Returns:
        True  -> Product is in stock
        False -> Product is out of stock
        None  -> Unable to determine stock status
    """

    context = None

    try:
        context = create_browser_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/137.0.0.0 Safari/537.36"
            ),
            headless=True,
        )

        context.route(
            "**/*",
            block_unnecessary_resources,
        )

        page = context.new_page()

        page.goto(
            product_url,
            wait_until="domcontentloaded",
            timeout=30000,
        )

        page.wait_for_timeout(4000)

        page_title = page.title().strip()

        logger.info(f"Page Title: {page_title}")

        blocked_page_keywords = [
            "robot check",
            "captcha",
            "sorry! something went wrong",
            "page not found",
            "access denied",
            "forbidden",
        ]

        if any(
            keyword in page_title.lower()
            for keyword in blocked_page_keywords
        ):
            logger.warning(
                "Amazon blocked the request or returned an invalid page."
            )
            return None

        availability_text = ""

        availability = page.locator("#availability")

        if availability.count() > 0:
            try:
                availability_text = (
                    availability.first
                    .inner_text(timeout=5000)
                    .strip()
                    .lower()
                )

            except Exception:
                availability_text = ""

        logger.info(
            f"Availability Text: "
            f"{availability_text or 'Not Found'}"
        )

        add_to_cart = page.locator(
            "#add-to-cart-button"
        ).count()

        buy_now = page.locator(
            "#buy-now-button"
        ).count()

        in_stock = page.get_by_text(
            "In stock",
            exact=True,
        ).count()

        only_left = page.locator(
            "#availability"
        ).get_by_text(
            "Only",
            exact=False,
        ).count()

        unavailable = page.get_by_text(
            "Currently unavailable",
            exact=True,
        ).count()

        logger.info(f"Add To Cart : {add_to_cart}")
        logger.info(f"Buy Now     : {buy_now}")
        logger.info(f"In Stock    : {in_stock}")
        logger.info(f"Only Left   : {only_left}")
        logger.info(f"Unavailable : {unavailable}")

        out_of_stock_keywords = [
            "currently unavailable",
            "temporarily out of stock",
            "out of stock",
            "not available",
        ]

        if any(
            keyword in availability_text
            for keyword in out_of_stock_keywords
        ):
            logger.warning("Product is OUT OF STOCK")
            return False

        in_stock_keywords = [
            "in stock",
            "only",
            "available to ship",
        ]

        if any(
            keyword in availability_text
            for keyword in in_stock_keywords
        ):
            logger.info("Product is IN STOCK")
            return True

        if unavailable > 0:
            logger.warning("Product is OUT OF STOCK")
            return False

        if (
            add_to_cart > 0
            or buy_now > 0
            or in_stock > 0
            or only_left > 0
        ):
            logger.info("Product is IN STOCK")
            return True

        logger.warning(
            "Unable to determine Amazon stock status."
        )
        return None

    except Exception as error:
        logger.exception(
            f"Amazon tracker error: {error}"
        )
        return None

    finally:
        # Sirf fresh context close hoga.
        # Reusable worker browser open rahega.
        if context is not None:
            try:
                context.close()
            except Exception:
                pass