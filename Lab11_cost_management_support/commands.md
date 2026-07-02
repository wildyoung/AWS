# Lab11 Cost Management and Support Commands

비용 관리 단원은 새 리소스를 만들지 않고 읽기 전용 확인 명령 위주로 정리했습니다. 실제 비용 금액, 계정 ID, ARN, 퍼블릭 IP는 저장소에 남기지 않습니다.

## 공통 변수

```bash
REGION=ap-northeast-2
ACCOUNT_ID=$(aws sts get-caller-identity \
  --query Account \
  --output text)
```

## Cost Explorer 비용 확인

Cost Explorer API는 실제 비용 정보를 반환하므로 결과를 공개 저장소에 저장하지 않습니다.

```bash
START=2026-07-01
END=2026-08-01

aws ce get-cost-and-usage \
  --time-period Start="${START}",End="${END}" \
  --granularity MONTHLY \
  --metrics UnblendedCost \
  --group-by Type=DIMENSION,Key=SERVICE \
  --output table
```

## Budget 목록 확인

```bash
aws budgets describe-budgets \
  --account-id "${ACCOUNT_ID}" \
  --query 'Budgets[].{Name:BudgetName,Type:BudgetType,Limit:BudgetLimit.Amount,Unit:BudgetLimit.Unit}' \
  --output table
```

## 태그 기준 리소스 확인

```bash
aws resourcegroupstaggingapi get-resources \
  --region "${REGION}" \
  --tag-filters Key=Lab \
  --query 'ResourceTagMappingList[].{Resource:ResourceARN,Tags:Tags}' \
  --output table
```

결과에는 ARN이 포함될 수 있으므로 GitHub에는 저장하지 않습니다.

## 과금 위험 리소스 점검

### 실행 중 EC2

```bash
aws ec2 describe-instances \
  --region "${REGION}" \
  --filters Name=instance-state-name,Values=pending,running,stopping,stopped \
  --query 'Reservations[].Instances[].{Name:Tags[?Key==`Name`]|[0].Value,State:State.Name,Type:InstanceType}' \
  --output table
```

### NAT Gateway

```bash
aws ec2 describe-nat-gateways \
  --region "${REGION}" \
  --filter Name=state,Values=pending,available \
  --query 'NatGateways[].{State:State,SubnetId:SubnetId}' \
  --output table
```

### Elastic IP

```bash
aws ec2 describe-addresses \
  --region "${REGION}" \
  --query 'Addresses[].{AllocationId:AllocationId,Associated:AssociationId != `null`}' \
  --output table
```

### Load Balancer

```bash
aws elbv2 describe-load-balancers \
  --region "${REGION}" \
  --query 'LoadBalancers[].{Name:LoadBalancerName,Type:Type,Scheme:Scheme,State:State.Code}' \
  --output table
```

### RDS

```bash
aws rds describe-db-instances \
  --region "${REGION}" \
  --query 'DBInstances[].{DB:DBInstanceIdentifier,Class:DBInstanceClass,Status:DBInstanceStatus,MultiAZ:MultiAZ,Storage:AllocatedStorage}' \
  --output table
```

### EBS 볼륨

```bash
aws ec2 describe-volumes \
  --region "${REGION}" \
  --query 'Volumes[].{VolumeId:VolumeId,State:State,Size:Size,Type:VolumeType}' \
  --output table
```

### EBS 스냅샷

```bash
aws ec2 describe-snapshots \
  --region "${REGION}" \
  --owner-ids self \
  --query 'Snapshots[].{SnapshotId:SnapshotId,State:State,VolumeSize:VolumeSize,StartTime:StartTime}' \
  --output table
```

### CloudWatch Logs

```bash
aws logs describe-log-groups \
  --region "${REGION}" \
  --query 'logGroups[].{Name:logGroupName,Retention:retentionInDays,StoredBytes:storedBytes}' \
  --output table
```

## Support API 확인

AWS Support API는 일반적으로 Business 또는 Enterprise 계열 지원 플랜이 필요합니다. Basic Support 계정에서는 오류가 날 수 있습니다.

```bash
aws support describe-services \
  --region us-east-1 \
  --language ko \
  --output table
```

## Trusted Advisor 확인

Trusted Advisor API도 지원 플랜에 따라 접근 범위가 달라질 수 있습니다.

```bash
aws support describe-trusted-advisor-checks \
  --region us-east-1 \
  --language ko \
  --query 'checks[].{Name:name,Category:category}' \
  --output table
```

## 예산 생성 예시

아래 명령은 실제 Budget을 생성하므로 필요할 때만 실행합니다. 이메일 주소와 금액은 본인 환경에 맞게 바꿔야 합니다.

```bash
aws budgets create-budget \
  --account-id "${ACCOUNT_ID}" \
  --budget '{
    "BudgetName": "monthly-study-budget",
    "BudgetLimit": {
      "Amount": "10",
      "Unit": "USD"
    },
    "TimeUnit": "MONTHLY",
    "BudgetType": "COST"
  }' \
  --notifications-with-subscribers '[
    {
      "Notification": {
        "NotificationType": "ACTUAL",
        "ComparisonOperator": "GREATER_THAN",
        "Threshold": 80,
        "ThresholdType": "PERCENTAGE"
      },
      "Subscribers": [
        {
          "SubscriptionType": "EMAIL",
          "Address": "your-email@example.com"
        }
      ]
    }
  ]'
```

## 정리 판단 기준

```text
1. 실습 중인 리소스인지 확인
2. 중지 가능한지 확인
3. 삭제 시 데이터 손실이 있는지 확인
4. 스냅샷이나 백업이 필요한지 확인
5. 정리 후 Cost Explorer와 Billing Dashboard에서 비용 추세 확인
```
