from playwright.sync_api import sync_playwright
from logs.logger import logger


def check_flipkart_stock(product_url: str):
    """
    Checks whether a Flipkart product is in stock.

    Returns:
        True  -> Product is in stock
        False -> Product is out of stock
        None  -> Unable to determine stock status
    """

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)

            page = browser.new_page()

            page.goto(
                product_url,
                wait_until="domcontentloaded",
                timeout=30000
            )

            page.wait_for_timeout(3000)
            logger.info(f"Page Title: {page.title()}")

            # Save page HTML (useful for debugging)
            with open("playwright_page.html", "w", encoding="utf-8") as f:
                f.write(page.content())

            # Flipkart stock locators
            buy_now = page.locator("text=Buy Now").count()
            add_to_cart = page.locator("text=Add to Cart").count()
            sold_out = page.locator("text=Sold Out").count()

            logger.info(f"Buy Now button : {buy_now}")
            logger.info(f"Add To Cart    : {add_to_cart}")
            logger.info(f"Sold Out text  : {sold_out}")

            if buy_now > 0 or add_to_cart > 0:
                logger.info("Product is IN STOCK")
                return True

            if sold_out > 0:
                logger.warning("Product is OUT OF STOCK")
                return False

            logger.warning("Unable to determine stock status.")
            return None

    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return None

