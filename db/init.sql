-- =============================================================
-- 이벤트 로그 테이블 스키마 (PostgreSQL)
--
-- 설계 의도:
-- 1. 단순 JSON 저장을 지양하고, 핵심 필드를 개별 컬럼으로 분리하여
--    SQL 분석 쿼리의 직관성과 효율을 높였습니다.
-- 2. 모든 이벤트에 공통인 필드(timestamp, user_id, event_type, platform)는
--    NOT NULL 컬럼으로 구성했습니다.
-- 3. 이벤트 타입별로 존재 여부가 다른 필드(page_url, amount, error_code)는
--    Nullable 컬럼으로 분리하여 스키마의 유연성을 확보했습니다.
-- 4. amount는 금융 데이터이므로 INT 대신 DECIMAL(10,2)을 사용하여
--    소수점 정확도를 보장합니다.
-- =============================================================

CREATE TABLE IF NOT EXISTS events (
    id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    timestamp   TIMESTAMP NOT NULL,
    user_id     INTEGER NOT NULL,
    event_type  VARCHAR(20) NOT NULL,
    platform    VARCHAR(10) NOT NULL,
    page_url    VARCHAR(255),
    amount      DECIMAL(10, 2),
    error_code  VARCHAR(10)
);

-- 분석 쿼리 성능을 위한 인덱스
-- event_type: 이벤트 타입별 필터링/그룹핑 최적화
CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type);
-- timestamp: 시간대별 분석 쿼리 최적화
CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp);
-- user_id: 유저별 집계 분석 최적화
CREATE INDEX IF NOT EXISTS idx_events_user_id ON events(user_id);
