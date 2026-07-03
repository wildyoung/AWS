# AWS Study Labs

AWS 개념과 실습 기록입니다.

## 실습 목록

- [Lab1 Networking](Lab01_networking/README.md)
- [Lab2 Computing](Lab02_computing/README.md)
- [Lab3 High Availability](Lab03_high_availability/README.md)
- [Lab4 Storage](Lab04_storage/README.md)
- [Lab5 VPC Peering](Lab05_vpc_peering/README.md)
- [Lab6 Domain and Traffic](Lab06_domain_traffic/README.md)
- [Lab7 Cloud Security](Lab07_cloud_security/README.md)
- [Lab8 Relational Database](Lab08_relational_database/README.md)
- [Lab9 Serverless](Lab09_serverless/README.md)
- [Lab10 CloudFormation](Lab10_cloudformation/README.md)
- [Lab11 Cost Management and Support](Lab11_cost_management_support/README.md)
- [Lab12 Disaster Recovery](Lab12_disaster_recovery/README.md)
- [Lab13 Kubernetes Basic](Lab13_kubernetes_basic/README.md)
- [Lab14 Kubernetes Pod](Lab14_kubernetes_pod/README.md)
- [Lab15 Kubernetes Controller](Lab15_kubernetes_controller/README.md)
- [Part2 Docker](Part2_Docker/README.md)

## 정리한 내용

- VPC, 서브넷, 라우팅 테이블
- 퍼블릭 서브넷과 프라이빗 서브넷의 차이
- 인터넷 게이트웨이와 NAT Gateway의 역할
- 보안 그룹과 네트워크 ACL의 차이
- 배스천 호스트를 통한 프라이빗 EC2 접속
- EC2 SSH 접속 및 네트워크 연결 확인 명령어
- EC2 기반 Web-WAS-DB 구성
- AMI 생성과 인스턴스 복제
- User data를 활용한 EC2 초기 구성
- 고가용성 아키텍처와 Multi-AZ 구성
- Application Load Balancer, 대상 그룹, 상태 확인
- CloudWatch 지표/경보와 SNS 알림
- Launch Template과 Auto Scaling Group
- Target Tracking Scaling을 통한 자동 증설/감설
- 블록, 파일, 객체 스토리지의 차이
- EBS 볼륨 생성, 마운트, 확장, 스냅샷 복구
- EFS 공유 파일시스템과 NFS 마운트
- S3 객체 업로드, 퍼블릭 액세스, 정적 웹사이트 호스팅
- VPC Peering을 통한 리전 간 프라이빗 통신
- 라우팅 테이블과 보안 그룹이 피어링 통신에 미치는 영향
- Transit Gateway, Site-to-Site VPN, Direct Connect, VPC Endpoint 개념
- Route 53 hosted zone, alias record, health check, DNS failover
- S3 정적 웹사이트 기반 장애조치 대상 구성
- CloudFront CDN, edge cache, cache hit/miss, TTL 개념
- AWS 공동 책임 모델과 IAM 사용자, 역할, 정책
- MFA, 루트 사용자 보안, CloudTrail, KMS, Organizations 개념
- EC2 인스턴스 프로파일을 통한 임시 자격증명 기반 S3 접근
- 관계형 데이터베이스와 비관계형 데이터베이스 비교
- Amazon RDS MySQL 생성, DB subnet group, RDS 보안 그룹
- DynamoDB, Redshift, Aurora, DMS 데이터베이스 서비스 개념
- 서버리스 아키텍처와 AWS Lambda 실행 모델
- DynamoDB 테이블 설계와 유연한 NoSQL 항목 구조
- Lambda 실행 역할, CloudWatch Logs, 이벤트 기반 처리
- AWS Well-Architected Framework 6대 원칙
- Infrastructure as Code와 CloudFormation 스택 관리
- CloudFormation 템플릿, 변경 세트, 스택 업데이트, 드리프트 감지
- Outputs Export와 ImportValue를 활용한 스택 분리
- AWS 요금 구조, TCO, Pricing Calculator, Cost Explorer, Budgets
- AWS Support 플랜, 지원 케이스 심각도, Trusted Advisor
- RPO/RTO와 재해 복구 전략
- Backup and Restore, Pilot Light, Warm Standby, Multi-site DR 패턴
- 클라우드 네이티브, MSA, DevOps, CI/CD 개념
- 컨테이너와 VM의 차이, Docker Engine 구조
- Docker 이미지, 컨테이너, Dockerfile, Registry 개념
- Docker 컨테이너 생명주기와 기본 명령
- Docker bridge/host/none 네트워크와 포트 매핑
- Docker volume, bind mount, tmpfs 데이터 저장 방식
- Dockerfile 지시어, 이미지 빌드, CMD와 ENTRYPOINT 차이
- 이미지 레이어, 태그, save/load, Docker Hub, Amazon ECR 흐름
- Docker Compose를 이용한 WordPress와 MySQL 멀티 컨테이너 구성
- 컨테이너 오케스트레이션과 Kubernetes 필요성
- Kubernetes Control Plane, Worker Node, kubelet, kube-proxy, containerd 구조
- Pod, Deployment, ReplicaSet, Service, Namespace, Ingress, Volume 개념
- Desired State, 선언형 구성, Kubernetes YAML manifest
- k3s 단일 노드 클러스터 구성과 kubectl 기본 명령
- Namespace 분리와 ClusterIP Service 접속 확인
- Pod IP 할당, Pod 생명주기, Single/Multi Container Pod
- LivenessProbe 기반 Self-healing, Init Container, 환경 변수 주입
- Pod 내부 localhost 통신과 컨테이너 간 네트워크 공유
- Kubernetes Controller의 watch, compare, act control loop
- ReplicationController와 ReplicaSet의 Pod 복제본 유지 방식
- Deployment rolling update, rollout history, rollback
- DaemonSet, Job, CronJob, StatefulSet의 목적과 동작 차이

