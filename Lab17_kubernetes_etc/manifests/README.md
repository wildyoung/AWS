# Kubernetes Etc Manifests

Lab17 Kubernetes 기타 요소 실습에서 사용하는 YAML 예제입니다.

| 파일 | 용도 |
| --- | --- |
| `mysql-emptydir.yaml` | `emptyDir` 임시 볼륨을 사용하는 MySQL Deployment |
| `cre-pvpvc.yaml` | hostPath 기반 PersistentVolume과 PersistentVolumeClaim |
| `mysql-pvc.yaml` | PVC를 사용하는 MySQL Deployment |
| `mysql-configmap.yaml` | MySQL 전체 환경 변수를 ConfigMap으로 관리 |
| `mysql-configmap-new.yaml` | 비밀번호를 Secret으로 분리한 뒤 사용하는 ConfigMap |
| `mysql-secret.yaml` | MySQL 비밀번호를 담은 Secret 예제 |
| `mysql-pvc-configmap.yaml` | PVC + ConfigMap 기반 MySQL Deployment |
| `mysql-pvc-new.yaml` | PVC + ConfigMap + Secret 기반 MySQL Deployment |

원본 실습 의도를 유지하되, MySQL readinessProbe는 실제 환경 변수와 맞도록 `-p1234`로 정리했습니다.
