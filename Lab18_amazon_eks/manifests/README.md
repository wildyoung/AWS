# Amazon EKS Manifests

Lab18 Amazon EKS 실습에서 사용하는 Kubernetes YAML 예제입니다.

| 파일 | 용도 |
| --- | --- |
| `demo_pod.yaml` | `kubectl apply` 전 기본 Pod |
| `demo_modify.yaml` | 같은 Pod의 label 변경을 apply로 반영 |
| `nginx_pod.yaml` | Pod 간 통신 확인용 Nginx Pod |
| `apache_pod.yaml` | Pod 간 통신 확인용 Apache Pod |
| `pod_multi.yaml` | 하나의 Pod 안에 두 컨테이너가 네트워크를 공유하는 예제 |
| `my_rs.yaml` | ReplicaSet self-healing 확인 |
| `my_deploy.yaml` | Deployment와 ReplicaSet 관계 확인 |
| `my_deploy_update.yaml` | Deployment rolling update 확인 |
| `hello_app.yaml` | Service backend용 Nginx Deployment |
| `hello_cip_svc.yaml` | ClusterIP Service와 Endpoints 확인 |
| `deploy_ubuntu.yaml` | Service DNS 접속 확인용 curl client Deployment |
| `hello_lb_svc.yaml` | AWS LoadBalancer Service 확인 |
| `my_svc.yaml` | AWS Load Balancer Controller Ingress용 Service 예제 |
| `my_ingress.yaml` | ALB Ingress 예제 |

`my_ingress.yaml`은 AWS Load Balancer Controller 설치 후 사용하는 선택 실습용 예제입니다.
