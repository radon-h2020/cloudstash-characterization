terraform {
  # configure s3 backend
  # variables are not allowed in this config block
  # as variables are created after terraform initialization
  # therefore YOU MUST ENSURE THAT THEY ARE CORRECT!
  backend "s3" {
    bucket = "cloudstash-characterization-terraform-state"
    # key is name of the terraform state file
    key = "ec2_orchestrator.tfstate"
    region = "eu-north-1"
  }
}
