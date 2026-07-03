# Docker05 Dockerfile

## Dockerfile이 필요한 이유

Dockerfile은 컨테이너 이미지를 만드는 절차를 코드로 기록한 파일입니다. 서버에 접속해 직접 패키지를 설치하고 설정을 바꾸면 재현하기 어렵지만, Dockerfile에 절차를 남기면 같은 이미지를 반복해서 만들 수 있습니다.

`docker commit`도 컨테이너 변경 내용을 이미지로 저장할 수 있지만, 어떤 명령을 실행했는지 남지 않습니다. 반대로 Dockerfile은 Git으로 버전 관리가 가능하고 리뷰할 수 있어 협업과 운영에 더 적합합니다.

## 이미지 빌드 흐름

1. 애플리케이션 파일과 Dockerfile을 준비합니다.
2. `docker build`가 Dockerfile을 읽고 레이어를 만듭니다.
3. 빌드 결과로 이미지가 생성됩니다.
4. `docker run`이 이미지를 컨테이너로 실행합니다.

```bash
docker build -t myubuntu:1.0 .
docker run -d -P --name testserver myubuntu:1.0
```

## 주요 지시어

| 지시어 | 역할 |
| --- | --- |
| `FROM` | 베이스 이미지 지정 |
| `LABEL` | 이미지 메타데이터 기록 |
| `RUN` | 이미지 빌드 중 실행할 명령 |
| `COPY` | 로컬 파일을 이미지로 복사 |
| `ADD` | 파일 복사, 로컬 tar 자동 압축 해제, URL 추가 지원 |
| `WORKDIR` | 이후 명령의 작업 디렉터리 지정 |
| `ENV` | 이미지와 컨테이너에서 사용할 환경 변수 |
| `ARG` | 빌드 시점에만 쓰는 변수 |
| `EXPOSE` | 컨테이너가 사용하는 포트 문서화 |
| `CMD` | 컨테이너 시작 시 기본 명령 |
| `ENTRYPOINT` | 컨테이너의 고정 실행 명령 |
| `VOLUME` | 컨테이너 데이터 저장 경로 선언 |

## 예제 Dockerfile

```dockerfile
FROM ubuntu:latest
LABEL description="This is a sample Dockerfile"
RUN apt-get update && apt-get install -y nginx
COPY index.html /usr/share/nginx/html/index.html
WORKDIR /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

빌드와 실행은 다음처럼 합니다.

```bash
docker build -t my-nginx:1.0 .
docker run -d --name my-nginx -p 8080:80 my-nginx:1.0
curl http://localhost:8080
```

## RUN과 CMD

`RUN`은 이미지 빌드 중 실행됩니다. 패키지 설치, 파일 생성, 의존성 설치에 사용합니다.

`CMD`는 컨테이너가 시작될 때 실행되는 기본 명령입니다. `docker run 이미지명 다른명령`처럼 실행하면 CMD는 덮어쓸 수 있습니다.

```dockerfile
RUN apt-get update && apt-get install -y nginx
CMD ["nginx", "-g", "daemon off;"]
```

## CMD와 ENTRYPOINT

`ENTRYPOINT`는 컨테이너의 고정 실행 파일처럼 동작합니다. `CMD`는 ENTRYPOINT에 넘겨줄 기본 인수로 사용할 수 있습니다.

```dockerfile
ENTRYPOINT ["echo", "Hello,"]
CMD ["Docker!"]
```

실행 예시는 다음과 같습니다.

```bash
docker build -f Dockerfile.entrypoint -t my-echo:1.0 .
docker run --rm my-echo:1.0
docker run --rm my-echo:1.0 "Welcome to Docker!"
```

## COPY와 ADD

보통은 `COPY`를 우선 사용합니다. `COPY`는 단순히 파일을 복사하므로 의도가 명확합니다. `ADD`는 로컬 tar 파일을 자동으로 풀거나 URL에서 가져오는 기능이 있어 편리하지만, 예상하지 못한 동작이 생길 수 있습니다.

## ENV와 실행 시 override

Dockerfile에서 기본 환경 변수를 지정하고, 실행할 때 `-e`로 값을 바꿀 수 있습니다.

```dockerfile
ENV APP_ENV=dev
CMD ["sh", "-c", "echo APP_ENV=$APP_ENV"]
```

```bash
docker build -f Dockerfile.env -t env-test:1.0 .
docker run --rm env-test:1.0
docker run --rm -e APP_ENV=prod env-test:1.0
```

## EXPOSE와 포트 매핑

`EXPOSE 80`은 이미지가 80 포트를 사용한다는 문서 역할을 합니다. 실제 외부 접근을 위해서는 `docker run -p` 옵션이 필요합니다.

```bash
docker run -d -p 8080:80 my-nginx:1.0
```

## 실습 파일

예제 Dockerfile은 [examples/lab05_dockerfile](../examples/lab05_dockerfile)에 정리했습니다.

## 실습 기록

Docker daemon이 실행 중이면 예제 디렉터리에서 다음 순서로 확인할 수 있습니다.

```bash
cd Part2_Docker/examples/lab05_dockerfile
docker build -t dockerfile-nginx:1.0 .
docker run -d --name dockerfile-nginx -p 8080:80 dockerfile-nginx:1.0
curl http://localhost:8080
docker rm -f dockerfile-nginx
```
