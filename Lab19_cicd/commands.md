# Lab19 Commands

실습 명령은 원본 GitHub 기반 흐름과 이번 AWS CLI 검증 흐름으로 나누어 정리했습니다. 실제 계정 ID, GitHub 토큰, ECR URI는 기록하지 않습니다.

## 1. 원본 실습 흐름

### ECR Repository 생성

```bash
aws ecr create-repository \
  --repository-name to-do-app \
  --image-scanning-configuration scanOnPush=true \
  --region ap-northeast-2
```

### GitHub 저장소 준비

```bash
git clone https://github.com/<GITHUB_USERNAME>/to-do-app.git
cd to-do-app
git branch -M main
```

GitHub PAT는 CodeBuild 환경변수 `GITHUB_TOKEN`으로만 넣고 파일에는 저장하지 않습니다.

### CodeBuild 환경변수

| 이름 | 값 |
| --- | --- |
| `GITHUB_TOKEN` | GitHub Personal Access Token |
| `GITHUB_USERNAME` | GitHub 사용자 이름 |

### CodeBuild Webhook 필터

`[skip ci]`가 들어간 commit은 다시 빌드를 시작하지 않도록 제외합니다.

| 항목 | 값 |
| --- | --- |
| 조건 | `DO_NOT_START_BUILD` |
| 이벤트 | `COMMIT_MESSAGE` |
| 패턴 | `.*\\[skip ci\\].*` |

### Argo CD 설치

```bash
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
kubectl get all -n argocd
```

### Argo CD Application 적용

```bash
kubectl apply -f todoapp_argo.yaml -n argocd
kubectl get deploy,rs,pods
kubectl get services
```

### 배포 변경 테스트

```bash
cp Dockerfile.updated Dockerfile
git add Dockerfile
git commit -m "index.html Updated"
git pull --rebase
git push origin main
```

이 push가 CodeBuild를 다시 실행하고, 새 ECR 이미지 태그가 생성되고, Argo CD가 EKS Deployment를 업데이트합니다.

## 2. 이번 AWS CLI 검증 흐름

로컬 Docker 데몬이 실행 중이 아니었기 때문에, Docker build는 CodeBuild에서 수행했습니다. GitHub PAT 없이 검증하기 위해 소스는 S3 zip으로 전달했습니다.

### 임시 ECR Repository 생성

```bash
aws ecr create-repository \
  --repository-name lab19-to-do-app \
  --image-scanning-configuration scanOnPush=true \
  --encryption-configuration encryptionType=AES256 \
  --region ap-northeast-2
```

### 소스 번들 업로드

```bash
zip -qr source.zip .
aws s3api create-bucket \
  --bucket <LAB_BUCKET> \
  --region ap-northeast-2 \
  --create-bucket-configuration LocationConstraint=ap-northeast-2
aws s3 cp source.zip s3://<LAB_BUCKET>/source.zip
```

### CodeBuild Role 생성

```bash
aws iam create-role \
  --role-name lab19-codebuild-service-role \
  --assume-role-policy-document file://codebuild-trust.json

aws iam put-role-policy \
  --role-name lab19-codebuild-service-role \
  --policy-name lab19-codebuild-service-role-policy \
  --policy-document file://codebuild-policy.json
```

### CodeBuild Project 생성

```bash
aws codebuild create-project \
  --name lab19-cicd-build \
  --source type=S3,location=<LAB_BUCKET>/source.zip,buildspec=buildspec.yml \
  --artifacts type=NO_ARTIFACTS \
  --environment type=LINUX_CONTAINER,image=aws/codebuild/standard:7.0,computeType=BUILD_GENERAL1_SMALL,privilegedMode=true \
  --service-role <CODEBUILD_ROLE_ARN> \
  --logs-config cloudWatchLogs='{status=ENABLED,groupName=/aws/codebuild/lab19-cicd-build,streamName=lab19}' \
  --region ap-northeast-2
```

### Build 실행과 확인

```bash
aws codebuild start-build \
  --project-name lab19-cicd-build \
  --region ap-northeast-2

aws codebuild batch-get-builds \
  --ids <BUILD_ID> \
  --region ap-northeast-2

aws ecr describe-images \
  --repository-name lab19-to-do-app \
  --region ap-northeast-2
```

## 3. 정리 명령

```bash
aws codebuild delete-project \
  --name lab19-cicd-build \
  --region ap-northeast-2

aws ecr delete-repository \
  --repository-name lab19-to-do-app \
  --force \
  --region ap-northeast-2

aws s3 rm s3://<LAB_BUCKET> --recursive --region ap-northeast-2
aws s3api delete-bucket --bucket <LAB_BUCKET> --region ap-northeast-2

aws iam delete-role-policy \
  --role-name lab19-codebuild-service-role \
  --policy-name lab19-codebuild-service-role-policy

aws iam delete-role \
  --role-name lab19-codebuild-service-role

aws logs delete-log-group \
  --log-group-name /aws/codebuild/lab19-cicd-build \
  --region ap-northeast-2
```
