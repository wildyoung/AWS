# Docker04 Network and Volume

## Docker Network

컨테이너는 격리된 네트워크 네임스페이스를 사용합니다. Docker는 컨테이너가 서로 통신하거나 외부와 통신할 수 있도록 여러 네트워크 드라이버를 제공합니다.

| 네트워크 | 설명 | 사용 예 |
| --- | --- | --- |
| bridge | 기본 네트워크. 같은 bridge 안의 컨테이너끼리 통신 | 일반 단일 호스트 실습 |
| user-defined bridge | 사용자가 만든 bridge. 컨테이너 이름 DNS 지원 | 여러 컨테이너 앱 |
| host | 호스트 네트워크를 그대로 사용 | 성능이 중요하거나 포트 격리가 필요 없을 때 |
| none | 네트워크를 붙이지 않음 | 네트워크 격리 테스트 |
| overlay | 여러 Docker host 사이 컨테이너 통신 | Swarm, 오케스트레이션 |

기본 bridge 네트워크는 Docker 설치 시 자동 생성되는 `docker0` 브리지를 사용합니다. 컨테이너를 실행하면 veth 인터페이스가 만들어지고, 컨테이너 네트워크와 호스트 bridge가 연결됩니다.

## 네트워크 실습 명령

기본 네트워크를 확인합니다.

```bash
docker network ls
docker network inspect bridge
```

사용자 정의 bridge 네트워크를 만들고 컨테이너를 연결합니다.

```bash
docker network create my-net
docker run -d --network my-net --name container1 ubuntu sleep 3600
docker run -d --network my-net --name container2 ubuntu sleep 3600
docker exec -it container1 ping container2
```

기존 컨테이너를 네트워크에 추가로 연결할 수 있습니다.

```bash
docker run -d --name container3 ubuntu sleep 3600
docker network connect my-net container3
docker exec -it container1 ping container3
docker network disconnect my-net container3
```

host와 none 네트워크도 비교합니다.

```bash
docker run --network host -d --name myweb nginx
docker run --network none -d --name testapp ubuntu sleep 1000
```

## Docker Volume

컨테이너의 writable layer는 컨테이너가 삭제되면 사라질 수 있습니다. 데이터베이스 파일, 업로드 파일, 로그처럼 보존해야 하는 데이터는 volume이나 bind mount에 저장해야 합니다.

| 방식 | 설명 | 특징 |
| --- | --- | --- |
| named volume | Docker가 관리하는 이름 있는 볼륨 | 운영에서 가장 일반적 |
| anonymous volume | 이름 없이 자동 생성되는 볼륨 | 추적과 정리가 어려울 수 있음 |
| bind mount | 호스트의 특정 경로를 직접 마운트 | 개발 환경에서 편리 |
| tmpfs | 메모리에만 저장 | 민감 데이터나 임시 데이터 |

## 볼륨 실습 명령

named volume을 생성하고 컨테이너에 연결합니다.

```bash
docker volume create mydata
docker run -d -v mydata:/app/data --name named-app nginx
docker volume ls
docker volume inspect mydata
```

컨테이너를 삭제해도 named volume은 남습니다.

```bash
docker rm -f named-app
docker volume ls
```

bind mount는 호스트 디렉터리를 직접 연결합니다.

```bash
mkdir -p ~/my-web-data
echo "Hello Docker Volume" > ~/my-web-data/index.html
docker run -d --name my-web-server -p 8080:80 -v ~/my-web-data:/usr/share/nginx/html nginx
curl http://localhost:8080
```

tmpfs는 컨테이너가 사라지면 데이터가 남지 않습니다.

```bash
docker run -d --name tmpfs-test --tmpfs /app/data nginx
```

## 네트워크와 볼륨 정리

```bash
docker rm -f container1 container2 container3 myweb testapp named-app my-web-server tmpfs-test
docker network rm my-net
docker volume rm mydata
docker network prune -f
docker volume prune -f
```

## 실습 포인트

- 같은 user-defined bridge에 있는 컨테이너는 컨테이너 이름으로 통신할 수 있습니다.
- `-p 8080:80`은 호스트의 8080 포트를 컨테이너의 80 포트로 연결합니다.
- 컨테이너 내부 데이터가 중요하면 volume을 먼저 설계해야 합니다.
- bind mount는 로컬 개발에는 편하지만 호스트 경로 의존성이 생깁니다.
