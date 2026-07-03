# Lab16 Verification

검증일: 2026-07-04

## AWS CLI

| 항목 | 결과 |
| --- | --- |
| CloudFormation template validation | 통과 |
| CloudFormation stack create | 성공 |
| SSM Run Command 연결 | 성공 |
| External HTTP check | 성공 |
| CloudFormation stack delete | 성공 |

## k3s

| 항목 | 결과 |
| --- | --- |
| k3s 설치 | 성공 |
| Kubernetes version | `v1.36.2+k3s1` |
| Node status | `Ready` |
| Traefik Ingress Controller | Running |
| k3s ServiceLB | Running |

## Network 실습

| 실습 | 결과 |
| --- | --- |
| Pod IP 재할당 | `nginx-web1` 삭제/재생성 시 IP 변경 확인 |
| Single Pod | Pod IP로 Nginx 응답 확인 |
| Multi-container Pod | `READY 2/2`, Nginx + Ubuntu 컨테이너 실행 확인 |
| Pod-to-Pod 통신 | Ubuntu 컨테이너에서 `single-pod` ping 성공 |
| Same Pod localhost | Ubuntu 컨테이너에서 `localhost`로 Nginx 응답 확인 |
| ClusterIP Service | `hello-svc:8020` DNS 접속 확인 |
| Endpoints | Pod 생성/삭제에 따라 Endpoint IP 변경 확인 |
| LoadBalancer Service | Public IP `:8020`, `:8050` 응답 확인 |
| Ingress | Public IP `/hello/`, `/world/` path routing 확인 |
| Kubernetes cleanup | 기본 `kubernetes` Service 외 실습 리소스 삭제 확인 |
| AWS cleanup | CloudFormation 스택 삭제 완료 |

## 캡처

- [Pod network](images/capture_01_pod_network.png)
- [ClusterIP endpoints](images/capture_02_clusterip_endpoints.png)
- [LoadBalancer](images/capture_03_loadbalancer.png)
- [Ingress](images/capture_04_ingress.png)
- [Cleanup](images/capture_05_cleanup.png)

## 비용 정리

실습 캡처 저장 후 `lab16-kubernetes-network` CloudFormation 스택을 삭제했습니다.
