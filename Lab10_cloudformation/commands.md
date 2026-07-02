# Lab10 CloudFormation Commands

이번 실습에서 사용한 주요 AWS CLI 명령어입니다. 계정 ID, 퍼블릭 IP, 실제 ARN은 저장소에 남기지 않습니다.

## 공통 변수

```bash
REGION=ap-northeast-2
KEY_NAME=my-key
STACK_ALL=test-all-stack
CHANGE_SET=lab10-add-private-nat
```

제공 템플릿에는 키페어 이름을 직접 넣는 부분이 있습니다. 실제 실행 전에는 `Your-Keypair-Name` 또는 `Your-Key-Name`을 본인 키페어 이름으로 바꿔야 합니다.

```bash
cp cre_testvpcAll.yaml /tmp/cre_testvpcAll.yaml
cp update_testvpcAll.yaml /tmp/update_testvpcAll.yaml
cp cre_ec2.yaml /tmp/cre_ec2.yaml

sed -i '' "s/Your-Keypair-Name/${KEY_NAME}/g; s/Your-Key-Name/${KEY_NAME}/g" /tmp/cre_testvpcAll.yaml
sed -i '' "s/Your-Keypair-Name/${KEY_NAME}/g; s/Your-Key-Name/${KEY_NAME}/g" /tmp/update_testvpcAll.yaml
sed -i '' "s/Your-Keypair-Name/${KEY_NAME}/g; s/Your-Key-Name/${KEY_NAME}/g" /tmp/cre_ec2.yaml
```

## 템플릿 검증

```bash
aws cloudformation validate-template \
  --region "${REGION}" \
  --template-body file://cre_testvpcAll.yaml

aws cloudformation validate-template \
  --region "${REGION}" \
  --template-body file://update_testvpcAll.yaml

aws cloudformation validate-template \
  --region "${REGION}" \
  --template-body file://cre_myvpc.yaml

aws cloudformation validate-template \
  --region "${REGION}" \
  --template-body file://cre_ec2.yaml

aws cloudformation validate-template \
  --region "${REGION}" \
  --template-body file://cre_alb.yaml
```

## 단일 스택 생성

```bash
aws cloudformation create-stack \
  --region "${REGION}" \
  --stack-name "${STACK_ALL}" \
  --template-body file:///tmp/cre_testvpcAll.yaml \
  --tags Key=Lab,Value=Lab10 Key=Purpose,Value=CloudFormationPractice

aws cloudformation wait stack-create-complete \
  --region "${REGION}" \
  --stack-name "${STACK_ALL}"

aws cloudformation describe-stack-resources \
  --region "${REGION}" \
  --stack-name "${STACK_ALL}" \
  --query 'StackResources[].{Logical:LogicalResourceId,Type:ResourceType,Status:ResourceStatus}' \
  --output table
```

## 변경 세트 생성과 확인

```bash
aws cloudformation create-change-set \
  --region "${REGION}" \
  --stack-name "${STACK_ALL}" \
  --change-set-name "${CHANGE_SET}" \
  --template-body file:///tmp/update_testvpcAll.yaml

aws cloudformation wait change-set-create-complete \
  --region "${REGION}" \
  --stack-name "${STACK_ALL}" \
  --change-set-name "${CHANGE_SET}"

aws cloudformation describe-change-set \
  --region "${REGION}" \
  --stack-name "${STACK_ALL}" \
  --change-set-name "${CHANGE_SET}" \
  --query 'Changes[].ResourceChange.{Action:Action,Logical:LogicalResourceId,Type:ResourceType,Replacement:Replacement}' \
  --output table
```

## 변경 세트 실행

```bash
aws cloudformation execute-change-set \
  --region "${REGION}" \
  --stack-name "${STACK_ALL}" \
  --change-set-name "${CHANGE_SET}"

aws cloudformation wait stack-update-complete \
  --region "${REGION}" \
  --stack-name "${STACK_ALL}"

aws cloudformation describe-stack-resources \
  --region "${REGION}" \
  --stack-name "${STACK_ALL}" \
  --query 'StackResources[].{Logical:LogicalResourceId,Type:ResourceType,Status:ResourceStatus}' \
  --output table
```

