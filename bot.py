import os
import random
import requests


WEBHOOK_URL = os.environ["DISCORD_WEBHOOK_URL"]
QUOTE_FILE = "quotes.txt"


def load_quotes():
    with open(QUOTE_FILE, "r", encoding="utf-8") as f:
        return [
            line.strip()
            for line in f
            if line.strip()
        ]


def send_quote():
    quotes = load_quotes()

    if not quotes:
        print("대사가 없습니다.")
        return

    quote = random.choice(quotes)

    response = requests.post(
        WEBHOOK_URL,
        json={"content": quote},
        timeout=10
    )

    response.raise_for_status()

    print("전송 완료:", quote)


send_quote()