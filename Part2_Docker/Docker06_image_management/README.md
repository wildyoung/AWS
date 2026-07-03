# Docker06 Image Management

## 이미지 레이어

Docker 이미지는 여러 레이어로 구성됩니다. Dockerfile의 `FROM`, `RUN`, `COPY` 같은 명령은 이미지 레이어를 만들 수 있고, Docker는 같은 레이어를 재사용해 빌드와 pull 시간을 줄입니다.

컨테이너를 실행하면 이미지의 읽기 전용 레이어 위에 쓰기 가능한 컨테이너 레이어가 추가됩니다. 컨테이너 내부 변경은 이 쓰기 레이어에 기록되고, 컨테이너 삭제 시 함께 사라질 수 있습니다.

## 레이어 확인

```bash
docker pull python:latest
docker image inspect python:latest
docker history python:latest
```

컨테이너 변경을 이미지로 저장할 수도 있습니다.

```bash
docker run -it --name hello-app python:latest /bin/bash
# 컨테이너 내부에서 파일 생성 후 exit
docker commit hello-app mypython:1.1
docker history mypython:1.1
```

운영에서는 Dockerfile 기반 빌드를 권장하지만, `commit`은 레이어 개념을 이해하는 실습에 유용합니다.

## 이미지 태그

태그는 같은 이미지에 붙는 이름입니다. 보통 `이미지명:버전` 형식으로 씁니다.

```bash
docker tag todo-app:1.0 myname/todo-app:1.0
docker tag todo-app:1.0 myname/todo-app:latest
docker images
```

`latest`는 항상 최신이라는 보장이 아니라 기본 태그 이름입니다. 운영 배포에서는 `1.0.0`, Git SHA, 빌드 번호처럼 추적 가능한 태그를 쓰는 것이 좋습니다.

## 이미지 save/load와 export/import

이미지를 파일로 저장하려면 `save`와 `load`를 사용합니다.

```bash
docker image save mysql:5.7 > mysql57.tar
docker image load -i mysql57.tar
```

컨테이너 파일시스템을 tar로 내보내려면 `export`와 `import`를 사용합니다.

```bash
docker export <container-id> > container.tar
docker import container.tar imported-image:1.0
```

이미지의 레이어와 메타데이터를 보존하려면 `save/load`가 더 적합합니다.

## Docker Hub push

```bash
docker build -t todo-app:1.0 .
docker tag todo-app:1.0 <dockerhub-username>/todo-app:1.0
docker login -u <dockerhub-username>
docker push <dockerhub-username>/todo-app:1.0
```

GitHub에 실제 Docker Hub 계정이나 토큰은 올리지 않습니다.

## Amazon ECR push

AWS에서 컨테이너 이미지를 저장할 때는 Amazon ECR을 사용할 수 있습니다.

```bash
aws ecr create-repository \
  --repository-name to-do-app \
  --region ap-northeast-2

aws ecr get-login-password --region ap-northeast-2 \
  | docker login \
      --username AWS \
      --password-stdin <account-id>.dkr.ecr.ap-northeast-2.amazonaws.com

docker build -t to-do-app .
docker tag to-do-app:latest <account-id>.dkr.ecr.ap-northeast-2.amazonaws.com/to-do-app:latest
docker push <account-id>.dkr.ecr.ap-northeast-2.amazonaws.com/to-do-app:latest
```

실습 후 ECR 저장소를 삭제하려면 다음 명령을 사용합니다.

```bash
aws ecr delete-repository \
  --repository-name to-do-app \
  --force \
  --region ap-northeast-2
```

## 이미지 최적화

- 불필요한 패키지를 설치하지 않습니다.
- 빌드 캐시를 활용할 수 있도록 자주 바뀌는 파일은 뒤쪽에서 복사합니다.
- `RUN` 명령에서 패키지 설치 후 캐시를 정리합니다.
- `.dockerignore`로 빌드 컨텍스트에 불필요한 파일이 들어가지 않게 합니다.
- 가능하면 작은 베이스 이미지나 multi-stage build를 사용합니다.

## 정리 명령

```bash
docker image prune -f
docker system prune -f
docker system prune -a --volumes -f
```

`docker system prune -a --volumes`는 사용하지 않는 이미지와 볼륨까지 삭제하므로 실습 데이터가 필요한 경우 주의해야 합니다.

## 실습 기록

실제 Docker Hub 또는 ECR push는 계정 정보와 과금 가능 리소스가 관련되어 수행하지 않았습니다. 대신 태그, push, ECR 로그인 흐름을 재현 가능한 명령으로 정리했습니다.
