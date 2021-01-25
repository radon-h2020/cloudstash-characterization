# Remote State Bucket

Terraform code to create an s3 bucket to use as a remote backend for terraform state files for the rest of the project.
The bucket should be created before creating any of the other terraform modules.

## Create the bucket

```sh
terraform init
terraform apply
```

## Use the bucket as backend

Each project should contain a `terraform.tf` that configures the module to use the bucket as backend:
Note that it is not possible to use variables here.

```terraform
terraform {
  # configure s3 backend
  # variables are not allowed in this config block
  # as variables are created after terraform initialization
  # therefore YOU MUST ENSURE THAT THEY ARE CORRECT!
  backend "s3" {
    bucket = "cloudstash-characterization-terraform-state"
    # key is name of the terraform state file
    key = "<project_name>.tfstate"
    region = "eu-north-1"
  }
}
```

Then `$ terraform init` should report the s3 backend was successfully configured.

If you get the `NoSuckBucket` error, use the `--reconfigure` flag with init to initialize terraform from a clean state.

This configuration assumes that you are logged in to the aws-cli with the same account for both the bucket and the project.
