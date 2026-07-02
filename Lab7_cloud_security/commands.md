# Lab7 Cloud Security Commands

이번 실습에서 사용한 주요 AWS CLI 명령어입니다. 콘솔 비밀번호, MFA 시드, Access Key는 생성하지 않았고 GitHub에도 남기지 않았습니다.

## 공통 변수

```bash
REGION=ap-northeast-2
SUFFIX=20260703023156

DEV_USER=dev01
ADMIN_USER=my-admin
ROLE_NAME=myS3AccessRole
PROFILE_NAME=myS3AccessRole
POLICY_NAME=Lab7S3BucketAccess-${SUFFIX}
BUCKET=wildyoung-lab7-security-${SUFFIX}
```

## IAM 사용자 생성

```bash
aws iam create-user \
  --user-name "${DEV_USER}" \
  --tags Key=Lab,Value=Lab7 Key=Purpose,Value=EC2OnlyPolicyDemo

aws iam attach-user-policy \
  --user-name "${DEV_USER}" \
  --policy-arn arn:aws:iam::aws:policy/AmazonEC2FullAccess

aws iam create-user \
  --user-name "${ADMIN_USER}" \
  --tags Key=Lab,Value=Lab7 Key=Purpose,Value=AdminPolicyDemoNoCredentials

aws iam attach-user-policy \
  --user-name "${ADMIN_USER}" \
  --policy-arn arn:aws:iam::aws:policy/AdministratorAccess
```

## 콘솔 비밀번호와 액세스 키 미생성 확인

```bash
for USER in "${DEV_USER}" "${ADMIN_USER}"; do
  aws iam get-login-profile --user-name "${USER}"
  aws iam list-access-keys --user-name "${USER}"
done
```

`get-login-profile`이 `NoSuchEntity`를 반환하면 콘솔 로그인 프로필이 없는 상태입니다.

## 정책 시뮬레이션

```bash
DEV_ARN=$(aws iam get-user \
  --user-name "${DEV_USER}" \
  --query 'User.Arn' \
  --output text)

ADMIN_ARN=$(aws iam get-user \
  --user-name "${ADMIN_USER}" \
  --query 'User.Arn' \
  --output text)

aws iam simulate-principal-policy \
  --policy-source-arn "${DEV_ARN}" \
  --action-names ec2:DescribeInstances ec2:StartInstances s3:ListAllMyBuckets iam:ListUsers \
  --query 'EvaluationResults[].{Action:EvalActionName,Decision:EvalDecision}' \
  --output table

aws iam simulate-principal-policy \
  --policy-source-arn "${ADMIN_ARN}" \
  --action-names ec2:DescribeInstances s3:ListAllMyBuckets iam:ListUsers \
  --query 'EvaluationResults[].{Action:EvalActionName,Decision:EvalDecision}' \
  --output table
```

## S3 비공개 버킷 생성

```bash
aws s3api create-bucket \
  --bucket "${BUCKET}" \
  --region "${REGION}" \
  --create-bucket-configuration LocationConstraint="${REGION}"

aws s3api put-public-access-block \
  --bucket "${BUCKET}" \
  --public-access-block-configuration \
  BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true

aws s3api put-bucket-encryption \
  --bucket "${BUCKET}" \
  --server-side-encryption-configuration \
  '{"Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"AES256"}}]}'
```

## EC2용 IAM 역할 생성

```bash
TRUST_POLICY='{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "ec2.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}'

aws iam create-role \
  --role-name "${ROLE_NAME}" \
  --assume-role-policy-document "${TRUST_POLICY}" \
  --description 'Lab7 EC2 role for scoped S3 access' \
  --tags Key=Lab,Value=Lab7
```

## Lab7 버킷 전용 권한 연결

수업 자료는 `AmazonS3FullAccess`를 사용하지만, 이번 실습에서는 최소 권한을 보여주기 위해 Lab7 버킷에만 접근하는 인라인 정책을 사용했습니다.

```bash
BUCKET_POLICY=$(printf '{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ListLab7Bucket",
      "Effect": "Allow",
      "Action": ["s3:ListBucket"],
      "Resource": "arn:aws:s3:::%s"
    },
    {
      "Sid": "ReadWriteLab7Objects",
      "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"],
      "Resource": "arn:aws:s3:::%s/*"
    }
  ]
}' "${BUCKET}" "${BUCKET}")

aws iam put-role-policy \
  --role-name "${ROLE_NAME}" \
  --policy-name "${POLICY_NAME}" \
  --policy-document "${BUCKET_POLICY}"
```

