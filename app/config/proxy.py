import os
from dotenv import load_dotenv

load_dotenv()

PROXY_SERVER = os.getenv("PROXY_SERVER")
PROXY_USERNAME = os.getenv("PROXY_USERNAME")
PROXY_PASSWORD = os.getenv("PROXY_PASSWORD")


def get_proxy():
    if not PROXY_SERVER:
        return None

    proxy = {
        "server": PROXY_SERVER
    }

    if PROXY_USERNAME:
        proxy["username"] = PROXY_USERNAME

    if PROXY_PASSWORD:
        proxy["password"] = PROXY_PASSWORD

    return proxy