## 단일 스택 삭제

```bash
aws cloudformation delete-stack \
  --region "${REGION}" \
  --stack-name "${STACK_ALL}"

aws cloudformation wait stack-delete-complete \
  --region "${REGION}" \
  --stack-name "${STACK_ALL}"
```

## 분리 스택 생성

### VPC 스택

```bash
aws cloudformation create-stack \
  --region "${REGION}" \
  --stack-name my-stack1 \
  --template-body file://cre_myvpc.yaml \
  --tags Key=Lab,Value=Lab10 Key=Purpose,Value=CloudFormationSplitStack

aws cloudformation wait stack-create-complete \
  --region "${REGION}" \
  --stack-name my-stack1

aws cloudformation list-exports \
  --region "${REGION}" \
  --query 'Exports[?Name==`VPCId` || Name==`SubnetId01` || Name==`SubnetId02` || Name==`SecurityGroupId`].{Name:Name}' \
  --output table
```

### EC2 스택

```bash
aws cloudformation create-stack \
  --region "${REGION}" \
  --stack-name my-stack2 \
  --template-body file:///tmp/cre_ec2.yaml \
  --tags Key=Lab,Value=Lab10 Key=Purpose,Value=CloudFormationSplitStack

aws cloudformation wait stack-create-complete \
  --region "${REGION}" \
  --stack-name my-stack2
```

### ALB 스택

```bash
aws cloudformation create-stack \
  --region "${REGION}" \
  --stack-name my-stack3 \
  --template-body file://cre_alb.yaml \
  --tags Key=Lab,Value=Lab10 Key=Purpose,Value=CloudFormationSplitStack

aws cloudformation wait stack-create-complete \
  --region "${REGION}" \
  --stack-name my-stack3
```

## 분리 스택 상태 확인

```bash
aws cloudformation describe-stacks \
  --region "${REGION}" \
  --query 'Stacks[].{StackName:StackName,Status:StackStatus}' \
  --output table

aws cloudformation describe-stack-resources \
  --region "${REGION}" \
  --stack-name my-stack1 \
  --query 'StackResources[].{Logical:LogicalResourceId,Type:ResourceType,Status:ResourceStatus}' \
  --output table

aws cloudformation describe-stack-resources \
  --region "${REGION}" \
  --stack-name my-stack2 \
  --query 'StackResources[].{Logical:LogicalResourceId,Type:ResourceType,Status:ResourceStatus}' \
  --output table

aws cloudformation describe-stack-resources \
  --region "${REGION}" \
  --stack-name my-stack3 \
  --query 'StackResources[].{Logical:LogicalResourceId,Type:ResourceType,Status:ResourceStatus}' \
  --output table
```

## 분리 스택 삭제

`my-stack2`와 `my-stack3`가 `my-stack1`의 Export를 Import하므로, VPC 스택인 `my-stack1`을 마지막에 삭제합니다.

```bash
aws cloudformation delete-stack \
  --region "${REGION}" \
  --stack-name my-stack2

aws cloudformation wait stack-delete-complete \
  --region "${REGION}" \
  --stack-name my-stack2

aws cloudformation delete-stack \
  --region "${REGION}" \
  --stack-name my-stack3

aws cloudformation wait stack-delete-complete \
  --region "${REGION}" \
  --stack-name my-stack3

aws cloudformation delete-stack \
  --region "${REGION}" \
  --stack-name my-stack1

aws cloudformation wait stack-delete-complete \
  --region "${REGION}" \
  --stack-name my-stack1
```

## 정리 확인

```bash
aws cloudformation list-exports \
  --region "${REGION}" \
  --query 'Exports[].Name' \
  --output text

aws cloudformation describe-stacks \
  --region "${REGION}" \
  --query 'Stacks[].{Name:StackName,Status:StackStatus}' \
  --output table
```

두 명령이 비어 있으면 Lab10에서 만든 활성 CloudFormation 스택과 Export가 남아 있지 않은 상태입니다.
