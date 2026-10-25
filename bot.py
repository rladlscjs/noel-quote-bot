import os
import random
import requests
import json
import hashlib

from datetime import datetime
from zoneinfo import ZoneInfo


WEBHOOK_URL = os.environ["DISCORD_WEBHOOK_URL"]
QUOTE_FILE = "quotes.txt"
STATE_FILE = "quote_state.json"

FORCE_SEND = os.environ.get("FORCE_SEND", "false").lower() == "true"


# ============================================
# 현재 한국 시간
# ============================================

now = datetime.now(ZoneInfo("Asia/Seoul"))
current_hour = now.strftime("%Y-%m-%d-%H")
hour = now.hour


# ============================================
# 새벽 03:00 ~ 07:59 자동 전송 금지
# ============================================

if not FORCE_SEND and 3 <= hour <= 7:
    print("현재는 전송하지 않는 시간대입니다.")
    exit()


# ============================================
# 대사 불러오기
# ============================================

with open(QUOTE_FILE, "r", encoding="utf-8") as f:
    quotes = [
        line.strip()
        for line in f
        if line.strip()
    ]


if not quotes:
    print("대사가 없습니다.")
    exit()


# ============================================
# quotes.txt 상태 확인용 해시 생성
# ============================================

quotes_text = "\n".join(quotes)

quotes_hash = hashlib.sha256(
    quotes_text.encode("utf-8")
).hexdigest()


# ============================================
# 기존 상태 불러오기
# ============================================

state = {
    "quotes_hash": "",
    "remaining": [],
    "last_sent": ""
}


if os.path.exists(STATE_FILE):
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            state = json.load(f)
    except Exception:
        print("기존 상태 파일을 읽지 못했습니다. 새로 생성합니다.")


# ============================================
# 이번 시간에 이미 보냈으면 종료
# ============================================

if not FORCE_SEND and state.get("last_sent") == current_hour:
    print("이번 시간에는 이미 대사를 보냈습니다.")
    exit()


# ============================================
# 대사가 추가/수정됐거나
# 모든 대사를 다 사용했다면 다시 섞기
# ============================================

remaining = state.get("remaining", [])

if (
    state.get("quotes_hash") != quotes_hash
    or not remaining
):
    remaining = list(range(len(quotes)))
    random.shuffle(remaining)

    print("대사 목록을 새로 섞었습니다.")


# ============================================
# 아직 안 나온 대사 하나 선택
# ============================================

quote_index = remaining.pop()
quote = quotes[quote_index]


# ============================================
# Discord 전송
# ============================================

response = requests.post(
    WEBHOOK_URL,
    json={"content": quote},
    timeout=10
)

response.raise_for_status()

print("전송 완료:", quote)
print("이번 회차 남은 대사:", len(remaining))


# ============================================
# 현재 상태 저장
# ============================================

state = {
    "quotes_hash": quotes_hash,
    "remaining": remaining,
    "last_sent": current_hour
}


with open(STATE_FILE, "w", encoding="utf-8") as f:
    json.dump(
        state,
        f,
        ensure_ascii=False,
        indent=2
    )


print("상태 저장 완료")
