"""
데이터 집계 분석 모듈 (Step 3)

3가지 분석 쿼리:
1. 이벤트 타입별 발생 비율 → 에러율 모니터링
2. 시간대별 이벤트 수 + 매출 추이 → 트래픽 피크 타임 파악
3. 유저별 이벤트 수 TOP 10 → 헤비 유저 식별
"""

import pandas as pd


QUERIES = {
    "event_type_distribution": {
        "description": "이벤트 타입별 발생 비율 (에러율 모니터링)",
        "sql": """
            SELECT event_type, COUNT(*) as count
            FROM events
            GROUP BY event_type
            ORDER BY count DESC;
        """,
    },
    "hourly_traffic_and_revenue": {
        "description": "시간대별 이벤트 수 및 매출 추이",
        "sql": """
            SELECT
                DATE_TRUNC('hour', timestamp) as hour,
                COUNT(*) as event_count,
                COALESCE(SUM(amount), 0) as total_revenue
            FROM events
            GROUP BY hour
            ORDER BY hour;
        """,
    },
    "top_users_by_events": {
        "description": "유저별 총 이벤트 수 TOP 10",
        "sql": """
            SELECT user_id, COUNT(*) as event_count
            FROM events
            GROUP BY user_id
            ORDER BY event_count DESC
            LIMIT 10;
        """,
    },
}


def run_analyses(conn) -> dict[str, pd.DataFrame]:
    """
    사전 정의된 분석 쿼리들을 실행하고 결과를 DataFrame으로 반환합니다.

    Args:
        conn: psycopg Connection 객체

    Returns:
        {분석명: DataFrame} 딕셔너리
    """
    results = {}

    for name, query_info in QUERIES.items():
        with conn.cursor() as cur:
            cur.execute(query_info["sql"])
            rows = cur.fetchall()
            columns = [desc[0] for desc in cur.description]
        df = pd.DataFrame(rows, columns=columns)
        results[name] = df
        print(f"📊 분석 완료: {query_info['description']} ({len(df)}행)")

    return results
