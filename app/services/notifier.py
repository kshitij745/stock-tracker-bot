import os
import requests
from dotenv import load_dotenv

load_dotenv()

FLIPKART_TOPIC_ID = os.getenv("FLIPKART_TOPIC_ID")
AMAZON_TOPIC_ID = os.getenv("AMAZON_TOPIC_ID")
CROMA_TOPIC_ID = os.getenv("CROMA_TOPIC_ID")
RELIANCE_TOPIC_ID = os.getenv("RELIANCE_TOPIC_ID")
ONEPLUS_TOPIC_ID = os.getenv("ONEPLUS_TOPIC_ID")


def get_topic_id(store_name: str):
    store = store_name.lower()

    if store == "flipkart":
        return FLIPKART_TOPIC_ID

    elif store == "amazon":
        return AMAZON_TOPIC_ID

    elif store == "croma":
        return CROMA_TOPIC_ID

    elif store == "reliance digital":
        return RELIANCE_TOPIC_ID

    elif store == "oneplus store":
        return ONEPLUS_TOPIC_ID

    return None


def send_telegram_message(
    bot_token: str,
    chat_id: str,
    store_name: str,
    message: str
) -> bool:
    """
    Sends message to the correct Telegram Topic.
    """

    topic_id = get_topic_id(store_name)

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
    }

    if topic_id:
        payload["message_thread_id"] = int(topic_id)

    try:
        response = requests.post(
            url,
            json=payload,
            timeout=10
        )

        if response.status_code == 200:
            print(f"✅ Telegram notification sent to {store_name} topic.")
            return True

        print(f"❌ Telegram Error: {response.text}")
        return False

    except Exception as e:
        print(f"❌ Error sending Telegram message: {e}")
        return False
    