# Lab15 Commands

이 문서는 Kubernetes Controller 실습에 사용한 주요 AWS CLI와 kubectl 명령을 정리한 것입니다. 실제 실행은 SSM Run Command로 수행했습니다.

## 1. CloudFormation 템플릿 검증

```bash
aws cloudformation validate-template \
  --template-body file://Lab15_kubernetes_controller/templates/k3s_single_node.yaml \
  --region ap-northeast-2
```

## 2. k3s 실습 환경 생성

```bash
aws cloudformation create-stack \
  --stack-name lab15-kubernetes-controller \
  --template-body file://Lab15_kubernetes_controller/templates/k3s_single_node.yaml \
  --capabilities CAPABILITY_IAM \
  --region ap-northeast-2

aws cloudformation wait stack-create-complete \
  --stack-name lab15-kubernetes-controller \
  --region ap-northeast-2
```

## 3. SSM 접속 상태 확인

```bash
INSTANCE_ID=$(aws cloudformation describe-stacks \
  --stack-name lab15-kubernetes-controller \
  --region ap-northeast-2 \
  --query 'Stacks[0].Outputs[?OutputKey==`InstanceId`].OutputValue' \
  --output text)

aws ssm describe-instance-information \
  --region ap-northeast-2 \
  --filters Key=InstanceIds,Values="$INSTANCE_ID"
```

## 4. 클러스터 준비 확인

```bash
sudo k3s kubectl wait --for=condition=Ready node --all --timeout=300s
sudo k3s kubectl get nodes -o wide
```

## 5. Deployment 기본 구조

```bash
sudo k3s kubectl create deployment webui --image=nginx --replicas=3
sudo k3s kubectl rollout status deployment/webui --timeout=180s
sudo k3s kubectl get deployment webui
sudo k3s kubectl get replicaset -l app=webui
sudo k3s kubectl get pods -l app=webui -o wide
```

## 6. ReplicationController

```bash
sudo k3s kubectl apply -f manifests/rc-nginx.yaml
sudo k3s kubectl get rc rc-nginx
sudo k3s kubectl get pods -l app=webui -o wide --show-labels

POD=$(sudo k3s kubectl get pods -l app=webui -o jsonpath='{.items[0].metadata.name}')
sudo k3s kubectl delete pod "$POD"

sudo k3s kubectl scale rc rc-nginx --replicas=2
sudo k3s kubectl get rc rc-nginx
```

## 7. ReplicaSet

```bash
sudo k3s kubectl apply -f manifests/rs-exam1.yaml
sudo k3s kubectl get rs rs-exam1

sudo k3s kubectl apply -f manifests/rs-nginx.yaml
sudo k3s kubectl get rs rs-nginx
sudo k3s kubectl get pods -l app=webui -o wide --show-labels

sudo k3s kubectl scale rs rs-nginx --replicas=2
sudo k3s kubectl delete rs rs-nginx --cascade=orphan
sudo k3s kubectl get pods -l app=webui -o wide --show-labels
```

## 8. Deployment self-healing

```bash
sudo k3s kubectl apply -f manifests/deploy-nginx.yaml
sudo k3s kubectl rollout status deployment/deploy-nginx --timeout=180s

POD=$(sudo k3s kubectl get pods -l app=webui -o jsonpath='{.items[0].metadata.name}')
sudo k3s kubectl delete pod "$POD"

RS=$(sudo k3s kubectl get rs -l app=webui -o jsonpath='{.items[0].metadata.name}')
sudo k3s kubectl delete rs "$RS"
```

## 9. Rolling update와 rollback

```bash
sudo k3s kubectl apply -f manifests/deploy-exam1.yaml
sudo k3s kubectl annotate deployment app-deploy \
  kubernetes.io/change-cause="version 1.14" \
  --overwrite

for version in 1.15 1.16 1.17 1.18; do
  sudo k3s kubectl set image deployment/app-deploy web=nginx:$version
  sudo k3s kubectl annotate deployment app-deploy \
    kubernetes.io/change-cause="version $version" \
    --overwrite
  sudo k3s kubectl rollout status deployment/app-deploy --timeout=240s
done

sudo k3s kubectl rollout history deployment/app-deploy
sudo k3s kubectl rollout undo deployment/app-deploy
sudo k3s kubectl rollout status deployment/app-deploy --timeout=240s
```

## 10. DaemonSet, Job, CronJob, StatefulSet

```bash
sudo k3s kubectl apply -f manifests/daemonset.yaml
sudo k3s kubectl get daemonset nginx-daemonset

sudo k3s kubectl apply -f manifests/job.yaml
sudo k3s kubectl wait --for=condition=complete job/scheduled-job --timeout=180s
sudo k3s kubectl logs -l app=scheduled-job

sudo k3s kubectl apply -f manifests/cron-job.yaml
sudo k3s kubectl get cronjob hello-cronjob
sudo k3s kubectl get jobs

sudo k3s kubectl apply -f manifests/statefulset.yaml
sudo k3s kubectl rollout status statefulset/simple-statefulset --timeout=240s
sudo k3s kubectl scale statefulset simple-statefulset --replicas=5
sudo k3s kubectl scale statefulset simple-statefulset --replicas=2
```

## 11. 실습 정리

```bash
sudo k3s kubectl delete deployment webui deploy-nginx app-deploy --ignore-not-found=true
sudo k3s kubectl delete rc rc-nginx --ignore-not-found=true
sudo k3s kubectl delete rs rs-nginx rs-exam1 --ignore-not-found=true
sudo k3s kubectl delete daemonset nginx-daemonset --ignore-not-found=true
sudo k3s kubectl delete job scheduled-job --ignore-not-found=true
sudo k3s kubectl delete cronjob hello-cronjob --ignore-not-found=true
sudo k3s kubectl delete statefulset simple-statefulset --ignore-not-found=true
sudo k3s kubectl delete service simple-statefulset --ignore-not-found=true

aws cloudformation delete-stack \
  --stack-name lab15-kubernetes-controller \
  --region ap-northeast-2

aws cloudformation wait stack-delete-complete \
  --stack-name lab15-kubernetes-controller \
  --region ap-northeast-2
```
