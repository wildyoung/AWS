# Lab4 Storage Commands

실제 계정 ID, 퍼블릭 IP, 버킷 이름, EFS ID, 볼륨 ID, 스냅샷 ID, 키 파일 내용은 문서에 남기지 않습니다. 아래 명령어는 실습 흐름을 재현할 수 있도록 플레이스홀더로 정리했습니다.

## EBS 볼륨 생성과 연결

```bash
VOL1=$(aws ec2 create-volume \
  --availability-zone ap-northeast-2a \
  --size 10 \
  --volume-type gp3 \
  --tag-specifications 'ResourceType=volume,Tags=[{Key=Name,Value=myweb01-vol01},{Key=Lab,Value=Lab4}]' \
  --query VolumeId \
  --output text)
```

```bash
aws ec2 wait volume-available --volume-ids "$VOL1"
aws ec2 attach-volume \
  --volume-id "$VOL1" \
  --instance-id <MY_WEB01_INSTANCE_ID> \
  --device /dev/sdf
aws ec2 wait volume-in-use --volume-ids "$VOL1"
```

## EC2 내부 파티션, XFS 포맷, 마운트

```bash
sudo apt-get install -y xfsprogs cloud-guest-utils parted
sudo parted -s /dev/nvme1n1 mklabel gpt mkpart primary xfs 1MiB 100%
sudo partprobe /dev/nvme1n1
sudo mkfs.xfs -f /dev/nvme1n1p1
sudo mkdir -p /data01
sudo mount /dev/nvme1n1p1 /data01
df -Th /data01
```

```bash
UUID=$(sudo blkid -s UUID -o value /dev/nvme1n1p1)
echo "UUID=$UUID /data01 xfs defaults,nofail 0 2" | sudo tee -a /etc/fstab
sudo umount /data01
sudo mount -a
```

## EBS 볼륨 확장

```bash
aws ec2 modify-volume \
  --volume-id "$VOL1" \
  --size 20
```

```bash
sudo growpart /dev/nvme1n1 1
sudo xfs_growfs -d /data01
lsblk /dev/nvme1n1
df -Th /data01
```

## EBS 스냅샷과 복구 볼륨

```bash
SNAP=$(aws ec2 create-snapshot \
  --volume-id "$VOL1" \
  --description 'Lab4 EBS snapshot from myweb01-vol01' \
  --tag-specifications 'ResourceType=snapshot,Tags=[{Key=Name,Value=myvolume-snap},{Key=Lab,Value=Lab4}]' \
  --query SnapshotId \
  --output text)
aws ec2 wait snapshot-completed --snapshot-ids "$SNAP"
```

```bash
VOL2=$(aws ec2 create-volume \
  --availability-zone ap-northeast-2a \
  --snapshot-id "$SNAP" \
  --volume-type gp3 \
  --tag-specifications 'ResourceType=volume,Tags=[{Key=Name,Value=myweb02-snapshot-vol},{Key=Lab,Value=Lab4}]' \
  --query VolumeId \
  --output text)
```

```bash
aws ec2 attach-volume \
  --volume-id "$VOL2" \
  --instance-id <MY_WEB02_INSTANCE_ID> \
  --device /dev/sdg
```

```bash
sudo mkdir -p /dir1
sudo mount /dev/nvme1n1p1 /dir1
df -Th /dir1
cat /dir1/lab4-ebs.txt
```

## EFS 생성과 Mount Target

```bash
aws ec2 authorize-security-group-ingress \
  --group-id <MY_WEB_SG_ID> \
  --ip-permissions '[{"IpProtocol":"tcp","FromPort":2049,"ToPort":2049,"UserIdGroupPairs":[{"GroupId":"<MY_WEB_SG_ID>"}]}]'
```

```bash
EFS_ID=$(aws efs create-file-system \
  --creation-token lab4-my-efs \
  --performance-mode generalPurpose \
  --throughput-mode bursting \
  --encrypted \
  --tags Key=Name,Value=my-efs Key=Lab,Value=Lab4 \
  --query FileSystemId \
  --output text)
```

```bash
aws efs create-mount-target \
  --file-system-id "$EFS_ID" \
  --subnet-id <MY_SUB01_ID> \
  --security-groups <MY_WEB_SG_ID>
```

