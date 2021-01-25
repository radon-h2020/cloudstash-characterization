variable "ssh_key_path" {
  default = "secrets/key"
  description = "path to private ssh key file"
}

variable "ssh_pubkey_path" {
  default = "secrets/key.pub"
  description = "path to public ssh key file"
}

variable "cloudstash_deployment_key" {
  default = "secrets/deploy_key"
  description = "path to deployment key for cloudstash git repository"
}

variable "region" {
  default = "eu-north-1"
  description = "which aws datacenter to create resources in"
}

variable "cloudstash_repository" {
  description = "the url to the cloudstash repository"
}

variable "cloudstash_git_host" {
  description = "the hostname of the git host for the cloudstash repository"
}
