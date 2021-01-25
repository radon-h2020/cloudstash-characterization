provider "aws" {
  region = "eu-north-1"
}

resource "aws_s3_bucket" "terraform_state" {
  bucket = "cloudstash-characterization-terraform-state"
  acl = "private"

  # allow delete bucket with things in it
  force_destroy = true

  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_s3_bucket_public_access_block" "no_public_access_to_bucket" {
  bucket = aws_s3_bucket.terraform_state.id

  block_public_acls   = true
  block_public_policy = true
}
