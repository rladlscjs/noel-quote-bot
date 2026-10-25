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

# Actions에서 직접 Run workflow를 눌렀을 때 True
FORCE_SEND = os.environ.get("FORCE_SEND", "false").lower() == "true"


# ============================================
# 현재 한국 시간
# ============================================

now = datetime.now(ZoneInfo("Asia/Seoul"))
current_hour = now.strftime("%Y-%m-%d-%H")
hour = now.hour


# ============================================
# 새벽 03:00 ~ 07:59 자동 전송 금지
# 단, 수동 테스트는 가능
# ============================================

if not FORCE_SEND and 3 <= hour <= 7:
    print("현재는 자동 전송하지 않는 시간대입니다.")
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
    print("quotes.txt에 대사가 없습니다.")
    exit()


# ============================================
# quotes.txt 변경 여부 확인용 해시
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

    except Exception as e:
        print("기존 상태 파일을 읽지 못했습니다.")
        print("새 상태로 시작합니다.")
        print(e)


# ============================================
# 이번 시간에 자동 대사를 이미 보냈으면 종료
# ============================================

if not FORCE_SEND and state.get("last_sent") == current_hour:
    print("이번 시간에는 이미 대사를 보냈습니다.")
    exit()


# ============================================
# 대사 순서 관리
#
# 모든 대사를 한 번씩 사용하기 전까지
# 같은 대사를 다시 사용하지 않음
# ============================================

remaining = state.get("remaining", [])


# quotes.txt가 변경되었거나
# 모든 대사를 다 썼다면 다시 섞기
if (
    state.get("quotes_hash") != quotes_hash
    or not remaining
):
    remaining = list(range(len(quotes)))
    random.shuffle(remaining)

    print("대사 목록을 새로 섞었습니다.")


# ============================================
# 아직 사용하지 않은 대사 하나 선택
# ============================================

quote_index = remaining.pop()
quote = quotes[quote_index]


# ============================================
# Discord로 전송
# ============================================

response = requests.post(
    WEBHOOK_URL,
    json={
        "content": quote
    },
    timeout=10
)

response.raise_for_status()

print("전송 완료:", quote)
print("이번 회차 남은 대사:", len(remaining))


# ============================================
# 상태 저장
# ============================================

# 수동 Run workflow는
# 정규 자동 전송 시간을 차지하지 않음
if FORCE_SEND:
    new_last_sent = state.get("last_sent", "")
    print("수동 테스트이므로 자동 전송 기록은 변경하지 않습니다.")

else:
    new_last_sent = current_hour
    print("자동 전송 시간 기록:", current_hour)


state = {
    "quotes_hash": quotes_hash,
    "remaining": remaining,
    "last_sent": new_last_sent
}


with open(STATE_FILE, "w", encoding="utf-8") as f:
    json.dump(
        state,
        f,
        ensure_ascii=False,
        indent=2
    )


print("상태 저장 완료")