```bash
aws efs create-mount-target \
  --file-system-id "$EFS_ID" \
  --subnet-id <MY_SUB02_ID> \
  --security-groups <MY_WEB_SG_ID>
```

## EC2에서 EFS 마운트

```bash
sudo apt-get update
sudo apt-get install -y nfs-common
sudo mkdir -p /home/ubuntu/efs
sudo mount -t nfs4 \
  -o nfsvers=4.1,rsize=1048576,wsize=1048576,hard,timeo=600,retrans=2,noresvport \
  <EFS_ID>.efs.ap-northeast-2.amazonaws.com:/ \
  /home/ubuntu/efs
sudo chown ubuntu:ubuntu /home/ubuntu/efs
chmod 775 /home/ubuntu/efs
echo "my-web01 logged in at $(date)" >> /home/ubuntu/efs/session.log
cat /home/ubuntu/efs/session.log
```

## S3 객체 업로드와 공개 확인

```bash
aws s3api create-bucket \
  --bucket <OBJECT_BUCKET_NAME> \
  --region ap-northeast-2 \
  --create-bucket-configuration LocationConstraint=ap-northeast-2
```

```bash
aws s3api put-bucket-ownership-controls \
  --bucket <OBJECT_BUCKET_NAME> \
  --ownership-controls 'Rules=[{ObjectOwnership=BucketOwnerPreferred}]'
```

```bash
aws s3api put-public-access-block \
  --bucket <OBJECT_BUCKET_NAME> \
  --public-access-block-configuration BlockPublicAcls=false,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=false
```

```bash
aws s3 cp cat1.jpeg s3://<OBJECT_BUCKET_NAME>/cat1.jpeg
curl -I https://<OBJECT_BUCKET_NAME>.s3.ap-northeast-2.amazonaws.com/cat1.jpeg
aws s3api put-object-acl \
  --bucket <OBJECT_BUCKET_NAME> \
  --key cat1.jpeg \
  --acl public-read
curl -I https://<OBJECT_BUCKET_NAME>.s3.ap-northeast-2.amazonaws.com/cat1.jpeg
```

## S3 정적 웹사이트 호스팅

```bash
aws s3api create-bucket \
  --bucket <SITE_BUCKET_NAME> \
  --region ap-northeast-2 \
  --create-bucket-configuration LocationConstraint=ap-northeast-2
```

```bash
aws s3api put-public-access-block \
  --bucket <SITE_BUCKET_NAME> \
  --public-access-block-configuration BlockPublicAcls=false,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=false
```

```bash
aws s3api put-bucket-website \
  --bucket <SITE_BUCKET_NAME> \
  --website-configuration '{"IndexDocument":{"Suffix":"index.html"},"ErrorDocument":{"Key":"index.html"}}'
```

```bash
aws s3api put-bucket-policy \
  --bucket <SITE_BUCKET_NAME> \
  --policy '{
    "Version": "2012-10-17",
    "Statement": [
      {
        "Sid": "PublicReadForStaticWebsite",
        "Effect": "Allow",
        "Principal": "*",
        "Action": "s3:GetObject",
        "Resource": "arn:aws:s3:::<SITE_BUCKET_NAME>/*"
      }
    ]
  }'
```

```bash
aws s3 sync s3_mysite/ s3://<SITE_BUCKET_NAME>/ --delete
curl -I http://<SITE_BUCKET_NAME>.s3-website.ap-northeast-2.amazonaws.com
```

## 정리 명령어

```bash
aws ec2 detach-volume --volume-id "$VOL1"
aws ec2 delete-volume --volume-id "$VOL1"
aws ec2 detach-volume --volume-id "$VOL2"
aws ec2 delete-volume --volume-id "$VOL2"
aws ec2 delete-snapshot --snapshot-id "$SNAP"
```

```bash
aws efs delete-mount-target --mount-target-id <MOUNT_TARGET_ID>
aws efs delete-file-system --file-system-id "$EFS_ID"
```

```bash
aws s3 rm s3://<OBJECT_BUCKET_NAME>/ --recursive
aws s3api delete-bucket --bucket <OBJECT_BUCKET_NAME>
aws s3 rm s3://<SITE_BUCKET_NAME>/ --recursive
aws s3api delete-bucket --bucket <SITE_BUCKET_NAME>
```
