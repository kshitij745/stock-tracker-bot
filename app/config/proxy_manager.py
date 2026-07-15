import itertools
import threading

from app.config.proxy import get_proxy


_lock = threading.Lock()

_proxy_cycle = None


def load_proxy_pool():
    """
    Proxy pool initialize karta hai.

    Abhi single proxy support hai.
    Future me multiple proxies support honge.
    """

    global _proxy_cycle

    proxy = get_proxy()

    if proxy:
        proxies = [proxy]
    else:
        proxies = [None]

    _proxy_cycle = itertools.cycle(proxies)


def get_next_proxy():
    """
    Next available proxy return karta hai.
    """

    global _proxy_cycle

    with _lock:

        if _proxy_cycle is None:
            load_proxy_pool()

        return next(_proxy_cycle)


def reload_proxy_pool():
    """
    Future use:
    Runtime me proxy list reload kar sakte hain.
    """

    with _lock:
        load_proxy_pool()