# Docker07 Docker Compose

## Docker Compose란?

Docker Compose는 여러 컨테이너로 구성된 애플리케이션을 하나의 YAML 파일로 정의하고 실행하는 도구입니다. 단일 컨테이너는 `docker run`으로 충분하지만, 웹 서버와 데이터베이스처럼 여러 컨테이너가 함께 필요한 경우 명령이 길고 복잡해집니다.

Compose를 사용하면 서비스, 네트워크, 볼륨, 환경 변수를 선언적으로 관리할 수 있습니다.

## docker run과 Compose 비교

WordPress와 MySQL을 직접 `docker run`으로 실행하면 네트워크 생성, DB 컨테이너 실행, WordPress 컨테이너 실행을 각각 명령으로 관리해야 합니다.

```bash
docker network create wordpress-net
docker run --name wordpress-db --network wordpress-net -e MYSQL_ROOT_PASSWORD=password -d mysql:8
docker run -d -p 8080:80 --network wordpress-net --name wordpress-web \
  -e WORDPRESS_DB_HOST=wordpress-db \
  -e WORDPRESS_DB_PASSWORD=password \
  wordpress:latest
```

Compose는 같은 구성을 `docker-compose.yml`에 저장하고 한 번에 실행합니다.

```bash
docker compose up -d
docker compose ps
docker compose logs
docker compose down
```

## Compose 파일 핵심 구조

| 항목 | 설명 |
| --- | --- |
| `services` | 실행할 컨테이너 목록 |
| `image` | 사용할 이미지 |
| `build` | Dockerfile로 이미지를 빌드할 경로 |
| `ports` | 호스트와 컨테이너 포트 매핑 |
| `environment` | 컨테이너 환경 변수 |
| `volumes` | 데이터 저장 볼륨 |
| `depends_on` | 서비스 시작 순서 의존성 |
| `networks` | 서비스가 사용할 네트워크 |

## WordPress + MySQL 예제

예제 파일은 [examples/lab07_compose/docker-compose.yml](../examples/lab07_compose/docker-compose.yml)에 있습니다.

```bash
cd Part2_Docker/examples/lab07_compose
docker compose up -d
docker compose ps
docker compose logs wordpress
```

브라우저에서 `http://localhost:8081`로 접속하면 WordPress 초기 설정 화면을 확인할 수 있습니다.

DB에 접속해 WordPress 데이터베이스를 확인합니다.

```bash
docker compose exec db mysql -u wpuser -p
show databases;
use wordpress;
show tables;
exit
```

## 중지와 삭제

컨테이너만 중지합니다.

```bash
docker compose stop
docker compose start
```

컨테이너와 네트워크를 삭제합니다. 기본적으로 named volume은 남습니다.

```bash
docker compose down
```

볼륨까지 삭제하려면 다음처럼 실행합니다.

```bash
docker compose down -v
```

## 주의할 점

- `depends_on`은 컨테이너 시작 순서를 보장하지만, DB가 완전히 준비될 때까지 기다려주지는 않습니다.
- 비밀번호는 실습에서는 YAML에 직접 적지만 운영에서는 secret manager나 환경 변수 파일을 사용해야 합니다.
- Compose는 로컬 개발과 단일 호스트 실습에 적합합니다. 여러 서버 운영은 ECS, EKS, Kubernetes 같은 오케스트레이션 도구가 필요합니다.

## 실습 기록

Docker daemon이 현재 실행 중이 아니어서 WordPress 컨테이너 실행은 수행하지 않았습니다. 대신 Compose 파일과 실행, 확인, 정리 명령을 재현 가능한 형태로 정리했습니다.
