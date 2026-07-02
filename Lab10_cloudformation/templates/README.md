# Lab10 CloudFormation Templates

이 폴더에는 실습에 사용한 CloudFormation YAML 템플릿을 보관했습니다.

| 파일 | 설명 |
| --- | --- |
| `cre_testvpcAll.yaml` | VPC, 퍼블릭 서브넷 2개, EC2 2개를 단일 스택으로 생성 |
| `update_testvpcAll.yaml` | 단일 스택에 프라이빗 서브넷 2개, NAT Gateway, Elastic IP, 프라이빗 라우팅 추가 |
| `cre_myvpc.yaml` | VPC, 퍼블릭 서브넷, 라우팅, 보안 그룹을 생성하고 값을 Export |
| `cre_ec2.yaml` | `!ImportValue`로 네트워크 값을 가져와 EC2 2개 생성 |
| `cre_alb.yaml` | `!ImportValue`로 네트워크 값을 가져와 ALB, Listener, Target Group 생성 |

실행 전 `Your-Keypair-Name` 또는 `Your-Key-Name`을 본인 키페어 이름으로 바꿔야 합니다. 이번 실습은 임시 복사본에서 키페어 이름을 바꾼 뒤 실행했고, 저장소에는 계정 식별자와 실제 ARN을 남기지 않았습니다.

`cre_alb.yaml`은 대상 그룹에 EC2를 등록하는 `AWS::ElasticLoadBalancingV2::TargetGroupAttachment` 리소스를 포함하지 않습니다. ALB로 실제 웹 응답까지 확인하려면 대상 등록 리소스를 추가해야 합니다.
