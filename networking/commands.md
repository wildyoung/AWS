# 명령어 정리

실제 시크릿, 계정 ID, 퍼블릭 IP는 문서에 남기지 않고 placeholder를 사용합니다.

## AWS CLI 설정

```bash
aws configure
```

이번 실습의 기본 리전:

```text
ap-northeast-2
```

현재 연결된 AWS 계정 확인:

```bash
aws sts get-caller-identity
```

## VPC 리소스 확인

```bash
aws ec2 describe-vpcs \
  --region ap-northeast-2 \
  --query 'Vpcs[].{VpcId:VpcId,Cidr:CidrBlock,Default:IsDefault,Name:Tags[?Key==`Name`]|[0].Value}' \
  --output table
```

```bash
aws ec2 describe-subnets \
  --region ap-northeast-2 \
  --query 'Subnets[].{SubnetId:SubnetId,VpcId:VpcId,Cidr:CidrBlock,Az:AvailabilityZone,Name:Tags[?Key==`Name`]|[0].Value}' \
  --output table
```

```bash
aws ec2 describe-route-tables \
  --region ap-northeast-2 \
  --query 'RouteTables[].{RouteTableId:RouteTableId,Routes:Routes[].{Destination:DestinationCidrBlock,Gateway:GatewayId,Nat:NatGatewayId},Associations:Associations[].SubnetId}' \
  --output json
```

## EC2 인스턴스 확인

```bash
aws ec2 describe-instances \
  --region ap-northeast-2 \
  --filters Name=instance-state-name,Values=pending,running,stopping,stopped \
  --query 'Reservations[].Instances[].{Name:Tags[?Key==`Name`]|[0].Value,InstanceId:InstanceId,State:State.Name,PublicIp:PublicIpAddress,PrivateIp:PrivateIpAddress,SubnetId:SubnetId}' \
  --output table
```

## SSH 키 권한 변경

```bash
chmod 600 ~/Downloads/my-key.pem
```

## 퍼블릭 EC2로 SSH 접속

서브넷에 인터넷 게이트웨이 라우트가 있어야 접속됩니다.

```bash
ssh -i ~/Downloads/my-key.pem ec2-user@<PUBLIC_IP>
```

## 배스천 호스트로 키 파일 복사

실습 편의용 방식입니다. 실제 운영 환경에서는 프라이빗 키를 서버에 복사하는 방식을 피해야 합니다.

```bash
scp -i ~/Downloads/my-key.pem \
  ~/Downloads/my-key.pem \
  ec2-user@<BASTION_PUBLIC_IP>:/home/ec2-user/
```

## 배스천 호스트에서 프라이빗 EC2로 SSH 접속

배스천 호스트에 접속한 뒤 실행합니다.

```bash
chmod 600 my-key.pem
ssh -i my-key.pem ec2-user@<PRIVATE_EC2_PRIVATE_IP>
```

## 연결 테스트

다른 EC2 인스턴스를 프라이빗 IP로 ping 테스트:

```bash
ping -c 5 <PRIVATE_IP>
```

NAT Gateway 구성 후 프라이빗 EC2에서 아웃바운드 인터넷 통신 테스트:

```bash
ping -c 5 8.8.8.8
```

## 정리 전 확인

```bash
aws ec2 describe-nat-gateways \
  --region ap-northeast-2 \
  --query 'NatGateways[].{NatGatewayId:NatGatewayId,State:State,VpcId:VpcId,SubnetId:SubnetId}' \
  --output table
```

```bash
aws ec2 describe-addresses \
  --region ap-northeast-2 \
  --query 'Addresses[].{AllocationId:AllocationId,PublicIp:PublicIp,AssociationId:AssociationId}' \
  --output table
```

```bash
aws ec2 describe-volumes \
  --region ap-northeast-2 \
  --query 'Volumes[].{VolumeId:VolumeId,State:State,Size:Size,AttachedTo:Attachments[0].InstanceId}' \
  --output table
```
