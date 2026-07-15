from app.services.browser_manager import create_browser_context
from app.utils.resource_blocker import block_unnecessary_resources
from logs.logger import logger


def check_reliance_stock(product_url: str):
    """
    Checks whether a Reliance Digital product is in stock.

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
            "access denied",
            "forbidden",
            "captcha",
            "robot check",
            "page not found",
            "something went wrong",
        ]

        if any(
            keyword in page_title.lower()
            for keyword in blocked_page_keywords
        ):
            logger.warning(
                "Reliance Digital returned a blocked or invalid page."
            )
            return None

        try:
            body_text = (
                page.locator("body")
                .inner_text(timeout=5000)
                .strip()
                .lower()
            )
        except Exception:
            body_text = ""

        add_to_cart = page.get_by_text(
            "Add to Cart",
            exact=True,
        ).count()

        buy_now = page.get_by_text(
            "Buy Now",
            exact=True,
        ).count()

        add_to_cart_buttons = page.locator(
            "button:has-text('Add to Cart'), "
            "a:has-text('Add to Cart')"
        ).count()

        buy_now_buttons = page.locator(
            "button:has-text('Buy Now'), "
            "a:has-text('Buy Now')"
        ).count()

        out_of_stock = page.get_by_text(
            "Out of Stock",
            exact=True,
        ).count()

        sold_out = page.get_by_text(
            "Sold Out",
            exact=True,
        ).count()

        unavailable = page.get_by_text(
            "Currently Unavailable",
            exact=True,
        ).count()

        notify_me = page.get_by_text(
            "Notify Me",
            exact=True,
        ).count()

        logger.info(f"Add To Cart  : {add_to_cart}")
        logger.info(f"Buy Now      : {buy_now}")
        logger.info(f"Cart Buttons : {add_to_cart_buttons}")
        logger.info(f"Buy Buttons  : {buy_now_buttons}")
        logger.info(f"Out of Stock : {out_of_stock}")
        logger.info(f"Sold Out     : {sold_out}")
        logger.info(f"Unavailable  : {unavailable}")
        logger.info(f"Notify Me    : {notify_me}")

        out_of_stock_keywords = [
            "currently unavailable",
            "temporarily unavailable",
            "out of stock",
            "sold out",
            "notify me when available",
            "notify me",
            "product unavailable",
        ]

        if (
            out_of_stock > 0
            or sold_out > 0
            or unavailable > 0
            or notify_me > 0
            or any(
                keyword in body_text
                for keyword in out_of_stock_keywords
            )
        ):
            logger.warning("Product is OUT OF STOCK")
            return False

        if (
            add_to_cart > 0
            or buy_now > 0
            or add_to_cart_buttons > 0
            or buy_now_buttons > 0
        ):
            logger.info("Product is IN STOCK")
            return True

        in_stock_keywords = [
            "add to cart",
            "buy now",
            "available",
            "in stock",
        ]

        if any(
            keyword in body_text
            for keyword in in_stock_keywords
        ):
            logger.info(
                "Product is IN STOCK "
                "(detected using page-text fallback)"
            )
            return True

        logger.warning(
            "Unable to determine Reliance Digital stock status."
        )
        return None

    except Exception as error:
        logger.exception(
            f"Reliance tracker error: {error}"
        )
        return None

    finally:
        # Sirf context close hoga.
        # Shared worker browser open rahega.
        if context is not None:
            try:
                context.close()
            except Exception:
                pass