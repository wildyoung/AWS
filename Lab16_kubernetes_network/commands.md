# Lab16 Commands

이 문서는 Kubernetes Network 실습에 사용한 주요 AWS CLI와 kubectl 명령을 정리한 것입니다. 실제 실행은 SSM Run Command로 수행했습니다.

## 1. CloudFormation 템플릿 검증

```bash
aws cloudformation validate-template \
  --template-body file://Lab16_kubernetes_network/templates/k3s_network_single_node.yaml \
  --region ap-northeast-2
```

## 2. k3s 실습 환경 생성

```bash
aws cloudformation create-stack \
  --stack-name lab16-kubernetes-network \
  --template-body file://Lab16_kubernetes_network/templates/k3s_network_single_node.yaml \
  --capabilities CAPABILITY_IAM \
  --region ap-northeast-2

aws cloudformation wait stack-create-complete \
  --stack-name lab16-kubernetes-network \
  --region ap-northeast-2
```

## 3. 클러스터 준비 확인

```bash
sudo k3s kubectl wait --for=condition=Ready node --all --timeout=300s
sudo k3s kubectl -n kube-system rollout status deployment/traefik --timeout=300s
sudo k3s kubectl get nodes -o wide
sudo k3s kubectl get svc -A
```

## 4. Pod IP 변경 확인

```bash
sudo k3s kubectl run nginx-web1 --image=nginx:1.14
sudo k3s kubectl get pods -o wide

sudo k3s kubectl delete pod nginx-web1
sudo k3s kubectl run nginx-web1 --image=nginx:1.14
sudo k3s kubectl run nginx-web2 --image=nginx:1.14
sudo k3s kubectl get pods -o wide
```

## 5. Single/Multi Container Pod 통신

```bash
sudo k3s kubectl apply -f manifests/single-pod.yaml
SINGLE_IP=$(sudo k3s kubectl get pod single-pod -o jsonpath='{.status.podIP}')
curl "http://$SINGLE_IP"

sudo k3s kubectl apply -f manifests/multi-pod.yaml
MULTI_IP=$(sudo k3s kubectl get pod multi-pod -o jsonpath='{.status.podIP}')
sudo k3s kubectl exec multi-pod -c nginx-container -- \
  sh -c 'echo "Hello My Web from multi-pod" > /usr/share/nginx/html/index.html'
curl "http://$MULTI_IP"

sudo k3s kubectl exec multi-pod -c ubuntu-container -- bash -lc \
  "apt-get update && apt-get install -y curl iputils-ping && ping -c 2 $SINGLE_IP && curl http://localhost"
```

## 6. ClusterIP Service와 Endpoints

```bash
sudo k3s kubectl apply -f manifests/hello-cip-svc.yaml
sudo k3s kubectl get service hello-svc
sudo k3s kubectl get endpoints hello-svc

sudo k3s kubectl apply -f manifests/hello-app.yaml
sudo k3s kubectl rollout status deployment/deploy-hello --timeout=300s
sudo k3s kubectl get pods -l app=hello-app -o wide
sudo k3s kubectl get endpoints hello-svc

sudo k3s kubectl delete pod -l app=hello-app
sudo k3s kubectl rollout status deployment/deploy-hello --timeout=300s
sudo k3s kubectl get endpoints hello-svc
```

## 7. ClusterIP DNS 접속

```bash
sudo k3s kubectl apply -f manifests/deploy-ubuntu.yaml
sudo k3s kubectl rollout status deployment/ubuntu-deployment --timeout=300s

UBUNTU_POD=$(sudo k3s kubectl get pods -l app=ubuntu -o jsonpath='{.items[0].metadata.name}')
sudo k3s kubectl exec "$UBUNTU_POD" -- \
  curl -s http://hello-svc:8020/hello/
```

## 8. LoadBalancer Service

```bash
sudo k3s kubectl apply -f manifests/hello-lb-svc.yaml
sudo k3s kubectl apply -f manifests/world-lb-svc.yaml
sudo k3s kubectl apply -f manifests/world-app.yaml

sudo k3s kubectl get service hello-svc world-svc
curl http://127.0.0.1:8020/hello/
curl http://127.0.0.1:8050/world/
```

외부 확인:

```bash
curl http://<public-ip>:8020/hello/
curl http://<public-ip>:8050/world/
```

## 9. Ingress

```bash
sudo k3s kubectl apply -f manifests/my-svc.yaml
sudo k3s kubectl apply -f manifests/my-ingress.yaml

sudo k3s kubectl get service hello-svc world-svc
sudo k3s kubectl get ingress my-ingress
curl http://127.0.0.1/hello/
curl http://127.0.0.1/world/
```

외부 확인:

```bash
curl http://<public-ip>/hello/
curl http://<public-ip>/world/
```

## 10. 실습 정리

```bash
sudo k3s kubectl delete ingress my-ingress --ignore-not-found=true
sudo k3s kubectl delete service hello-svc world-svc --ignore-not-found=true
sudo k3s kubectl delete deployment deploy-hello world-app-deployment ubuntu-deployment --ignore-not-found=true
sudo k3s kubectl delete pod nginx-web1 nginx-web2 single-pod multi-pod --ignore-not-found=true

aws cloudformation delete-stack \
  --stack-name lab16-kubernetes-network \
  --region ap-northeast-2

aws cloudformation wait stack-delete-complete \
  --stack-name lab16-kubernetes-network \
  --region ap-northeast-2
```