## 읽는 순서

1. `Lab01_networking`: VPC, 서브넷, 라우팅, 인터넷 연결, 프라이빗/퍼블릭 서브넷 차이를 이해합니다.
2. `Lab02_computing`: EC2 위에 Web-WAS-DB를 구성하고 AMI와 user data로 서버 구성을 재사용합니다.
3. `Lab03_high_availability`: 단일 서버 중심 구성을 ALB와 Auto Scaling 기반 고가용성 구조로 확장합니다.
4. `Lab04_storage`: EC2가 사용하는 블록 스토리지, 여러 서버가 공유하는 파일 스토리지, 인터넷에서 접근하는 객체 스토리지를 비교합니다.
5. `Lab05_vpc_peering`: 서로 다른 리전의 VPC를 피어링하고, 라우팅/보안그룹 조건에 따라 프라이빗 통신이 달라지는 것을 확인합니다.
6. `Lab06_domain_traffic`: Route 53 DNS 흐름, S3 정적 웹사이트 장애조치, CloudFront 캐싱 효과를 확인합니다.
7. `Lab07_cloud_security`: IAM 권한 모델, MFA, EC2 역할 기반 S3 접근, 계정 보안 기본 원칙을 확인합니다.
8. `Lab08_relational_database`: RDS MySQL을 구성하고 EC2에서 SQL 접속/테이블 조회를 검증합니다.
9. `Lab09_serverless`: Lambda가 DynamoDB에 주문 데이터를 저장하는 서버리스 흐름을 검증합니다.
10. `Lab10_cloudformation`: CloudFormation으로 단일 스택을 생성/업데이트하고, VPC/EC2/ALB를 분리 스택으로 관리합니다.
11. `Lab11_cost_management_support`: AWS 비용 구조, 비용 분석 도구, 예산 관리, 지원 플랜을 정리합니다.
12. `Lab12_disaster_recovery`: RPO/RTO를 기준으로 재해 복구 패턴과 서비스별 복구 전략을 비교합니다.
13. `Part2_Docker`: 클라우드 네이티브 개념에서 Docker 기본 명령, 네트워크/볼륨, Dockerfile, 이미지 관리, Compose까지 정리합니다.
14. `Lab13_kubernetes_basic`: EC2 단일 노드 k3s 환경에서 Kubernetes 구조, kubectl, namespace, YAML manifest, Service 흐름을 실습합니다.
15. `Lab14_kubernetes_pod`: Pod IP, 단일/멀티 컨테이너 Pod, livenessProbe, init container, 환경 변수 전달을 실습합니다.
16. `Lab15_kubernetes_controller`: RC, ReplicaSet, Deployment, DaemonSet, Job, CronJob, StatefulSet의 Controller 동작을 실습합니다.

## 보안 주의사항

GitHub에는 민감 정보를 올리지 않습니다.

- `.pem` 키 파일을 커밋하지 않습니다.
- AWS Access Key, Secret Access Key를 커밋하지 않습니다.
- 실제 계정 ID, 퍼블릭 IP, 교육 계정 정보는 노출하지 않습니다.
- 실습 후 EC2, NAT Gateway, Elastic IP 등 과금 가능 리소스를 정리합니다.
