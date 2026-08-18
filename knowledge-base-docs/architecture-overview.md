# Total-Lab 아키텍처 개요 (지식 테스트용 참조 문서)

이 문서는 `rg-diag-total-lab` 리소스 그룹의 토폴로지를 설명합니다. SRE Agent의 Knowledge base
기능 검증을 위해 업로드하는 샘플 문서로, **의도적으로 구체적인 리소스명/역할을 명시**했습니다 —
에이전트가 조사 중 이 문서를 인용하는지 확인하는 용도입니다.

## 리소스 구성

| 리소스 이름(패턴) | 역할 |
|---|---|
| `win-sql` (Windows Server 2022 VM) | SQL Server 2022 Developer 설치, `mssql_diagnose` IaaS 시나리오 대상 |
| `linux-mysql` (Ubuntu 22.04 VM) | MySQL Server 설치, `mysql_diagnose` IaaS 시나리오 대상 |
| PostgreSQL Flexible Server (`diagdb`) | Burstable SKU, `pg_stat_statements` 사전 구성. **`max_connections`가 낮게 설정되어 있어 부하 시 커넥션 고갈이 가장 먼저 발생하는 컴포넌트** |
| Azure Database for MySQL Flexible Server (`diagdb`) | PaaS 시나리오 대상, 복제/잠금 경합 테스트에 사용 |
| Azure SQL Database (`diagdb`) | PaaS 시나리오 대상 |
| Log Analytics Workspace | Windows/Linux Perf·Event·Syslog + VM Insights(Dependency Agent) 수집 |

## 네트워크

- VNet 대역: `10.20.0.0/16`
- Windows VM: `10.20.1.5`
- Linux VM: `10.20.1.6`
- 두 VM은 5분 간격으로 PaaS DB 3종 + 서로에게 TCP 연결을 시도하도록 스케줄링되어 있음
  (서비스 맵 토폴로지 데이터 생성용).

## 알려진 제약 사항

- PostgreSQL Flexible Server는 **Burstable SKU**로 배포되어 `max_connections`가 낮음(기본값
  근처). 진단/테스트 스크립트가 다수의 연결을 동시에 열면 **커넥션 고갈로 인한 신규 연결 거부**가
  가장 먼저 나타나는 장애 패턴입니다.
- MySQL/PostgreSQL Flexible Server는 중지가 최대 7일까지만 가능하며, 장기 미사용 시 삭제를 권장.
- `aks`/`eh`/`agw` 진단 도구는 이 랩 범위에 포함되지 않음(별도 클러스터/네임스페이스/게이트웨이 필요).

## 온콜/운영 정보

- 담당 팀: 진단 플랫폼팀
- 리소스 그룹: `rg-diag-total-lab`
- 배포 스크립트: `Total-Lab/full-lab/00_deploy.ps1`
