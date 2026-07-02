# Lab12 Disaster Recovery Commands

재해 복구 단원은 실제 복구 리소스를 만들지 않고 읽기 전용 점검 명령 위주로 정리했습니다. 결과에는 계정 정보, ARN, 버킷명, 리소스 ID가 포함될 수 있으므로 공개 저장소에 저장하지 않습니다.

## 공통 변수

```bash
REGION=ap-northeast-2
DR_REGION=ap-northeast-1
```

## AWS Backup 점검

### Backup vault 목록

```bash
aws backup list-backup-vaults \
  --region "${REGION}" \
  --query 'BackupVaultList[].{Name:BackupVaultName,RecoveryPoints:NumberOfRecoveryPoints}' \
  --output table
```

### Backup plan 목록

```bash
aws backup list-backup-plans \
  --region "${REGION}" \
  --query 'BackupPlansList[].{Name:BackupPlanName,Id:BackupPlanId,Version:VersionId}' \
  --output table
```

## EBS 스냅샷 점검

```bash
aws ec2 describe-snapshots \
  --region "${REGION}" \
  --owner-ids self \
  --query 'Snapshots[].{SnapshotId:SnapshotId,State:State,VolumeSize:VolumeSize,StartTime:StartTime}' \
  --output table
```

## AMI 점검

```bash
aws ec2 describe-images \
  --region "${REGION}" \
  --owners self \
  --query 'Images[].{Name:Name,ImageId:ImageId,State:State,CreationDate:CreationDate}' \
  --output table
```

## RDS 백업 설정 점검

엔드포인트와 주소 정보는 출력하지 않도록 쿼리를 제한합니다.

```bash
aws rds describe-db-instances \
  --region "${REGION}" \
  --query 'DBInstances[].{DB:DBInstanceIdentifier,Status:DBInstanceStatus,MultiAZ:MultiAZ,BackupRetention:BackupRetentionPeriod,StorageEncrypted:StorageEncrypted,DeletionProtection:DeletionProtection}' \
  --output table
```

## RDS 스냅샷 점검

```bash
aws rds describe-db-snapshots \
  --region "${REGION}" \
  --snapshot-type manual \
  --query 'DBSnapshots[].{DB:DBInstanceIdentifier,Snapshot:DBSnapshotIdentifier,Status:Status,Encrypted:Encrypted,Created:SnapshotCreateTime}' \
  --output table
```

## DynamoDB 백업 설정 점검

```bash
TABLE_NAME=my-orders

aws dynamodb describe-continuous-backups \
  --region "${REGION}" \
  --table-name "${TABLE_NAME}" \
  --query 'ContinuousBackupsDescription.{Status:ContinuousBackupsStatus,PITR:PointInTimeRecoveryDescription.PointInTimeRecoveryStatus}' \
  --output table
```

## S3 버전 관리 확인

```bash
BUCKET_NAME=your-bucket-name

aws s3api get-bucket-versioning \
  --bucket "${BUCKET_NAME}" \
  --output json
```

## S3 복제 설정 확인

복제가 구성되지 않은 버킷에서는 오류가 날 수 있습니다.

```bash
aws s3api get-bucket-replication \
  --bucket "${BUCKET_NAME}" \
  --output json
```

## Route 53 Health Check 확인

```bash
aws route53 list-health-checks \
  --query 'HealthChecks[].{Id:Id,Type:HealthCheckConfig.Type,Disabled:HealthCheckConfig.Disabled}' \
  --output table
```

## CloudFormation 템플릿 기반 복구 준비 확인

```bash
aws cloudformation list-stacks \
  --region "${REGION}" \
  --stack-status-filter CREATE_COMPLETE UPDATE_COMPLETE \
  --query 'StackSummaries[].{Name:StackName,Status:StackStatus,Updated:LastUpdatedTime}' \
  --output table
```

## DR 리전 기본 준비 상태 확인

```bash
aws ec2 describe-vpcs \
  --region "${DR_REGION}" \
  --query 'Vpcs[].{VpcId:VpcId,Cidr:CidrBlock,Default:IsDefault}' \
  --output table

aws ec2 describe-subnets \
  --region "${DR_REGION}" \
  --query 'Subnets[].{SubnetId:SubnetId,VpcId:VpcId,Az:AvailabilityZone,Cidr:CidrBlock}' \
  --output table
```

## 실제 복구 작업 예시

아래 명령은 실제 리소스를 생성하거나 복사할 수 있으므로 문서 예시로만 보관합니다. 비용과 데이터 영향도를 확인한 뒤 실행해야 합니다.

### AMI 교차 리전 복사

```bash
SOURCE_AMI_ID=ami-xxxxxxxxxxxxxxxxx

aws ec2 copy-image \
  --region "${DR_REGION}" \
  --source-region "${REGION}" \
  --source-image-id "${SOURCE_AMI_ID}" \
  --name "dr-copy-${SOURCE_AMI_ID}"
```

### EBS 스냅샷 교차 리전 복사

```bash
SOURCE_SNAPSHOT_ID=snap-xxxxxxxxxxxxxxxxx

aws ec2 copy-snapshot \
  --region "${DR_REGION}" \
  --source-region "${REGION}" \
  --source-snapshot-id "${SOURCE_SNAPSHOT_ID}" \
  --description "DR copy of ${SOURCE_SNAPSHOT_ID}"
```

### RDS 스냅샷 복사

```bash
SOURCE_DB_SNAPSHOT_ARN=arn:aws:rds:ap-northeast-2:ACCOUNT_ID:snapshot:SOURCE_SNAPSHOT
TARGET_SNAPSHOT_ID=dr-copy-source-snapshot

aws rds copy-db-snapshot \
  --region "${DR_REGION}" \
  --source-db-snapshot-identifier "${SOURCE_DB_SNAPSHOT_ARN}" \
  --target-db-snapshot-identifier "${TARGET_SNAPSHOT_ID}"
```

## DR 점검 질문

```text
1. 각 서비스의 RPO/RTO가 문서화되어 있는가?
2. 백업이 실제로 생성되고 있는가?
3. 백업에서 복원 테스트를 해본 적이 있는가?
4. 복구 리전의 네트워크와 권한이 준비되어 있는가?
5. DNS 전환 절차가 문서화되어 있는가?
6. 장애 후 원래 리전으로 돌아오는 failback 절차가 있는가?
7. 마지막 game day 결과와 개선 사항이 기록되어 있는가?
```
