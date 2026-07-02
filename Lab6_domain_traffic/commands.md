# Lab6 Domain and Traffic Commands

이번 실습에서 사용한 주요 AWS CLI 명령어입니다. 실제 도메인이 필요한 Route 53 hosted zone과 failover record 생성은 예시 명령으로 남겼고, 실행한 항목은 S3, Route 53 health check, CloudFront입니다.

## 공통 변수

```bash
REGION=ap-northeast-2
US_EAST_1=us-east-1
SUFFIX=20260703021919

ALB_DNS=my-alb-456796347.ap-northeast-2.elb.amazonaws.com
SITE_BUCKET=wildyoung-lab6-site-${SUFFIX}
DIRECT_BUCKET=wildyoung-lab6-direct-${SUFFIX}
CF_BUCKET=wildyoung-lab6-cf-origin-${SUFFIX}
OBJECT_KEY=lab6-cache-test.bin
HEALTH_CHECK_ID=d5330231-70c2-40d1-9426-b0c383a9519d
CLOUDFRONT_ID=E2D97RB2LI6MKC
CLOUDFRONT_DOMAIN=drytce7emp5dc.cloudfront.net
```

## ALB 상태 확인

```bash
curl -I http://${ALB_DNS}/
```

## Route 53 Health Check

```bash
HEALTH_CHECK_ID=$(aws route53 create-health-check \
  --caller-reference "lab6-${SUFFIX}" \
  --health-check-config "Type=HTTP,FullyQualifiedDomainName=${ALB_DNS},Port=80,ResourcePath=/,RequestInterval=30,FailureThreshold=3" \
  --query 'HealthCheck.Id' \
  --output text)

aws route53 change-tags-for-resource \
  --resource-type healthcheck \
  --resource-id "${HEALTH_CHECK_ID}" \
  --add-tags Key=Name,Value=my-web-status Key=Lab,Value=Lab6

aws route53 get-health-check-status \
  --health-check-id "${HEALTH_CHECK_ID}" \
  --query 'HealthCheckObservations[].StatusReport.Status' \
  --output text
```

## S3 정적 웹사이트 호스팅

```bash
aws s3api create-bucket \
  --bucket "${SITE_BUCKET}" \
  --region "${REGION}" \
  --create-bucket-configuration LocationConstraint="${REGION}"

aws s3api put-public-access-block \
  --bucket "${SITE_BUCKET}" \
  --public-access-block-configuration \
  BlockPublicAcls=false,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=false

aws s3api put-bucket-website \
  --bucket "${SITE_BUCKET}" \
  --website-configuration '{"IndexDocument":{"Suffix":"index.html"},"ErrorDocument":{"Key":"error.html"}}'

SITE_POLICY=$(printf '{"Version":"2012-10-17","Statement":[{"Sid":"PublicReadForWebsite","Effect":"Allow","Principal":"*","Action":"s3:GetObject","Resource":"arn:aws:s3:::%s/*"}]}' "${SITE_BUCKET}")

aws s3api put-bucket-policy \
  --bucket "${SITE_BUCKET}" \
  --policy "${SITE_POLICY}"

aws s3 cp site/index.html "s3://${SITE_BUCKET}/index.html" \
  --content-type text/html

aws s3 cp site/error.html "s3://${SITE_BUCKET}/error.html" \
  --content-type text/html

curl -I "http://${SITE_BUCKET}.s3-website.${REGION}.amazonaws.com"
```

## CloudFront 테스트용 S3 버킷

```bash
for BUCKET in "${DIRECT_BUCKET}" "${CF_BUCKET}"; do
  aws s3api create-bucket \
    --bucket "${BUCKET}" \
    --region "${US_EAST_1}"

  aws s3api put-public-access-block \
    --bucket "${BUCKET}" \
    --public-access-block-configuration \
    BlockPublicAcls=false,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=false

  POLICY=$(printf '{"Version":"2012-10-17","Statement":[{"Sid":"PublicReadForLab6CacheTest","Effect":"Allow","Principal":"*","Action":"s3:GetObject","Resource":"arn:aws:s3:::%s/*"}]}' "${BUCKET}")

  aws s3api put-bucket-policy \
    --bucket "${BUCKET}" \
    --policy "${POLICY}"
done
```

## 테스트 객체 업로드

수업 자료는 1GB 이상의 ISO 파일을 사용하지만, 비용과 시간을 줄이기 위해 32MiB 테스트 객체를 사용했습니다. 캐싱 흐름은 동일합니다.

```bash
dd if=/dev/zero of="${OBJECT_KEY}" bs=1m count=32

aws s3 cp "${OBJECT_KEY}" "s3://${DIRECT_BUCKET}/${OBJECT_KEY}" \
  --content-type application/octet-stream

aws s3 cp "${OBJECT_KEY}" "s3://${CF_BUCKET}/${OBJECT_KEY}" \
  --content-type application/octet-stream
```

