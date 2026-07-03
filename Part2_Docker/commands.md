# Docker 실습 명령 모음

이 파일은 Docker 파트 실습을 다시 수행할 때 사용하는 명령 모음입니다. 현재 저장소에는 실제 계정 ID, Access Key, Secret Key, 퍼블릭 IP를 기록하지 않습니다.

## 1. Docker host 선택

로컬에서 Docker Desktop을 실행한 뒤 확인합니다.

```bash
docker --version
docker compose version
docker info
```

AWS EC2 Docker host를 사용할 경우, CloudFormation 템플릿을 검증한 뒤 필요할 때만 스택을 생성합니다.

```bash
aws cloudformation validate-template \
  --template-body file://Part2_Docker/examples/lab01_settings/cre_myvpc.yaml \
  --region ap-northeast-2

aws cloudformation validate-template \
  --template-body file://Part2_Docker/examples/lab01_settings/cre_dockerhost.yaml \
  --region ap-northeast-2
```

선택적으로 스택을 생성합니다.

```bash
aws cloudformation create-stack \
  --stack-name docker-vpc \
  --template-body file://Part2_Docker/examples/lab01_settings/cre_myvpc.yaml \
  --region ap-northeast-2

aws cloudformation wait stack-create-complete \
  --stack-name docker-vpc \
  --region ap-northeast-2

aws cloudformation create-stack \
  --stack-name docker-host \
  --template-body file://Part2_Docker/examples/lab01_settings/cre_dockerhost.yaml \
  --parameters ParameterKey=KeyName,ParameterValue=<key-pair-name> \
  --region ap-northeast-2
```

## 2. 기본 컨테이너 명령

```bash
docker run hello-world
docker images
docker ps -a
docker rm <container-name-or-id>
docker rmi hello-world:latest
```

```bash
docker run -d --name my-webserver -p 8080:80 nginx
docker ps
docker logs my-webserver
curl http://localhost:8080
```

```bash
docker pause my-webserver
docker unpause my-webserver
docker stop my-webserver
docker start my-webserver
docker exec -it my-webserver /bin/bash
docker rm -f my-webserver
docker rmi nginx:latest
```

## 3. 이미지 태그, 저장, 불러오기

```bash
docker pull nginx
docker run -d --name myweb01 -p 8080:80 nginx
docker commit myweb01 mynginx:1.0
docker tag mynginx:1.0 mynginx:latest
docker images
```

```bash
docker pull mysql:5.7
docker image save mysql:5.7 > mysql57.tar
docker image rmi mysql:5.7
docker image load -i mysql57.tar
```

## 4. Docker network

```bash
docker network ls
docker network inspect bridge
```

```bash
docker network create my-net
docker run -d --network my-net --name container1 ubuntu sleep 3600
docker run -d --network my-net --name container2 ubuntu sleep 3600
docker exec -it container1 ping container2
```

```bash
docker run -d --name container3 ubuntu sleep 3600
docker network connect my-net container3
docker exec -it container1 ping container3
docker network disconnect my-net container3
```

```bash
docker network create --driver bridge --subnet 192.168.1.0/24 --gateway 192.168.1.1 test-net
docker network inspect test-net
docker network rm my-net test-net
```

## 5. Docker volume

```bash
docker volume create mydata
docker run -d -v mydata:/app/data --name named-app nginx
docker volume ls
docker volume inspect mydata
docker rm -f named-app
docker volume rm mydata
```

```bash
mkdir -p ~/my-web-data
echo "Hello Docker Volume" > ~/my-web-data/index.html
docker run -d --name my-web-server -p 8080:80 -v ~/my-web-data:/usr/share/nginx/html nginx
curl http://localhost:8080
docker rm -f my-web-server
```

## 6. Dockerfile

```bash
cd Part2_Docker/examples/lab05_dockerfile
docker build -t dockerfile-nginx:1.0 .
docker run -d --name dockerfile-nginx -p 8080:80 dockerfile-nginx:1.0
curl http://localhost:8080
docker rm -f dockerfile-nginx
```

```bash
docker build -f Dockerfile.env -t env-test:1.0 .
docker run --rm env-test:1.0
docker run --rm -e APP_ENV=prod env-test:1.0
```

```bash
docker build -f Dockerfile.entrypoint -t entrypoint-test:1.0 .
docker run --rm entrypoint-test:1.0
docker run --rm entrypoint-test:1.0 "Welcome to Docker!"
```

## 7. Image registry

Docker Hub 예시입니다.

```bash
docker build -t todo-app:1.0 .
docker tag todo-app:1.0 <dockerhub-username>/todo-app:1.0
docker login -u <dockerhub-username>
docker push <dockerhub-username>/todo-app:1.0
```

Amazon ECR 예시입니다.

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

## 8. Docker Compose

```bash
cd Part2_Docker/examples/lab07_compose
docker compose up -d
docker compose ps
docker compose logs wordpress
```

```bash
docker compose exec db mysql -u wpuser -p
show databases;
use wordpress;
show tables;
exit
```

```bash
docker compose stop
docker compose start
docker compose down
docker compose down -v
```

## 9. 전체 정리

```bash
docker stop $(docker ps -aq)
docker rm $(docker ps -aq)
docker network prune -f
docker volume prune -f
docker image prune -a -f
docker system prune -a --volumes -f
```

AWS 리소스를 만들었다면 다음 순서로 삭제합니다.

```bash
aws cloudformation delete-stack --stack-name docker-host --region ap-northeast-2
aws cloudformation wait stack-delete-complete --stack-name docker-host --region ap-northeast-2
aws cloudformation delete-stack --stack-name docker-vpc --region ap-northeast-2
aws cloudformation wait stack-delete-complete --stack-name docker-vpc --region ap-northeast-2
```
