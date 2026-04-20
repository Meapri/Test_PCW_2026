"""
이벤트 생성기 (Step 1)
웹 서비스(이커머스)에서 발생하는 유저 행동 이벤트를 랜덤 생성합니다.

이벤트 타입 설계:
- page_view (60%): 유저가 페이지를 조회하는 가장 기본적인 행동
- purchase (25%): 상품 구매 (전환율이 낮으므로 page_view보다 적은 비율)
- error (15%): 시스템/클라이언트 에러 (일정 비율로 항상 발생)

비율 근거: 실제 이커머스에서 대부분의 트래픽은 페이지 조회이고,
구매 전환율은 약 2~5%이나, 데이터 분석 의미를 위해 25%로 설정했습니다.
"""

import random
from faker import Faker

fake = Faker()
Faker.seed(42)
random.seed(42)

# 50명의 유저 풀을 유지하여 유저별 분석이 의미 있게 동작하도록 합니다.
USER_POOL = list(range(1, 51))

# 이벤트 타입별 발생 가중치
EVENT_WEIGHTS = {
    "page_view": 60,
    "purchase": 25,
    "error": 15,
}

# 에러 코드 목록 (HTTP 표준 에러 코드 기반)
ERROR_CODES = ["E400", "E401", "E403", "E404", "E500", "E502", "E503"]

# 플랫폼 목록
PLATFORMS = ["web", "ios", "android"]


def generate_events(n: int = 2000) -> list[dict]:
    """
    n건의 랜덤 이벤트를 생성합니다.

    Args:
        n: 생성할 이벤트 수 (기본값: 2000)

    Returns:
        이벤트 딕셔너리 리스트
    """
    event_types = list(EVENT_WEIGHTS.keys())
    weights = list(EVENT_WEIGHTS.values())

    events = []
    for _ in range(n):
        event_type = random.choices(event_types, weights=weights, k=1)[0]

        event = {
            "timestamp": fake.date_time_between(
                start_date="-7d", end_date="now"
            ),
            "user_id": random.choice(USER_POOL),
            "event_type": event_type,
            "platform": random.choice(PLATFORMS),
            # 이벤트 타입에 따라 존재 여부가 다른 가변 필드
            "page_url": fake.uri_path() if event_type == "page_view" else None,
            "amount": (
                round(random.uniform(1000, 150000), 2)
                if event_type == "purchase"
                else None
            ),
            "error_code": (
                random.choice(ERROR_CODES) if event_type == "error" else None
            ),
        }
        events.append(event)

    return events
