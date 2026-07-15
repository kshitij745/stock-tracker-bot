import atexit
import threading

from playwright.sync_api import sync_playwright
from logs.logger import logger

from app.config.proxy_manager import get_next_proxy


_thread_local = threading.local()
_created_browsers = []
_browser_lock = threading.Lock()


def get_browser():
    """
    Har worker thread ke liye ek reusable Chromium browser return karta hai.

    Ek hi worker jab multiple products check karega,
    to Chromium dobara launch nahi hoga.
    """

    browser = getattr(_thread_local, "browser", None)

    if browser is not None:
        try:
            if browser.is_connected():
                return browser
        except Exception:
            pass

    playwright = getattr(_thread_local, "playwright", None)

    if playwright is None:
        playwright = sync_playwright().start()
        _thread_local.playwright = playwright

    logger.info(
        f"Launching reusable browser for worker "
        f"{threading.current_thread().name}"
    )

    browser = playwright.chromium.launch(
        headless=True,
        proxy=get_next_proxy(),
        args=[
            "--disable-blink-features=AutomationControlled",
            "--disable-dev-shm-usage",
            "--no-sandbox",
        ],
    )

    _thread_local.browser = browser

    with _browser_lock:
        _created_browsers.append(browser)

    return browser


def create_browser_context(
    user_agent: str,
    locale: str = "en-IN",
    timezone_id: str = "Asia/Kolkata",
):
    """
    Reusable browser ke andar ek fresh isolated context create karta hai.

    Browser reuse hota hai, lekin cookies/session har product ke liye
    fresh rehte hain.
    """

    browser = get_browser()

    return browser.new_context(
        viewport={
            "width": 1366,
            "height": 768,
        },
        user_agent=user_agent,
        locale=locale,
        timezone_id=timezone_id,
        extra_http_headers={
            "Accept-Language": "en-IN,en;q=0.9",
        },
    )


def close_thread_browser():
    """
    Current worker thread ka browser aur Playwright instance close karta hai.
    """

    browser = getattr(_thread_local, "browser", None)

    if browser is not None:
        try:
            browser.close()
        except Exception:
            pass

        _thread_local.browser = None

    playwright = getattr(_thread_local, "playwright", None)

    if playwright is not None:
        try:
            playwright.stop()
        except Exception:
            pass

        _thread_local.playwright = None


def close_all_browsers():
    """
    Application shutdown ke waqt available browsers close karta hai.
    """

    with _browser_lock:
        browsers = list(_created_browsers)
        _created_browsers.clear()

    for browser in browsers:
        try:
            if browser.is_connected():
                browser.close()
        except Exception:
            pass


atexit.register(close_all_browsers)