# Lab13 Kubernetes Basic Commands

이 파일은 Lab13 Kubernetes Basic 실습을 AWS CLI와 kubectl로 재현하기 위한 명령 모음입니다.

## 1. CloudFormation 템플릿 검증

```bash
aws cloudformation validate-template \
  --template-body file://Lab13_kubernetes_basic/templates/k3s_single_node.yaml \
  --region ap-northeast-2
```

## 2. k3s 실습 환경 생성

```bash
aws cloudformation create-stack \
  --stack-name lab13-kubernetes-basic \
  --template-body file://Lab13_kubernetes_basic/templates/k3s_single_node.yaml \
  --capabilities CAPABILITY_IAM \
  --region ap-northeast-2

aws cloudformation wait stack-create-complete \
  --stack-name lab13-kubernetes-basic \
  --region ap-northeast-2
```

인스턴스 ID를 조회합니다.

```bash
INSTANCE_ID=$(aws cloudformation describe-stacks \
  --stack-name lab13-kubernetes-basic \
  --region ap-northeast-2 \
  --query "Stacks[0].Outputs[?OutputKey=='InstanceId'].OutputValue" \
  --output text)
```

SSM 연결 상태를 확인합니다.

```bash
aws ssm describe-instance-information \
  --region ap-northeast-2 \
  --filters Key=InstanceIds,Values="$INSTANCE_ID" \
  --query 'InstanceInformationList[0].PingStatus' \
  --output text
```

## 3. k3s 설치 확인

```bash
aws ssm send-command \
  --region ap-northeast-2 \
  --instance-ids "$INSTANCE_ID" \
  --document-name AWS-RunShellScript \
  --comment "Lab13 k3s readiness" \
  --parameters commands='[
    "systemctl status k3s --no-pager | sed -n 1,18p",
    "sudo -u ec2-user KUBECONFIG=/home/ec2-user/.kube/config kubectl get nodes -o wide",
    "sudo -u ec2-user KUBECONFIG=/home/ec2-user/.kube/config kubectl get pods -A"
  ]'
```

## 4. kubectl 기본 조회

EC2 안에서 실행하는 명령입니다.

```bash
export KUBECONFIG=/home/ec2-user/.kube/config

kubectl get nodes
kubectl get nodes -o wide
kubectl get pods -A
kubectl get services -A
kubectl api-resources
```

## 5. Deployment 생성과 삭제

```bash
kubectl create deployment nginx --image=nginx:1.25
kubectl rollout status deployment/nginx --timeout=180s
kubectl get deployments,pods -o wide
kubectl delete deployment nginx
```

## 6. 단일 Pod 실행

```bash
kubectl run webserver --image=nginx:1.14 --port=80
kubectl wait --for=condition=Ready pod/webserver --timeout=180s
kubectl get pods -o wide
kubectl describe pod webserver
kubectl logs webserver --tail=20
kubectl delete pod webserver
```

## 7. Namespace 실습

```bash
kubectl get namespace
kubectl create namespace lab13
kubectl run ns-nginx --image=nginx:1.25 --port=80 --namespace=lab13
kubectl wait --for=condition=Ready pod/ns-nginx --namespace=lab13 --timeout=180s
kubectl get pods --namespace=lab13 -o wide
kubectl config set-context --current --namespace=lab13
kubectl config view --minify | grep namespace
kubectl config set-context --current --namespace=default
kubectl delete namespace lab13
```

## 8. YAML manifest 적용

EC2 안에서 바로 실행할 수 있도록 실습 YAML을 `/tmp`에 생성합니다. 같은 내용의 예제 파일은 [manifests/nginx-deployment-service.yaml](manifests/nginx-deployment-service.yaml)에 있습니다.

```bash
cat <<'YAML' > /tmp/nginx-deployment-service.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-deployment
  labels:
    app: myapp
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
    spec:
      containers:
        - name: nginx
          image: nginx:1.25
          ports:
            - containerPort: 80
---
apiVersion: v1
kind: Service
metadata:
  name: my-service
spec:
  selector:
    app: myapp
  ports:
    - protocol: TCP
      port: 80
      targetPort: 80
  type: ClusterIP
YAML

kubectl apply -f /tmp/nginx-deployment-service.yaml
kubectl rollout status deployment/my-deployment --timeout=180s
kubectl get deployment my-deployment
kubectl get pods -l app=myapp -o wide
kubectl get service my-service
```

Service ClusterIP로 Nginx 응답을 확인합니다.

```bash
SVC_IP=$(kubectl get service my-service -o jsonpath='{.spec.clusterIP}')
curl -s "http://${SVC_IP}" | sed -n '1,6p'
```

정리합니다.

```bash
kubectl delete -f /tmp/nginx-deployment-service.yaml
```

## 9. AWS 리소스 삭제

```bash
aws cloudformation delete-stack \
  --stack-name lab13-kubernetes-basic \
  --region ap-northeast-2

aws cloudformation wait stack-delete-complete \
  --stack-name lab13-kubernetes-basic \
  --region ap-northeast-2
```
