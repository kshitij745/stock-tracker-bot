import re

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
            headless=True,
            use_proxy=False,
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

        # Reliance ka dynamic product content load hone do.
        try:
            page.wait_for_load_state(
                "networkidle",
                timeout=10000,
            )
        except Exception:
            pass

        page.wait_for_timeout(5000)

        # Product action section render trigger karne ke liye scroll.
        try:
            page.evaluate(
                """
                window.scrollTo(
                    0,
                    Math.min(1000, document.body.scrollHeight)
                )
                """
            )

            page.wait_for_timeout(2000)

            page.evaluate("window.scrollTo(0, 0)")

            page.wait_for_timeout(1000)

        except Exception:
            pass

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
                .inner_text(timeout=7000)
                .strip()
                .lower()
            )

        except Exception:
            body_text = ""

        # Case-insensitive visible text selectors
        add_to_cart_text = page.get_by_text(
            re.compile(
                r"^\s*add\s+to\s+cart\s*$",
                re.IGNORECASE,
            )
        ).count()

        buy_now_text = page.get_by_text(
            re.compile(
                r"^\s*buy\s+now\s*$",
                re.IGNORECASE,
            )
        ).count()

        # Buttons, links and role-based actions
        add_to_cart_buttons = page.locator(
            "button:has-text('Add to Cart'), "
            "button:has-text('ADD TO CART'), "
            "a:has-text('Add to Cart'), "
            "a:has-text('ADD TO CART'), "
            "[role='button']:has-text('Add to Cart'), "
            "[role='button']:has-text('ADD TO CART')"
        ).count()

        buy_now_buttons = page.locator(
            "button:has-text('Buy Now'), "
            "button:has-text('BUY NOW'), "
            "a:has-text('Buy Now'), "
            "a:has-text('BUY NOW'), "
            "[role='button']:has-text('Buy Now'), "
            "[role='button']:has-text('BUY NOW')"
        ).count()

        # Class and data-attribute fallback
        cart_action_elements = page.locator(
            "[class*='add-to-cart' i], "
            "[class*='addtocart' i], "
            "[class*='cart-button' i], "
            "[data-testid*='cart' i], "
            "[data-test*='cart' i]"
        ).count()

        buy_action_elements = page.locator(
            "[class*='buy-now' i], "
            "[class*='buynow' i], "
            "[class*='buy-button' i], "
            "[data-testid*='buy' i], "
            "[data-test*='buy' i]"
        ).count()

        out_of_stock = page.get_by_text(
            re.compile(
                r"^\s*out\s+of\s+stock\s*$",
                re.IGNORECASE,
            )
        ).count()

        sold_out = page.get_by_text(
            re.compile(
                r"^\s*sold\s+out\s*$",
                re.IGNORECASE,
            )
        ).count()

        unavailable = page.get_by_text(
            re.compile(
                r"^\s*currently\s+unavailable\s*$",
                re.IGNORECASE,
            )
        ).count()

        notify_me = page.get_by_text(
            re.compile(
                r"^\s*notify\s+me\s*$",
                re.IGNORECASE,
            )
        ).count()

        logger.info(f"Add To Cart Text : {add_to_cart_text}")
        logger.info(f"Buy Now Text     : {buy_now_text}")
        logger.info(f"Cart Buttons     : {add_to_cart_buttons}")
        logger.info(f"Buy Buttons      : {buy_now_buttons}")
        logger.info(f"Cart Elements    : {cart_action_elements}")
        logger.info(f"Buy Elements     : {buy_action_elements}")
        logger.info(f"Out of Stock     : {out_of_stock}")
        logger.info(f"Sold Out         : {sold_out}")
        logger.info(f"Unavailable      : {unavailable}")
        logger.info(f"Notify Me        : {notify_me}")

        out_of_stock_keywords = [
            "currently unavailable",
            "temporarily unavailable",
            "out of stock",
            "sold out",
            "notify me when available",
            "notify me",
            "product unavailable",
        ]

        # Out-of-stock ko priority.
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

        # Primary in-stock detection.
        if (
            add_to_cart_text > 0
            or buy_now_text > 0
            or add_to_cart_buttons > 0
            or buy_now_buttons > 0
            or cart_action_elements > 0
            or buy_action_elements > 0
        ):
            logger.info("Product is IN STOCK")
            return True

        # Final visible page-text fallback.
        in_stock_keywords = [
            "add to cart",
            "buy now",
            "in stock",
            "available for delivery",
            "check delivery",
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
        if context is not None:
            try:
                context.close()
            except Exception:
                pass