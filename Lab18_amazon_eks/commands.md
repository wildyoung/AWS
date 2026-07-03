# Lab18 Commands

Lab18 Amazon EKS 실습에서 사용한 AWS CLI와 kubectl 명령 흐름입니다.

## 1. VPC와 IAM Role 생성

```bash
aws cloudformation validate-template \
  --template-body file://Lab18_amazon_eks/templates/eks_base.yaml \
  --region ap-northeast-2

aws cloudformation create-stack \
  --stack-name lab18-eks-base \
  --template-body file://Lab18_amazon_eks/templates/eks_base.yaml \
  --capabilities CAPABILITY_IAM \
  --region ap-northeast-2 \
  --tags Key=Lab,Value=Lab18AmazonEKS

aws cloudformation wait stack-create-complete \
  --stack-name lab18-eks-base \
  --region ap-northeast-2
```

## 2. CloudFormation Output 조회

```bash
ALL_SUBNETS=$(aws cloudformation describe-stacks \
  --stack-name lab18-eks-base \
  --region ap-northeast-2 \
  --query "Stacks[0].Outputs[?OutputKey=='AllSubnetIds'].OutputValue" \
  --output text)

PUBLIC_SUBNETS=$(aws cloudformation describe-stacks \
  --stack-name lab18-eks-base \
  --region ap-northeast-2 \
  --query "Stacks[0].Outputs[?OutputKey=='PublicSubnetIds'].OutputValue" \
  --output text)

CLUSTER_ROLE=$(aws cloudformation describe-stacks \
  --stack-name lab18-eks-base \
  --region ap-northeast-2 \
  --query "Stacks[0].Outputs[?OutputKey=='ClusterRoleArn'].OutputValue" \
  --output text)

NODE_ROLE=$(aws cloudformation describe-stacks \
  --stack-name lab18-eks-base \
  --region ap-northeast-2 \
  --query "Stacks[0].Outputs[?OutputKey=='NodeRoleArn'].OutputValue" \
  --output text)
```

## 3. EKS Cluster 생성

```bash
aws eks create-cluster \
  --name lab18-eks \
  --kubernetes-version 1.35 \
  --role-arn "$CLUSTER_ROLE" \
  --resources-vpc-config "subnetIds=$ALL_SUBNETS,endpointPublicAccess=true,endpointPrivateAccess=true" \
  --access-config "bootstrapClusterCreatorAdminPermissions=true,authenticationMode=API_AND_CONFIG_MAP" \
  --tags Lab=Lab18AmazonEKS,Name=lab18-eks \
  --region ap-northeast-2

aws eks wait cluster-active \
  --name lab18-eks \
  --region ap-northeast-2

aws eks update-kubeconfig \
  --name lab18-eks \
  --region ap-northeast-2
```

## 4. Managed Node Group 생성

```bash
IFS=',' read -r PUBLIC_SUBNET_1 PUBLIC_SUBNET_2 <<< "$PUBLIC_SUBNETS"

aws eks create-nodegroup \
  --cluster-name lab18-eks \
  --nodegroup-name lab18-nodegroup \
  --node-role "$NODE_ROLE" \
  --subnets "$PUBLIC_SUBNET_1" "$PUBLIC_SUBNET_2" \
  --instance-types t3.small \
  --disk-size 20 \
  --scaling-config minSize=1,maxSize=2,desiredSize=2 \
  --capacity-type ON_DEMAND \
  --tags Lab=Lab18AmazonEKS,Name=lab18-nodegroup \
  --region ap-northeast-2

aws eks wait nodegroup-active \
  --cluster-name lab18-eks \
  --nodegroup-name lab18-nodegroup \
  --region ap-northeast-2

kubectl wait --for=condition=Ready nodes --all --timeout=420s
```

## 5. EKS 기본 확인

```bash
kubectl get nodes -o wide
kubectl get namespaces
kubectl get services
kubectl get endpoints
kubectl get pods -n kube-system
kubectl top nodes || echo "metrics-server is not installed by default"
```

## 6. Pod IP와 VPC CNI 확인

```bash
kubectl run nginx-web --image=nginx:1.25 --restart=Never
kubectl wait --for=condition=Ready pod/nginx-web --timeout=240s
kubectl get pod nginx-web -o wide

kubectl delete pod nginx-web --wait=true

kubectl run nginx-web --image=nginx:1.25 --restart=Never
kubectl wait --for=condition=Ready pod/nginx-web --timeout=240s
kubectl get pod nginx-web -o wide

kubectl delete pod nginx-web --wait=true
```

## 7. Pod와 Pod 통신

