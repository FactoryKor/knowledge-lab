#!/usr/bin/env python
"""MySQL 잠금 경합(lock contention) 주입 스크립트 (knowledge-lab 보조 시나리오용).

하나의 세션이 행(row) 잠금을 잡은 채 커밋하지 않고 대기하고, 여러 세션이 같은 행을
업데이트하려다 블로킹되는 상황을 재현합니다. Total-Lab의 MySQL Flexible Server
전용입니다 — 운영 DB에는 사용하지 마세요.
"""
import argparse
import os
import sys
import threading
import time

import pymysql

TABLE = "klab_lock_test"


def parse_args():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--host", required=True)
    p.add_argument("--port", type=int, default=3306)
    p.add_argument("--dbname", default="diagdb")
    p.add_argument("--user", required=True)
    p.add_argument("--password-env", default="KLAB_MYSQL_PASSWORD")
    p.add_argument("--hold-seconds", type=int, default=300,
                    help="블로커가 잠금을 유지할 시간(초), 기본 300초(5분)")
    p.add_argument("--waiters", type=int, default=5,
                    help="같은 행을 기다리는 대기 세션 수 (기본 5)")
    return p.parse_args()


def connect(args, password):
    return pymysql.connect(
        host=args.host, port=args.port, database=args.dbname,
        user=args.user, password=password, connect_timeout=5, autocommit=False,
    )


def ensure_table(args, password):
    conn = connect(args, password)
    try:
        with conn.cursor() as cur:
            cur.execute(f"CREATE TABLE IF NOT EXISTS {TABLE} (id INT PRIMARY KEY, val INT)")
            cur.execute(f"INSERT IGNORE INTO {TABLE} (id, val) VALUES (1, 0)")
        conn.commit()
    finally:
        conn.close()


def waiter(args, password, idx):
    conn = connect(args, password)
    try:
        start = time.time()
        with conn.cursor() as cur:
            cur.execute(f"UPDATE {TABLE} SET val = val + 1 WHERE id = 1")
        conn.commit()
        elapsed = time.time() - start
        print(f"[대기세션 {idx}] {elapsed:.1f}초 대기 후 업데이트 완료")
    except Exception as e:
        print(f"[대기세션 {idx}] 오류: {e}")
    finally:
        conn.close()


def main():
    args = parse_args()
    password = os.environ.get(args.password_env)
    if not password:
        sys.exit(f"환경변수 {args.password_env}에 비밀번호를 설정하세요.")

    ensure_table(args, password)

    blocker = connect(args, password)
    try:
        with blocker.cursor() as cur:
            cur.execute(f"SELECT * FROM {TABLE} WHERE id = 1 FOR UPDATE")
        print(f"[{time.strftime('%H:%M:%S')}] 블로커 세션이 행 잠금을 획득했습니다 "
              f"(커밋하지 않고 {args.hold_seconds}초 유지).")

        threads = [threading.Thread(target=waiter, args=(args, password, i))
                   for i in range(args.waiters)]
        for t in threads:
            t.start()

        print("지금 SRE Agent 채팅에 조사를 요청하세요: "
              "'rg-diag-total-lab의 MySQL 서버 쿼리가 멈춰있어요. 원인을 조사해줘.'")
        time.sleep(args.hold_seconds)
    finally:
        blocker.rollback()
        blocker.close()
        print(f"[{time.strftime('%H:%M:%S')}] 블로커 세션을 롤백하여 잠금을 해제했습니다.")
        for t in threads:
            t.join(timeout=10)


if __name__ == "__main__":
    main()
