provider "aws" {
  region = "eu-north-1"
}

resource "aws_s3_bucket" "terraform_state" {
  bucket = "cloudstash-characterization-tfstate"
  acl = "private"
  lifecycle {
    prevent_destroy = true
  }
}

# resource "aws_dynamodb_table" "terraform_state_lock" {
  # name           = "app-state"
  # read_capacity  = 1
  # write_capacity = 1
  # hash_key       = "LockID"

  # attribute {
    # name = "LockID"
    # type = "S"
  # }
# }
