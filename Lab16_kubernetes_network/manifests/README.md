# Kubernetes Network Manifests

Lab16 Kubernetes Network 실습에서 사용하는 YAML 예제입니다.

| 파일 | 용도 |
| --- | --- |
| `single-pod.yaml` | 단일 Nginx Pod |
| `multi-pod.yaml` | Nginx + Ubuntu multi-container Pod |
| `deploy-ubuntu.yaml` | ClusterIP Service 접속 테스트용 Ubuntu Deployment |
| `hello-app.yaml` | hello 애플리케이션 Deployment |
| `hello-cip-svc.yaml` | hello 앱 ClusterIP Service |
| `hello-lb-svc.yaml` | hello 앱 LoadBalancer Service |
| `world-app.yaml` | world 애플리케이션 Deployment |
| `world-cip-svc.yaml` | world 앱 ClusterIP Service |
| `world-lb-svc.yaml` | world 앱 LoadBalancer Service |
| `my-svc.yaml` | Ingress backend용 hello/world ClusterIP Service |
| `my-ingress.yaml` | Traefik Ingress path routing |

원본 실습 흐름을 유지하면서 `my-ingress.yaml`은 최신 Kubernetes YAML 스타일로 정리했습니다.
