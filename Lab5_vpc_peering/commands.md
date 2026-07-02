# Lab5 VPC Peering Commands

실제 계정 ID, 퍼블릭 IP, VPC Peering ID, 인스턴스 ID, 키 파일 내용은 문서에 남기지 않습니다. 아래 명령어는 실습 흐름을 재현할 수 있도록 주요 값을 플레이스홀더로 정리했습니다.

## 기본 변수

```bash
SEOUL=ap-northeast-2
TOKYO=ap-northeast-1
MY_VPC=<MY_VPC_ID>
MY_ROUTE=<MY_ROUTE_TABLE_ID>
MY_WEB_SG=<MY_WEB_SECURITY_GROUP_ID>
MY_WEB01_PUBLIC=<MY_WEB01_PUBLIC_IP>
TK_AMI=<AMAZON_LINUX_2023_AMI_IN_TOKYO>
```

## 도쿄 VPC 생성

```bash
TK_VPC=$(aws ec2 create-vpc \
  --region "$TOKYO" \
  --cidr-block 10.10.0.0/16 \
  --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=tk-vpc},{Key=Lab,Value=Lab5}]' \
  --query Vpc.VpcId \
  --output text)
```

```bash
aws ec2 modify-vpc-attribute \
  --region "$TOKYO" \
  --vpc-id "$TK_VPC" \
  --enable-dns-support '{"Value":true}'
aws ec2 modify-vpc-attribute \
  --region "$TOKYO" \
  --vpc-id "$TK_VPC" \
  --enable-dns-hostnames '{"Value":true}'
```

## 도쿄 서브넷과 인터넷 게이트웨이

```bash
TK_SUB01=$(aws ec2 create-subnet \
  --region "$TOKYO" \
  --vpc-id "$TK_VPC" \
  --cidr-block 10.10.1.0/24 \
  --availability-zone ap-northeast-1a \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=tk-sub01},{Key=Lab,Value=Lab5}]' \
  --query Subnet.SubnetId \
  --output text)
```

```bash
TK_SUB02=$(aws ec2 create-subnet \
  --region "$TOKYO" \
  --vpc-id "$TK_VPC" \
  --cidr-block 10.10.2.0/24 \
  --availability-zone ap-northeast-1c \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=tk-sub02},{Key=Lab,Value=Lab5}]' \
  --query Subnet.SubnetId \
  --output text)
```

```bash
aws ec2 modify-subnet-attribute \
  --region "$TOKYO" \
  --subnet-id "$TK_SUB01" \
  --map-public-ip-on-launch
```

```bash
TK_IGW=$(aws ec2 create-internet-gateway \
  --region "$TOKYO" \
  --tag-specifications 'ResourceType=internet-gateway,Tags=[{Key=Name,Value=tk-igw},{Key=Lab,Value=Lab5}]' \
  --query InternetGateway.InternetGatewayId \
  --output text)
aws ec2 attach-internet-gateway \
  --region "$TOKYO" \
  --internet-gateway-id "$TK_IGW" \
  --vpc-id "$TK_VPC"
```

## 도쿄 퍼블릭 라우팅 테이블

```bash
TK_ROUTE=$(aws ec2 create-route-table \
  --region "$TOKYO" \
  --vpc-id "$TK_VPC" \
  --tag-specifications 'ResourceType=route-table,Tags=[{Key=Name,Value=tk-route},{Key=Lab,Value=Lab5}]' \
  --query RouteTable.RouteTableId \
  --output text)
```

```bash
aws ec2 create-route \
  --region "$TOKYO" \
  --route-table-id "$TK_ROUTE" \
  --destination-cidr-block 0.0.0.0/0 \
  --gateway-id "$TK_IGW"
aws ec2 associate-route-table \
  --region "$TOKYO" \
  --route-table-id "$TK_ROUTE" \
  --subnet-id "$TK_SUB01"
```

## 도쿄 보안 그룹

```bash
TK_SG=$(aws ec2 create-security-group \
  --region "$TOKYO" \
  --group-name tk-web-sg \
  --description 'Lab5 Tokyo web security group' \
  --vpc-id "$TK_VPC" \
  --tag-specifications 'ResourceType=security-group,Tags=[{Key=Name,Value=tk-web-sg},{Key=Lab,Value=Lab5}]' \
  --query GroupId \
  --output text)
```

```bash
aws ec2 authorize-security-group-ingress \
  --region "$TOKYO" \
  --group-id "$TK_SG" \
  --ip-permissions '[
    {"IpProtocol":"tcp","FromPort":22,"ToPort":22,"IpRanges":[{"CidrIp":"0.0.0.0/0"}]},
    {"IpProtocol":"icmp","FromPort":-1,"ToPort":-1,"IpRanges":[{"CidrIp":"0.0.0.0/0"}]},
    {"IpProtocol":"-1","IpRanges":[{"CidrIp":"10.0.0.0/16"}]}
  ]'
```

