# Lab3 High Availability Commands

실제 계정 ID, 퍼블릭 IP, 이메일 주소, 키 파일 내용은 문서에 남기지 않습니다. 아래 명령어는 실습에서 사용한 흐름을 재현할 수 있도록 주요 값만 플레이스홀더로 정리했습니다.

## 기본 변수

```bash
REGION=ap-northeast-2
VPC_ID=<MY_VPC_ID>
SUBNET1=<MY_SUB01_ID>
SUBNET2=<MY_SUB02_ID>
WEB_SG=<MY_WEB_SG_ID>
WEB01=<MY_WEB01_INSTANCE_ID>
WEB02=<MY_WEB02_INSTANCE_ID>
AMI_ID=<WEB_SERVER_AMI_ID>
KEY_NAME=my-key
INSTANCE_TYPE=t3.micro
EMAIL_ENDPOINT=<EMAIL_ADDRESS>
```

## ALB 보안 그룹

```bash
ALB_SG=$(aws ec2 create-security-group \
  --group-name my-alb-sg \
  --description 'Lab3 ALB HTTP security group' \
  --vpc-id "$VPC_ID" \
  --query 'GroupId' \
  --output text)
```

```bash
aws ec2 authorize-security-group-ingress \
  --group-id "$ALB_SG" \
  --protocol tcp \
  --port 80 \
  --cidr 0.0.0.0/0
```

## Target Group

```bash
TG_ARN=$(aws elbv2 create-target-group \
  --name webserver-tg \
  --protocol HTTP \
  --port 80 \
  --vpc-id "$VPC_ID" \
  --target-type instance \
  --health-check-path / \
  --matcher HttpCode=200-399 \
  --query 'TargetGroups[0].TargetGroupArn' \
  --output text)
```

```bash
aws elbv2 register-targets \
  --target-group-arn "$TG_ARN" \
  --targets Id="$WEB01" Id="$WEB02"
```

## Application Load Balancer

```bash
ALB_ARN=$(aws elbv2 create-load-balancer \
  --name my-alb \
  --type application \
  --scheme internet-facing \
  --ip-address-type ipv4 \
  --security-groups "$ALB_SG" \
  --subnets "$SUBNET1" "$SUBNET2" \
  --query 'LoadBalancers[0].LoadBalancerArn' \
  --output text)
```

```bash
aws elbv2 wait load-balancer-available \
  --load-balancer-arns "$ALB_ARN"
```

```bash
aws elbv2 create-listener \
  --load-balancer-arn "$ALB_ARN" \
  --protocol HTTP \
  --port 80 \
  --default-actions Type=forward,TargetGroupArn="$TG_ARN"
```

## 웹 서버 보안 그룹 조정

```bash
aws ec2 revoke-security-group-ingress \
  --group-id "$WEB_SG" \
  --protocol tcp \
  --port 80 \
  --cidr 0.0.0.0/0
```

```bash
aws ec2 authorize-security-group-ingress \
  --group-id "$WEB_SG" \
  --ip-permissions "[{\"IpProtocol\":\"tcp\",\"FromPort\":80,\"ToPort\":80,\"UserIdGroupPairs\":[{\"GroupId\":\"$ALB_SG\"}]}]"
```

## SNS Topic과 CloudWatch Alarm

```bash
TOPIC_ARN=$(aws sns create-topic \
  --name admin-topic \
  --query TopicArn \
  --output text)
```

```bash
aws sns subscribe \
  --topic-arn "$TOPIC_ARN" \
  --protocol email \
  --notification-endpoint "$EMAIL_ENDPOINT"
```

```bash
aws cloudwatch put-metric-alarm \
  --alarm-name my-web01-cpu-high \
  --alarm-description 'Lab3 alarm: my-web01 CPUUtilization over 50 percent' \
  --namespace AWS/EC2 \
  --metric-name CPUUtilization \
  --dimensions Name=InstanceId,Value="$WEB01" \
  --statistic Average \
  --period 300 \
  --evaluation-periods 1 \
  --threshold 50 \
  --comparison-operator GreaterThanThreshold \
  --alarm-actions "$TOPIC_ARN" \
  --unit Percent
```

## Launch Template

```bash
LT_ID=$(aws ec2 create-launch-template \
  --launch-template-name webserver-template \
  --version-description 'Lab3 web server template' \
  --launch-template-data "{\"ImageId\":\"$AMI_ID\",\"InstanceType\":\"$INSTANCE_TYPE\",\"KeyName\":\"$KEY_NAME\",\"SecurityGroupIds\":[\"$WEB_SG\"]}" \
  --query 'LaunchTemplate.LaunchTemplateId' \
  --output text)
```

## Auto Scaling Group

```bash
aws elbv2 deregister-targets \
  --target-group-arn "$TG_ARN" \
  --targets Id="$WEB01" Id="$WEB02"
```

```bash
aws autoscaling create-auto-scaling-group \
  --auto-scaling-group-name web-asg \
  --launch-template "LaunchTemplateId=$LT_ID,Version=\$Latest" \
  --min-size 1 \
  --max-size 5 \
  --desired-capacity 2 \
  --vpc-zone-identifier "$SUBNET1,$SUBNET2" \
  --target-group-arns "$TG_ARN" \
  --health-check-type ELB \
  --health-check-grace-period 300 \
  --tags Key=Name,Value=web-asg-instance,PropagateAtLaunch=true
```

```bash
aws autoscaling enable-metrics-collection \
  --auto-scaling-group-name web-asg \
  --granularity '1Minute'
```

```bash
aws autoscaling put-scaling-policy \
  --auto-scaling-group-name web-asg \
  --policy-name web-asg-target-cpu-50 \
  --policy-type TargetTrackingScaling \
  --target-tracking-configuration '{"PredefinedMetricSpecification":{"PredefinedMetricType":"ASGAverageCPUUtilization"},"TargetValue":50.0}'
```

## 확인 명령어

```bash
aws elbv2 describe-target-health \
  --target-group-arn "$TG_ARN" \
  --query 'TargetHealthDescriptions[].{Instance:Target.Id,State:TargetHealth.State,Reason:TargetHealth.Reason}' \
  --output table
```

```bash
aws autoscaling describe-auto-scaling-groups \
  --auto-scaling-group-names web-asg \
  --query 'AutoScalingGroups[].{Desired:DesiredCapacity,Min:MinSize,Max:MaxSize,Instances:Instances[].{Id:InstanceId,Lifecycle:LifecycleState,Health:HealthStatus}}' \
  --output table
```

```bash
curl -I http://<ALB_DNS_NAME>/
```

## 부하 테스트

```bash
ssh -i <KEY_FILE> ubuntu@<ASG_INSTANCE_PUBLIC_IP> \
  'nohup stress --cpu 4 --timeout 480 >/tmp/lab3-stress.log 2>&1 &'
```

```bash
aws autoscaling describe-scaling-activities \
  --auto-scaling-group-name web-asg \
  --max-items 6 \
  --query 'Activities[].{Status:StatusCode,Description:Description}' \
  --output table
```

## 정리 명령어

```bash
aws autoscaling delete-auto-scaling-group \
  --auto-scaling-group-name web-asg \
  --force-delete
```

```bash
aws ec2 delete-launch-template \
  --launch-template-name webserver-template
```

```bash
aws elbv2 delete-load-balancer \
  --load-balancer-arn "$ALB_ARN"
```

```bash
aws elbv2 delete-target-group \
  --target-group-arn "$TG_ARN"
```

```bash
aws sns delete-topic \
  --topic-arn "$TOPIC_ARN"
```
