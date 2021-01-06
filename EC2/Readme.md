# EC2 Instance

This directory contains sample code to create EC2 instance in Stockholm (eu-north-1)

## Step 1: Create keys

When prompted for filename/path enter: key

```sh
mkdir ssh_key
ssh-keygen -t rsa -b 4096 -f ssh_key/key
```

Set stricter file permissions on keys
```sh
chmod 400 ssh_key/key*
```

## Step 2: Terraform

Make sure that the remote state s3 bucket has been created before applying this module, see `cloudstash-characterization/RemoteStateBucket`.

```sh
terraform init
terraform validate
terraform plan
terraform apply
```

## Step 3: SSH

Use terraform output to grap the ip, use tr to strip the quotes from the output.

```sh
ssh -i ssh_key/key ubuntu@$(terraform output public_ip | tr -d '"')
```
