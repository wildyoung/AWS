# Kubernetes Manifests

Lab13 Kubernetes Basic 실습에서 사용하는 YAML 예제입니다.

| 파일 | 내용 |
| --- | --- |
| `nginx-pod.yaml` | 단일 Nginx Pod 생성 |
| `namespace-nginx.yaml` | `lab13` namespace와 namespace 내부 Pod 생성 |
| `nginx-deployment-service.yaml` | Nginx Deployment 3개 replica와 ClusterIP Service 생성 |

적용:

```bash
kubectl apply -f nginx-pod.yaml
kubectl apply -f namespace-nginx.yaml
kubectl apply -f nginx-deployment-service.yaml
```

정리:

```bash
kubectl delete -f nginx-pod.yaml
kubectl delete -f namespace-nginx.yaml
kubectl delete -f nginx-deployment-service.yaml
```
