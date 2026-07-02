# AWS Study Labs

AWS 개념과 실습 기록입니다.

## 실습 목록

- [Lab1 Networking](Lab1_networking/README.md)
- [Lab2 Computing](Lab2_computing/README.md)
- [Lab3 High Availability](Lab3_high_availability/README.md)
- [Lab4 Storage](Lab4_storage/README.md)

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

## 읽는 순서

1. `Lab1_networking`: VPC, 서브넷, 라우팅, 인터넷 연결, 프라이빗/퍼블릭 서브넷 차이를 이해합니다.
2. `Lab2_computing`: EC2 위에 Web-WAS-DB를 구성하고 AMI와 user data로 서버 구성을 재사용합니다.
3. `Lab3_high_availability`: 단일 서버 중심 구성을 ALB와 Auto Scaling 기반 고가용성 구조로 확장합니다.
4. `Lab4_storage`: EC2가 사용하는 블록 스토리지, 여러 서버가 공유하는 파일 스토리지, 인터넷에서 접근하는 객체 스토리지를 비교합니다.

## 보안 주의사항

GitHub에는 민감 정보를 올리지 않습니다.

- `.pem` 키 파일을 커밋하지 않습니다.
- AWS Access Key, Secret Access Key를 커밋하지 않습니다.
- 실제 계정 ID, 퍼블릭 IP, 교육 계정 정보는 노출하지 않습니다.
- 실습 후 EC2, NAT Gateway, Elastic IP 등 과금 가능 리소스를 정리합니다.
