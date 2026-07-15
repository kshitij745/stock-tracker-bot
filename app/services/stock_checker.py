from app.trackers.flipkart_tracker import check_flipkart_stock
from app.trackers.amazon_tracker import check_amazon_stock
from app.trackers.croma_tracker import check_croma_stock
from app.trackers.reliance_tracker import check_reliance_stock
from app.trackers.oneplus_tracker import check_oneplus_stock


def check_stock(product_url: str):
    """
    Detect the store from the URL and call the correct tracker.
    """

    url = product_url.lower()

    if "flipkart.com" in url:
        return check_flipkart_stock(product_url)

    elif "amazon." in url:
        return check_amazon_stock(product_url)

    elif "croma.com" in url:
        return check_croma_stock(product_url)

    elif "reliancedigital.in" in url:
        return check_reliance_stock(product_url)

    elif "oneplus.in" in url:
        return check_oneplus_stock(product_url)

    else:
        print("⚠️ Unsupported store.")
        return None