# Lab14 Kubernetes Pod Commands

이 파일은 Lab14 Kubernetes Pod 실습을 AWS CLI와 kubectl로 재현하기 위한 명령 모음입니다.

## 1. CloudFormation 템플릿 검증

```bash
aws cloudformation validate-template \
  --template-body file://Lab14_kubernetes_pod/templates/k3s_single_node.yaml \
  --region ap-northeast-2
```

## 2. k3s 실습 환경 생성

```bash
aws cloudformation create-stack \
  --stack-name lab14-kubernetes-pod \
  --template-body file://Lab14_kubernetes_pod/templates/k3s_single_node.yaml \
  --capabilities CAPABILITY_IAM \
  --region ap-northeast-2

aws cloudformation wait stack-create-complete \
  --stack-name lab14-kubernetes-pod \
  --region ap-northeast-2
```

인스턴스 ID를 조회합니다.

```bash
INSTANCE_ID=$(aws cloudformation describe-stacks \
  --stack-name lab14-kubernetes-pod \
  --region ap-northeast-2 \
  --query "Stacks[0].Outputs[?OutputKey=='InstanceId'].OutputValue" \
  --output text)
```

## 3. k3s와 kubectl 확인

EC2 내부에서 실행합니다.

```bash
export KUBECONFIG=/home/ec2-user/.kube/config

kubectl get nodes -o wide
kubectl get pods -A -o wide
```

## 4. Pod IP 할당 방식 확인

```bash
kubectl run nginx-web1 --image=nginx:1.14
kubectl wait --for=condition=Ready pod/nginx-web1 --timeout=180s
kubectl get pods nginx-web1 -o wide

kubectl delete pod nginx-web1

kubectl run nginx-web1 --image=nginx:1.14
kubectl wait --for=condition=Ready pod/nginx-web1 --timeout=180s
kubectl get pods nginx-web1 -o wide

kubectl run nginx-web2 --image=nginx:1.14
kubectl wait --for=condition=Ready pod/nginx-web2 --timeout=180s
kubectl get pods -o wide
```

## 5. Single Container Pod

```bash
kubectl create -f Lab14_kubernetes_pod/manifests/single-pod.yaml
kubectl wait --for=condition=Ready pod/single-pod --timeout=180s
kubectl get pods single-pod -o wide

SINGLE_IP=$(kubectl get pod single-pod -o jsonpath='{.status.podIP}')
curl -s "http://${SINGLE_IP}" | sed -n '1,6p'
```

## 6. Multi Container Pod

```bash
kubectl create -f Lab14_kubernetes_pod/manifests/multi-pod.yaml
kubectl wait --for=condition=Ready pod/multi-pod --timeout=240s
kubectl get pods multi-pod -o wide
kubectl describe pod multi-pod

MULTI_IP=$(kubectl get pod multi-pod -o jsonpath='{.status.podIP}')
curl -s "http://${MULTI_IP}" | sed -n '1,6p'
```

Nginx 컨테이너의 index.html을 수정합니다.

```bash
kubectl exec multi-pod -c nginx-container -- \
  /bin/sh -c 'echo "Hello My Web" > /usr/share/nginx/html/index.html'

curl -s "http://${MULTI_IP}"
```

Ubuntu 컨테이너에서 single-pod로 ping하고, 같은 Pod 안의 Nginx를 localhost로 호출합니다.

```bash
kubectl exec multi-pod -c ubuntu-container -- /bin/sh -c \
  "apt-get update >/dev/null && \
   apt-get install -y curl iputils-ping >/dev/null && \
   ping -c 3 ${SINGLE_IP} && \
   curl -s localhost"
```

## 7. LivenessProbe

```bash
kubectl create -f Lab14_kubernetes_pod/manifests/liveness-pod.yaml
kubectl wait --for=condition=Ready pod/liveness-pod --timeout=180s
kubectl get pod liveness-pod -o wide

kubectl exec liveness-pod -- /bin/sh -c 'nginx -s stop'
kubectl get pod liveness-pod -o wide
kubectl describe pod liveness-pod
```

`RESTARTS` 값이 증가하면 kubelet이 컨테이너를 재시작한 것입니다.

## 8. Init Container

```bash
kubectl create -f Lab14_kubernetes_pod/manifests/init-container-pod.yaml
kubectl wait --for=condition=Ready pod/init-container-pod --timeout=180s
kubectl get pod init-container-pod -o wide
kubectl logs init-container-pod -c init-myservice
kubectl logs init-container-pod -c myapp-container --tail=20
kubectl describe pod init-container-pod
```

`describe` 결과에서 init container의 `State: Terminated`, `Reason: Completed`, `Exit Code: 0`을 확인합니다.

## 9. Environment Variable

```bash
kubectl create -f Lab14_kubernetes_pod/manifests/env-pod.yaml
kubectl wait --for=condition=Ready pod/env-var-pod --timeout=180s
kubectl logs env-var-pod
kubectl exec env-var-pod -- /bin/sh -c 'echo $MY_ENV_VAR'
kubectl get pod env-var-pod -o wide
```

## 10. Pod 정리

```bash
kubectl get pods -o wide
kubectl delete pod --all
kubectl get pods
```

## 11. AWS 리소스 삭제

```bash
aws cloudformation delete-stack \
  --stack-name lab14-kubernetes-pod \
  --region ap-northeast-2

aws cloudformation wait stack-delete-complete \
  --stack-name lab14-kubernetes-pod \
  --region ap-northeast-2
```
