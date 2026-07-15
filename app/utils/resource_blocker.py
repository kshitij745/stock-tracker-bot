from playwright.sync_api import Request, Route


BLOCKED_RESOURCE_TYPES = {
    "image",
    "media",
    "font",
}

BLOCKED_URL_KEYWORDS = {
    "google-analytics",
    "googletagmanager",
    "googlesyndication",
    "doubleclick",
    "amazon-adsystem",
    "facebook.com/tr",
    "facebook",
    "analytics",
    "advertising",
    "adservice",
    "adsystem",
    "/ads/",
    "metrics",
    "telemetry",
    "tracking",
    "pixel",
    "hotjar",
    "clarity.ms",
    "fls-",
    "unagi.amazon",
}


def block_unnecessary_resources(
    route: Route,
    request: Request,
):
    """
    Images, videos, fonts, advertisements, analytics aur
    tracking requests ko block karta hai.
    """

    resource_type = request.resource_type
    request_url = request.url.lower()

    should_block_url = any(
        keyword in request_url
        for keyword in BLOCKED_URL_KEYWORDS
    )

    try:
        if (
            resource_type in BLOCKED_RESOURCE_TYPES
            or should_block_url
        ):
            route.abort()
            return

        route.continue_()

    except Exception:
        # Context ya page close hote waqt pending request cancel
        # ho sakti hai. Is situation ko safely ignore karte hain.
        pass