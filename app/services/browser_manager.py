import atexit
import threading

from playwright.sync_api import Browser, sync_playwright

from app.config.proxy_manager import get_next_proxy
from logs.logger import logger


_thread_local = threading.local()

_created_browsers: list[Browser] = []
_browser_lock = threading.Lock()


def _get_playwright():
    """
    Current worker thread ke liye reusable Playwright instance return karta hai.
    """

    playwright = getattr(
        _thread_local,
        "playwright",
        None,
    )

    if playwright is None:
        playwright = sync_playwright().start()
        _thread_local.playwright = playwright

    return playwright


def _get_thread_browsers() -> dict:
    """
    Current worker thread ke reusable browsers ka dictionary return karta hai.

    Dictionary key:
        (headless, use_proxy)
    """

    browsers = getattr(
        _thread_local,
        "browsers",
        None,
    )

    if browsers is None:
        browsers = {}
        _thread_local.browsers = browsers

    return browsers


def get_browser(
    headless: bool = True,
    use_proxy: bool = True,
):
    """
    Current worker thread ke liye matching reusable browser return karta hai.

    Browser mode combinations:

    (True, True)
        Headless + proxy

    (False, True)
        Headed + proxy

    (True, False)
        Headless + direct connection

    (False, False)
        Headed + direct connection
    """

    browsers = _get_thread_browsers()

    browser_key = (
        headless,
        use_proxy,
    )

    browser = browsers.get(browser_key)

    if browser is not None:
        try:
            if browser.is_connected():
                return browser

        except Exception:
            pass

        browsers[browser_key] = None

    playwright = _get_playwright()

    browser_mode = (
        "headless"
        if headless
        else "headed"
    )

    connection_mode = (
        "proxy"
        if use_proxy
        else "direct"
    )

    logger.info(
        f"Launching reusable {browser_mode} browser "
        f"with {connection_mode} connection "
        f"for worker {threading.current_thread().name}"
    )

    launch_options = {
        "headless": headless,
        "args": [
            "--disable-blink-features=AutomationControlled",
            "--disable-dev-shm-usage",
            "--no-sandbox",
        ],
    }

    if use_proxy:
        proxy = get_next_proxy()

        if proxy is not None:
            launch_options["proxy"] = proxy

    browser = playwright.chromium.launch(
        **launch_options
    )

    browsers[browser_key] = browser

    with _browser_lock:
        _created_browsers.append(browser)

    return browser


def create_browser_context(
    user_agent: str,
    headless: bool = True,
    use_proxy: bool = True,
    locale: str = "en-IN",
    timezone_id: str = "Asia/Kolkata",
):
    """
    Reusable browser ke andar fresh isolated context create karta hai.

    Args:
        user_agent:
            Browser user-agent string.

        headless:
            True  -> Background browser.
            False -> Visible/headed browser.

        use_proxy:
            True  -> Configured proxy use hogi.
            False -> Direct internet connection use hogi.

        locale:
            Browser locale.

        timezone_id:
            Browser timezone.
    """

    browser = get_browser(
        headless=headless,
        use_proxy=use_proxy,
    )

    context = browser.new_context(
        viewport={
            "width": 1366,
            "height": 768,
        },
        screen={
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

    context.add_init_script(
        """
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });

        Object.defineProperty(navigator, 'languages', {
            get: () => ['en-IN', 'en']
        });

        Object.defineProperty(navigator, 'platform', {
            get: () => 'Win32'
        });

        Object.defineProperty(navigator, 'hardwareConcurrency', {
            get: () => 8
        });

        Object.defineProperty(navigator, 'deviceMemory', {
            get: () => 8
        });

        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5]
        });

        if (!window.chrome) {
            window.chrome = {};
        }

        if (!window.chrome.runtime) {
            window.chrome.runtime = {};
        }
        """
    )

    return context


def close_thread_browsers():
    """
    Current worker thread ke sab reusable browsers close karta hai.
    """

    browsers = getattr(
        _thread_local,
        "browsers",
        None,
    )

    if browsers is not None:
        for browser_key, browser in list(browsers.items()):
            if browser is None:
                continue

            try:
                if browser.is_connected():
                    browser.close()

            except Exception:
                pass

            browsers[browser_key] = None

    playwright = getattr(
        _thread_local,
        "playwright",
        None,
    )

    if playwright is not None:
        try:
            playwright.stop()

        except Exception:
            pass

        _thread_local.playwright = None


def close_all_browsers():
    """
    Application shutdown par sab reusable browsers close karta hai.
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