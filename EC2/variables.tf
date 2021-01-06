variable "ssh_key_path" {
  default = "ssh_key/key"
  description = "path to private ssh key file"
}

variable "ssh_pubkey_path" {
  default = "ssh_key/key.pub"
  description = "path to public ssh key file"
}

variable "region" {
  default = "eu-north-1"
  description = "which aws datacenter to create resources in"
}
