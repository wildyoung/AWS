# Lab17 Verification

검증일: 2026-07-04

## 환경 검증

| 항목 | 결과 |
| --- | --- |
| CloudFormation template validation | 성공 |
| CloudFormation stack create | 성공 |
| SSM Run Command | 성공 |
| k3s node | `Ready` |
| Kubernetes version | `v1.36.2+k3s1` |
| StorageClass | `local-path (default)` |
| CloudFormation stack delete | 성공 |

## 실습 검증

| 단계 | 검증 내용 | 결과 |
| --- | --- | --- |
| 1 | `emptyDir` MySQL Pod 생성 | `READY 1/1` |
| 2 | `emptyDir`에 `member` 테이블과 샘플 데이터 생성 | `101 Tom`, `102 Jenny` 조회 |
| 3 | `emptyDir` Pod 삭제 후 재생성 | `SHOW TABLES` 결과 없음 |
| 4 | PV/PVC 생성 | PV `Available`, PVC 바인딩 후 Pod 실행 |
| 5 | PVC에 MySQL 데이터 생성 | `member` 테이블과 샘플 데이터 조회 |
| 6 | PVC Pod 삭제 후 재생성 | `member` 테이블과 데이터 유지 |
| 7 | ConfigMap 적용 | `MYSQL_DATABASE`, `MYSQL_USER` 환경 변수 주입 확인 |
| 8 | Secret 적용 | 비밀번호 값을 Secret으로 분리하고 Pod에 주입 확인 |
| 9 | Kubernetes 리소스 삭제 | 기본 `kubernetes` Service와 `kube-root-ca.crt` ConfigMap만 남음 |
| 10 | AWS 리소스 삭제 | CloudFormation 스택 삭제 완료 |

## 결과 로그

실습 출력은 [results/kubectl_result_sanitized.txt](results/kubectl_result_sanitized.txt)에 저장했습니다.

민감 정보 보호를 위해 다음 값은 마스킹했습니다.

- 실제 AWS Account ID
- EC2 instance ID
- VPC ID
- 노드 private IP
- Kubernetes resource UID
- Secret과 비밀번호 값

## 결론

`emptyDir`은 Pod 수명에 묶인 임시 저장소라 Pod 삭제 후 데이터가 사라졌습니다. 반면 PVC를 사용하는 MySQL Pod는 Pod가 재생성되어도 같은 PersistentVolume을 다시 마운트해 데이터를 유지했습니다. ConfigMap과 Secret은 설정값과 민감값을 Pod 스펙에서 분리해 관리하는 용도로 확인했습니다.