## CloudFront 배포 생성

```bash
CF_ORIGIN_DOMAIN="${CF_BUCKET}.s3.amazonaws.com"

aws cloudfront create-distribution \
  --origin-domain-name "${CF_ORIGIN_DOMAIN}" \
  --default-root-object index.html \
  --query 'Distribution.{Id:Id,DomainName:DomainName,Status:Status,Enabled:DistributionConfig.Enabled}' \
  --output json

aws cloudfront wait distribution-deployed \
  --id "${CLOUDFRONT_ID}"
```

## 다운로드 테스트

```bash
DIRECT_URL="https://${DIRECT_BUCKET}.s3.amazonaws.com/${OBJECT_KEY}"
CLOUDFRONT_URL="https://${CLOUDFRONT_DOMAIN}/${OBJECT_KEY}"

curl -L -o /dev/null -sS \
  -w 'direct_s3 total=%{time_total}s speed=%{speed_download}B/s size=%{size_download}B\n' \
  "${DIRECT_URL}"

HEADER_FILE=$(mktemp)
curl -L -D "${HEADER_FILE}" -o /dev/null -sS \
  -w 'cloudfront total=%{time_total}s speed=%{speed_download}B/s size=%{size_download}B\n' \
  "${CLOUDFRONT_URL}"
awk 'BEGIN{IGNORECASE=1} /^x-cache:/ {gsub("\r", ""); print}' "${HEADER_FILE}"
rm -f "${HEADER_FILE}"
```

## Route 53 Hosted Zone 예시

실제 소유 도메인이 준비되면 다음 흐름으로 진행합니다.

```bash
DOMAIN_NAME=example.com

HOSTED_ZONE_ID=$(aws route53 create-hosted-zone \
  --name "${DOMAIN_NAME}" \
  --caller-reference "lab6-${SUFFIX}-${DOMAIN_NAME}" \
  --hosted-zone-config Comment="Lab6 public hosted zone",PrivateZone=false \
  --query 'HostedZone.Id' \
  --output text)

aws route53 list-resource-record-sets \
  --hosted-zone-id "${HOSTED_ZONE_ID}" \
  --query 'ResourceRecordSets[?Type==`NS`]'
```

위 명령으로 확인한 NS 4개를 도메인 등록기관의 네임서버로 설정해야 합니다.

## Failover 레코드 예시

아래 예시는 형식을 보여주기 위한 것입니다. 실제 실행 전 hosted zone ID, ALB hosted zone ID, S3 website hosted zone ID를 확인해야 합니다.

```bash
aws route53 change-resource-record-sets \
  --hosted-zone-id "${HOSTED_ZONE_ID}" \
  --change-batch file://route53-failover-records.json
```

`route53-failover-records.json`의 핵심 구조는 다음과 같습니다.

```json
{
  "Changes": [
    {
      "Action": "UPSERT",
      "ResourceRecordSet": {
        "Name": "example.com.",
        "Type": "A",
        "SetIdentifier": "web-first",
        "Failover": "PRIMARY",
        "HealthCheckId": "HEALTH_CHECK_ID",
        "AliasTarget": {
          "HostedZoneId": "ALB_HOSTED_ZONE_ID",
          "DNSName": "dualstack.my-alb.example.elb.amazonaws.com.",
          "EvaluateTargetHealth": true
        }
      }
    },
    {
      "Action": "UPSERT",
      "ResourceRecordSet": {
        "Name": "example.com.",
        "Type": "A",
        "SetIdentifier": "web-second",
        "Failover": "SECONDARY",
        "AliasTarget": {
          "HostedZoneId": "S3_WEBSITE_HOSTED_ZONE_ID",
          "DNSName": "s3-website.ap-northeast-2.amazonaws.com.",
          "EvaluateTargetHealth": false
        }
      }
    }
  ]
}
```

## 정리 명령어

```bash
aws cloudfront get-distribution-config \
  --id "${CLOUDFRONT_ID}"

# CloudFront는 먼저 Enabled=false로 업데이트해 비활성화한 뒤 삭제합니다.
# 배포 삭제는 ETag 값을 If-Match로 넣어야 합니다.

aws route53 delete-health-check \
  --health-check-id "${HEALTH_CHECK_ID}"

aws s3 rm "s3://${SITE_BUCKET}" --recursive
aws s3 rb "s3://${SITE_BUCKET}"

aws s3 rm "s3://${DIRECT_BUCKET}" --recursive
aws s3 rb "s3://${DIRECT_BUCKET}"

aws s3 rm "s3://${CF_BUCKET}" --recursive
aws s3 rb "s3://${CF_BUCKET}"
```
