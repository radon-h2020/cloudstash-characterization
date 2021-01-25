# EC2 Instance

This directory contains sample code to create EC2 instance in Stockholm (eu-north-1)

## Step 1: Create keys

When prompted for filename/path enter: key

```sh
mkdir ssh_key
ssh-keygen -t rsa -b 4096 -f secrets/key
```

Set stricter file permissions on keys
```sh
chmod 400 secrets/key*
```
### Add deployment key for cloudstash

Key should be stored in `secrets/deploy_key` and `deploy_key.pub`

### Add aws credentials

Create an AWS IAM role that can create lambda/s3/dynamodb resources and put the `config` and `credentials` files in `secrets/.aws`

## Step 2: Terraform

Make sure that the remote state s3 bucket has been created before applying this module, see `cloudstash-characterization/RemoteStateBucket`.

```sh
terraform init --reconfigure
terraform validate
terraform plan
terraform apply
```

## Step 3: SSH

Use `terraform output` to grap the ip, use `tr` to strip the quotes from the output.

```sh
ssh -i secrets/key ubuntu@$(terraform output public_ip | tr -d '"')
```

Or simply:

```sh
ssh -i secrets/key ubuntu@$<ip>
```
