import re

from app.services.browser_manager import create_browser_context
from app.utils.resource_blocker import block_unnecessary_resources
from logs.logger import logger


def check_oneplus_stock(product_url: str):
    """
    Checks whether a OnePlus Store product is in stock.

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

        # Dynamic OnePlus content load hone ka wait
        try:
            page.wait_for_load_state(
                "networkidle",
                timeout=10000,
            )
        except Exception:
            pass

        page.wait_for_timeout(5000)

        # CTA/button render trigger karne ke liye light scroll
        try:
            page.evaluate(
                "window.scrollTo(0, Math.min(900, document.body.scrollHeight))"
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
                "OnePlus Store returned a blocked or invalid page."
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

        # Case-insensitive visible text detection
        buy_now_text = page.get_by_text(
            re.compile(r"^\s*buy\s+now\s*$", re.IGNORECASE)
        ).count()

        add_to_cart_text = page.get_by_text(
            re.compile(r"^\s*add\s+to\s+cart\s*$", re.IGNORECASE)
        ).count()

        # Button, link and role-based selectors
        buy_now_buttons = page.locator(
            "button:has-text('Buy Now'), "
            "button:has-text('BUY NOW'), "
            "a:has-text('Buy Now'), "
            "a:has-text('BUY NOW'), "
            "[role='button']:has-text('Buy Now'), "
            "[role='button']:has-text('BUY NOW')"
        ).count()

        add_to_cart_buttons = page.locator(
            "button:has-text('Add to Cart'), "
            "button:has-text('ADD TO CART'), "
            "a:has-text('Add to Cart'), "
            "a:has-text('ADD TO CART'), "
            "[role='button']:has-text('Add to Cart'), "
            "[role='button']:has-text('ADD TO CART')"
        ).count()

        # Class/data attribute fallback
        buy_action_elements = page.locator(
            "[class*='buy-now' i], "
            "[class*='buynow' i], "
            "[data-testid*='buy' i], "
            "[data-test*='buy' i]"
        ).count()

        cart_action_elements = page.locator(
            "[class*='add-to-cart' i], "
            "[class*='addtocart' i], "
            "[data-testid*='cart' i], "
            "[data-test*='cart' i]"
        ).count()

        sold_out = page.get_by_text(
            re.compile(r"^\s*sold\s+out\s*$", re.IGNORECASE)
        ).count()

        out_of_stock = page.get_by_text(
            re.compile(r"^\s*out\s+of\s+stock\s*$", re.IGNORECASE)
        ).count()

        unavailable = page.get_by_text(
            re.compile(
                r"^\s*currently\s+unavailable\s*$",
                re.IGNORECASE,
            )
        ).count()

        notify_me = page.get_by_text(
            re.compile(r"^\s*notify\s+me\s*$", re.IGNORECASE)
        ).count()

        coming_soon = page.get_by_text(
            re.compile(r"^\s*coming\s+soon\s*$", re.IGNORECASE)
        ).count()

        logger.info(f"Buy Now Text  : {buy_now_text}")
        logger.info(f"Cart Text     : {add_to_cart_text}")
        logger.info(f"Buy Buttons   : {buy_now_buttons}")
        logger.info(f"Cart Buttons  : {add_to_cart_buttons}")
        logger.info(f"Buy Elements  : {buy_action_elements}")
        logger.info(f"Cart Elements : {cart_action_elements}")
        logger.info(f"Sold Out      : {sold_out}")
        logger.info(f"Out Of Stock  : {out_of_stock}")
        logger.info(f"Unavailable   : {unavailable}")
        logger.info(f"Notify Me     : {notify_me}")
        logger.info(f"Coming Soon   : {coming_soon}")

        out_of_stock_keywords = [
            "currently unavailable",
            "temporarily unavailable",
            "out of stock",
            "sold out",
            "notify me when available",
            "notify me",
            "coming soon",
            "product unavailable",
        ]

        # Out-of-stock indicators ko priority
        if (
            sold_out > 0
            or out_of_stock > 0
            or unavailable > 0
            or notify_me > 0
            or coming_soon > 0
            or any(
                keyword in body_text
                for keyword in out_of_stock_keywords
            )
        ):
            logger.warning("Product is OUT OF STOCK")
            return False

        # Primary in-stock detection
        if (
            buy_now_text > 0
            or add_to_cart_text > 0
            or buy_now_buttons > 0
            or add_to_cart_buttons > 0
            or buy_action_elements > 0
            or cart_action_elements > 0
        ):
            logger.info("Product is IN STOCK")
            return True

        # Final page-text fallback
        in_stock_keywords = [
            "buy now",
            "add to cart",
            "in stock",
            "available for delivery",
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
            "Unable to determine OnePlus stock status."
        )
        return None

    except Exception as error:
        logger.exception(
            f"OnePlus tracker error: {error}"
        )
        return None

    finally:
        if context is not None:
            try:
                context.close()
            except Exception:
                pass