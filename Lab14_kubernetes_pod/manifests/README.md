# Kubernetes Pod Manifests

Lab14 Kubernetes Pod 실습에서 사용하는 YAML 예제입니다.

| 파일 | 내용 |
| --- | --- |
| `single-pod.yaml` | 단일 Nginx 컨테이너 Pod |
| `multi-pod.yaml` | Nginx와 Ubuntu 컨테이너가 함께 실행되는 Pod |
| `init-container-pod.yaml` | init container 완료 후 main container가 실행되는 Pod |
| `env-pod.yaml` | 환경 변수를 컨테이너에 전달하는 Pod |
| `liveness-pod.yaml` | HTTP livenessProbe로 컨테이너 상태를 감시하는 Pod |

적용:

```bash
kubectl create -f single-pod.yaml
kubectl create -f multi-pod.yaml
kubectl create -f init-container-pod.yaml
kubectl create -f env-pod.yaml
kubectl create -f liveness-pod.yaml
```

정리:

```bash
kubectl delete pod --all
```
