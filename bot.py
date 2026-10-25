import os
import random
import requests

from datetime import datetime
from zoneinfo import ZoneInfo


WEBHOOK_URL = os.environ["DISCORD_WEBHOOK_URL"]
QUOTE_FILE = "quotes.txt"
STATE_FILE = "last_sent.txt"

FORCE_SEND = os.environ.get("FORCE_SEND", "false").lower() == "true"

now = datetime.now(ZoneInfo("Asia/Seoul"))
current_hour = now.strftime("%Y-%m-%d-%H")
hour = now.hour


# 새벽 03:00 ~ 07:59 자동 전송 금지
if not FORCE_SEND and 3 <= hour <= 7:
    print("현재는 전송하지 않는 시간대입니다.")
    exit()


# 마지막 전송 시간 확인
last_sent = ""

if os.path.exists(STATE_FILE):
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        last_sent = f.read().strip()


# 이미 이번 시간에 보냈다면 종료
if not FORCE_SEND and last_sent == current_hour:
    print("이번 시간에는 이미 대사를 보냈습니다.")
    exit()


# 대사 읽기
with open(QUOTE_FILE, "r", encoding="utf-8") as f:
    quotes = [
        line.strip()
        for line in f
        if line.strip()
    ]


if not quotes:
    print("대사가 없습니다.")
    exit()


# 랜덤 대사 선택
quote = random.choice(quotes)

response = requests.post(
    WEBHOOK_URL,
    json={"content": quote},
    timeout=10
)

response.raise_for_status()

print("전송 완료:", quote)


# 이번 시간 전송 완료 기록
with open(STATE_FILE, "w", encoding="utf-8") as f:
    f.write(current_hour)

print("전송 시간 기록:", current_hour)
