# Kubernetes Controller Manifests

Lab15 Kubernetes Controller 실습에서 사용하는 YAML 예제입니다.

| 파일 | Controller |
| --- | --- |
| `rc-nginx.yaml` | ReplicationController |
| `rs-nginx.yaml` | ReplicaSet |
| `rs-exam1.yaml` | ReplicaSet matchExpressions |
| `deploy-nginx.yaml` | Deployment 기본 |
| `deploy-exam1.yaml` | Deployment rolling update |
| `deploy-exam2.yaml` | Deployment rolling update strategy |
| `daemonset.yaml` | DaemonSet |
| `job.yaml` | Job |
| `cron-job.yaml` | CronJob |
| `statefulset.yaml` | Headless Service + StatefulSet |
| `redis.yaml` | Label selector 동작 확인용 Pod |

StatefulSet은 최신 Kubernetes에서 `spec.serviceName`이 필요하므로 headless Service를 함께 정의했습니다.