```bash
kubectl apply -f manifests/demo_pod.yaml
kubectl wait --for=condition=Ready pod/demo-app --timeout=240s
kubectl get pod demo-app --show-labels

kubectl apply -f manifests/demo_modify.yaml
kubectl get pod demo-app --show-labels

kubectl apply -f manifests/nginx_pod.yaml
kubectl apply -f manifests/apache_pod.yaml
kubectl wait --for=condition=Ready pod/nginx-pod --timeout=240s
kubectl wait --for=condition=Ready pod/apache-pod --timeout=240s

APACHE_IP=$(kubectl get pod apache-pod -o jsonpath='{.status.podIP}')
kubectl exec nginx-pod -- curl -sI --max-time 5 "http://$APACHE_IP"

kubectl apply -f manifests/pod_multi.yaml
kubectl wait --for=condition=Ready pod/multi-pod --timeout=240s
kubectl exec multi-pod -c curl-container -- curl -sI --max-time 5 http://localhost
```

## 8. ReplicaSet과 Deployment

```bash
kubectl apply -f manifests/my_rs.yaml
kubectl wait --for=condition=Ready pod -l app=my-rs --timeout=240s
kubectl get replicasets
kubectl get pods -o wide -l app=my-rs

RS_POD=$(kubectl get pod -l app=my-rs -o jsonpath='{.items[0].metadata.name}')
kubectl delete pod "$RS_POD" --wait=true
kubectl get pods -o wide -l app=my-rs
kubectl delete replicasets my-rs --wait=true

kubectl apply -f manifests/my_deploy.yaml
kubectl rollout status deployment/my-deploy --timeout=240s
kubectl get deployments,replicasets,pods

DEPLOY_POD=$(kubectl get pod -l app=my-deploy -o jsonpath='{.items[0].metadata.name}')
kubectl delete pod "$DEPLOY_POD" --wait=true
kubectl rollout status deployment/my-deploy --timeout=240s

kubectl apply -f manifests/my_deploy_update.yaml
kubectl rollout status deployment/my-deploy --timeout=300s
kubectl get rs,pods -l app=my-deploy
kubectl delete deployment my-deploy --wait=true
```

## 9. Service와 LoadBalancer

```bash
kubectl apply -f manifests/hello_app.yaml
kubectl rollout status deployment/deploy-hello --timeout=240s

kubectl apply -f manifests/hello_cip_svc.yaml
kubectl get services
kubectl get endpoints hello-svc

kubectl apply -f manifests/deploy_ubuntu.yaml
kubectl rollout status deployment/ubuntu-deployment --timeout=240s

CURL_POD=$(kubectl get pod -l app=ubuntu-client -o jsonpath='{.items[0].metadata.name}')
kubectl exec "$CURL_POD" -- curl -s --max-time 5 http://hello-svc

kubectl delete pod -l app=hello-app --wait=true
kubectl rollout status deployment/deploy-hello --timeout=240s
kubectl get endpoints hello-svc
kubectl exec "$CURL_POD" -- curl -s --max-time 5 http://hello-svc

kubectl delete service hello-svc --wait=true
kubectl apply -f manifests/hello_lb_svc.yaml
kubectl get services hello-svc
curl http://<NLB-DNS>:8020
```

## 10. 정리

```bash
kubectl delete service hello-svc --ignore-not-found=true
kubectl delete deployment deploy-hello ubuntu-deployment my-deploy --ignore-not-found=true
kubectl delete replicasets my-rs --ignore-not-found=true
kubectl delete pod nginx-web demo-app nginx-pod apache-pod multi-pod --ignore-not-found=true

aws eks delete-nodegroup \
  --cluster-name lab18-eks \
  --nodegroup-name lab18-nodegroup \
  --region ap-northeast-2

aws eks wait nodegroup-deleted \
  --cluster-name lab18-eks \
  --nodegroup-name lab18-nodegroup \
  --region ap-northeast-2

aws eks delete-cluster \
  --name lab18-eks \
  --region ap-northeast-2

aws eks wait cluster-deleted \
  --name lab18-eks \
  --region ap-northeast-2

aws cloudformation delete-stack \
  --stack-name lab18-eks-base \
  --region ap-northeast-2

aws cloudformation wait stack-delete-complete \
  --stack-name lab18-eks-base \
  --region ap-northeast-2
```

## 참고

- 원본 교안의 `t3.medium`은 현재 계정 정책상 생성이 제한되어 `t3.small`로 조정했습니다.
- `metrics-server`는 이번 EKS 기본 생성에는 자동 설치되지 않았습니다.
- Ingress 실습은 AWS Load Balancer Controller, OIDC, IRSA, Helm 설치가 필요하므로 선택 실습으로 정리했습니다.
