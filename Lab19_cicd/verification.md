# Lab19 Verification

검증일: 2026-07-04

## 환경 검증

| 항목 | 결과 |
| --- | --- |
| AWS 리전 | `ap-northeast-2` |
| ECR 기존 Repository | 없음 |
| EKS Cluster | 없음 |
| 로컬 Docker CLI | 설치됨 |
| 로컬 Docker daemon | 실행되지 않음 |
| 실습 방식 | CodeBuild에서 Docker build 수행 |

## 실제 검증 결과

| 단계 | 검증 내용 | 결과 |
| --- | --- | --- |
| 1 | S3 source bundle 업로드 | 성공 |
| 2 | ECR Repository 생성 | `lab19-to-do-app` 생성 |
| 3 | CodeBuild Project 생성 | `lab19-cicd-build` 생성 |
| 4 | CodeBuild privileged mode | Docker build 가능 |
| 5 | `DOWNLOAD_SOURCE` | 성공 |
| 6 | `PRE_BUILD` | ECR login 성공 |
| 7 | `BUILD` | Docker image build/tag 성공 |
| 8 | `POST_BUILD` | ECR push 성공 |
| 9 | ECR image 확인 | `cli-lab` tag 확인 |
| 10 | Cleanup | CodeBuild, ECR, S3, IAM Role, CloudWatch Logs 삭제 |

## CodeBuild Phase 결과

| Phase | 상태 | 시간 |
| --- | --- | --- |
| `SUBMITTED` | `SUCCEEDED` | 0s |
| `QUEUED` | `SUCCEEDED` | 0s |
| `PROVISIONING` | `SUCCEEDED` | 6s |
| `DOWNLOAD_SOURCE` | `SUCCEEDED` | 1s |
| `INSTALL` | `SUCCEEDED` | 0s |
| `PRE_BUILD` | `SUCCEEDED` | 13s |
| `BUILD` | `SUCCEEDED` | 8s |
| `POST_BUILD` | `SUCCEEDED` | 6s |
| `UPLOAD_ARTIFACTS` | `SUCCEEDED` | 0s |
| `FINALIZING` | `SUCCEEDED` | 0s |

## ECR 이미지 결과

| 항목 | 값 |
| --- | --- |
| Repository | `lab19-to-do-app` |
| Tag | `cli-lab` |
| Digest | `sha256:124a63363d7af8d2c8182ca77b077a16e0971013e94e5641084221f6ed5e7b35` |
| Size | `49320063` bytes |

## 미실행 범위와 이유

| 범위 | 이유 |
| --- | --- |
| GitHub PAT 연결 | PAT는 개인 민감 정보라 임의 생성/입력하지 않음 |
| GitHub Webhook 자동 트리거 | PAT와 GitHub 저장소 권한 연결 필요 |
| Argo CD 실제 설치 | 지속 EKS Cluster가 필요하고 비용이 발생함 |
| EKS LoadBalancer 접속 | EKS/Argo CD 미유지 방침에 따라 절차와 개념으로 정리 |

## Cleanup 검증

| 리소스 | 결과 |
| --- | --- |
| CodeBuild Project | 목록 비어 있음 |
| ECR Repository | 목록 비어 있음 |
| S3 Lab Bucket | 목록 비어 있음 |
| IAM Role | 목록 비어 있음 |
| CloudWatch Log Group | 목록 비어 있음 |
| EKS Cluster | 목록 비어 있음 |

## 결과 로그

마스킹된 실행 로그는 [results/codebuild_result_sanitized.txt](results/codebuild_result_sanitized.txt)에 저장했습니다.

다음 값은 공개 저장소에 노출되지 않도록 마스킹했습니다.

- AWS Account ID
- ECR repository URI의 account ID
- IAM Role ARN의 account ID
- 임시 S3 bucket 이름
- AWS Console deep link

## 결론

이번 검증으로 CodeBuild가 소스 번들을 받아 Docker 이미지를 빌드하고 ECR에 push하는 CI 구간을 실제로 확인했습니다. GitHub Webhook과 Argo CD 기반 CD 구간은 PAT와 지속 EKS 리소스가 필요하므로 문서화 중심으로 정리했습니다.
