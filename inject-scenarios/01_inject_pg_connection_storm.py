#!/usr/bin/env python
"""PostgreSQL 커넥션 스톰 주입 스크립트 (knowledge-lab Phase 2/4용).

Total-Lab의 PostgreSQL Flexible Server(Burstable SKU)에 다수의 idle 연결을 열어
커넥션 고갈(connection exhaustion) 장애를 재현합니다. SRE Agent의 Knowledge/Memory
기능 테스트용으로만 사용하세요 — 운영 DB에는 사용하지 마세요.
"""
import argparse
import os
import sys
import time

import psycopg2


def parse_args():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--host", required=True, help="PostgreSQL Flexible Server FQDN")
    p.add_argument("--port", type=int, default=5432)
    p.add_argument("--dbname", default="diagdb")
    p.add_argument("--user", required=True)
    p.add_argument("--password-env", default="KLAB_PG_PASSWORD",
                    help="비밀번호를 담은 환경변수 이름 (기본 KLAB_PG_PASSWORD)")
    p.add_argument("--sslmode", default="require")
    p.add_argument("--connections", type=int, default=80,
                    help="동시에 열어둘 idle 연결 수 (기본 80)")
    p.add_argument("--hold-seconds", type=int, default=600,
                    help="연결을 유지할 시간(초), 기본 600초(10분)")
    return p.parse_args()


def main():
    args = parse_args()
    password = os.environ.get(args.password_env)
    if not password:
        sys.exit(f"환경변수 {args.password_env}에 비밀번호를 설정하세요.")

    conns = []
    try:
        print(f"[{time.strftime('%H:%M:%S')}] {args.connections}개 연결 시도 중...")
        for i in range(args.connections):
            try:
                conn = psycopg2.connect(
                    host=args.host, port=args.port, dbname=args.dbname,
                    user=args.user, password=password, sslmode=args.sslmode,
                    connect_timeout=5,
                )
                conns.append(conn)
            except psycopg2.OperationalError as e:
                print(f"[{time.strftime('%H:%M:%S')}] {i}번째 연결에서 거부됨(=커넥션 고갈 재현됨): {e}")
                break
        print(f"[{time.strftime('%H:%M:%S')}] {len(conns)}개 연결 확보. "
              f"{args.hold_seconds}초 동안 유지합니다 (Ctrl+C로 조기 종료 가능)...")
        print("지금 SRE Agent 채팅에 조사를 요청하세요: "
              "'rg-diag-total-lab의 PostgreSQL 서버 연결이 갑자기 안 됩니다. 원인을 조사해줘.'")
        time.sleep(args.hold_seconds)
    except KeyboardInterrupt:
        print("\n중단 요청 받음, 연결을 정리합니다...")
    finally:
        for conn in conns:
            try:
                conn.close()
            except Exception:
                pass
        print(f"[{time.strftime('%H:%M:%S')}] {len(conns)}개 연결 모두 종료했습니다.")


if __name__ == "__main__":
    main()
