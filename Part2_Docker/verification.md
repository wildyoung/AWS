# Docker Part Verification

검증일: 2026-07-03

## 로컬 Docker 확인

| 명령 | 결과 |
| --- | --- |
| `docker --version` | Docker version 29.5.3 |
| `docker compose version` | Docker Compose version v5.1.4 |
| `docker ps` | Docker daemon 미실행으로 연결 실패 |

Docker CLI와 Compose는 설치되어 있으나, 현재 로컬 Docker daemon이 실행 중이 아니어서 컨테이너 실행 실습은 수행하지 않았습니다.

## AWS CLI 검증

아래 명령은 리소스를 생성하지 않고 CloudFormation 템플릿 문법만 검증합니다.

```bash
aws cloudformation validate-template \
  --template-body file://Part2_Docker/examples/lab01_settings/cre_myvpc.yaml \
  --region ap-northeast-2
```

결과: 통과

```bash
aws cloudformation validate-template \
  --template-body file://Part2_Docker/examples/lab01_settings/cre_dockerhost.yaml \
  --region ap-northeast-2
```

결과: 통과

## Docker Compose 검증

```bash
docker compose -f Part2_Docker/examples/lab07_compose/docker-compose.yml config
```

결과: 통과