## 도쿄 EC2 생성

```bash
aws ec2 create-key-pair \
  --region "$TOKYO" \
  --key-name tk-key \
  --query 'KeyMaterial' \
  --output text > tk-key.pem
chmod 400 tk-key.pem
```

```bash
TK_WEB01=$(aws ec2 run-instances \
  --region "$TOKYO" \
  --image-id "$TK_AMI" \
  --instance-type t3.micro \
  --key-name tk-key \
  --subnet-id "$TK_SUB01" \
  --security-group-ids "$TK_SG" \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=tk-web01},{Key=Lab,Value=Lab5}]' \
  --query 'Instances[0].InstanceId' \
  --output text)
```

```bash
TK_WEB02=$(aws ec2 run-instances \
  --region "$TOKYO" \
  --image-id "$TK_AMI" \
  --instance-type t3.micro \
  --key-name tk-key \
  --subnet-id "$TK_SUB02" \
  --security-group-ids "$TK_SG" \
  --no-associate-public-ip-address \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=tk-web02},{Key=Lab,Value=Lab5}]' \
  --query 'Instances[0].InstanceId' \
  --output text)
```

## 피어링 전 확인

```bash
ssh -i <KEY_FILE> ubuntu@<MY_WEB01_PUBLIC_IP>
ping -c 3 <TK_WEB01_PUBLIC_IP>
ping -c 3 <TK_WEB01_PRIVATE_IP>
ping -c 3 <TK_WEB02_PRIVATE_IP>
```

## VPC Peering 생성과 수락

```bash
PCX=$(aws ec2 create-vpc-peering-connection \
  --region "$SEOUL" \
  --vpc-id "$MY_VPC" \
  --peer-vpc-id "$TK_VPC" \
  --peer-region "$TOKYO" \
  --tag-specifications 'ResourceType=vpc-peering-connection,Tags=[{Key=Name,Value=my-peer},{Key=Lab,Value=Lab5}]' \
  --query VpcPeeringConnection.VpcPeeringConnectionId \
  --output text)
```

```bash
aws ec2 accept-vpc-peering-connection \
  --region "$TOKYO" \
  --vpc-peering-connection-id "$PCX"
```

## 피어링 라우팅과 보안 그룹

```bash
aws ec2 create-route \
  --region "$SEOUL" \
  --route-table-id "$MY_ROUTE" \
  --destination-cidr-block 10.10.0.0/16 \
  --vpc-peering-connection-id "$PCX"
```

```bash
aws ec2 create-route \
  --region "$TOKYO" \
  --route-table-id "$TK_ROUTE" \
  --destination-cidr-block 10.0.0.0/16 \
  --vpc-peering-connection-id "$PCX"
```

```bash
aws ec2 authorize-security-group-ingress \
  --region "$SEOUL" \
  --group-id "$MY_WEB_SG" \
  --ip-permissions '[{"IpProtocol":"-1","IpRanges":[{"CidrIp":"10.10.0.0/16"}]}]'
```

## 피어링 후 확인

```bash
ping -c 3 <TK_WEB01_PRIVATE_IP>
ping -c 3 <TK_WEB02_PRIVATE_IP>
```

`tk-web02`가 실패하면 `tk-sub02`가 사용하는 route table에도 피어링 경로가 필요합니다.

```bash
TK_MAIN_RT=$(aws ec2 describe-route-tables \
  --region "$TOKYO" \
  --filters Name=vpc-id,Values="$TK_VPC" Name=association.main,Values=true \
  --query 'RouteTables[0].RouteTableId' \
  --output text)
```

```bash
aws ec2 create-route \
  --region "$TOKYO" \
  --route-table-id "$TK_MAIN_RT" \
  --destination-cidr-block 10.0.0.0/16 \
  --vpc-peering-connection-id "$PCX"
```

## 정리 명령어

```bash
aws ec2 delete-route \
  --region "$SEOUL" \
  --route-table-id "$MY_ROUTE" \
  --destination-cidr-block 10.10.0.0/16
```

```bash
aws ec2 delete-route \
  --region "$TOKYO" \
  --route-table-id "$TK_ROUTE" \
  --destination-cidr-block 10.0.0.0/16
aws ec2 delete-route \
  --region "$TOKYO" \
  --route-table-id "$TK_MAIN_RT" \
  --destination-cidr-block 10.0.0.0/16
```

```bash
aws ec2 delete-vpc-peering-connection \
  --region "$SEOUL" \
  --vpc-peering-connection-id "$PCX"
```

```bash
aws ec2 terminate-instances \
  --region "$TOKYO" \
  --instance-ids "$TK_WEB01" "$TK_WEB02"
```

도쿄 VPC를 삭제하려면 EC2, 서브넷, 라우팅 테이블, 인터넷 게이트웨이, 보안 그룹 순서로 의존 리소스를 먼저 정리해야 합니다.
