# Docker03 Basic Commands

## Docker 명령 구조

Docker CLI는 대체로 다음 구조를 가집니다.

```bash
docker [대상] [동작] [옵션]
```

예를 들어 `docker container ls`는 컨테이너 목록을 조회하고, `docker image ls`는 이미지 목록을 조회합니다. 짧은 명령으로는 `docker ps`, `docker images`도 자주 사용합니다.

## 컨테이너 생명주기

컨테이너는 이미지에서 만들어지고, 실행되고, 중지되고, 삭제됩니다.

| 단계 | 명령 | 의미 |
| --- | --- | --- |
| 생성 | `docker create` | 컨테이너를 만들지만 실행하지 않음 |
| 생성 + 실행 | `docker run` | 이미지 pull, 컨테이너 생성, 실행을 한 번에 수행 |
| 시작 | `docker start` | 중지된 컨테이너 시작 |
| 중지 | `docker stop` | 정상 종료 신호를 보내고 중지 |
| 강제 종료 | `docker kill` | 즉시 종료 |
| 삭제 | `docker rm` | 중지된 컨테이너 삭제 |

## 자주 쓰는 실행 옵션

| 옵션 | 의미 | 예시 |
| --- | --- | --- |
| `-d` | 백그라운드 실행 | `docker run -d nginx` |
| `--name` | 컨테이너 이름 지정 | `--name my-web` |
| `-p` | 호스트 포트와 컨테이너 포트 연결 | `-p 8080:80` |
| `-v` | 볼륨 또는 bind mount 연결 | `-v mydata:/data` |
| `-e` | 환경 변수 주입 | `-e MYSQL_ROOT_PASSWORD=1234` |
| `-it` | 대화형 터미널 | `docker run -it ubuntu bash` |
| `--rm` | 종료 시 컨테이너 자동 삭제 | `docker run --rm hello-world` |

## 기본 실습 명령

```bash
docker run hello-world
docker images
docker ps -a
docker rm <container-name-or-id>
docker rmi hello-world:latest
```

Nginx 컨테이너를 웹 서버로 실행합니다.

```bash
docker run -d --name my-webserver -p 8080:80 nginx
docker ps
docker logs my-webserver
curl http://localhost:8080
```

컨테이너를 일시 정지, 재개, 중지, 시작합니다.

```bash
docker pause my-webserver
docker unpause my-webserver
docker stop my-webserver
docker start my-webserver
```

컨테이너 내부로 접속합니다.

```bash
docker exec -it my-webserver /bin/bash
```

컨테이너와 이미지를 정리합니다.

```bash
docker stop my-webserver
docker rm my-webserver
docker rmi nginx:latest
```

## commit과 tag

컨테이너 내부 변경을 이미지로 저장할 수 있습니다.

```bash
docker commit my-webserver mynginx:1.0
docker tag mynginx:1.0 mynginx:latest
docker images
```

운영 환경에서는 `docker commit`보다 Dockerfile을 권장합니다. Dockerfile은 변경 절차가 코드로 남기 때문에 재현성과 리뷰가 좋습니다.

## save와 load

이미지를 파일로 저장하고 다시 불러올 수 있습니다.

```bash
docker pull mysql:5.7
docker image save mysql:5.7 > mysql57.tar
docker image rmi mysql:5.7
docker image load -i mysql57.tar
```

## 실습 기록

Docker daemon이 현재 실행 중이 아니어서 실제 컨테이너 실행은 생략했습니다. 대신 수업 실습 흐름에 맞춰 컨테이너 생성, 실행, 중지, 삭제, 이미지 태그, 저장/불러오기 명령을 정리했습니다.
