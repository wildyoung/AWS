# Lab01 Docker Settings Examples

이 디렉터리는 선택적으로 EC2 Docker host를 만들 때 사용할 CloudFormation 템플릿입니다. 이번 정리는 비용 방지를 위해 실제 스택을 생성하지 않고 템플릿 검증만 수행했습니다.

## 검증

```bash
aws cloudformation validate-template \
  --template-body file://Part2_Docker/examples/lab01_settings/cre_myvpc.yaml \
  --region ap-northeast-2

aws cloudformation validate-template \
  --template-body file://Part2_Docker/examples/lab01_settings/cre_dockerhost.yaml \
  --region ap-northeast-2
```

## 생성

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

## 삭제

```bash
aws cloudformation delete-stack --stack-name docker-host --region ap-northeast-2
aws cloudformation wait stack-delete-complete --stack-name docker-host --region ap-northeast-2
aws cloudformation delete-stack --stack-name docker-vpc --region ap-northeast-2
aws cloudformation wait stack-delete-complete --stack-name docker-vpc --region ap-northeast-2
```
