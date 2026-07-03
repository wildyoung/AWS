# Lab18 Verification

검증일: 2026-07-04

## 환경 검증

| 항목 | 결과 |
| --- | --- |
| CloudFormation template validation | 성공 |
| EKS 지원 버전 확인 | `1.35` 지원 확인 |
| VPC/IAM Stack 생성 | 성공 |
| EKS Cluster 생성 | `ACTIVE` |
| EKS 인증 모드 | `API_AND_CONFIG_MAP` |
| Managed Node Group | `ACTIVE` |
| Worker Node | 2개 노드 `Ready` |
| Node instance type | `t3.small` |
| Kubernetes version | `v1.35.6-eks-7d6f6ec` |
| AWS cleanup | EKS Cluster 목록 비어 있음, CloudFormation Stack 없음 |

## 실습 검증

| 단계 | 검증 내용 | 결과 |
| --- | --- | --- |
| 1 | EKS Cluster 생성 | `ACTIVE` |
| 2 | Managed Node Group 생성 | `ACTIVE`, desired 2 |
| 3 | 기본 namespace와 Service 확인 | `default`, `kube-system`, `kubernetes` Service 확인 |
| 4 | kube-system Pod 확인 | `aws-node`, `coredns`, `kube-proxy` Running |
| 5 | Metrics Server 확인 | 기본 설치되지 않음 |
| 6 | VPC CNI Pod IP 확인 | Pod IP가 VPC CIDR 대역에서 할당됨 |
| 7 | `kubectl apply` 확인 | Pod label 변경 반영 |
| 8 | Pod-to-Pod 통신 | Nginx Pod에서 Apache Pod로 `HTTP/1.1 200 OK` |
| 9 | Multi-container Pod | `READY 2/2`, localhost curl 성공 |
| 10 | ReplicaSet self-healing | Pod 삭제 후 새 Pod 생성, READY 3 유지 |
| 11 | Deployment self-healing | Pod 삭제 후 Deployment가 복구 |
| 12 | Deployment rolling update | `nginx:1.19`에서 `nginx:1.25`로 업데이트 |
| 13 | ClusterIP Service | Endpoints가 backend Pod IP로 등록 |
| 14 | Endpoint 자동 갱신 | Pod 재생성 후 Endpoints 변경 |
| 15 | LoadBalancer Service | AWS Network Load Balancer 생성 |
| 16 | 외부 접속 | NLB DNS `:8020` curl 성공 |
| 17 | Kubernetes cleanup | 실습 Service/Deployment/Pod 삭제 |
| 18 | AWS cleanup | NLB, Node Group, EKS Cluster, Stack 삭제 |

## 계정 제약과 조정

원본 실습 명령은 `t3.medium` 노드그룹을 사용하지만, 현재 계정은 Free Tier 대상 인스턴스만 생성할 수 있어 `t3.medium` 생성이 실패했습니다.

이후 Free Tier 허용 타입인 `t3.small`로 노드그룹을 다시 생성해 실습을 완료했습니다.

## 결과 로그

실습 출력은 [results/kubectl_result_sanitized.txt](results/kubectl_result_sanitized.txt)에 저장했습니다.

민감 정보 보호를 위해 다음 값은 마스킹했습니다.

- AWS Account ID
- IAM Role ARN
- VPC ID
- Subnet ID
- EKS API Endpoint
- EC2 instance ID
- Node public/private IP
- Pod IP
- NLB DNS 이름

## 결론

EKS에서는 AWS가 Control Plane을 관리하고, Managed Node Group이 Worker Node를 제공하며, Amazon VPC CNI가 Pod IP를 VPC CIDR에서 직접 할당합니다. Kubernetes Service는 ClusterIP와 Endpoints로 내부 트래픽을 안정화하고, LoadBalancer 타입 Service는 AWS Network Load Balancer를 생성해 외부 트래픽을 Pod까지 전달합니다.
