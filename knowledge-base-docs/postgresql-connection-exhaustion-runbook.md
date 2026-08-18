# Runbook: PostgreSQL 커넥션 고갈(Connection Exhaustion) 대응 절차

**대상**: `rg-diag-total-lab`의 PostgreSQL Flexible Server (`diagdb`)
**적용 증상**: 신규 연결 시도 시 `FATAL: too many connections`, 애플리케이션 타임아웃, `pg_diagnose`의
연결수 지표가 `max_connections`에 근접/초과.

## 1. 즉시 확인

1. 현재 연결 수와 상한 확인:
   ```sql
   SELECT count(*) AS current_connections FROM pg_stat_activity;
   SHOW max_connections;
   ```
2. 유휴(idle) 연결이 다수인지 확인:
   ```sql
   SELECT pid, usename, state, state_change, query
   FROM pg_stat_activity
   WHERE state = 'idle'
   ORDER BY state_change ASC;
   ```

## 2. 조치

1. **유휴 연결 정리(가장 먼저 시도)**:
   ```sql
   SELECT pg_terminate_backend(pid)
   FROM pg_stat_activity
   WHERE state = 'idle' AND state_change < now() - interval '5 minutes';
   ```
2. **애플리케이션 측 커넥션 풀 점검**: 커넥션 풀 최대 크기가 서버 `max_connections`보다 크게
   설정되어 있지 않은지 확인. 풀링 미들웨어(PgBouncer 등) 도입을 검토.
3. **서버 파라미터 조정(임시 완화책)**: Burstable SKU에서 `max_connections`를 상향 조정할 수
   있으나, 메모리 부족으로 이어질 수 있으므로 상위 SKU 전환을 우선 검토.
4. **재발 방지**: 커넥션 스톰을 유발하는 배치/스크립트가 있는지 확인(테스트 스크립트가 연결을
   닫지 않고 종료되는 경우가 흔한 원인).

## 3. 에스컬레이션

위 조치로 5분 내 해소되지 않으면 `escalation-procedures.md` 절차에 따라 온콜 담당자에게 에스컬레이션.

## 4. 관련 진단 도구

`pg_diagnose --format json`의 `connections` 카테고리에서 `current`/`max`/`utilization_pct`를
확인하면 이 장애를 사전에 포착할 수 있습니다.
