"""
데이터베이스 연결 및 데이터 적재 모듈 (Step 2)

주요 설계 포인트:
- 환경변수(DATABASE_URL)를 통한 DB 접속 정보 주입 → 하드코딩 방지
- 앱 레벨 재시도 로직 → Docker healthcheck와 이중 안전장치
- 배치 INSERT로 대량 데이터 효율적 적재
"""

import os
import time

import psycopg


def get_connection(max_retries: int = 10, delay: int = 2):
    """
    PostgreSQL 연결을 생성합니다.
    DB가 아직 준비되지 않았을 경우를 대비해 재시도 로직을 포함합니다.

    Args:
        max_retries: 최대 재시도 횟수
        delay: 재시도 간격(초)

    Returns:
        psycopg.Connection 객체

    Raises:
        ConnectionError: 최대 재시도 횟수를 초과한 경우
    """
    db_url = os.getenv(
        "DATABASE_URL",
        "postgresql://pipeline_user:pipeline_pass@db:5432/events_db",
    )

    for attempt in range(1, max_retries + 1):
        try:
            conn = psycopg.connect(db_url)
            print(f"✅ DB 연결 성공 (시도 {attempt}회)")
            return conn
        except psycopg.OperationalError as e:
            if attempt == max_retries:
                raise ConnectionError(
                    f"DB 연결 실패: 최대 재시도 횟수({max_retries}) 초과"
                ) from e
            print(f"⏳ DB 연결 대기 중... ({attempt}/{max_retries})")
            time.sleep(delay)


def truncate_events(conn):
    """기존 이벤트 데이터를 초기화합니다 (재실행 시 중복 방지)."""
    with conn.cursor() as cur:
        cur.execute("TRUNCATE TABLE events;")
    conn.commit()
    print("🗑️  기존 이벤트 데이터 초기화 완료")


def insert_events(conn, events: list[dict]):
    """
    이벤트 목록을 events 테이블에 배치 삽입합니다.

    Args:
        conn: psycopg Connection 객체
        events: 삽입할 이벤트 딕셔너리 리스트
    """
    insert_query = """
        INSERT INTO events (timestamp, user_id, event_type, platform, page_url, amount, error_code)
        VALUES (%(timestamp)s, %(user_id)s, %(event_type)s, %(platform)s, %(page_url)s, %(amount)s, %(error_code)s)
    """

    with conn.cursor() as cur:
        cur.executemany(insert_query, events)

    conn.commit()
    print(f"✅ {len(events)}건 이벤트 적재 완료")
