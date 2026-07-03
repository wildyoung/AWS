# Lab14 Verification

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

## Pod 실습

| 실습 | 결과 |
| --- | --- |
| Pod IP 재할당 | 같은 이름의 Pod 삭제/재생성 시 IP 변경 확인 |
| Single Container Pod | `single-pod` Ready, Nginx HTTP 응답 확인 |
| Multi Container Pod | `multi-pod` Ready `2/2` 확인 |
| Multi container IP 공유 | 두 컨테이너가 같은 Pod IP 공유 |
| Pod 내부 localhost 통신 | Ubuntu 컨테이너에서 `curl localhost`로 Nginx 응답 확인 |
| LivenessProbe | Nginx 중지 후 `RESTARTS=1` 확인 |
| Init Container | `init-myservice` Completed 후 main container Running 확인 |
| Environment Variable | 로그와 exec에서 `Hello, Kubernetes!` 확인 |
| Pod cleanup | `kubectl delete pod --all` 완료 |
| AWS cleanup | CloudFormation 스택 삭제 완료 |

## 캡처

- [Pod IP and single pod](images/capture_01_pod_ip_single.png)
- [Multi container pod](images/capture_02_multi_container.png)
- [Liveness probe](images/capture_03_liveness_probe.png)
- [Init container and env](images/capture_04_init_env.png)
- [Cleanup](images/capture_05_cleanup.png)

## 비용 정리

실습 캡처 저장 후 `lab14-kubernetes-pod` CloudFormation 스택을 삭제했습니다.
