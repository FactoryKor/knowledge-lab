# 온콜 에스컬레이션 절차 (Total-Lab / 진단 플랫폼팀)

## 1차 대응

1. 담당자: 진단 플랫폼팀 온콜 (Slack `#diag-lab-oncall` 채널)
2. 대응 시간 목표: 알림 수신 후 5분 이내 확인 시작

## 에스컬레이션 순서

1. **1단계 (0~5분)**: Slack `#diag-lab-oncall` 채널에 알림, 온콜 담당자 자동 확인
2. **2단계 (5~15분)**: 온콜 담당자 응답 없으면 팀 리드에게 직접 연락(전화)
3. **3단계 (15분 초과)**: 팀 리드도 응답 없으면 플랫폼 전체 온콜(secondary on-call)로 에스컬레이션

## 커뮤니케이션 규칙

- 모든 장애는 해결 여부와 관계없이 `#diag-lab-oncall`에 요약을 남긴다.
- 5분 내 해소되지 않는 장애는 별도 인시던트 채널을 생성한다.
- 근본 원인이 확인되면 관련 runbook(`postgresql-connection-exhaustion-runbook.md`,
  `mysql-lock-contention-runbook.md`)을 갱신한다.
