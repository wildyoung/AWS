# Lab13 Verification

검증일: 2026-07-03

## AWS CLI

| 항목 | 결과 |
| --- | --- |
| CloudFormation template validation | 통과 |
| CloudFormation stack create | 성공 |
| SSM Run Command 연결 | 성공 |
| CloudFormation stack delete | 성공 |

## k3s

| 항목 | 결과 |
| --- | --- |
| k3s 설치 | 성공 |
| Kubernetes version | `v1.36.2+k3s1` |
| Node status | `Ready` |
| Container runtime | `containerd` |
| kube-system Pod | Running 또는 Completed |

## kubectl 실습

| 실습 | 결과 |
| --- | --- |
| `kubectl get nodes -o wide` | 정상 조회 |
| `kubectl get pods -A -o wide` | 정상 조회 |
| `kubectl create deployment nginx --image=nginx:1.25` | 생성 성공 |
| `kubectl rollout status deployment/nginx` | rollout 성공 |
| `kubectl run webserver --image=nginx:1.14 --port=80` | Pod Ready |
| `kubectl describe pod webserver` | Pod 상세 확인 |
| `kubectl create namespace lab13` | namespace 생성 성공 |
| namespace 내부 Pod 실행 | Pod Ready |
| YAML manifest apply | Deployment와 Service 생성 성공 |
| Deployment replica | `3/3` |
| Service ClusterIP HTTP test | Nginx HTML 응답 확인 |
| Kubernetes 실습 리소스 삭제 | 완료 |

## 캡처

- [Cluster status](images/capture_01_cluster_status.png)
- [Deployment and pod](images/capture_02_deployment_and_pod.png)
- [Namespace YAML service](images/capture_03_namespace_yaml_service.png)
- [Cleanup check](images/capture_04_cleanup_check.png)

## 비용 정리

실습 캡처 저장 후 `lab13-kubernetes-basic` CloudFormation 스택을 삭제했습니다.
