from app.trackers.flipkart_tracker import check_flipkart_stock


def check_stock(product_url: str):
    """
    Detect the store from the URL and call the correct tracker.
    """

    url = product_url.lower()

    if "flipkart.com" in url:
        return check_flipkart_stock(product_url)

    elif "amazon." in url:
        print("⚠️ Amazon tracker not implemented yet.")
        return None

    else:
        print("⚠️ Unsupported store.")
        return None