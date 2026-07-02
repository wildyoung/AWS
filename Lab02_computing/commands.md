# Lab2 Computing Commands

실제 계정 ID, 퍼블릭 IP, 키 파일 내용은 문서에 남기지 않습니다.

## Web 서버 구성

```bash
sudo hostnamectl set-hostname web01
sudo apt update
sudo apt install -y nginx git mysql-client curl stress
sudo systemctl enable nginx
sudo systemctl status nginx --no-pager
```

```bash
git clone https://github.com/my-ciel/aws_labs.git /home/ubuntu/labfiles
sudo chmod +x ~/labfiles/*
~/labfiles/setup_web.sh
```

## DB 서버 구성

```bash
sudo apt update
sudo apt install mysql-server -y
sudo sed -i 's/bind-address\s*=\s*127.0.0.1/bind-address = 0.0.0.0/' /etc/mysql/mysql.conf.d/mysqld.cnf
sudo systemctl restart mysql
```

```sql
CREATE USER 'member'@'%' IDENTIFIED BY '<DB_PASSWORD>';
GRANT ALL PRIVILEGES ON *.* TO 'member'@'%';
FLUSH PRIVILEGES;
CREATE DATABASE memberdb;
```

## WAS 서버 구성

```bash
sudo apt update
sudo apt install -y mysql-client git curl
mysql -h <DB_PRIVATE_IP> -u member -p
```

```bash
git clone https://github.com/my-ciel/aws_labs.git /home/ubuntu/labfiles
sed -i 's/10.0.2.0/<DB_PRIVATE_IP>/g' /home/ubuntu/labfiles/setup_was.sh
sudo chmod +x /home/ubuntu/labfiles/*
/home/ubuntu/labfiles/setup_was.sh
```

## API 테스트

```bash
curl -X POST http://<WEB_PUBLIC_IP>/api/signup \
  -H 'Content-Type: application/json' \
  -d '{"userid":"user3","password":"<APP_PASSWORD>","username":"실습사용자","email":"labuser@example.com"}'
```

```bash
curl -X POST http://<WEB_PUBLIC_IP>/api/login \
  -H 'Content-Type: application/json' \
  -d '{"userid":"user3","password":"<APP_PASSWORD>"}'
```

## User Data 예시

```bash
#!/bin/bash
sudo -i
dnf -y upgrade-minimal
dnf install -y httpd
systemctl start httpd
systemctl enable httpd
echo '<div style="display: flex; height: 100vh; justify-content: center; align-items: center;"><h1>Hello World from <span style="color:red;">myweb03</span></h1></div>' > /var/www/html/index.html
dnf install -y https://dev.mysql.com/get/mysql80-community-release-el9-1.noarch.rpm
dnf -y install --nogpgcheck mysql-community-client
dnf -y install stress
```
