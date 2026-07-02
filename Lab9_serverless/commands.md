# Lab9 Serverless Commands

이번 실습에서 사용한 주요 AWS CLI 명령어입니다. 계정 ID와 ARN은 명령 실행 시 변수로 가져오며, 저장소에는 실제 계정 식별자를 남기지 않습니다.

## 공통 변수

```bash
REGION=ap-northeast-2
TABLE_NAME=my-orders
POLICY_NAME=my-dynamodb-policy
ROLE_NAME=my-dynamodb-role
FUNCTION_NAME=my-orders-insert
RUNTIME=python3.13
HANDLER=lambda_function.lambda_handler
```

수업 PDF에는 Python 3.9가 표시되어 있지만, 이번 실습은 현재 Lambda 런타임에서 사용할 수 있는 Python 3.13으로 생성했습니다.

## DynamoDB 테이블 생성

```bash
aws dynamodb create-table \
  --region "${REGION}" \
  --table-name "${TABLE_NAME}" \
  --attribute-definitions AttributeName=OrderID,AttributeType=S AttributeName=CustomerID,AttributeType=S \
  --key-schema AttributeName=OrderID,KeyType=HASH AttributeName=CustomerID,KeyType=RANGE \
  --billing-mode PAY_PER_REQUEST \
  --tags Key=Lab,Value=Lab9 Key=Name,Value=my-orders

aws dynamodb wait table-exists \
  --region "${REGION}" \
  --table-name "${TABLE_NAME}"
```

## IAM 정책 생성

```bash
ACCOUNT_ID=$(aws sts get-caller-identity \
  --query Account \
  --output text)

TABLE_ARN="arn:aws:dynamodb:${REGION}:${ACCOUNT_ID}:table/${TABLE_NAME}"

POLICY_DOC=$(printf '{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:PutItem",
        "dynamodb:BatchWriteItem"
      ],
      "Resource": "%s"
    }
  ]
}' "${TABLE_ARN}")

POLICY_ARN=$(aws iam create-policy \
  --policy-name "${POLICY_NAME}" \
  --policy-document "${POLICY_DOC}" \
  --tags Key=Lab,Value=Lab9 \
  --query 'Policy.Arn' \
  --output text)
```

## Lambda 실행 역할 생성

```bash
TRUST_DOC='{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}'

aws iam create-role \
  --role-name "${ROLE_NAME}" \
  --assume-role-policy-document "${TRUST_DOC}" \
  --description 'Lab9 Lambda role for DynamoDB order inserts' \
  --tags Key=Lab,Value=Lab9

ROLE_ARN=$(aws iam get-role \
  --role-name "${ROLE_NAME}" \
  --query 'Role.Arn' \
  --output text)

aws iam attach-role-policy \
  --role-name "${ROLE_NAME}" \
  --policy-arn "${POLICY_ARN}"

aws iam attach-role-policy \
  --role-name "${ROLE_NAME}" \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
```

## Lambda 배포 패키지 생성

```bash
zip -r function.zip lambda_function.py
```

`lambda_function.py`는 [lambda_function.py](lambda_function.py)에 정리했습니다.

## Lambda 함수 생성

```bash
aws lambda create-function \
  --region "${REGION}" \
  --function-name "${FUNCTION_NAME}" \
  --runtime "${RUNTIME}" \
  --role "${ROLE_ARN}" \
  --handler "${HANDLER}" \
  --zip-file fileb://function.zip \
  --timeout 30 \
  --memory-size 128 \
  --description 'Lab9 Lambda inserts sample orders into DynamoDB' \
  --tags Lab=Lab9,Name=my-orders-insert

aws lambda wait function-active \
  --region "${REGION}" \
  --function-name "${FUNCTION_NAME}"
```

## Lambda 테스트 호출

AWS CLI v1 환경에서는 `--cli-binary-format` 옵션이 없으므로 `file://` payload 방식을 사용했습니다.

```bash
printf '{"source":"codex-lab9-test"}' > event.json

aws lambda invoke \
  --region "${REGION}" \
  --function-name "${FUNCTION_NAME}" \
  --payload file://event.json \
  lambda-response.json \
  --query '{StatusCode:StatusCode,FunctionError:FunctionError,ExecutedVersion:ExecutedVersion}' \
  --output json

cat lambda-response.json
```

## DynamoDB 항목 확인

```bash
aws dynamodb scan \
  --region "${REGION}" \
  --table-name "${TABLE_NAME}" \
  --projection-expression 'OrderID, CustomerID, ShippingAddress, GiftMessage, DiscountCode, PriorityDelivery' \
  --output table
```

## 상태 확인

```bash
aws dynamodb describe-table \
  --region "${REGION}" \
  --table-name "${TABLE_NAME}" \
  --query 'Table.{Name:TableName,Status:TableStatus,KeySchema:KeySchema,BillingMode:BillingModeSummary.BillingMode}' \
  --output table

aws lambda get-function \
  --region "${REGION}" \
  --function-name "${FUNCTION_NAME}" \
  --query 'Configuration.{Name:FunctionName,Runtime:Runtime,State:State,Handler:Handler,Timeout:Timeout,Memory:MemorySize}' \
  --output table
```

## 정리 명령어

```bash
aws lambda delete-function \
  --region "${REGION}" \
  --function-name "${FUNCTION_NAME}"

aws logs delete-log-group \
  --region "${REGION}" \
  --log-group-name "/aws/lambda/${FUNCTION_NAME}"

aws iam detach-role-policy \
  --role-name "${ROLE_NAME}" \
  --policy-arn "${POLICY_ARN}"

aws iam detach-role-policy \
  --role-name "${ROLE_NAME}" \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

aws iam delete-role \
  --role-name "${ROLE_NAME}"

aws iam delete-policy \
  --policy-arn "${POLICY_ARN}"

aws dynamodb delete-table \
  --region "${REGION}" \
  --table-name "${TABLE_NAME}"
```
