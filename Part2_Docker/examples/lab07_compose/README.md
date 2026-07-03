# Lab07 Docker Compose Example

WordPress와 MySQL을 Compose로 실행하는 예제입니다.

```bash
docker compose up -d
docker compose ps
docker compose logs wordpress
```

브라우저에서 `http://localhost:8081`로 접속합니다.

DB 확인:

```bash
docker compose exec db mysql -u wpuser -p
show databases;
use wordpress;
show tables;
exit
```

정리:

```bash
docker compose down -v
```

실습 비밀번호 `1234`는 교육용 예시입니다. 실제 환경에서는 secret manager나 `.env` 파일을 사용하고 GitHub에 민감 정보를 올리지 않습니다.
