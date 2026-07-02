# Lab8 Relational Database Commands

이번 실습에서 사용한 주요 AWS CLI와 MySQL 명령어입니다. DB 비밀번호와 RDS endpoint는 저장소에 남기지 않습니다.

## 공통 변수

```bash
REGION=ap-northeast-2
VPC_ID=<MY_VPC_ID>
SUBNET1=<MY_SUB01_ID>
SUBNET2=<MY_SUB02_ID>
WEB_SG=<MY_WEB_SG_ID>

DB_IDENTIFIER=rds01
DB_NAME=product
DB_USER=admin
DB_PASSWORD=<DB_PASSWORD>
DB_SUBNET_GROUP=my-rds-subnet-group
RDS_SG_NAME=my-rds-sg
```

## RDS 보안 그룹 생성

```bash
RDS_SG=$(aws ec2 create-security-group \
  --region "${REGION}" \
  --group-name "${RDS_SG_NAME}" \
  --description 'Lab8 RDS MySQL access from web security group' \
  --vpc-id "${VPC_ID}" \
  --tag-specifications 'ResourceType=security-group,Tags=[{Key=Name,Value=my-rds-sg},{Key=Lab,Value=Lab8}]' \
  --query 'GroupId' \
  --output text)

aws ec2 authorize-security-group-ingress \
  --region "${REGION}" \
  --group-id "${RDS_SG}" \
  --ip-permissions "IpProtocol=tcp,FromPort=3306,ToPort=3306,UserIdGroupPairs=[{GroupId=${WEB_SG},Description='mysql from my-web-sg'}]"
```

## DB Subnet Group 생성

```bash
aws rds create-db-subnet-group \
  --region "${REGION}" \
  --db-subnet-group-name "${DB_SUBNET_GROUP}" \
  --db-subnet-group-description 'Lab8 RDS subnet group across my-sub01 and my-sub02' \
  --subnet-ids "${SUBNET1}" "${SUBNET2}" \
  --tags Key=Lab,Value=Lab8 Key=Name,Value=my-rds-subnet-group
```

## RDS MySQL 생성

```bash
aws rds create-db-instance \
  --region "${REGION}" \
  --db-instance-identifier "${DB_IDENTIFIER}" \
  --engine mysql \
  --engine-version 8.0.46 \
  --db-instance-class db.t3.micro \
  --allocated-storage 20 \
  --storage-type gp2 \
  --db-name "${DB_NAME}" \
  --master-username "${DB_USER}" \
  --master-user-password "${DB_PASSWORD}" \
  --db-subnet-group-name "${DB_SUBNET_GROUP}" \
  --vpc-security-group-ids "${RDS_SG}" \
  --backup-retention-period 0 \
  --no-multi-az \
  --no-publicly-accessible \
  --storage-encrypted \
  --copy-tags-to-snapshot \
  --no-deletion-protection \
  --tags Key=Lab,Value=Lab8 Key=Name,Value=rds01
```

## RDS 생성 완료 대기와 Endpoint 확인

```bash
aws rds wait db-instance-available \
  --region "${REGION}" \
  --db-instance-identifier "${DB_IDENTIFIER}"

RDS_ENDPOINT=$(aws rds describe-db-instances \
  --region "${REGION}" \
  --db-instance-identifier "${DB_IDENTIFIER}" \
  --query 'DBInstances[0].Endpoint.Address' \
  --output text)
```

## RDS 상태 확인

```bash
aws rds describe-db-instances \
  --region "${REGION}" \
  --db-instance-identifier "${DB_IDENTIFIER}" \
  --query 'DBInstances[0].{Id:DBInstanceIdentifier,Status:DBInstanceStatus,Engine:Engine,Version:EngineVersion,Class:DBInstanceClass,Public:PubliclyAccessible,Encrypted:StorageEncrypted,MultiAZ:MultiAZ}' \
  --output table
```

## EC2에서 RDS 접속

`my-web01`에서 실행합니다.

```bash
mysql -h "${RDS_ENDPOINT}" -u "${DB_USER}" -p
```

비밀번호는 프롬프트에 직접 입력합니다. 저장소에 남기지 않습니다.

## SQL 실습

```sql
SHOW DATABASES;
USE product;

CREATE TABLE IF NOT EXISTS product_list (
  id INT,
  name VARCHAR(20)
);

TRUNCATE TABLE product_list;

INSERT INTO product_list VALUES
  (1, 'Book Shelf'),
  (2, 'Chair'),
  (3, 'Pencil Holder');

SELECT * FROM product_list ORDER BY id;
```

## CLI에서 비대화형으로 SQL 실행

비밀번호를 명령줄에 직접 쓰지 않으려면 임시 option file을 사용합니다.

```bash
cat > /tmp/lab8-my.cnf <<EOF
[client]
host=${RDS_ENDPOINT}
user=${DB_USER}
password=${DB_PASSWORD}
ssl-mode=DISABLED
EOF

chmod 600 /tmp/lab8-my.cnf

mysql --defaults-extra-file=/tmp/lab8-my.cnf product <<'SQL'
CREATE TABLE IF NOT EXISTS product_list (
  id INT,
  name VARCHAR(20)
);
TRUNCATE TABLE product_list;
INSERT INTO product_list VALUES
  (1, 'Book Shelf'),
  (2, 'Chair'),
  (3, 'Pencil Holder');
SELECT * FROM product_list ORDER BY id;
SQL

rm -f /tmp/lab8-my.cnf
```

## 정리 명령어

```bash
aws rds delete-db-instance \
  --region "${REGION}" \
  --db-instance-identifier "${DB_IDENTIFIER}" \
  --skip-final-snapshot \
  --delete-automated-backups

aws rds wait db-instance-deleted \
  --region "${REGION}" \
  --db-instance-identifier "${DB_IDENTIFIER}"

aws rds delete-db-subnet-group \
  --region "${REGION}" \
  --db-subnet-group-name "${DB_SUBNET_GROUP}"

aws ec2 delete-security-group \
  --region "${REGION}" \
  --group-id "${RDS_SG}"
```
