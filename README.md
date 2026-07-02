# AWS Study Labs

AWS 개념과 실습 기록입니다.

## 실습 목록

- [Lab1 Networking](Lab1_networking/README.md)
- [Lab2 Computing](Lab2_computing/README.md)

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

## 보안 주의사항

GitHub에는 민감 정보를 올리지 않습니다.

- `.pem` 키 파일을 커밋하지 않습니다.
- AWS Access Key, Secret Access Key를 커밋하지 않습니다.
- 실제 계정 ID, 퍼블릭 IP, 교육 계정 정보는 노출하지 않습니다.
- 실습 후 EC2, NAT Gateway, Elastic IP 등 과금 가능 리소스를 정리합니다.
