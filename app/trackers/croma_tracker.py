from app.services.browser_manager import create_browser_context
from app.utils.resource_blocker import block_unnecessary_resources
from logs.logger import logger

def check_croma_stock(product_url: str):
    """
    Checks whether a Croma product is in stock.

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
                "Chrome/138.0.0.0 Safari/537.36"
            ),
            headless=False,
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

        page.wait_for_timeout(5000)

        page_title = page.title().strip()

        logger.info(f"Page Title: {page_title}")

        try:
            body_text = (
                page.locator("body")
                .inner_text(timeout=5000)
                .strip()
                .lower()
            )

        except Exception:
            body_text = ""

        blocked_page_keywords = [
            "access denied",
            "request blocked",
            "forbidden",
            "captcha",
            "robot check",
            "security check",
            "temporarily blocked",
        ]

        if (
            any(
                keyword in page_title.lower()
                for keyword in blocked_page_keywords
            )
            or any(
                keyword in body_text
                for keyword in blocked_page_keywords
            )
        ):
            logger.warning(
                "Croma blocked the request. "
                "A working proxy is required."
            )
            return None

        invalid_page_keywords = [
            "page not found",
            "something went wrong",
            "product not found",
            "404",
        ]

        if any(
            keyword in page_title.lower()
            for keyword in invalid_page_keywords
        ):
            logger.warning(
                "Croma returned an invalid product page."
            )
            return None

        buy_now = page.get_by_text(
            "Buy Now",
            exact=True,
        ).count()

        add_to_cart = page.get_by_text(
            "Add to Cart",
            exact=True,
        ).count()

        add_to_cart_caps = page.get_by_text(
            "ADD TO CART",
            exact=True,
        ).count()

        button_buy_now = page.locator(
            "button:has-text('Buy Now'), "
            "a:has-text('Buy Now')"
        ).count()

        button_add_to_cart = page.locator(
            "button:has-text('Add to Cart'), "
            "button:has-text('ADD TO CART'), "
            "a:has-text('Add to Cart'), "
            "a:has-text('ADD TO CART')"
        ).count()

        out_of_stock = page.get_by_text(
            "Out of Stock",
            exact=True,
        ).count()

        unavailable = page.get_by_text(
            "Currently Unavailable",
            exact=True,
        ).count()

        sold_out = page.get_by_text(
            "Sold Out",
            exact=True,
        ).count()

        notify_me = page.get_by_text(
            "Notify Me",
            exact=True,
        ).count()

        logger.info(f"Buy Now        : {buy_now}")
        logger.info(f"Add To Cart    : {add_to_cart}")
        logger.info(f"ADD TO CART    : {add_to_cart_caps}")
        logger.info(f"Buy Buttons    : {button_buy_now}")
        logger.info(f"Cart Buttons   : {button_add_to_cart}")
        logger.info(f"Out Of Stock   : {out_of_stock}")
        logger.info(f"Unavailable    : {unavailable}")
        logger.info(f"Sold Out       : {sold_out}")
        logger.info(f"Notify Me      : {notify_me}")

        out_of_stock_keywords = [
            "out of stock",
            "currently unavailable",
            "temporarily unavailable",
            "sold out",
            "notify me when available",
            "product unavailable",
        ]

        if (
            out_of_stock > 0
            or unavailable > 0
            or sold_out > 0
            or notify_me > 0
            or any(
                keyword in body_text
                for keyword in out_of_stock_keywords
            )
        ):
            logger.warning("Product is OUT OF STOCK")
            return False

        if (
            buy_now > 0
            or add_to_cart > 0
            or add_to_cart_caps > 0
            or button_buy_now > 0
            or button_add_to_cart > 0
        ):
            logger.info("Product is IN STOCK")
            return True

        in_stock_keywords = [
            "buy now",
            "add to cart",
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
            "Unable to determine Croma stock status."
        )
        return None

    except Exception as error:
        logger.exception(
            f"Croma tracker error: {error}"
        )
        return None

    finally:
        # Sirf current product ka context close hoga.
        # Shared worker browser open rahega.
        if context is not None:
            try:
                context.close()
            except Exception:
                pass