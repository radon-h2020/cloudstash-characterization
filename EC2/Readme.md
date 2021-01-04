# EC2 Instance

This directory contains sample code to create EC2 instance in Stockholm (eu-north-1)

## Step 1: Create keys

When prompted for filename/path enter: key

```
ssh-keygen -t rsa 
```

```
chmod 400 key*
```

## Step 2: Terraform

```
terraform init
terraform plan
terraform apply
```

## Step 3: Provision

Currently done with ssh. See ip in output after terraform apply

```
ssh -i key ubuntu@[ip]
```
