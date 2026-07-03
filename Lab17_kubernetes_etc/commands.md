# Lab17 Commands

Lab17 Kubernetes Etc 실습에서 사용한 AWS CLI와 kubectl 명령 흐름입니다. 실제 실습은 SSM Run Command로 원격 EC2의 k3s 클러스터에서 실행했습니다.

## 1. CloudFormation 실습 환경 생성

```bash
aws cloudformation validate-template \
  --template-body file://Lab17_kubernetes_etc/templates/k3s_single_node.yaml \
  --region ap-northeast-2

aws cloudformation create-stack \
  --stack-name lab17-kubernetes-etc \
  --template-body file://Lab17_kubernetes_etc/templates/k3s_single_node.yaml \
  --capabilities CAPABILITY_NAMED_IAM \
  --region ap-northeast-2

aws cloudformation wait stack-create-complete \
  --stack-name lab17-kubernetes-etc \
  --region ap-northeast-2
```

## 2. k3s와 StorageClass 확인

```bash
kubectl get nodes -o wide
kubectl get storageclass
```

## 3. emptyDir 데이터 손실 확인

```bash
kubectl apply -f manifests/mysql-emptydir.yaml
kubectl rollout status deployment/mysql-emptydir --timeout=240s

POD=$(kubectl get pod -l app=mysql-emptydir -o jsonpath='{.items[0].metadata.name}')

kubectl exec "$POD" -- mysql -uroot -p1234 -e "
  CREATE DATABASE IF NOT EXISTS demodb;
  USE demodb;
  CREATE TABLE member(id INT PRIMARY KEY, name VARCHAR(30));
  INSERT INTO member VALUES (101, 'Tom'), (102, 'Jenny');
  SELECT * FROM member;
"

kubectl delete pod "$POD"
kubectl rollout status deployment/mysql-emptydir --timeout=240s

NEW_POD=$(kubectl get pod -l app=mysql-emptydir -o jsonpath='{.items[0].metadata.name}')
kubectl exec "$NEW_POD" -- mysql -uroot -p1234 demodb -e "SHOW TABLES;"
```

## 4. PV/PVC 데이터 유지 확인

```bash
kubectl delete -f manifests/mysql-emptydir.yaml
kubectl apply -f manifests/cre-pvpvc.yaml
kubectl apply -f manifests/mysql-pvc.yaml
kubectl rollout status deployment/mysql-pvc --timeout=240s

POD=$(kubectl get pod -l app=mysql-pvc -o jsonpath='{.items[0].metadata.name}')

kubectl exec "$POD" -- mysql -uroot -p1234 -e "
  CREATE DATABASE IF NOT EXISTS demodb;
  USE demodb;
  CREATE TABLE member(id INT PRIMARY KEY, name VARCHAR(30));
  INSERT INTO member VALUES (101, 'Tom'), (102, 'Jenny')
    ON DUPLICATE KEY UPDATE name=VALUES(name);
  SELECT * FROM member;
"

kubectl delete pod "$POD"
kubectl rollout status deployment/mysql-pvc --timeout=240s

NEW_POD=$(kubectl get pod -l app=mysql-pvc -o jsonpath='{.items[0].metadata.name}')
kubectl exec "$NEW_POD" -- mysql -uroot -p1234 demodb -e "SHOW TABLES; SELECT * FROM member;"
```

## 5. ConfigMap 환경 변수 주입

```bash
kubectl delete -f manifests/mysql-pvc.yaml
kubectl apply -f manifests/mysql-configmap.yaml
kubectl apply -f manifests/mysql-pvc-configmap.yaml
kubectl rollout status deployment/mysql-pvc --timeout=240s

POD=$(kubectl get pod -l app=mysql-pvc -o jsonpath='{.items[0].metadata.name}')
kubectl get configmap mysql-config -o yaml
kubectl exec "$POD" -- env | grep '^MYSQL_' | sort
```

## 6. Secret 분리

```bash
kubectl delete -f manifests/mysql-pvc-configmap.yaml
kubectl apply -f manifests/mysql-secret.yaml
kubectl apply -f manifests/mysql-configmap-new.yaml
kubectl apply -f manifests/mysql-pvc-new.yaml
kubectl rollout status deployment/mysql-pvc --timeout=240s

POD=$(kubectl get pod -l app=mysql-pvc -o jsonpath='{.items[0].metadata.name}')
kubectl get secret mysql-secret -o yaml
kubectl get configmap mysql-config -o yaml
kubectl exec "$POD" -- env | grep '^MYSQL_' | sort
```

## 7. Kubernetes 리소스 정리

```bash
kubectl delete deployment mysql-emptydir mysql-pvc --ignore-not-found=true
kubectl delete service mysql-emptydir mysql-pvc --ignore-not-found=true
kubectl delete configmap mysql-config --ignore-not-found=true
kubectl delete secret mysql-secret --ignore-not-found=true
kubectl delete pvc mysql-pvc --ignore-not-found=true
kubectl delete pv mysql-pv --ignore-not-found=true
sudo rm -rf /home/ec2-user/data/mysql-pv/*

kubectl get all
kubectl get configmap,secret,pv,pvc
```

## 8. CloudFormation 스택 삭제

```bash
aws cloudformation delete-stack \
  --stack-name lab17-kubernetes-etc \
  --region ap-northeast-2

aws cloudformation wait stack-delete-complete \
  --stack-name lab17-kubernetes-etc \
  --region ap-northeast-2
```

## 참고

- `1234`는 실습용 샘플 비밀번호입니다.
- GitHub에 올린 결과 로그에서는 실제 노드 private IP, EC2/VPC ID, Secret 값 등을 마스킹했습니다.
- `hostPath` PV는 단일 노드 학습용입니다. 운영 환경에서는 EBS/EFS CSI 같은 스토리지 드라이버 사용을 권장합니다.
