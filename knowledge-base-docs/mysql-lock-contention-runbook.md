# Runbook: MySQL 잠금 경합(Lock Contention) 대응 절차

**대상**: `rg-diag-total-lab`의 Azure Database for MySQL Flexible Server (`diagdb`)
**적용 증상**: 쿼리 응답 지연, `Threads_running` 급증, `mysql_diagnose`의 잠금 대기(lock wait)
지표 상승.

## 1. 즉시 확인

1. 현재 잠금 대기 확인(MySQL 8.0+):
   ```sql
   SELECT * FROM performance_schema.data_lock_waits;
   ```
2. 실행 중인 쿼리와 대기 시간 확인:
   ```sql
   SELECT id, user, host, db, time, state, info
   FROM information_schema.processlist
   ORDER BY time DESC;
   ```

## 2. 조치

1. **블로킹 세션 식별 후 종료(최후 수단)**:
   ```sql
   KILL <blocking_thread_id>;
   ```
   업무에 영향이 없는지 먼저 확인 후 실행.
2. **장기 트랜잭션 커밋/롤백 유도**: 애플리케이션이 트랜잭션을 열어둔 채 방치하는 패턴이 있는지
   확인(커넥션 풀 타임아웃 설정 점검).
3. **인덱스 점검**: 잠금 범위가 넓어지는 원인이 인덱스 부재로 인한 풀 스캔인지 확인.

## 3. 에스컬레이션

5분 내 해소되지 않으면 `escalation-procedures.md` 절차를 따름.

## 4. 관련 진단 도구

`mysql_diagnose`의 잠금 대기(`information_schema.processlist` 기반) 및 `Threads_running` 지표로
사전 탐지 가능.