## Instance Profile 생성과 EC2 연결

```bash
aws iam create-instance-profile \
  --instance-profile-name "${PROFILE_NAME}" \
  --tags Key=Lab,Value=Lab7

aws iam add-role-to-instance-profile \
  --instance-profile-name "${PROFILE_NAME}" \
  --role-name "${ROLE_NAME}"

WEB01_ID=$(aws ec2 describe-instances \
  --region "${REGION}" \
  --filters 'Name=tag:Name,Values=my-web01' 'Name=instance-state-name,Values=running' \
  --query 'Reservations[0].Instances[0].InstanceId' \
  --output text)

WEB02_ID=$(aws ec2 describe-instances \
  --region "${REGION}" \
  --filters 'Name=tag:Name,Values=my-web02' 'Name=instance-state-name,Values=running' \
  --query 'Reservations[0].Instances[0].InstanceId' \
  --output text)

for INSTANCE_ID in "${WEB01_ID}" "${WEB02_ID}"; do
  aws ec2 associate-iam-instance-profile \
    --region "${REGION}" \
    --instance-id "${INSTANCE_ID}" \
    --iam-instance-profile Name="${PROFILE_NAME}"
done
```

## EC2에서 AWS CLI 설치

```bash
ssh -i <KEY_FILE> ubuntu@<EC2_PUBLIC_IP>

sudo apt-get update -y
sudo apt-get install -y unzip curl
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o /tmp/awscliv2.zip
unzip -q /tmp/awscliv2.zip -d /tmp
sudo /tmp/aws/install --update
aws --version
```

## EC2에서 S3 업로드/다운로드

EC2 안에서 실행합니다.

```bash
unset AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN AWS_PROFILE

aws sts get-caller-identity --query Arn --output text

echo "Lab7 EC2 S3 role test" > /tmp/hello-s3.txt
aws s3 cp /tmp/hello-s3.txt "s3://${BUCKET}/my-web01/hello-s3.txt"
rm -f /tmp/hello-s3-downloaded.txt
aws s3 cp "s3://${BUCKET}/my-web01/hello-s3.txt" /tmp/hello-s3-downloaded.txt
cmp /tmp/hello-s3.txt /tmp/hello-s3-downloaded.txt

aws s3 ls "s3://${BUCKET}/my-web01/"

# 최소 권한 확인: 전체 버킷 목록은 허용하지 않았으므로 거부되어야 합니다.
aws s3 ls
```

## S3 보안 설정 확인

```bash
aws s3api get-public-access-block \
  --bucket "${BUCKET}" \
  --query 'PublicAccessBlockConfiguration' \
  --output json

aws s3api get-bucket-encryption \
  --bucket "${BUCKET}" \
  --query 'ServerSideEncryptionConfiguration.Rules[0].ApplyServerSideEncryptionByDefault.SSEAlgorithm' \
  --output text
```

## 정리 명령어

```bash
ASSOC_IDS=$(aws ec2 describe-iam-instance-profile-associations \
  --region "${REGION}" \
  --filters Name=instance-id,Values="${WEB01_ID}","${WEB02_ID}" \
  --query 'IamInstanceProfileAssociations[].AssociationId' \
  --output text)

for ASSOC_ID in ${ASSOC_IDS}; do
  aws ec2 disassociate-iam-instance-profile \
    --region "${REGION}" \
    --association-id "${ASSOC_ID}"
done

aws iam remove-role-from-instance-profile \
  --instance-profile-name "${PROFILE_NAME}" \
  --role-name "${ROLE_NAME}"

aws iam delete-instance-profile \
  --instance-profile-name "${PROFILE_NAME}"

aws iam delete-role-policy \
  --role-name "${ROLE_NAME}" \
  --policy-name "${POLICY_NAME}"

aws iam delete-role \
  --role-name "${ROLE_NAME}"

aws iam detach-user-policy \
  --user-name "${DEV_USER}" \
  --policy-arn arn:aws:iam::aws:policy/AmazonEC2FullAccess

aws iam delete-user \
  --user-name "${DEV_USER}"

aws iam detach-user-policy \
  --user-name "${ADMIN_USER}" \
  --policy-arn arn:aws:iam::aws:policy/AdministratorAccess

aws iam delete-user \
  --user-name "${ADMIN_USER}"

aws s3 rm "s3://${BUCKET}" --recursive
aws s3 rb "s3://${BUCKET}"
```
