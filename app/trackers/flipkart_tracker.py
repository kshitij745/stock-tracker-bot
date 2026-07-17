from app.services.browser_manager import create_browser_context

from app.utils.resource_blocker import (
    block_unnecessary_resources,
)

from logs.logger import logger


def check_flipkart_stock(product_url: str):
    """
    Checks whether a Flipkart product is in stock.

    Returns:
        True  -> Product is in stock
        False -> Product is out of stock
        None  -> Unable to determine stock status
    """

    context = None

    try:
        # Reusable worker browser ke andar fresh context create hoga.
        context = create_browser_context(
            user_agent=(
                "Mozilla/5.0 "
                "(Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/138.0.0.0 Safari/537.36"
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

        page.wait_for_timeout(3000)

        page_title = page.title().strip()

        logger.info(
            f"Flipkart Page Title: {page_title}"
        )

        blocked_page_keywords = [
            "access denied",
            "captcha",
            "robot check",
            "forbidden",
            "page not found",
        ]

        if any(
            keyword in page_title.lower()
            for keyword in blocked_page_keywords
        ):
            logger.warning(
                "Flipkart returned a blocked or invalid page."
            )
            return None

        html_lower = page.content().lower()

        # =================================================
        # STRUCTURED DATA DETECTION
        # =================================================

        if "https://schema.org/instock" in html_lower:
            logger.info(
                "Flipkart product is IN STOCK "
                "(detected from structured data)"
            )
            return True

        if "https://schema.org/outofstock" in html_lower:
            logger.warning(
                "Flipkart product is OUT OF STOCK "
                "(detected from structured data)"
            )
            return False

        # Some pages may use schema.org without https.
        if "schema.org/instock" in html_lower:
            logger.info(
                "Flipkart product is IN STOCK "
                "(detected from structured data)"
            )
            return True

        if "schema.org/outofstock" in html_lower:
            logger.warning(
                "Flipkart product is OUT OF STOCK "
                "(detected from structured data)"
            )
            return False

        # =================================================
        # BUTTON/TEXT FALLBACK DETECTION
        # =================================================

        buy_now = page.get_by_text(
            "Buy Now",
            exact=False,
        ).count()

        add_to_cart = page.get_by_text(
            "Add to Cart",
            exact=False,
        ).count()

        sold_out = page.get_by_text(
            "Sold Out",
            exact=False,
        ).count()

        currently_unavailable = page.get_by_text(
            "Currently Unavailable",
            exact=False,
        ).count()

        logger.info(
            f"Flipkart Buy Now: {buy_now}"
        )
        logger.info(
            f"Flipkart Add To Cart: {add_to_cart}"
        )
        logger.info(
            f"Flipkart Sold Out: {sold_out}"
        )
        logger.info(
            "Flipkart Currently Unavailable: "
            f"{currently_unavailable}"
        )

        # Out-of-stock ko pehle priority do.
        if sold_out > 0 or currently_unavailable > 0:
            logger.warning(
                "Flipkart product is OUT OF STOCK "
                "(detected from page text)"
            )
            return False

        if buy_now > 0 or add_to_cart > 0:
            logger.info(
                "Flipkart product is IN STOCK "
                "(detected from page buttons)"
            )
            return True

        logger.warning(
            "Unable to determine Flipkart stock status."
        )
        return None

    except Exception as error:
        logger.exception(
            f"Flipkart tracker error: {error}"
        )
        return None

    finally:
        # Sirf context close hoga.
        # Shared worker browser close nahi hoga.
        if context is not None:
            try:
                context.close()
            except Exception:
                pass