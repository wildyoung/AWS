# Lab15 Verification

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

## Controller 실습

| 실습 | 결과 |
| --- | --- |
| Deployment 기본 생성 | Deployment, ReplicaSet, Pod 3개 생성 확인 |
| ReplicationController | Pod 삭제 후 재생성, scale 확인 |
| ReplicaSet | `matchExpressions` selector와 orphan cascade 확인 |
| Deployment self-healing | Pod/ReplicaSet 삭제 후 재생성 확인 |
| Rolling update | `nginx:1.14`에서 `1.18`까지 변경 확인 |
| Rollback | `kubectl rollout undo`로 이전 revision 복구 확인 |
| Rolling strategy | `maxSurge=25%`, `maxUnavailable=25%` 확인 |
| DaemonSet | 단일 노드에서 Pod 1개 실행 확인 |
| Job | `Complete 1/1`, `Hello, Kubernetes!` 로그 확인 |
| CronJob | 2분 주기 Job 생성과 로그 확인 |
| StatefulSet | ordinal 유지, scale out/in 확인 |
| Kubernetes cleanup | 실습 리소스 삭제 확인 |
| AWS cleanup | CloudFormation 스택 삭제 완료 |

## 캡처

- [Deployment ReplicaSet Pod](images/capture_01_deployment_replication.png)
- [ReplicationController ReplicaSet](images/capture_02_rc_rs.png)
- [Deployment rollout](images/capture_03_deployment_rollout.png)
- [DaemonSet Job CronJob](images/capture_04_daemon_job_cron.png)
- [StatefulSet cleanup](images/capture_05_statefulset_cleanup.png)

## 비용 정리

실습 캡처 저장 후 `lab15-kubernetes-controller` CloudFormation 스택을 삭제했습니다.
