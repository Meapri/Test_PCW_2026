"""
이벤트 로그 파이프라인 — 메인 오케스트레이터

실행 흐름:
1. 이벤트 2,000건 랜덤 생성 (generator.py)
2. PostgreSQL DB에 연결 및 데이터 적재 (db.py)
3. 3가지 분석 쿼리 실행 (analyzer.py)
4. 분석 결과를 대시보드 이미지로 저장 (visualizer.py)

docker compose up 시 자동으로 실행됩니다.
"""

import os

from generator import generate_events
from db import get_connection, insert_events, truncate_events
from analyzer import run_analyses
from visualizer import create_dashboard


def main():
    print("=" * 55)
    print("🚀 이벤트 로그 파이프라인 시작")
    print("=" * 55)

    # 환경변수에서 이벤트 생성 건수를 읽음 (기본값: 2000)
    event_count = int(os.getenv("EVENT_COUNT", "2000"))

    # ── Step 1: 이벤트 생성 ──
    print("\n📌 [Step 1] 이벤트 생성 중...")
    events = generate_events(n=event_count)
    print(f"   ✅ {len(events)}건 이벤트 생성 완료")

    # ── Step 2: DB 연결 및 적재 ──
    print("\n📌 [Step 2] DB 연결 및 데이터 적재 중...")
    conn = get_connection()
    truncate_events(conn)
    insert_events(conn, events)

    # ── Step 3 & 5: 분석 및 시각화 ──
    print("\n📌 [Step 3] 데이터 집계 분석 중...")
    results = run_analyses(conn)

    print("\n📌 [Step 5] 결과 시각화 중...")
    create_dashboard(results, output_path="/app/output/dashboard.png")

    # ── 정리 ──
    conn.close()

    print("\n" + "=" * 55)
    print("✅ 파이프라인 완료!")
    print("   결과 차트: ./output/dashboard.png")
    print("=" * 55)


if __name__ == "__main__":
    main()
